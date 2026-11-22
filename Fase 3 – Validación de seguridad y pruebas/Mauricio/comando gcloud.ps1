# ==============================================================================
# 1. HABILITACIÓN DE APIS Y DESPLIEGUE AISLADO EN CLOUD RUN (SANDBOX GCP)
# ==============================================================================
gcloud services enable run.googleapis.com compute.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com

gcloud run deploy waf-sandbox-app `
    --source . `
    --region us-central1 `
    --platform managed `
    --ingress internal-and-cloud-load-balancing `
    --allow-unauthenticated

# ==============================================================================
# 2. POLÍTICA CLOUD ARMOR (RATE LIMITING, SQLI, XSS) Y GLOBAL LOAD BALANCER
# ==============================================================================
gcloud compute security-policies create waf-shield-sn2-policy `
    --description "Politica WAF Fase 3 - Grupo SN-2"

# Prioridad 1000: Rate Limiting (10 peticiones / 60 segundos por IP -> HTTP 429)
gcloud compute security-policies rules create 1000 `
    --security-policy waf-shield-sn2-policy `
    --src-ip-ranges "*" `
    --action throttle `
    --rate-limit-threshold-count 10 `
    --rate-limit-threshold-interval-sec 60 `
    --conform-action allow `
    --exceed-action deny-429 `
    --enforce-on-key IP

# Prioridad 2000: Firma preconfigurada OWASP SQL Injection (-> HTTP 403)
gcloud compute security-policies rules create 2000 `
    --security-policy waf-shield-sn2-policy `
    --expression "evaluatePreconfiguredWaf('sqli-v33-stable')" `
    --action deny-403

# Prioridad 3000: Firma preconfigurada OWASP Cross-Site Scripting (-> HTTP 403)
gcloud compute security-policies rules create 3000 `
    --security-policy waf-shield-sn2-policy `
    --expression "evaluatePreconfiguredWaf('xss-v33-stable')" `
    --action deny-403

# Enlace Serverless NEG -> Backend Service -> Cloud Armor -> Load Balancer HTTP
gcloud compute network-endpoint-groups create waf-sandbox-neg `
    --region=us-central1 `
    --network-endpoint-type=serverless `
    --cloud-run-service=waf-sandbox-app

gcloud compute backend-services create waf-shield-backend `
    --global `
    --load-balancing-scheme=EXTERNAL_MANAGED

gcloud compute backend-services add-backend waf-shield-backend `
    --global `
    --network-endpoint-group=waf-sandbox-neg `
    --network-endpoint-group-region=us-central1

gcloud compute backend-services update waf-shield-backend `
    --security-policy=waf-shield-sn2-policy `
    --global

gcloud compute url-maps create waf-shield-url-map --default-service=waf-shield-backend
gcloud compute target-http-proxies create waf-shield-proxy --url-map=waf-shield-url-map

gcloud compute forwarding-rules create waf-shield-forwarding-rule `
    --load-balancing-scheme=EXTERNAL_MANAGED `
    --network-tier=PREMIUM `
    --address-region=global `
    --global `
    --target-http-proxy=waf-shield-proxy `
    --ports=80

# Consulta de dirección IPv4 pública asignada al balanceador
gcloud compute forwarding-rules describe waf-shield-forwarding-rule --global --format="value(IPAddress)"

# ==============================================================================
# 3. DESMANTELAMIENTO Y LIMPIEZA FINOPS ($0.00/h) TRAS AUDITORÍA
# ==============================================================================
gcloud compute forwarding-rules delete waf-shield-forwarding-rule --global --quiet
gcloud compute target-http-proxies delete waf-shield-proxy --quiet
gcloud compute url-maps delete waf-shield-url-map --quiet
gcloud compute backend-services delete waf-shield-backend --global --quiet
gcloud compute network-endpoint-groups delete waf-sandbox-neg --region=us-central1 --quiet
gcloud compute security-policies delete waf-shield-sn2-policy --quiet
gcloud run services delete waf-sandbox-app --region=us-central1 --quiet