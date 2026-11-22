import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

# Cambia esta URL por la IP pública de tu Load Balancer al migrar a GCP
BASE_URL = "http://localhost:8080"
ENDPOINT = "/login"
TOTAL_REQUESTS = 20
CONCURRENCY = 5
TIMEOUT_SECONDS = 5

HEADERS_TO_SHOW = ("Content-Type", "Server", "Retry-After")


def send_probe(req_id):
    url = f"{BASE_URL}{ENDPOINT}"
    payload = {"email": f"auditoria_{req_id}@nova.edu", "password": "Password123!"}
    started = time.perf_counter()

    try:
        res = requests.post(url, json=payload, timeout=TIMEOUT_SECONDS)
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        content_type = res.headers.get("Content-Type", "")
        layer = "BACKEND (Node.js)" if "application/json" in content_type else "PERÍMETRO (WAF)"
        headers = {k: res.headers[k] for k in HEADERS_TO_SHOW if k in res.headers}
        return req_id, res.status_code, latency_ms, layer, headers
    except requests.RequestException as exc:
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        return req_id, f"ERROR: {type(exc).__name__}", latency_ms, "RED", {}


def run_rate_limit_audit():
    print("=" * 80)
    print(f"AUDITORÍA MODULAR 1: RATE LIMITING Y CONCURRENCIA ({TOTAL_REQUESTS} reqs / {CONCURRENCY} hilos)")
    print(f"Objetivo: {BASE_URL}{ENDPOINT}")
    print("=" * 80)

    started_total = time.perf_counter()
    results = []

    with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        futures = [executor.submit(send_probe, i) for i in range(1, TOTAL_REQUESTS + 1)]
        for future in as_completed(futures):
            results.append(future.result())

    results.sort(key=lambda item: item[0])

    blocked_count = 0
    for req_id, status, latency, layer, headers in results:
        if status in (403, 429) and "PERÍMETRO" in layer:
            blocked_count += 1
        print(f"  [Req {req_id:02d}] HTTP: {str(status):6} | {latency:6} ms | Origen: {layer}")
        if headers and status in (403, 429):
            print(f"           Encabezados: {headers}")

    total_time = round(time.perf_counter() - started_total, 2)
    print("-" * 80)
    print(f"Tiempo total: {total_time}s | Bloqueadas en perímetro (403/429): {blocked_count}/{TOTAL_REQUESTS}")


if __name__ == "__main__":
    run_rate_limit_audit()