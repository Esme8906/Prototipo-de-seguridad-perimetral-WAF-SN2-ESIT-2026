#!/bin/bash
# ------------------------------------------------------------------------------
# PROYECTO: WAF Shield Cloud - Grupo SN-2
# DESCRIPCIÓN: Script de despliegue automatizado de política perimetral en GCP
# AUTOR: Mauricio Alberto Grande Martínez
# ------------------------------------------------------------------------------

# 1. Crear la política de seguridad perimetral en Cloud Armor
gcloud compute security-policies create waf-shield-sn2-policy \
    --description="Politica perimetral WAF Shield Cloud - Grupo SN-2"

# 2. Regla 1000: Rate Limiting en /login (Mitigación de Fuerza Bruta)
# Restringe a máximo 5 peticiones por minuto por dirección IP; banea por 5 minutos al exceder.
gcloud compute security-policies rules create 1000 \
    --security-policy=waf-shield-sn2-policy \
    --expression="request.path.matches('/login')" \
    --action="rate-based-ban" \
    --rate-limit-threshold-count=5 \
    --rate-limit-threshold-interval-sec=60 \
    --ban-duration-sec=300 \
    --conform-action="allow" \
    --exceed-action="deny(403)" \
    --enforce-on-key="IP"

# 3. Regla 2000: Protección contra Inyección SQL (SQLi en L7)
# Utiliza el conjunto de reglas preconfiguradas de OWASP para SQLi
gcloud compute security-policies rules create 2000 \
    --security-policy=waf-shield-sn2-policy \
    --expression="evaluatePreconfiguredExpr('sqli-v933100')" \
    --action="deny(403)"

# 4. Regla 3000: Protección contra Cross-Site Scripting (XSS en L7)
# Utiliza el conjunto de reglas preconfiguradas de OWASP para XSS
gcloud compute security-policies rules create 3000 \
    --security-policy=waf-shield-sn2-policy \
    --expression="evaluatePreconfiguredExpr('xss-v941100')" \
    --action="deny(403)"

# 5. Regla 4000: Restricción de acceso a rutas administrativas (/admin)
# Intercepta en el perímetro cualquier intento de acceso a la consola interna
gcloud compute security-policies rules create 4000 \
    --security-policy=waf-shield-sn2-policy \
    --expression="request.path.matches('/admin')" \
    --action="deny(403)"