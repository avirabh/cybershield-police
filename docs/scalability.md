# Scalability Plan

CyberShield Police is a local-first hackathon prototype, but the architecture is intentionally shaped so it can grow into a larger district or state deployment.

## From SQLite to PostgreSQL

- Current: SQLite stores demo cases, reports, users, quiz results, threat intelligence, and transaction records locally.
- Next: move database access behind repository/service modules and switch `DATABASE_URL` to PostgreSQL.
- Production additions: migrations, indexes on case status/category/risk/location/date, backups, row-level access rules, and audit logs.

## From Static Demo Data to Verified Sources

- Current datasets are synthetic JSON files for safe demonstration.
- Real deployment should ingest only verified complaint data, authorized police intelligence, bank/payment partner feeds, and approved public threat feeds.
- Data onboarding should include deduplication, privacy checks, redaction, and source confidence scoring.

## Service Separation

Suggested future services:

- Scam detection service
- Phishing/URL trust service
- Transaction monitoring service
- Screenshot/OCR analysis service
- CyberDost assistant service
- Threat intelligence service
- Reports/case management service
- Users/auth/access-control service
- Analytics/reporting service

The current `backend/app/services` folder starts this separation for optional AI and screenshot analysis while keeping local execution simple.

## Rate Limiting and Background Jobs

- Add API rate limiting at FastAPI middleware or reverse proxy level.
- Move long-running OCR, AI summaries, enrichment, export generation, and clustering to background jobs.
- Use queues such as Redis Queue, Celery, or managed cloud queues in production.

## AI Provider Swapping

The current optional AI adapter supports `AI_PROVIDER=multi`, which tries Gemini, OpenRouter, Groq, and Hugging Face when their keys are configured, then falls back to local deterministic responses. The interface is intentionally isolated in `backend/app/services/ai_provider.py` so provider changes do not require frontend rewrites.

Local deterministic risk scoring remains authoritative. AI providers may only summarize, explain, or improve citizen/police wording.

## Privacy and Access Control

- Never store OTP, PIN, CVV, passwords, full bank details, or private evidence unless a real approved evidence workflow exists.
- Use role-based access for Citizen, Police Officer, and Admin/SP.
- Add audit logs for report views, status updates, exports, and officer notes.
- Screenshot analysis should default to metadata/manual text only. External AI must be explicit opt-in.

## Deployment Readiness

- Backend environment values are documented in `.env.example` and `backend/.env.example`.
- Frontend API target is documented in `frontend/.env.example`.
- No secrets are hardcoded.
- Production should add HTTPS, secure cookies/session auth, monitoring, backups, and a real identity verification workflow.
