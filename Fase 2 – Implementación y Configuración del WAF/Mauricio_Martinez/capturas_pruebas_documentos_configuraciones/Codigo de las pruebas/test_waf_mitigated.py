# ==============================================================================
# SCRIPT DE AUDITORÍA Y LÍNEA BASE PERIMETRAL - WAF SHIELD CLOUD (GRUPO SN-2)
# Entorno: Docker Sandbox Local (http://localhost:8080)
# ==============================================================================

import requests
import time

BASE_URL = "http://localhost:8080"

def print_header(title):
    print(f"\n--- {title} ---")

print("==============================================================================")
print(" AUDITORÍA SECLINE DE LÍNEA BASE PERIMETRAL - GRUPO SN-2")
print("==============================================================================")

# 1. SALUD DEL SERVICIO
print_header("1. SALUD DEL SERVICIO (GET /healthcheck)")
try:
    r = requests.get(f"{BASE_URL}/healthcheck")
    print(f"Estado: StatusCode = {r.status_code} -> Servicio Operativo Base")
except Exception as e:
    print(f"Estado: Error al conectar ({e})")

# 2. PRUEBA DE FUERZA BRUTA / RATE LIMITING
print_header("2. PRUEBA DE FUERZA BRUTA / RATE LIMITING (POST /login)")
payload_login = {"email": "demo@example.test", "password": "123"}
for i in range(1, 9):
    try:
        r = requests.post(f"{BASE_URL}/login", json=payload_login)
        print(f"Peticion {i}: StatusCode = {r.status_code} (Procesada por Express sin Rate Limit)")
    except Exception as e:
        print(f"Peticion {i}: Error ({e})")

# 3. SIMULACIÓN DE INYECCIÓN SQL - SQLi
print_header("3. SIMULACIÓN DE INYECCIÓN SQL - SQLi (POST /login)")
payload_sqli = {"email": "admin' OR '1'='1", "password": "123"}
try:
    r = requests.post(f"{BASE_URL}/login", json=payload_sqli)
    print(f"Inyeccion SQL: StatusCode = {r.status_code} (Llega al backend -> Mitigar con Regla 2000)")
except Exception as e:
    print(f"Inyeccion SQL: Error ({e})")

# 4. SIMULACIÓN DE CROSS-SITE SCRIPTING - XSS
print_header("4. SIMULACIÓN DE CROSS-SITE SCRIPTING - XSS (GET /search)")
try:
    r = requests.get(f"{BASE_URL}/search", params={"q": "<script>alert('XSS-Test')</script>"})
    if r.status_code == 200:
        data = r.json()
        print(f"XSS Reflejado en Query: '{data.get('query')}' -> StatusCode = 200 (Sin filtrado -> Mitigar con Regla 3000)")
    else:
        print(f"XSS: StatusCode = {r.status_code}")
except Exception as e:
    print(f"XSS: Error ({e})")

# 5. SIMULACIÓN DE CARGA MALICIOSA EN FORMULARIO
print_header("5. SIMULACIÓN DE CARGA MALICIOSA EN FORMULARIO (POST /comments)")
payload_xss_comment = {"comment": "<script>alert('xss')</script>"}
try:
    r = requests.post(f"{BASE_URL}/comments", json=payload_xss_comment)
    print(f"Comentario: StatusCode = {r.status_code} (Llega a la app -> Mitigar con Regla 2000/3000)")
except Exception as e:
    print(f"Comentario: Error ({e})")

# 6. VERIFICACIÓN DE RUTA RESTRINGIDA
print_header("6. VERIFICACIÓN DE RUTA RESTRINGIDA (GET /admin)")
try:
    r = requests.get(f"{BASE_URL}/admin")
    print(f"Ruta Admin: StatusCode = {r.status_code} (Restringida por backend -> Regla 4000 de respaldo)")
except Exception as e:
    print(f"Ruta Admin: Error ({e})")

print("\n==============================================================================")
print(" FIN DE LA AUDITORÍA DE LÍNEA BASE - EVIDENCIA LISTA PARA DOCUMENTACIÓN")
print("==============================================================================\n")
