# Prototipo-de-seguridad-perimetral-WAF-ESIT-2026
# WAF Shield Cloud - Seguridad Perimetral para Aplicaciones en la Nube

## 1. Descripción General
Este repositorio contiene el desarrollo del Proyecto 7: WAF Shield Cloud, enfocado en implementar una estrategia de seguridad perimetral para proteger aplicaciones web desplegadas en la nube. El proyecto es desarrollado para la Unidad de Seguridad Digital y Protección de Servicios Cloud (USDP-SC) de la Universidad Nova Digital.

El objetivo principal es reducir la exposición a amenazas web comunes (OWASP Top 10), filtrar tráfico malicioso antes de que llegue al backend y generar evidencias de control, monitoreo y mitigación de incidentes.

## 2. Duración y Fases del Proyecto
El proyecto está estructurado para una duración de 10 semanas divididas en las siguientes etapas:
- Fase 0: Onboarding y planificación.
- Fase 1: Análisis del entorno, riesgos y diseño de la solución.
- Fase 2: Implementación del entorno protegido y configuración del WAF.
- Fase 3: Validación de seguridad, pruebas de tráfico y refinamiento.
- Fase 4: Cierre, documentación y entrega profesional.

## 3. Equipo de Trabajo y Roles
- Julissa Girón (@Esme8906) - Líder de proyecto Jr. y Documentador Jr.
- David Guzmán (@trabajodavidg) - Ingeniero de Infraestructura Jr.
- Edwin Gómez (@edchellowin31) - Analista QA / Seguridad Jr.
- Jhony Jiménez (@jhonyuls-svg) - Desarrollador Web Jr.
- Mauricio Martínez (@Mauricio-coder783) - Ingeniero de Seguridad Cloud Jr.

## 4. Stack Tecnológico y Plan de Recursos (Fase 1)
Para el desarrollo de este prototipo y de acuerdo con el análisis técnico del equipo, se ha seleccionado el siguiente stack optimizado para entornos educativos y de control perimetral:
- **Alojamiento de Aplicación Web (Backend / Cloud):** Google Cloud Platform (GCP) / Cloud Run
- **Seguridad Perimetral y WAF:** Google Cloud Platform (GCP) / Cloud Armor. En la Fase 2 se reportó la política `waf-shield-policy` con reglas SQLi y XSS.
- **Control de Versiones y Gestión:** GitHub y GitHub Projects (Tablero Kanban).
- **Herramientas de Diagramación y Calidad:** Draw.io / Lucidchart y Matrices de Riesgos OWASP.

## 5. Estructura del Repositorio
- Fase 0 – Onboarding y Planificación
- Fase 1 – Análisis del entorno, riesgos y diseño de la solución
- Fase 2 – Implementación y Configuración del WAF
- Fase 3 – Validación de seguridad, pruebas de tráfico y refinamiento

## 6. Avances por fase

### Fase 1 – Análisis del entorno, riesgos y diseño

Se analizó el entorno, la superficie de exposición y los riesgos del proyecto, y se definió el diseño inicial de la solución. Entre los entregables de esta fase están la matriz de riesgos OWASP, el diagrama de topología y flujo de tráfico, y las bitácoras del equipo. Los documentos están disponibles en la [Carpeta de Fase 1](<Fase 1 – Análisis del entorno, riesgos y diseño de la solución/>) 

### Fase 2 – Implementación y configuración del WAF

Se desplegó la aplicación de prueba en Cloud Run y se configuró Cloud Armor detrás del balanceador HTTPS. Según las validaciones reportadas, el tráfico legítimo respondió HTTP 200 por el balanceador, las solicitudes de prueba SQLi/XSS recibieron HTTP 403 y el acceso directo a la URL de Cloud Run respondió HTTP 404.

Las pruebas funcionales locales de la aplicación reportaron 5/5 casos aprobados; estas no representan una validación del WAF. La matriz de QA quedó preparada, pero las pruebas de seguridad no se reportaron como ejecutadas. En Cloud Logging no se encontraron solicitudes WAF para atribuir los bloqueos. Las bitácoras y evidencias están disponibles en la [carpeta de Fase 2](<Fase 2 – Implementación y Configuración del WAF/>).

### Fase 3 – Validación de seguridad, pruebas de tráfico y refinamiento
Se ejecutaron pruebas controladas de tráfico legítimo y malicioso, verificaciones de infraestructura en Google Cloud (`proyecto-7-waf-shield-cloud`, rutas `v1` y `v2-test`), correlación con Cloud Logging (`sampleRate=1.0`), pruebas unitarias locales de la aplicación (`npm test`, 6/6 aprobadas) y pruebas comparativas en entorno local y sandbox aislado (`waf-shield-esit-sn2-2026`, desmantelado con costo `$0.00/h`).

Entre los hallazgos y límites documentados en esta fase se encuentran: el bloqueo de solicitudes legítimas en `POST /comments` por la regla SQLi de prioridad `1000` (posible falso positivo en `V-05`), la atribución secuencial que impidió demostrar de forma independiente la regla XSS de prioridad `1100`, el bloqueo del refinamiento `R-05` por restricciones de permisos IAM (`compute.securityPolicies.update`) y el ajuste autorizado de la regla prioridad `2000` en `waf-shield-policy-v2` para la IP `34.75.169.185/32`.

Las bitácoras individuales, la bitácora grupal, la matriz QA OWASP 2025 y las evidencias están disponibles en la [Carpeta de Fase 3](https://github.com/Esme8906/Prototipo-de-seguridad-perimetral-WAF-SN2-ESIT-2026/tree/main/Fase%203%20%E2%80%93%20Validaci%C3%B3n%20de%20seguridad%20y%20pruebas). 

## 7. Enlaces de Interés
- Tablero de Gestión (GitHub Projects): https://github.com/users/Esme8906/projects/2
