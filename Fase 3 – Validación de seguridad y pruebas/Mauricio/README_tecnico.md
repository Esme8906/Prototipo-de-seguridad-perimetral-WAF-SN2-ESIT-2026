# 🛡️ WAF Shield Cloud — Arquitectura y Auditoría de Seguridad Perimetral (ESIT · Grupo SN-2)

[![Cloud Run](https://img.shields.io/badge/GCP-Cloud%20Run-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/run)
[![Cloud Armor](https://img.shields.io/badge/WAF-Google%20Cloud%20Armor-34A853?logo=googlecloud&logoColor=white)](https://cloud.google.com/armor)
[![ModSecurity](https://img.shields.io/badge/Local%20WAF-Nginx%20%2B%20ModSecurity%20OWASP%20CRS-009639?logo=nginx&logoColor=white)](https://modsecurity.org/)
[![Node.js](https://img.shields.io/badge/Backend-Node.js%2020%20Alpine-339933?logo=nodedotjs&logoColor=white)](https://nodejs.org/)
[![Python](https://img.shields.io/badge/Telemetry-Python%203-3776AB?logo=python&logoColor=white)](https://www.python.org/)

> **Proyecto de Estancia Profesional — Escuela Superior de Innovación y Tecnología (ESIT)**  
> **Fase 3:** *Validación de seguridad, pruebas de tráfico y refinamiento*  
> **Equipo:** SN-2 · **Tutor:** Carlos G. Rodriguez  
> **Integrantes:** Mauricio Alberto Grande Martínez (Arquitectura Cloud, Ciberseguridad y Auditoría) & Jhony (Desarrollo Web Full-Stack v2)

---

## 📋 Descripción General

**WAF Shield Cloud** es un prototipo de arquitectura de defensa perimetral diseñado para evaluar, contrastar y refinar mecanismos de protección de capa de aplicación ($L7$) antes de su despliegue en entornos productivos oficiales de Google Cloud Platform (GCP).

Durante la **Fase 3**, todas las pruebas ofensivas, de carga concurrente y de calibración de políticas se ejecutaron en un **entorno *sandbox* completamente aislado** (`waf-shield-esit-sn2-2026`), garantizando cero riesgos operativos o conflictos sobre la infraestructura oficial de GCP. El sistema contrasta empíricamente dos arquitecturas:

1. **Entorno Local Contenerizado (`http://localhost:8080`):** Proxy inverso **Nginx + ModSecurity v3** con reglas **OWASP Core Rule Set (CRS)** por inspección profunda de carga útil (DPI).
2. **Entorno Cloud Administrado (`http://8.233.53.34` — Sandbox GCP):** Contenedor sin servidor en **Cloud Run** con ingreso restringido (`internal-and-cloud-load-balancing`), expuesto exclusivamente a través de un **Global External Application Load Balancer** protegido por **Google Cloud Armor**.

---

## 🏗️ Arquitectura del Sistema

```text
                        ┌───────────────────────────────────────────┐
                        │   Monitor Local de Trazabilidad Atómica   │
                        │    waf_telemetry_server.py (:5050)        │
                        │    (Suite de 17 Vectores + Export JSON)   │
                        └───────────────┬───────────┬───────────────┘
                                        │           │
                 ┌──────────────────────┘           └──────────────────────┐
                 ▼ (Entorno Local)                                         ▼ (Entorno Sandbox GCP)
┌─────────────────────────────────┐                     ┌─────────────────────────────────────────────┐
│   Nginx + ModSecurity v3 (CRS)  │                     │   Global External Load Balancer (HTTP :80)  │
│        localhost:8080           │                     │              IP: 8.233.53.34                │
└────────────────┬────────────────┘                     └──────────────────────┬──────────────────────┘
                 │                                                             │
                 │                                      ┌──────────────────────▼──────────────────────┐
                 │                                      │       Política Google Cloud Armor           │
                 │                                      │        (waf-shield-sn2-policy)              │
                 │                                      │  • Prio 1000: Rate Limit (10 req/60s -> 429) │
                 │                                      │  • Prio 2000: sqli-v33-stable (-> 403)      │
                 │                                      │  • Prio 3000: xss-v33-stable  (-> 403)      │
                 │                                      └──────────────────────┬──────────────────────┘
                 │                                                             │ (Serverless NEG)
                 ▼                                                             ▼
┌─────────────────────────────────┐                     ┌─────────────────────────────────────────────┐
│    Backend Node.js (Local)      │                     │     Cloud Run: waf-sandbox-app (us-central1)│
│  Sesiones dinámicas UUID v2     │                     │  Ingress: internal-and-cloud-load-balancing │
└─────────────────────────────────┘                     └─────────────────────────────────────────────┘
```

---

## 📁 Estructura del Repositorio

```text
tarea-main/
├── src/
│   └── app.js                   # Servidor Node.js v2 (autenticación dinámica UUID, Bearer y rutas API)
├── public/
│   ├── index.html               # Portal académico objetivo
│   ├── app.js                   # Cliente JS con manejo tolerante de bloqueos HTML/JSON (403/429)
│   └── styles.css               # Hoja de estilos de la aplicación web
├── Dockerfile                   # Empaquetado minimalista basado en node:20-alpine para Cloud Run
├── waf_telemetry_server.py      # Servidor web (:5050) y motor de auditoría atómica de 17 vectores
├── comandos gcloud.ps1          # Script de aprovisionamiento Cloud Run/Armor y limpieza FinOps
├── package.json                 # Dependencias y metadatos del servicio Node.js
└── README.md                    # Documentación técnica del repositorio
```

---

## 🚀 Guía de Ejecución y Despliegue

### 1. Ejecución del Monitor Local de Trazabilidad Atómica
El monitor de auditoría corre localmente en Python 3 (sin dependencias externas complejas) y permite disparar la batería de 17 pruebas contra cualquier destino local o en la nube:

```powershell
python waf_telemetry_server.py
```
Una vez iniciado, abre **`http://localhost:5050`** en tu navegador, ingresa la URL objetivo (`http://localhost:8080` o la IP pública del Load Balancer), selecciona el modo de aislamiento (**`10s (Estricto GCP)`** recomendado para nube) y haz clic en **▶ Ejecutar Auditoría en Vivo**.

### 2. Despliegue en Google Cloud Platform (Sandbox Aislado)
Los comandos completos de creación de infraestructura y desmantelamiento se encuentran documentados en `comandos gcloud.ps1`:

```powershell
# 1. Desplegar contenedor en Cloud Run bloqueando el acceso directo por URL nativa
gcloud run deploy waf-sandbox-app `
    --source . `
    --region us-central1 `
    --platform managed `
    --ingress internal-and-cloud-load-balancing `
    --allow-unauthenticated

# 2. Crear política Cloud Armor y reglas (Prioridades 1000, 2000 y 3000)
gcloud compute security-policies create waf-shield-sn2-policy --description "Politica WAF Fase 3 - Grupo SN-2"

gcloud compute security-policies rules create 1000 --security-policy waf-shield-sn2-policy --src-ip-ranges "*" --action throttle --rate-limit-threshold-count 10 --rate-limit-threshold-interval-sec 60 --conform-action allow --exceed-action deny-429 --enforce-on-key IP
gcloud compute security-policies rules create 2000 --security-policy waf-shield-sn2-policy --expression "evaluatePreconfiguredWaf('sqli-v33-stable')" --action deny-403
gcloud compute security-policies rules create 3000 --security-policy waf-shield-sn2-policy --expression "evaluatePreconfiguredWaf('xss-v33-stable')" --action deny-403
```

*(Ver `comandos gcloud.ps1` para el enlace completo con `Serverless NEG`, `Backend Service`, `URL Map`, `HTTP Proxy`, `Forwarding Rule` y el bloque de limpieza FinOps).*

---

## 📊 Resultados de Auditoría Comparativa (17 Vectores)

| Fase / Vector Evaluado | Petición | Entorno Local (`Nginx + ModSecurity`) | Entorno Nube (`GCP Cloud Armor · 8.233.53.34`) |
| :--- | :---: | :--- | :--- |
| **1. Healthcheck** | `GET /healthcheck` | `200 OK` · `230.31 ms` (Backend) | `200 OK` · `314.46 ms` (Backend) |
| **2. Login Legítimo** | `POST /login` | `200 OK` · `34.86 ms` (Backend) | `200 OK` · `222.95 ms` (Backend) |
| **3. Dashboard Protegido** | `GET /dashboard` | `200 OK` · `24.98 ms` (Backend) | `200 OK` · `199.93 ms` (Backend) |
| **4. Credenciales Inválidas** | `POST /login` | `401 Unauthorized` · `21.94 ms` | `401 Unauthorized` · `187.50 ms` |
| **5. Control App (`/admin`)** | `GET /admin` | `403 Forbidden` · `27.62 ms` | `403 Forbidden` · `215.34 ms` |
| **6. Firma L7 SQLi** | `POST /login` | **`403 Forbidden`** · `10.92 ms` (**WAF**) | `401 Unauthorized` · `210.47 ms` (Backend) |
| **7. Firma L7 XSS** | `GET /search` | **`403 Forbidden`** · `8.55 ms` (**WAF**) | `200 OK` · `214.31 ms` (Backend) |
| **8. Concurrencia (×10)** | `POST /login` | `0` bloqueos WAF (`10/10` `401` Backend) | **`7` bloqueos `429`** en borde (`270–785 ms`) |
| **Totales Consolidados** | **17 peticiones** | **3 bloqueos WAF** · Latencia: **`85.81 ms`** | **7 bloqueos WAF** · Latencia: **`239.30 ms`** |

---

## 🔍 Conclusiones y Refinamiento Técnico

1. **Complementariedad entre DPI y Mitigación Volumétrica:** ModSecurity local detuvo instantáneamente firmas básicas de SQLi (`10.92 ms`) y XSS (`8.55 ms`), mientras que **Cloud Armor** protegió la disponibilidad del contenedor en la nube rechazando el **70 %** de la ráfaga de fuerza bruta con `HTTP 429 Too Many Requests` en el borde de red.
2. **Calibración de Sensibilidad (*Sensitivity Tuning*):** Las firmas preconfiguradas `sqli-v33-stable` y `xss-v33-stable` en GCP operan por defecto con sensibilidad conservadora para minimizar falsos positivos. Antes de migrar al entorno oficial de GCP (Fase 4), se recomienda elevar el nivel de sensibilidad (`sensitivity=2` o `3`) y mantener sanitización estricta en el código de la aplicación.
3. **Disciplina FinOps:** Tras exportar los reportes JSON y validar el perímetro, toda la infraestructura del *sandbox* (`forwarding-rule`, `proxy`, `url-map`, `backend`, `NEG`, `security-policy` y `Cloud Run`) fue desmantelada para garantizar un costo residual de **`$0.00/h`**.

---

## 📅 Hoja de Ruta

- [x] **Fase 1 & 2:** Diseño arquitectónico y despliegue de aplicación web v2 con WAF local.
- [x] **Fase 3:** *Validación de seguridad, pruebas de tráfico y refinamiento* (Auditoría comparativa en *sandbox* GCP aislado y cierre FinOps).
- [ ] **Fase 4:** *Cierre, documentación y entrega profesional* (Consolidación de informe final, anexos gráficos y sustentación ante tutor).
