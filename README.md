# MeetSpot — Le Meilleur Compromis de Rencontre Entre Amis

MeetSpot est une application indépendante intégrée à l'écosystème [oussamma.tn](https://oussamma.tn), accessible sur `https://meet.oussamma.tn`. Elle permet de trouver le meilleur café, restaurant, parc ou activité pour un rassemblement selon les contraintes individuelles et collectives de chaque participant.

---

## 🌟 Fonctionnalités Clés

- 📍 **Algorithme d'équité géographique & transport** : Stratégies **MINIMAX** (minimise le trajet du plus éloigné), **TOTAL** (somme minimale), **BALANCED** (réduit les inégalités entre participants) et **BUDGET**.
- 🤖 **Recherche conversationnelle LiteLLM** : Transforme une requête en langage naturel en contraintes et filtres structurés validés par Pydantic.
- 🔐 **SSO oussamma.tn & Accès invité sans compte** : Connexion via OpenID Connect avec création automatique de profil, et liens d'invitation sécurisés avec hachage SHA-256 pour les invités.
- 🗺️ **Cartographie interactive MapLibre GL** : Visualisation claire des lieux candidats, des scores et des compromis de trajet.
- 🗳️ **Shortlist et Vote collectif** : Élection démocratique du lieu idéal et confirmation d'itinéraire.
- 🛡️ **Respect strict de la vie privée** : Masquage des adresses de départ exactes des participants.

---

## 🛠️ Stack Technique

- **Frontend** : Next.js 14 (App Router, Standalone), TypeScript, Tailwind CSS, shadcn/ui tokens, MapLibre GL JS, Lucide Icons, PWA.
- **Backend** : Python 3.12, FastAPI, SQLAlchemy 2 (Async), Pydantic v2, PostgreSQL + PostGIS, Redis.
- **Intégrations** : LiteLLM Gateway (`ai.oussamma.tn`), SSO Provider (`sso-a.oussamma.tn`).
- **Déploiement** : Docker multi-stage, Docker Compose, Coolify.

---

## 🚀 Démarrage Rapide

### Prérequis
- Docker & Docker Compose

### Lancement avec Docker Compose
```bash
cp .env.example .env
docker compose up -d --build
```
- Frontend : `http://localhost:3000`
- API Backend & Swagger : `http://localhost:8000/docs`
- Healthcheck : `http://localhost:8000/health`
