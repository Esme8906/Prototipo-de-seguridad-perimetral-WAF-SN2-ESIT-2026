import time
import requests

BASE_URL = "http://localhost:8080"
ENDPOINT = "/search"
WAIT_ISOLATION_SECONDS = 10
TIMEOUT_SECONDS = 5


def run_xss_verification():
    print("=" * 80)
    print("AUDITORÍA MODULAR 3: VERIFICACIÓN DE FIRMA L7 - XSS (AISLADA)")
    print(f"Objetivo: {BASE_URL}{ENDPOINT}")
    print("=" * 80)

    print(f"[*] Aplicando aislamiento temporal ({WAIT_ISOLATION_SECONDS}s)...")
    time.sleep(WAIT_ISOLATION_SECONDS)

    # Marcador estándar de verificación OWASP CRS
    params = {"q": "<script>alert(1)</script>"}
    started = time.perf_counter()

    try:
        print("[*] Enviando petición única de verificación...")
        res = requests.get(f"{BASE_URL}{ENDPOINT}", params=params, timeout=TIMEOUT_SECONDS)
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        content_type = res.headers.get("Content-Type", "")
        layer = "BACKEND (Node.js)" if "application/json" in content_type else "PERÍMETRO (WAF)"
        preview = res.text[:140].replace("\r", " ").replace("\n", " ")

        print(f"  Estado HTTP: {res.status_code} | Latencia: {latency_ms} ms")
        print(f"  Capa Origen: {layer}")
        print(f"  Respuesta:   {preview}")

        if res.status_code == 403 and "PERÍMETRO" in layer:
            print("\n[OK] Firma XSS interceptada legítimamente en el perímetro WAF.")
        else:
            print("\n[ALERTA] La petición no fue detenida por el WAF perimetral.")
    except requests.RequestException as exc:
        print(f"[ERROR] Fallo de conexión: {exc}")


if __name__ == "__main__":
    run_xss_verification()