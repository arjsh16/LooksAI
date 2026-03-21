# LooksAI

> Upload 3 face photos. Get your ideal haircut, a personalized barber brief, and targeted skincare tips — powered by MediaPipe, EfficientNet, and Mistral.

## How it works

1. **Upload** front, left-profile, and right-profile photos
2. **Analyze** — MediaPipe extracts 468 face landmarks; a geometric classifier derives your face shape; EfficientNet evaluates skin condition; a feature extractor labels jawline, forehead, and cheekbone prominence
3. **Chat** — the bot summarizes findings, asks your maintenance and length preferences, then streams a full recommendation via Mistral Small
4. **Receive** — narrative explanation, a barber-ready markdown table, and targeted skincare / lifestyle tips

## Stack

| Layer | Tech |
|---|---|
| Frontend | React 18, Vite, GitHub Pages |
| Backend | FastAPI, async SQLAlchemy, Redis |
| ML | MediaPipe, EfficientNet (PyTorch), OpenCV |
| LLM | Mistral Small (streaming) |
| DB | PostgreSQL 16 |
| Infra | Docker Compose (dev), Kubernetes (prod), Nginx |

## Datasets used for training

- **ACNE04** — acne severity grading
- **CelebA** — face attribute labels
- **FFHQ** — high-quality face images for skin analysis
- **300W** — facial landmark localization
- **UTKFace** — face attribute diversity

## Quickstart (dev)
```bash
cp .env.example .env          # fill in secrets
docker compose up --build     # starts backend + postgres + redis
cd frontend && npm install && npm run dev
```

## Environment variables

See `.env.example` for the full list. Required keys:
- `SECRET_KEY` — JWT signing secret
- `DATABASE_URL` — `postgresql+asyncpg://...`
- `MISTRAL_API_KEY`

## Project structure
```
LooksAI/
├── README.md
├── requirements.txt
├── LICENSE
├── .gitignore
│
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── index.jsx
│   │   ├── App.jsx
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx
│   │   │   ├── AnalysisPage.jsx
│   │   │   └── ChatPage.jsx
│   │   ├── components/
│   │   │   ├── auth/
│   │   │   │   ├── LoginForm.jsx
│   │   │   │   └── RegisterForm.jsx
│   │   │   ├── analysis/
│   │   │   │   ├── PhotoUploader.jsx
│   │   │   │   └── AnalysisStatus.jsx
│   │   │   ├── chat/
│   │   │   │   ├── ChatWindow.jsx
│   │   │   │   ├── MessageBubble.jsx
│   │   │   │   └── ChoiceButtons.jsx
│   │   │   └── ui/
│   │   │       ├── Spinner.jsx
│   │   │       └── MarkdownRenderer.jsx
│   │   ├── hooks/
│   │   │   ├── useAuth.js
│   │   │   ├── useWebSocket.js
│   │   │   └── useAnalysis.js
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── context/
│   │   │   └── AuthContext.jsx
│   │   └── styles/
│   │       └── index.css
│   ├── package.json
│   └── vite.config.js
│
├── backend/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   ├── models/
│   │   ├── user.py
│   │   └── analysis.py
│   ├── routers/
│   │   ├── auth.py
│   │   ├── analysis.py
│   │   ├── recommendations.py
│   │   └── chat.py
│   └── services/
│       ├── face_analysis/
│       │   ├── pipeline.py
│       │   ├── mediapipe_mesh.py
│       │   ├── shape_classifier.py
│       │   ├── skin_analyzer.py
│       │   └── feature_extractor.py
│       ├── recommendation/
│       │   └── engine.py
│       └── llm/
│           └── mistral_client.py
│
├── database/
│   ├── schema.sql
│   ├── alembic.ini
│   └── migrations/
│       ├── env.py
│       ├── script.py.mako
│       └── versions/
│           └── 0001_initial.py
│
└── infrastructure/
    ├── docker-compose.yml
    ├── docker-compose.prod.yml
    ├── nginx/
    │   ├── nginx.conf
    │   └── default.conf
    └── k8s/
        ├── namespace.yaml
        ├── backend-deployment.yaml
        ├── backend-service.yaml
        ├── postgres-statefulset.yaml
        ├── postgres-service.yaml
        ├── redis-deployment.yaml
        ├── redis-service.yaml
        ├── ingress.yaml
        └── secrets.yaml
```

## License

MIT