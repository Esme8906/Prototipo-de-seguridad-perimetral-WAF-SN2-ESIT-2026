import json
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 5050
DEFAULT_TARGET = "http://localhost:8080"

# Almacén en memoria de trazas atómicas
AUDIT_LOGS = []
LOGS_LOCK = threading.Lock()


def record_event(phase, method, path, target_url, status_code, latency_ms, layer, headers, preview, verdict):
    entry = {
        "id": len(AUDIT_LOGS) + 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "phase": phase,
        "method": method,
        "path": path,
        "target_url": target_url,
        "status_code": status_code,
        "latency_ms": round(latency_ms, 2),
        "layer": layer,
        "headers": headers,
        "preview": preview,
        "verdict": verdict,
    }
    with LOGS_LOCK:
        AUDIT_LOGS.append(entry)
    return entry


def send_http_probe(target_base, method, path, json_body=None, headers=None, params=None):
    url = f"{target_base.rstrip('/')}{path}"
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"

    req_headers = {"User-Agent": "WAF-Shield-Telemetry-Monitor/1.0"}
    if headers:
        req_headers.update(headers)

    data_bytes = None
    if json_body is not None:
        data_bytes = json.dumps(json_body).encode("utf-8")
        req_headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data_bytes, headers=req_headers, method=method)
    started = time.perf_counter()

    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            latency = (time.perf_counter() - started) * 1000
            raw = resp.read().decode("utf-8", errors="replace")
            resp_headers = dict(resp.headers.items())
            return resp.status, latency, resp_headers, raw
    except urllib.error.HTTPError as err:
        latency = (time.perf_counter() - started) * 1000
        raw = err.read().decode("utf-8", errors="replace")
        resp_headers = dict(err.headers.items())
        return err.code, latency, resp_headers, raw
    except Exception as exc:
        latency = (time.perf_counter() - started) * 1000
        return 0, latency, {}, f"Error de conexión: {exc}"


def classify_layer(status_code, headers, body_text):
    if status_code == 0:
        return "RED / TIMEOUT", "ERROR"
    content_type = headers.get("Content-Type", headers.get("content-type", ""))
    is_json = "application/json" in content_type.lower()
    if status_code == 403 and not is_json:
        return "PERÍMETRO (WAF / ModSecurity)", "BLOCKED_WAF"
    if status_code == 429:
        return "PERÍMETRO (Rate Limit)", "BLOCKED_RATE"
    if is_json:
        return "BACKEND (Node.js)", "PASSED_TO_APP"
    return "PERÍMETRO / PROXY", "INSPECTED"


