# Architecture

CyberShield Police is a local-first React + FastAPI prototype designed for Mission Y4 Prakasam Police Hackathon 2026, Challenge 05: Cybercrime Detection & Digital Fraud.

## System View

```text
React + Vite SPA
  | src/api.js
  v
FastAPI backend
  | local services + deterministic detectors
  v
SQLite demo database + synthetic JSON datasets
```

Optional AI providers sit behind the backend only. The frontend never receives API keys.

## Frontend Architecture

Important frontend modules:

- Landing and role-based access
- Scam Analyzer
- URL/UPI/Phishing Scanner
- Screenshot Scam Analyzer
- Transaction Monitor
- Citizen Reporting
- Police/Admin dashboards
- Case Management and Case Details
- Hotspot and Cyber Threat Intelligence dashboards
- Awareness Hub and CyberDost chatbot
- Multilingual support through `src/i18n/translations.js`

All backend access is centralized in `frontend/src/api.js`.

## Backend Architecture

Important backend modules:

- `app/main.py` - FastAPI routes and request schemas
- `app/database.py` - SQLite persistence
- `app/scam_detector.py` - deterministic text/URL scam scoring
- `app/transaction_detector.py` - deterministic transaction risk scoring
- `app/phishing_examples.py` - synthetic phishing examples
- `app/seed_data.py` - demo seeding
- `app/services/ai_provider.py` - optional AI provider adapter with local fallback
- `app/services/screenshot_analyzer.py` - metadata/manual-text screenshot analysis

## Data Flow

1. Citizen/officer submits message, URL, transaction, screenshot metadata, or report.
2. FastAPI validates input using Pydantic request models.
3. Local deterministic detectors compute risk score, risk level, category, confidence, rule matches, citizen explanation, police summary, and triage priority.
4. Optional AI may refine explanations only when configured and explicitly enabled.
5. Cases/reports/transactions are saved to SQLite.
6. Dashboards aggregate analytics from local records and synthetic datasets.
7. Reports can be exported with ReportLab.

## AI Fallback

AI provider priority:

1. Gemini
2. Hugging Face
3. OpenRouter
4. Groq
5. Local fallback

The adapter handles missing keys, failures, timeouts, empty responses, and unsafe outputs by returning local rule-based text. Final classification always comes from local deterministic scoring.

## Local-First Safety

- No paid API is required.
- No real victim, police, bank, UPI, phone, email, or private social media data is used.
- Screenshot analysis stores metadata only by default.
- Optional AI calls are opt-in and should not include sensitive personal information.
