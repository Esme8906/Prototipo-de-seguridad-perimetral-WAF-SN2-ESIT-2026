import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

BASE_URL = "http://localhost:8080"
TIMEOUT_SECONDS = 5
WAIT_ISOLATION_SECONDS = 10

# Restricción preventiva para pruebas locales
if not BASE_URL.startswith(("http://localhost", "http://127.0.0.1")):
    raise ValueError("Por seguridad, ajusta la validación antes de apuntar a un entorno remoto.")

HEADERS_TO_INSPECT = ("Content-Type", "Server", "Via", "Retry-After")


def inspect_response(label, method, path, json_data=None, headers=None, params=None):
    """Ejecuta una petición y clasifica qué capa (WAF o Backend) generó la respuesta."""
    url = f"{BASE_URL}{path}"
    started = time.perf_counter()

    try:
        res = requests.request(
            method=method,
            url=url,
            json=json_data,
            headers=headers or {},
            params=params,
            timeout=TIMEOUT_SECONDS,
        )
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        content_type = res.headers.get("Content-Type", "")

        # Clasificación de capa de respuesta
        if "application/json" in content_type:
            layer = "BACKEND (Node.js)"
            detail = res.json()
        else:
            layer = "PERÍMETRO (WAF / Nginx)"
            detail = res.text[:150].replace("\r", " ").replace("\n", " ")

        filtered_headers = {k: res.headers[k] for k in HEADERS_TO_INSPECT if k in res.headers}

        print(f"[{label}]")
        print(f"  Ruta:        {method} {path}")
        print(f"  Estado HTTP: {res.status_code} | Latencia: {latency_ms} ms")
        print(f"  Capa Origen: {layer}")
        if filtered_headers:
            print(f"  Encabezados: {filtered_headers}")
        print(f"  Detalle:     {detail}\n")
        return res

    except requests.RequestException as exc:
        print(f"[{label}] Error de red: {exc}\n")
        return None


def run_functional_and_perimeter_audit():
    print("=" * 80)
    print("AUDITORÍA DE FLUJO COMPLETO Y TELEMETRÍA PERIMETRAL (WAF SHIELD CLOUD)")
    print("=" * 80)

    # 1. Salud del servicio
    inspect_response("1. Healthcheck", "GET", "/healthcheck")

    # 2. Autenticación legítima
    login_res = inspect_response(
        "2. Login Legítimo",
        "POST",
        "/login",
        json_data={"email": "estudiante@nova.edu", "password": "Nova2026!"},
    )

    # 3. Consumo de ruta protegida con el token emitido
    token = ""
    if login_res and login_res.status_code == 200:
        token = login_res.json().get("token", "")

    inspect_response(
        "3. Acceso Post-Login (/dashboard)",
        "GET",
        "/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )

    # 4. Credenciales inválidas (debe atravesar el WAF y recibir 401 del backend)
    inspect_response(
        "4. Credenciales Inválidas",
        "POST",
        "/login",
        json_data={"email": "estudiante@nova.edu", "password": "ClaveIncorrecta123"},
    )

    # 5. Control de acceso de aplicación (/admin sin firmas maliciosas -> 403 JSON del backend)
    inspect_response("5. Ruta Administrativa (/admin)", "GET", "/admin")

    # 6. Prueba aislada de firma L7 (SQLi estándar de verificación OWASP)
    print(f"[*] Pausa de aislamiento ({WAIT_ISOLATION_SECONDS}s) para evitar solapamiento de tasa...")
    time.sleep(WAIT_ISOLATION_SECONDS)
    inspect_response(
        "6. Verificación Firma L7 (SQLi)",
        "POST",
        "/login",
        json_data={"email": "admin' OR '1'='1", "password": "test"},
    )

    # 7. Prueba aislada de firma L7 (XSS estándar de verificación OWASP)
    print(f"[*] Pausa de aislamiento ({WAIT_ISOLATION_SECONDS}s)...")
    time.sleep(WAIT_ISOLATION_SECONDS)
    inspect_response(
        "7. Verificación Firma L7 (XSS)",
        "GET",
        "/search",
        params={"q": "<script>alert(1)</script>"},
    )


def run_concurrency_check(total_requests=20, concurrency=5):
    print("=" * 80)
    print(f"PRUEBA DE CONCURRENCIA CONTROLADA ({total_requests} peticiones / {concurrency} hilos)")
    print("=" * 80)

    def worker(req_id):
        started = time.perf_counter()
        res = requests.post(
            f"{BASE_URL}/login",
            json={"email": f"test_{req_id}@nova.edu", "password": "Password123!"},
            timeout=TIMEOUT_SECONDS,
        )
        latency = round((time.perf_counter() - started) * 1000, 2)
        return req_id, res.status_code, latency

    results = []
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(worker, i) for i in range(1, total_requests + 1)]
        for f in as_completed(futures):
            results.append(f.result())

    results.sort(key=lambda x: x[0])
    for req_id, status, latency in results:
        print(f"  Solicitud {req_id:02d} -> HTTP {status} ({latency} ms)")


if __name__ == "__main__":
    run_functional_and_perimeter_audit()
    run_concurrency_check()