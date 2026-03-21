# LooksAI 

> Upload 3 face photos. Get your ideal haircut, a barber-ready brief, and targeted skincare tips — powered by MediaPipe, EfficientNet, and Mistral.

---

## How it works

1. **Upload** front, left-profile, and right-profile photos  
2. **Analyse** — MediaPipe extracts 468 face landmarks; a geometric classifier derives your face shape; EfficientNet evaluates skin condition; a feature extractor labels jawline, forehead, and cheekbone prominence  
3. **Chat** — the bot summarises findings, asks your maintenance and length preferences, then streams a full recommendation via Mistral Small  
4. **Receive** — narrative explanation, a barber-ready markdown table, and targeted skincare / lifestyle tips  

---

## Stack

| Layer    | Tech                                           |
|----------|------------------------------------------------|
| Frontend | React 18, Vite, GitHub Pages                   |
| Backend  | FastAPI, async SQLAlchemy, Redis               |
| ML       | MediaPipe, EfficientNet B0 (PyTorch), OpenCV   |
| LLM      | Mistral Small (streaming SSE)                  |
| DB       | PostgreSQL 16                                  |
| Infra    | Docker Compose (dev), Kubernetes (prod), Nginx |

---

## Quickstart (dev)

```bash
# 1. Clone and set up secrets
cp .env.example .env          # fill in SECRET_KEY + MISTRAL_API_KEY

# 2. Start backend services
cd infrastructure
docker compose up --build     # starts backend + postgres + redis

# 3. Start frontend
cd frontend
npm install
npm run dev                   # → http://localhost:5173/LooksAI/
```

---

## Environment variables

See `.env.example` for the full list. Minimum required:

| Variable          | Description                                    |
|-------------------|------------------------------------------------|
| `SECRET_KEY`      | JWT signing secret (generate with `openssl rand -hex 32`) |
| `DATABASE_URL`    | `postgresql+asyncpg://user:pass@host/db`       |
| `MISTRAL_API_KEY` | From [console.mistral.ai](https://console.mistral.ai) |

---

## Database migrations

```bash
# Run from repo root
alembic -c database/alembic.ini upgrade head
```

---

## Deploy frontend to GitHub Pages

```bash
cd frontend
npm run deploy    # builds and pushes to gh-pages branch
```

Set the GitHub Pages source to the `gh-pages` branch in your repo settings.  
The Vite base is pre-configured as `/LooksAI/`.

---

## ML models

The EfficientNet skin model requires a fine-tuned checkpoint at `models/skin_efficientnet.pth`.  
If no checkpoint is present the backend **automatically falls back to heuristic-only analysis** — the app stays fully functional, just with slightly less accurate skin scoring.

Recommended training datasets: **ACNE04**, **CelebA**, **FFHQ**, **300W**, **UTKFace**.

---

## Project structure

```
LooksAI/
├── backend/
│   ├── main.py                          # FastAPI app + lifespan
│   ├── core/                            # config, database, security (JWT)
│   ├── models/                          # SQLAlchemy ORM (user, analysis, chat)
│   ├── routers/                         # auth, analysis, recommendations, chat (WS)
│   └── services/
│       ├── face_analysis/               # MediaPipe → shape → skin → features
│       ├── recommendation/engine.py     # 3-D haircut hashmap
│       └── llm/mistral_client.py        # streaming Mistral integration
├── frontend/
│   └── src/
│       ├── context/AuthContext.jsx      # JWT auth state
│       ├── hooks/                       # useAuth, useAnalysis, useWebSocket
│       ├── services/api.js              # axios + WS URL factory
│       ├── components/                  # PhotoUploader, ChatWindow, bubbles…
│       └── pages/                       # LoginPage, AnalysisPage, ChatPage
├── database/
│   ├── schema.sql                       # Raw DDL (used by Docker init)
│   └── migrations/                      # Alembic async migrations
└── infrastructure/
    ├── docker-compose.yml               # Dev stack
    ├── docker-compose.prod.yml          # Prod stack (with nginx)
    ├── nginx/                           # Reverse proxy + WS upgrade config
    └── k8s/                             # Kubernetes manifests
```

---

## License

MIT
