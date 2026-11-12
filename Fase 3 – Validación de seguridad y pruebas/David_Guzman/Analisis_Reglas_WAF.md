# Análisis de reglas WAF y falsos positivos — Fase 3

**Proyecto:** WAF Shield Cloud — Equipo SN-2  
**Responsable:** [@trabajodavidg](https://github.com/trabajodavidg)  
**Fecha del análisis:** 12 de noviembre de 2026  
**Fecha límite de Kanban:** 19 de noviembre de 2026  
**Política:** `waf-shield-policy`

## 1. Objetivo

Comparar los resultados del tráfico legítimo y sospechoso, identificar bloqueos inesperados o solicitudes sospechosas permitidas, y determinar con evidencia si corresponde modificar las reglas de Cloud Armor.

## 2. Configuración observada

| Prioridad | Expresión | Acción | Estado de evaluación |
|---|---|---|---|
| 1000 | `evaluatePreconfiguredWaf('sqli-v33-stable')` | `deny(403)` | `preview: false` |
| 1100 | `evaluatePreconfiguredWaf('xss-v33-stable')` | `deny(403)` | `preview: false` |
| 2147483647 | Regla predeterminada | `allow` | `preview: false` |

**Fuente:** [E3-DG-03 — Configuración de reglas](Evidencias/E3-DG-03_Reglas_Cloud_Armor.png).

## 3. Comparación de resultados

Según la [matriz de ocho pruebas](Matriz_Pruebas.md):

- **Tráfico legítimo:** 4 de 4 casos recibieron HTTP 200, incluido `O'Reilly`, una entrada con apóstrofo. **No se observó un falso positivo en estos casos.**
- **Tráfico sospechoso:** 4 de 4 casos recibieron HTTP 403 (un SQLi y tres variantes XSS). **No se observó una solicitud sospechosa permitida en esta muestra.**
- Los resultados observados coincidieron con los esperados, pero la muestra es limitada y no prueba la ausencia general de falsos positivos o falsos negativos.

## 4. Hallazgo: coincidencias SQLi en solicitudes XSS

| Caso | Evidencia de solicitud | Evidencia de registro | Regla aplicada | Firma registrada |
|---|---|---|---|---|
| F3-DG-05 — SQLi | [E3-DG-09](Evidencias/E3-DG-09_Prueba_SQL_Injection.png) | [E3-DG-12](Evidencias/E3-DG-12_Consulta_Eventos_WAF.png) | Prioridad 1000 | `owasp-crs-v030301-id942180-sqli` (registro 16:12:25) |
| F3-DG-06 — XSS `script` | [E3-DG-10](Evidencias/E3-DG-10_Prueba_XSS.png) | [E3-DG-12](Evidencias/E3-DG-12_Consulta_Eventos_WAF.png) | Prioridad 1000 | `owasp-crs-v030301-id942431-sqli` |
| F3-DG-07 — XSS `img` | [E3-DG-13](Evidencias/E3-DG-13_Validacion_Adicional_XSS.png) | [E3-DG-14](Evidencias/E3-DG-14_Correlacion_XSS_Cloud_Armor.png) | Prioridad 1000 | `owasp-crs-v030301-id942431-sqli` |
| F3-DG-08 — XSS `svg` | [E3-DG-16](Evidencias/E3-DG-16_Prueba_Adicional_XSS_SVG.png) | [E3-DG-17](Evidencias/E3-DG-17_Correlacion_XSS_SVG_Cloud_Armor.png) | Prioridad 1000 | `owasp-crs-v030301-id942432-sqli` |

Los registros incluyen `enforcedSecurityPolicy.name: waf-shield-policy`, `configuredAction: DENY`, `outcome: DENY` y `statusDetails: denied_by_security_policy`. La correlación se apoya en las marcas de tiempo, las rutas y los parámetros codificados de las solicitudes.

**Interpretación:** la regla SQLi de prioridad 1000 coincidió con las tres cargas XSS evaluadas y produjo el rechazo. Esto no demuestra que la regla XSS de prioridad 1100 esté defectuosa; tampoco demuestra que esa regla haya bloqueado independientemente una solicitud.

La búsqueda de eventos `enforcedSecurityPolicy.priority=1100` del 12/11/2026 no devolvió resultados ([E3-DG-15](Evidencias/E3-DG-15_Busqueda_Eventos_Regla_XSS.png)). La ausencia de registros coincidentes **no equivale** a prueba de mal funcionamiento.

## 5. Decisión sobre ajustes

**Decisión al 12/11/2026: no modificar reglas.**

**Justificación:** todos los casos ejecutados produjeron el código esperado; no se observó un falso positivo en los cuatro casos legítimos ni una solicitud sospechosa permitida en los cuatro casos sospechosos. Los eventos recuperados confirman que Cloud Armor ejecutó las denegaciones documentadas.

**Cambios realizados:** ninguno.  
**Pruebas posteriores a cambios:** no aplican, porque no se modificó la política.

Esta decisión es **acotada a los casos probados**. La prioridad 1100 permanece sin validación independiente y debe documentarse como limitación, no como falla confirmada.

## 6. Seguimiento recomendado

1. Ampliar la matriz con entradas legítimas representativas para mejorar la detección de falsos positivos.
2. Diseñar una validación controlada de la regla XSS que permita observar su actuación sin debilitar la protección del entorno; documentar cualquier cambio **antes** de aplicarlo y repetir los casos afectados.
3. Conservar registros con marcas UTC, URL, política, prioridad, firma y acción.
4. Si se identifica un bloqueo legítimo o un ataque permitido, abrir un análisis específico y justificar cualquier ajuste antes de ejecutarlo.

## 7. Estado de la tarjeta Kanban

**Análisis técnico:** completado el 12/11/2026.  
**Ajustes:** no necesarios según los casos evaluados; ninguno realizado.  

