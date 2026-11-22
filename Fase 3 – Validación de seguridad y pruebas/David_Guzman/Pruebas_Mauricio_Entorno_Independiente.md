# Pruebas complementarias de Mauricio — Fase 3

**Fuente:** carpeta `Fase 3 – Validación de seguridad y pruebas/Mauricio/` del ZIP del repositorio actualizado. **Entorno independiente** del proyecto GCP principal de David. No se desplegó esta aplicación en el entorno de David.

## Evidencia documental revisada

El README del entorno de Mauricio describe una comparación entre Nginx + ModSecurity local y Cloud Armor en un sandbox GCP, con 17 solicitudes de auditoría. Reporta:

| Prueba | Local Nginx/ModSecurity | Sandbox Cloud Armor |
| --- | --- | --- |
| Healthcheck | HTTP 200 | HTTP 200 |
| Login legítimo | HTTP 200 | HTTP 200 |
| SQLi en login | HTTP 403 (WAF) | HTTP 401 (backend; no bloqueo WAF) |
| XSS en búsqueda | HTTP 403 (WAF) | HTTP 200 (backend; no bloqueo WAF) |
| Concurrencia, 10 solicitudes | 0 bloqueos WAF | 7 respuestas HTTP 429 atribuidas a rate limiting |

El script `comando gcloud.ps1` incluye una política de sandbox `waf-shield-sn2-policy`: throttle 10 solicitudes/60 s/IP prioridad 1000, SQLi prioridad 2000, XSS prioridad 3000; crea y elimina infraestructura temporal. **No ejecutar aun en el proyecto principal**: incluye nombres de recursos que coinciden con los existentes (`waf-shield-backend`, `waf-shield-url-map`) y comandos destructivos.

## 
