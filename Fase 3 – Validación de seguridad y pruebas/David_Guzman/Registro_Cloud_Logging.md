# Registro de Cloud Logging — Fase 3

**Proyecto:** WAF Shield Cloud — Equipo SN-2  
**Responsable:** [@trabajodavidg](https://github.com/trabajodavidg)  
**Proyecto GCP:** `proyecto-7-waf-shield-cloud`  
**Backend:** `waf-shield-backend`  
**Política:** `waf-shield-policy`  
**Fecha de las consultas:** 12 de noviembre de 2026 (UTC)  
**Fecha límite de Kanban:** 19 de noviembre de 2026

## 1. Objetivo

Recuperar eventos de Cloud Logging relacionados con pruebas realizadas a través del balanceador HTTPS, documentar los filtros e intervalos consultados y atribuir acciones de Cloud Armor únicamente cuando los registros lo permitan.

## 2. Configuración del backend

En [E3-DG-11 — Verificación de logging](Evidencias/E3-DG-11_Verificacion_Logging_Backend.png), ejecutada a las **16:18:24 UTC**, se observó:

```yaml
logConfig:
  enable: true
  optionalMode: EXCLUDE_ALL_OPTIONAL
  sampleRate: 1.0
name: waf-shield-backend
securityPolicy: https://www.googleapis.com/compute/v1/projects/proyecto-7-waf-shield-cloud/global/securityPolicies/waf-shield-policy
```

`sampleRate: 1.0` indica muestreo configurado al 100 % para solicitudes elegibles; no garantiza por sí solo que cualquier consulta devuelva eventos.

## 3. Consultas y resultados

### E3-DG-12 — Eventos HTTP 403 del balanceador

**Consulta ejecutada:** 12/11/2026, **16:20:28 UTC**.  
**Intervalo:** `2026-11-12T16:10:00Z` a `2026-11-12T16:17:00Z` (inclusive en los filtros utilizados).  
**Filtro:**

```text
resource.type="http_load_balancer"
AND timestamp>="2026-11-12T16:10:00Z"
AND timestamp<="2026-11-12T16:17:00Z"
AND httpRequest.status=403
```

**Resultado:** cuatro eventos HTTP 403 relacionados con las pruebas, con política `waf-shield-policy`, `outcome: DENY`, prioridad 1000 y `statusDetails: denied_by_security_policy`.

| Marca UTC del evento | Solicitud identificada | Prioridad | Firma visible |
|---|---|---|---|
| 16:10:36.572038 | SQLi, ejecución inicial | 1000 | `owasp-crs-v030301-id942180-sqli` |
| 16:12:09.927886 | SQLi, ejecución adicional | 1000 | `owasp-crs-v030301-id942180-sqli` |
| 16:12:25.903376 | SQLi, caso F3-DG-05 | 1000 | `owasp-crs-v030301-id942180-sqli` |
| 16:14:11.705859 | XSS `script`, caso F3-DG-06 | 1000 | `owasp-crs-v030301-id942431-sqli` |

**Evidencia:** [E3-DG-12](Evidencias/E3-DG-12_Consulta_Eventos_WAF.png). Las marcas incluyen fracciones de segundo leídas de la captura.

### E3-DG-14 — Correlación del XSS `img`

**Consulta ejecutada:** 12/11/2026, **16:28:38 UTC**.  
**Intervalo:** `16:26:00Z` a `16:29:00Z`.  
**Filtro adicional:** `httpRequest.status=403`.

**Evento identificado:** `2026-11-12T16:27:10.195881Z`; ruta `/search`, parámetro `q` con `<img src=x onerror=alert(1)>` codificado en URL; `outcome: DENY`, prioridad **1000**, firma `owasp-crs-v030301-id942431-sqli`.

**Evidencia:** [E3-DG-14](Evidencias/E3-DG-14_Correlacion_XSS_Cloud_Armor.png).

### E3-DG-15 — Búsqueda de eventos de prioridad 1100

**Consulta ejecutada:** 12/11/2026, **16:30:42 UTC**.  
**Intervalo:** `2026-11-12T00:00:00Z` a `2026-11-13T00:00:00Z` (extremo superior excluido).  
**Filtro:**

```text
resource.type="http_load_balancer"
AND timestamp>="2026-11-12T00:00:00Z"
AND timestamp<"2026-11-13T00:00:00Z"
AND jsonPayload.enforcedSecurityPolicy.priority=1100
```

**Resultado:** sin eventos devueltos por esta consulta. No se puede concluir de ello que la regla XSS esté deshabilitada o no funcione.

**Evidencia:** [E3-DG-15](Evidencias/E3-DG-15_Busqueda_Eventos_Regla_XSS.png).

### E3-DG-17 — Correlación del XSS `svg`

**Consulta ejecutada:** 12/11/2026, **16:33:29 UTC**.  
**Intervalo:** `16:31:00Z` a `16:34:00Z`.  
**Filtro adicional:** `httpRequest.status=403`.

**Evento identificado:** `2026-11-12T16:32:12.420508Z`; ruta `/search`, parámetro `q` con `<svg/onload=alert(1)>` codificado en URL; `outcome: DENY`, prioridad **1000**, firma `owasp-crs-v030301-id942432-sqli`.

**Evidencia:** [E3-DG-17](Evidencias/E3-DG-17_Correlacion_XSS_SVG_Cloud_Armor.png).

## 4. Interpretación y límites

- Los eventos de E3-DG-12, E3-DG-14 y E3-DG-17 permiten relacionar solicitudes concretas con acciones `DENY` de Cloud Armor por coincidencia de marca UTC, ruta, parámetro y código HTTP.
- Los tres payloads XSS ensayados fueron bloqueados por la regla **SQLi prioridad 1000**. No se obtuvo un evento que demuestre la aplicación independiente de la regla XSS prioridad 1100.
- La ausencia de resultados de E3-DG-15 es un resultado de búsqueda, **no** evidencia de que la regla 1100 sea defectuosa.
- No se modificó ninguna regla como parte de estas consultas.

## 5. Comando reutilizable de consulta

```bash
gcloud logging read \
  'resource.type="http_load_balancer"
   AND timestamp>="2026-11-12T16:10:00Z"
   AND timestamp<="2026-11-12T16:17:00Z"
   AND httpRequest.status=403' \
  --project=proyecto-7-waf-shield-cloud \
  --limit=20 \
  --format="yaml(timestamp,httpRequest.requestUrl,httpRequest.status,jsonPayload.enforcedSecurityPolicy,jsonPayload.statusDetails)"
```

Este comando consulta registros existentes y no altera la configuración.

## 6. Estado de la tarjeta Kanban

**Objetivo técnico de trazabilidad:** alcanzado el 12/11/2026 para los eventos identificados.  
**Resultado:** registros atribuibles recuperados, con política, prioridad, firma, acción y URL.  
**Limitación:** sin eventos observados de prioridad 1100 en el intervalo consultado.  

