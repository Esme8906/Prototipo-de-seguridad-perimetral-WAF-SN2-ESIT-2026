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
  - Documento de Análisis y Diseño
  - Diagramas de Topología y Flujo de Tráfico
  - Bitácoras individuales y grupales de la Fase 1
- [Fase 2 – Implementación y Configuración del WAF](<Fase 2 – Implementación y Configuración del WAF/>)
- Fase 3 – Validación y Pruebas de Tráfico
- Fase 4 – Cierre y Documentación Final

## 6. Avances de la Fase 2

Durante esta fase se desplegó la aplicación de prueba en Cloud Run y se configuró Cloud Armor detrás del balanceador HTTPS.

Según las validaciones reportadas, el tráfico legítimo respondió HTTP 200 por el balanceador; las solicitudes de prueba SQLi/XSS recibieron HTTP 403; y el acceso directo a la URL de Cloud Run respondió HTTP 404.

Las pruebas funcionales de la aplicación reportaron 5/5 casos aprobados en el entorno local. Estas pruebas no representan una validación del WAF. La matriz de QA quedó preparada para ejecutarse en la siguiente fase. En Cloud Logging se revisó una consulta, pero no se encontraron solicitudes WAF para atribuir bloqueos.

Las bitácoras y evidencias de la Fase 2 están organizadas en la [carpeta de Fase 2](<Fase 2 – Implementación y Configuración del WAF/>).

## 7. Enlaces de Interés
- Tablero de Gestión (GitHub Projects): https://github.com/users/Esme8906/projects/2
