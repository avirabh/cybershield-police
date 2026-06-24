# Deployment Guide

CyberShield Police is a local-first hackathon prototype. It can be shown live with Replit for a temporary demo, or split between Render and Vercel for a cleaner public deployment.

## Option 1: Replit Preview

1. Create a new Replit project and import the GitHub repository.
2. Add optional secrets in Replit Secrets:
   - `GEMINI_API_KEY`
   - `GEMINI_MODEL=gemini-2.5-flash`
   - `AI_PROVIDER=multi`
   - `AI_PROVIDER_ORDER=gemini,openrouter,groq,huggingface`
   - `OPENROUTER_API_KEY` optional
   - `GROQ_API_KEY` optional
   - `HUGGINGFACE_API_KEY` optional
   - `AI_TIMEOUT_SECONDS=20`
3. Keep the app working without AI keys by leaving all provider keys blank.
4. Run:

```bash
bash start-replit.sh
```

The script installs backend and frontend dependencies, seeds fictional demo data, starts FastAPI on `0.0.0.0:8000`, and starts Vite on `0.0.0.0:5173`.

## Option 2: Render Backend + Vercel Frontend

Backend on Render:

- Root directory: `backend`
- Build command: `pip install -r requirements.txt && python seed_demo_data.py`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Environment variables:
  - `DATABASE_URL=sqlite:///./cybershield_demo.db`
  - `CORS_ORIGINS=https://YOUR-VERCEL-APP.vercel.app`
  - `GEMINI_API_KEY` optional
  - `GEMINI_MODEL=gemini-2.5-flash`
  - `AI_PROVIDER=multi`
  - `AI_PROVIDER_ORDER=gemini,openrouter,groq,huggingface`
  - `OPENROUTER_API_KEY` optional
  - `GROQ_API_KEY` optional
  - `HUGGINGFACE_API_KEY` optional
  - `AI_TIMEOUT_SECONDS=20`
  - `URL_CHECK_PROVIDER=local_only`
  - `GOOGLE_SAFE_BROWSING_API_KEY` optional
  - `URLHAUS_AUTH_KEY` optional

Frontend on Vercel:

- Root directory: `frontend`
- Build command: `npm install && npm run build`
- Output directory: `dist`
- Environment variable:
  - `VITE_API_BASE_URL=https://YOUR-RENDER-BACKEND.onrender.com`

## Optional URL Reputation API

The phishing scanner always runs local explainable URL rules. To add external reputation enrichment, set:

```text
URL_CHECK_PROVIDER=multi
GOOGLE_SAFE_BROWSING_API_KEY=<YOUR_LEGAL_API_KEY>
URLHAUS_AUTH_KEY=<YOUR_FREE_URLHAUS_AUTH_KEY>
```

You can also use `URL_CHECK_PROVIDER=google_safe_browsing` or `URL_CHECK_PROVIDER=urlhaus` for one provider. If keys are absent, the scanner stays local. External `no_match` results are never treated as a safety guarantee; local rules still classify suspicious domains.

## Final Live Demo Checks

- Homepage opens.
- Demo login works for Citizen, Police Officer, and Admin/SP.
- Citizen report saves.
- Phishing scanner and CyberDost call the backend.
- Transaction Monitor saves synthetic transactions.
- Police dashboard loads seeded analytics.
- No real data or real credentials are entered.
- If Gemini is not configured, Local Safety Mode still works.