def run_audit_sequence(target_base, isolation_delay=2):
    with LOGS_LOCK:
        AUDIT_LOGS.clear()

    # Fase 1: Healthcheck
    st, lat, hdrs, body = send_http_probe(target_base, "GET", "/healthcheck")
    layer, verdict = classify_layer(st, hdrs, body)
    record_event("1. Healthcheck", "GET", "/healthcheck", target_base, st, lat, layer, hdrs, body[:180], verdict)

    # Fase 2: Login Legítimo
    st, lat, hdrs, body = send_http_probe(
        target_base,
        "POST",
        "/login",
        json_body={"email": "estudiante@nova.edu", "password": "Nova2026!"},
    )
    layer, verdict = classify_layer(st, hdrs, body)
    record_event("2. Login Legítimo", "POST", "/login", target_base, st, lat, layer, hdrs, body[:180], verdict)

    token = ""
    if st == 200:
        try:
            token = json.loads(body).get("token", "")
        except Exception:
            token = ""

    # Fase 3: Acceso Post-Login (/dashboard)
    st, lat, hdrs, body = send_http_probe(
        target_base,
        "GET",
        "/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )
    layer, verdict = classify_layer(st, hdrs, body)
    record_event("3. Dashboard Protegido", "GET", "/dashboard", target_base, st, lat, layer, hdrs, body[:180], verdict)

    # Fase 4: Credenciales Inválidas
    st, lat, hdrs, body = send_http_probe(
        target_base,
        "POST",
        "/login",
        json_body={"email": "estudiante@nova.edu", "password": "ClaveIncorrecta123"},
    )
    layer, verdict = classify_layer(st, hdrs, body)
    record_event("4. Credenciales Inválidas", "POST", "/login", target_base, st, lat, layer, hdrs, body[:180], verdict)

    # Fase 5: Ruta Restringida de Aplicación (/admin)
    st, lat, hdrs, body = send_http_probe(target_base, "GET", "/admin")
    layer, verdict = classify_layer(st, hdrs, body)
    record_event("5. Control App (/admin)", "GET", "/admin", target_base, st, lat, layer, hdrs, body[:180], verdict)

    # Fase 6: Verificación Firma SQLi (OWASP CRS estándar)
    time.sleep(isolation_delay)
    st, lat, hdrs, body = send_http_probe(
        target_base,
        "POST",
        "/login",
        json_body={"email": "admin' OR '1'='1", "password": "test"},
    )
    layer, verdict = classify_layer(st, hdrs, body)
    record_event("6. Firma L7 SQLi", "POST", "/login", target_base, st, lat, layer, hdrs, body[:180], verdict)

    # Fase 7: Verificación Firma XSS (OWASP CRS estándar)
    time.sleep(isolation_delay)
    st, lat, hdrs, body = send_http_probe(
        target_base,
        "GET",
        "/search",
        params={"q": "<script>alert(1)</script>"},
    )
    layer, verdict = classify_layer(st, hdrs, body)
    record_event("7. Firma L7 XSS", "GET", "/search", target_base, st, lat, layer, hdrs, body[:180], verdict)

    # Fase 8: Ráfaga de Concurrencia Controlada (10 peticiones / 5 hilos)
    def burst_worker(idx):
        s_code, lat_ms, h_map, b_txt = send_http_probe(
            target_base,
            "POST",
            "/login",
            json_body={"email": f"rafaga_{idx}@nova.edu", "password": "Password123!"},
        )
        ly, vd = classify_layer(s_code, h_map, b_txt)
        return idx, s_code, lat_ms, ly, h_map, b_txt[:140], vd

    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = [pool.submit(burst_worker, i) for i in range(1, 11)]
        burst_results = [f.result() for f in as_completed(futures)]

    burst_results.sort(key=lambda x: x[0])
    for idx, s_code, lat_ms, ly, h_map, prev, vd in burst_results:
        record_event(f"8. Concurrencia #{idx:02d}", "POST", "/login", target_base, s_code, lat_ms, ly, h_map, prev, vd)


DASHBOARD_HTML = """<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>WAF Shield Cloud · Servidor Local de Trazabilidad Atómica</title>
  <style>
    :root { --bg:#090e17; --card:#111827; --border:#1f2937; --text:#f3f4f6; --muted:#9ca3af; --cyan:#22d3ee; --green:#10b981; --red:#ef4444; --amber:#f59e0b; }
    * { box-sizing:border-box; }
    body { margin:0; font-family:system-ui,-apple-system,sans-serif; background:var(--bg); color:var(--text); padding:24px; }
    .wrap { max-width:1280px; margin:auto; }
    header { display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:16px; border-bottom:1px solid var(--border); padding-bottom:16px; margin-bottom:20px; }
    h1 { margin:0; font-size:20px; color:var(--cyan); }
    .sub { font-size:12px; color:var(--muted); margin-top:4px; }
    .controls { display:flex; flex-wrap:wrap; gap:10px; align-items:center; }
    input, select, button { background:#1f2937; color:var(--text); border:1px solid #374151; border-radius:6px; padding:9px 12px; font-size:13px; }
    input { width:250px; }
    button { cursor:pointer; font-weight:600; }
    button.primary { background:#0891b2; border-color:#06b6d4; color:#fff; }
    button.primary:hover { background:#0e7490; }
    button:disabled { opacity:.5; cursor:not-allowed; }
    .kpis { display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:14px; margin-bottom:20px; }
    .kpi { background:var(--card); border:1px solid var(--border); border-radius:8px; padding:14px 16px; }
    .kpi span { font-size:11px; color:var(--muted); text-transform:uppercase; letter-spacing:.05em; }
    .kpi strong { display:block; font-size:24px; margin-top:6px; }
    table { width:100%; border-collapse:collapse; background:var(--card); border:1px solid var(--border); border-radius:8px; overflow:hidden; font-size:12px; }
    th, td { padding:10px 12px; text-align:left; border-bottom:1px solid var(--border); vertical-align:top; }
    th { background:#0f172a; color:var(--muted); font-weight:600; }
    tr:hover { background:#1e293b55; }
    .badge { display:inline-block; padding:3px 7px; border-radius:4px; font-weight:700; font-family:monospace; font-size:11px; }
    .b-200 { background:#064e3b; color:#6ee7b7; }
    .b-401 { background:#78350f; color:#fcd34d; }
    .b-403 { background:#7f1d1d; color:#fca5a5; }
    .b-err { background:#374151; color:#d1d5db; }
    pre { margin:0; white-space:pre-wrap; word-break:break-all; font-family:monospace; font-size:11px; color:#cbd5e1; max-width:420px; }
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <div>
        <h1>WAF Shield Cloud · Monitor Local de Trazabilidad Atómica</h1>
        <div class="sub">Servidor Python en vivo (http://localhost:5050) · Ejecuta pruebas contra el WAF y registra cada evidencia</div>
      </div>
      <div class="controls">
        <input id="target" value="http://localhost:8080" placeholder="URL objetivo (ej. http://localhost:8080)" />
        <select id="delay">
          <option value="2">Aislamiento: 2s (Rápido)</option>
          <option value="10">Aislamiento: 10s (Estricto GCP)</option>
        </select>
        <button class="primary" id="runBtn" onclick="runAudit()">▶ Ejecutar Auditoría en Vivo</button>
        <button onclick="downloadJson()">⬇ Exportar JSON</button>
      </div>
    </header>

    <div class="kpis">
      <div class="kpi"><span>Total Peticiones</span><strong id="kTotal">0</strong></div>
      <div class="kpi"><span>Bloqueadas en Perímetro (WAF)</span><strong id="kBlocked" style="color:var(--red)">0</strong></div>
      <div class="kpi"><span>Procesadas por Backend</span><strong id="kBackend" style="color:var(--green)">0</strong></div>
      <div class="kpi"><span>Latencia Promedio</span><strong id="kLat" style="color:var(--cyan)">0 ms</strong></div>
    </div>

    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Timestamp (UTC)</th>
          <th>Fase / Vector</th>
          <th>Petición</th>
          <th>HTTP</th>
          <th>Latencia</th>
          <th>Capa Origen</th>
          <th>Evidencia / Respuesta</th>
        </tr>
      </thead>
      <tbody id="tbody">
        <tr><td colspan="8" style="text-align:center;color:var(--muted);padding:24px;">Haz clic en "Ejecutar Auditoría en Vivo" para disparar las peticiones contra el WAF y registrar la trazabilidad.</td></tr>
      </tbody>
    </table>
  </div>

  <script>
    let latestLogs = [];

    function badgeClass(code) {
      if (code === 200 || code === 201) return 'b-200';
      if (code === 401 || code === 400) return 'b-401';
      if (code === 403 || code === 429) return 'b-403';
      return 'b-err';
    }

    async function runAudit() {
      const btn = document.getElementById('runBtn');
      const target = document.getElementById('target').value.trim();
      const delay = Number(document.getElementById('delay').value);
      btn.disabled = true;
      btn.textContent = '⏳ Ejecutando pruebas...';

      try {
        const res = await fetch('/api/run', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ target, delay })
        });
        const data = await res.json();
        latestLogs = data.logs || [];
        renderTable(latestLogs);
      } catch (e) {
        alert('Error ejecutando auditoría: ' + e);
      } finally {
        btn.disabled = false;
        btn.textContent = '▶ Ejecutar Auditoría en Vivo';
      }
    }

    function renderTable(logs) {
      const tbody = document.getElementById('tbody');
      if (!logs.length) return;

      let blocked = 0, backend = 0, latSum = 0;
      tbody.innerHTML = logs.map(item => {
        if (item.layer.includes('PERÍMETRO')) blocked++;
        if (item.layer.includes('BACKEND')) backend++;
        latSum += item.latency_ms;
        return `<tr>
          <td>${item.id}</td>
          <td style="font-family:monospace;font-size:11px;color:#9ca3af">${item.timestamp}</td>
          <td><strong>${item.phase}</strong></td>
          <td style="font-family:monospace">${item.method} ${item.path}</td>
          <td><span class="badge ${badgeClass(item.status_code)}">${item.status_code}</span></td>
          <td style="font-family:monospace">${item.latency_ms} ms</td>
          <td><strong>${item.layer}</strong></td>
          <td><pre>${escapeHtml(item.preview)}</pre></td>
        </tr>`;
      }).join('');

      document.getElementById('kTotal').textContent = logs.length;
      document.getElementById('kBlocked').textContent = blocked;
      document.getElementById('kBackend').textContent = backend;
      document.getElementById('kLat').textContent = (latSum / logs.length).toFixed(2) + ' ms';
    }

    function escapeHtml(str) {
      return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    }

    function downloadJson() {
      if (!latestLogs.length) return alert('Ejecuta primero una auditoría.');
      const blob = new Blob([JSON.stringify(latestLogs, null, 2)], { type: 'application/json' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = `trazabilidad_waf_${new Date().toISOString().slice(0,19).replace(/:/g,'-')}.json`;
      a.click();
    }
  </script>
</body>
</html>
"""


class TelemetryHandler(BaseHTTPRequestHandler):
    def _send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/" or self.path.startswith("/?"):
            html_bytes = DASHBOARD_HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html_bytes)))
            self.end_headers()
            self.wfile.write(html_bytes)
        elif self.path == "/api/logs":
            with LOGS_LOCK:
                self._send_json(200, {"logs": AUDIT_LOGS})
        else:
            self._send_json(404, {"error": "Ruta no encontrada"})

    def do_POST(self):
        if self.path == "/api/run":
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8") if length else "{}"
            try:
                body = json.loads(raw)
            except Exception:
                body = {}
            target = str(body.get("target") or DEFAULT_TARGET).strip()
            delay = int(body.get("delay") or 2)
            run_audit_sequence(target, isolation_delay=delay)
            with LOGS_LOCK:
                self._send_json(200, {"status": "completed", "logs": AUDIT_LOGS})
        else:
            self._send_json(404, {"error": "Ruta no encontrada"})

    def log_message(self, format, *args):
        # Silenciar logs HTTP ruidosos del propio monitor
        return


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", PORT), TelemetryHandler)
    print("=" * 75)
    print(f"SERVIDOR DE TRAZABILIDAD WAF INICIADO EN: http://localhost:{PORT}")
    print("Abre esa URL en tu navegador para ejecutar pruebas y ver logs atómicos.")
    print("Presiona Ctrl+C para detener.")
    print("=" * 75)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
        server.server_close()
