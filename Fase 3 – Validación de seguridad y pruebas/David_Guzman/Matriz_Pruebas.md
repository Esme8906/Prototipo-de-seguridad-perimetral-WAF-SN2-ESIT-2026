# Matriz de pruebas — Fase 3

**Proyecto:** WAF Shield Cloud – Seguridad Perimetral para Aplicaciones en la Nube  
**Equipo:** SN-2  
**Responsable:** [@trabajodavidg](https://github.com/trabajodavidg)  
**Proyecto GCP:** `proyecto-7-waf-shield-cloud`  
**Aplicación:** `waf-shield-app` (Cloud Run, `us-central1`)  
**Punto de entrada probado:** `https://34.160.56.213` (balanceador HTTPS; certificado autofirmado de laboratorio)  
**Fecha de ejecución:** 12 de noviembre de 2026 (UTC)  
**Fecha límite de Kanban:** 19 de noviembre de 2026

## Objetivo y alcance

Comparar solicitudes legítimas y sospechosas enviadas por el balanceador HTTPS, registrar resultados esperados y observados, y relacionar cada caso con una evidencia. Los resultados corresponden únicamente a los escenarios ejecutados; no constituyen una evaluación exhaustiva del WAF.

## Matriz consolidada

| Caso | Evidencia | Hora UTC (12/11/2026) | Tipo | Método y ruta / entrada | Esperado | Observado | Evaluación |
|---|---|---|---|---|---|---|---|
| F3-DG-01 | [E3-DG-05](Evidencias/E3-DG-05_Prueba_Trafico_Legitimo_Healthcheck.png) | 07:14:31 | Legítimo | `GET /healthcheck` | 200 | 200 | Conforme |
| F3-DG-02 | [E3-DG-06](Evidencias/E3-DG-06_Prueba_Trafico_Legitimo_Pagina_Principal.png) | 07:14:56 | Legítimo | `GET /` | 200 | 200 | Conforme |
| F3-DG-03 | [E3-DG-07](Evidencias/E3-DG-07_Prueba_Busqueda_Legitima.png) | 07:16:31 | Legítimo | `GET /search?q=universidad` | 200 | 200 | Conforme |
| F3-DG-04 | [E3-DG-08](Evidencias/E3-DG-08_Busqueda_Legitima_Con_Apostrofo.png) | 07:16:59 | Legítimo | `GET /search`, `q=O'Reilly` | 200 | 200 | Conforme |
| F3-DG-05 | [E3-DG-09](Evidencias/E3-DG-09_Prueba_SQL_Injection.png) | 16:12:25 | Sospechoso: SQLi | `GET /search`, `q=' OR 1=1 --` | 403 | 403 | Conforme |
| F3-DG-06 | [E3-DG-10](Evidencias/E3-DG-10_Prueba_XSS.png) | 16:14:11 | Sospechoso: XSS | `GET /search`, `q=<script>alert(1)</script>` | 403 | 403 | Conforme |
| F3-DG-07 | [E3-DG-13](Evidencias/E3-DG-13_Validacion_Adicional_XSS.png) | 16:27:10 | Sospechoso: XSS | `GET /search`, `q=<img src=x onerror=alert(1)>` | 403 | 403 | Conforme |
| F3-DG-08 | [E3-DG-16](Evidencias/E3-DG-16_Prueba_Adicional_XSS_SVG.png) | 16:32:12 | Sospechoso: XSS | `GET /search`, `q=<svg/onload=alert(1)>` | 403 | 403 | Conforme |

**Balance:** 4/4 solicitudes legítimas respondieron 200 y 4/4 solicitudes sospechosas respondieron 403. Se obtuvieron 8/8 resultados esperados **en los casos ejecutados**.

## Evidencias de infraestructura previas

- [E3-DG-01 — Proyecto GCP activo](Evidencias/E3-DG-01_Proyecto_GCP_Activo.png).
- [E3-DG-02 — Cloud Run e ingreso restringido](Evidencias/E3-DG-02_Configuracion_Cloud_Run.png): `internal-and-cloud-load-balancing`.
- [E3-DG-03 — Política Cloud Armor](Evidencias/E3-DG-03_Reglas_Cloud_Armor.png): SQLi prioridad 1000 `deny(403)`; XSS prioridad 1100 `deny(403)`; regla predeterminada `allow`.
- [E3-DG-04 — Asociación del backend](Evidencias/E3-DG-04_Backend_Politica_WAF.png): `waf-shield-backend` asociado a `waf-shield-policy`.

## Aclaraciones metodológicas

- Las horas corresponden a las **repeticiones documentadas** en las capturas, no a las primeras ejecuciones históricas.
- El certificado HTTPS es autofirmado; las pruebas `curl` utilizaron `-k` para omitir la validación de confianza del certificado. Esto **no** demuestra HTTPS con certificado público confiable.
- Un HTTP 403 aislado no identifica la regla aplicada; la atribución se documenta separadamente en [Registro_Cloud_Logging.md](Registro_Cloud_Logging.md).
- Las pruebas de acceso directo a Cloud Run pertenecen a evidencias previas de Fase 2; no se repitieron dentro de esta matriz de ocho casos de Fase 3.
- Los enlaces relativos funcionarán una vez que los archivos PNG se suban a la carpeta `Evidencias/` con los nombres indicados.

## Estado administrativo

**Ejecución técnica:** completada el 12/11/2026.  


