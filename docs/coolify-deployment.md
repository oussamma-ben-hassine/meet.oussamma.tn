# Déploiement Coolify — MeetSpot (meet.oussamma.tn)

MeetSpot est conçu pour être déployé en un clic sur l'infrastructure Coolify de l'écosystème **oussamma.tn**.

## 1. Création de l'application dans Coolify
- **Type** : Docker Compose
- **Dépôt Git** : `https://github.com/oussamma-ben-hassine/meet.oussamma.tn.git`
- **Branche** : `main`
- **Domaine principal** : `https://meet.oussamma.tn`

## 2. Variables d'environnement requises

```env
APP_ENV=production
DEBUG=false
APP_URL=https://meet.oussamma.tn
BACKEND_URL=https://meet.oussamma.tn
SECRET_KEY=cle_secrete_ultra_robuste_generee_aleatoirement

# SSO oussamma.tn
SSO_BASE_URL=https://sso-a.oussamma.tn
SSO_CLIENT_ID=client_424090bad2dcadc34cdda40f
SSO_CLIENT_SECRET=sec_RGhuA2Qsxu5YDZ_7NT4j8wNeWnGrd3l8E9dbeko0QcM
SSO_REDIRECT_URI=https://meet.oussamma.tn/auth/callback
SUPER_ADMIN_EMAILS=contact@oussamma.tn

# LiteLLM
LITELLM_BASE_URL=https://ai.oussamma.tn/v1
LITELLM_API_KEY=sk-oussamma-master-gateway-2026
LITELLM_DEFAULT_MODEL=chatgpt/gpt-5.4

# Database
POSTGRES_USER=meetspot_user
POSTGRES_PASSWORD=meetspot_secure_password_2026
POSTGRES_DB=meetspot_db
```

## 3. Configuration réseau & Traefik
Le service frontend écoute sur le port `3000` et gère le routage transparent des requêtes `/api/v1/*` vers le service backend FastAPI sur le port `8000` au sein du réseau Docker interne `meetspot_internal`.
