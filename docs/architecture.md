# MeetSpot Architecture & System Overview

MeetSpot is a full-stack, AI-powered multi-criteria meeting place recommendation engine built for the **oussamma.tn** ecosystem.

## High-Level Architecture

```mermaid
flowchart TD
    Client["Client Browser (PWA Next.js 14)"] -->|HTTPS| Proxy["Reverse Proxy / Traefik (Coolify)"]
    Proxy -->|Port 3000| Frontend["Frontend (Next.js Standalone)"]
    Proxy -->|Port 8000| Backend["Backend (FastAPI Python 3.12)"]
    
    Backend -->|SQLAlchemy 2 / AsyncPG| DB[("PostgreSQL + PostGIS")]
    Backend -->|Cache & Sessions| Redis[("Redis")]
    Backend -->|OIDC / UserInfo| SSO["Ecosystem SSO (sso-a.oussamma.tn)"]
    Backend -->|NLP Filtering & Extraction| LiteLLM["LiteLLM AI Gateway (ai.oussamma.tn)"]
    Backend -->|Multi-modal Routing| Routing["Routing Service (OSRM / ORS / Urban Model)"]
```

## System Components

1. **Frontend (`/frontend`)**:
   - Next.js 14 App Router, TypeScript, Tailwind CSS with official `oussamma.tn` tokens.
   - MapLibre GL JS for interactive candidate displays and routes.
   - PWA ready.

2. **Backend (`/backend`)**:
   - Python 3.12, FastAPI, SQLAlchemy 2 Async, Pydantic v2.
   - Multi-criteria deterministic equity algorithm (Minimax, Total, Balanced, Budget).
   - SSO token verification and automatic user provisioning.

3. **AI Gateway**:
   - Interfaced with `https://ai.oussamma.tn/v1` (LiteLLM) using models `chatgpt/gpt-5.4`.
   - Parses unstructured conversational user prompts into strict JSON filter schemas.
