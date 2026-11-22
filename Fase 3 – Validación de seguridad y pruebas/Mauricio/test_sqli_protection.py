import time
import requests

BASE_URL = "http://localhost:8080"
ENDPOINT = "/login"
WAIT_ISOLATION_SECONDS = 10
TIMEOUT_SECONDS = 5


def run_sqli_verification():
    print("=" * 80)
    print("AUDITORÍA MODULAR 2: VERIFICACIÓN DE FIRMA L7 - SQLi (AISLADA)")
    print(f"Objetivo: {BASE_URL}{ENDPOINT}")
    print("=" * 80)

    print(f"[*] Aplicando aislamiento temporal ({WAIT_ISOLATION_SECONDS}s) para evitar solapamiento de tasa...")
    time.sleep(WAIT_ISOLATION_SECONDS)

    # Marcador estándar de verificación OWASP CRS
    payload = {"email": "admin' OR '1'='1", "password": "Password123!"}
    started = time.perf_counter()

    try:
        print("[*] Enviando petición única de verificación...")
        res = requests.post(f"{BASE_URL}{ENDPOINT}", json=payload, timeout=TIMEOUT_SECONDS)
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        content_type = res.headers.get("Content-Type", "")
        layer = "BACKEND (Node.js)" if "application/json" in content_type else "PERÍMETRO (WAF)"
        preview = res.text[:140].replace("\r", " ").replace("\n", " ")

        print(f"  Estado HTTP: {res.status_code} | Latencia: {latency_ms} ms")
        print(f"  Capa Origen: {layer}")
        print(f"  Respuesta:   {preview}")

        if res.status_code == 403 and "PERÍMETRO" in layer:
            print("\n[OK] Firma SQLi interceptada legítimamente en el perímetro WAF.")
        else:
            print("\n[ALERTA] La petición no fue detenida por el WAF perimetral.")
    except requests.RequestException as exc:
        print(f"[ERROR] Fallo de conexión: {exc}")


if __name__ == "__main__":
    run_sqli_verification()