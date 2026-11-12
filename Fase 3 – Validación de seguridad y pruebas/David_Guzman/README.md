# David_Guzman
README — FASE 3 | DAVID GUZMÁN
Proyecto: WAF Shield Cloud – Seguridad Perimetral para Aplicaciones en la Nube
Equipo: SN-2
Responsable: David Guzmán | GitHub: https://github.com/trabajodavidg
Fecha de las verificaciones: 12 de noviembre de 2026 (UTC)
Fecha límite de las tarjetas Kanban: 19 de noviembre de 2026

1. PROPÓSITO DE ESTA CARPETA

Documentar las actividades individuales de la Fase 3: ejecución de pruebas de tráfico legítimo y sospechoso, análisis de resultados y posibles ajustes del WAF, y verificación de eventos de Cloud Logging. El contenido refleja los resultados efectivamente observados; no constituye una auditoría exhaustiva de seguridad.

2. ENTORNO UTILIZADO

Proyecto GCP: proyecto-7-waf-shield-cloud
Región: us-central1
Aplicación: waf-shield-app (Cloud Run)
Balanceador HTTPS: https://34.160.56.213
Backend global: waf-shield-backend
Política de Cloud Armor: waf-shield-policy
Reglas: prioridad 1000 SQLi deny(403); prioridad 1100 XSS deny(403); regla predeterminada allow.
Ingreso de Cloud Run: internal-and-cloud-load-balancing.
Nota: el certificado HTTPS del laboratorio es autofirmado. En las pruebas con curl se utilizó -k para omitir su validación; esto no equivale a una configuración TLS apta para producción.

3. TAREA 1 — PRUEBAS DE TRÁFICO

Se ejecutaron ocho casos a través del balanceador HTTPS:

F3-DG-01 | E3-DG-05 | 07:14:31 UTC | GET /healthcheck                 | Esperado 200 | Observado 200
F3-DG-02 | E3-DG-06 | 07:14:56 UTC | GET /                            | Esperado 200 | Observado 200
F3-DG-03 | E3-DG-07 | 07:16:31 UTC | GET /search?q=universidad        | Esperado 200 | Observado 200
F3-DG-04 | E3-DG-08 | 07:16:59 UTC | GET /search?q=O'Reilly           | Esperado 200 | Observado 200
F3-DG-05 | E3-DG-09 | 16:12:25 UTC | SQLi: ' OR 1=1 --                | Esperado 403 | Observado 403
F3-DG-06 | E3-DG-10 | 16:14:11 UTC | XSS: <script>alert(1)</script>   | Esperado 403 | Observado 403
F3-DG-07 | E3-DG-13 | 16:27:10 UTC | XSS: <img src=x onerror=alert(1)> | Esperado 403 | Observado 403
F3-DG-08 | E3-DG-16 | 16:32:12 UTC | XSS: <svg/onload=alert(1)>       | Esperado 403 | Observado 403

Balance: 4 de 4 solicitudes legítimas permitidas y 4 de 4 solicitudes sospechosas rechazadas. Los ocho resultados coincidieron con lo esperado en la muestra ejecutada.

4. TAREA 2 — ANÁLISIS DE REGLAS Y AJUSTES

No se observaron falsos positivos en los cuatro casos legítimos evaluados. No se realizaron cambios en las reglas: los ocho casos respondieron según lo esperado y no se identificó una necesidad de ajuste respaldada por las pruebas.

Hallazgo: las tres solicitudes con payload XSS fueron bloqueadas por firmas del conjunto SQLi aplicadas mediante la regla de prioridad 1000. Esto no demuestra un fallo de la regla XSS de prioridad 1100, pero tampoco acredita su funcionamiento independiente. La comprobación específica de esa regla queda como limitación y recomendación para pruebas posteriores.

5. TAREA 3 — CLOUD LOGGING

E3-DG-11: backend con logConfig.enable=true, sampleRate=1.0 y optionalMode=EXCLUDE_ALL_OPTIONAL.
E3-DG-12: consulta de eventos HTTP 403 del balanceador, 12/11/2026 16:10–16:17 UTC. Se recuperaron eventos atribuibles a Cloud Armor con acción DENY, política waf-shield-policy y prioridad 1000.
E3-DG-14: evento XSS con IMG correlacionado con firma SQLi id942431, prioridad 1000, DENY.
E3-DG-15: búsqueda de eventos con prioridad 1100 para el 12/11/2026 UTC; la consulta no devolvió resultados.
E3-DG-17: evento XSS con SVG correlacionado con firma SQLi id942432, prioridad 1000, DENY.

La correlación se basó en fecha/hora, URL/payload, código HTTP y campos de la política en los registros. No se atribuye ningún evento a la regla 1100 sin evidencia.

6. EVIDENCIAS Y DOCUMENTOS

Documentos en esta misma carpeta:
- Matriz_Pruebas.md: casos, fechas, resultados y referencias a capturas.
- Analisis_Reglas_WAF.md: análisis comparativo, hallazgos y decisión de no ajustar.
- Registro_Cloud_Logging.md: consultas, intervalos y eventos correlacionados.

Las imágenes de respaldo deben colocarse en la subcarpeta Evidencias/ con los nombres citados en los documentos. Se emplean los identificadores E3-DG-01 a E3-DG-17; no todos los números representan una captura independiente. No se debe afirmar que las imágenes ya están publicadas en GitHub hasta verificar su carga y enlaces.

Evidencias principales:
E3-DG-01 a E3-DG-04: verificación inicial de infraestructura.
E3-DG-05 a E3-DG-10: pruebas principales de tráfico.
E3-DG-11 a E3-DG-12: configuración de logging y primeros eventos.
E3-DG-13 a E3-DG-17: pruebas XSS adicionales y correlación de registros.

7. ESTADO Y PASOS PARA EL CIERRE EN GITHUB

Ejecución técnica: completada para los casos documentados el 12/11/2026.
Cambios en política WAF durante esta etapa: ninguno.
Cierre administrativo: pendiente de verificar la publicación de archivos y capturas, agregar enlaces reales a las tarjetas Kanban, registrar la fecha de cierre y actualizar el estado de cada tarjeta según corresponda.

Ruta sugerida en el repositorio:
Fase-3/David-Guzman/
  README_David_Guzman_Fase_3.txt
  Matriz_Pruebas.md
  Analisis_Reglas_WAF.md
  Registro_Cloud_Logging.md
  Evidencias/

8. CONCLUSIÓN

La aplicación respondió correctamente a las solicitudes legítimas y rechazó los cuatro patrones sospechosos ejecutados mediante el balanceador HTTPS. Cloud Logging permitió confirmar acciones DENY de Cloud Armor y correlacionar los eventos sospechosos con la política y las firmas aplicadas. No se justificaron ajustes con la evidencia reunida; permanece como limitación la falta de validación independiente de la regla XSS de prioridad 1100.

Responsable: @trabajodavidg
