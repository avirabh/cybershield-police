# API Reference

Base URL: `http://localhost:8000`

## Health and AI

- `GET /` - API status.
- `GET /ai/status` - optional AI provider status. Does not expose API keys.
- `POST /ai/test` - optional Gemini provider test endpoint. Returns provider used and fallback status.

## Authentication

- `POST /auth/login`
- `POST /auth/register/citizen`
- `POST /auth/register/police`
- `GET /auth/me?email=...`
- `POST /auth/logout`

Authentication is mock/demo-based for hackathon evaluation.

## Scam and Phishing Analysis

- `POST /analyze` - scam/message/URL analysis.
- `POST /phishing/scan` - URL/email/message phishing scan with optional AI explanation.
  - Local URL/domain rules are authoritative.
  - Optional URL reputation enrichment is available with `URL_CHECK_PROVIDER=google_safe_browsing`, `URL_CHECK_PROVIDER=urlhaus`, or `URL_CHECK_PROVIDER=multi`.
  - Configure `GOOGLE_SAFE_BROWSING_API_KEY` and/or `URLHAUS_AUTH_KEY` for external checks.
  - A threat match raises the scan to phishing triage. A `no_match` result is not treated as proof of safety.
- `POST /screenshots/analyze` - screenshot metadata/manual-text analysis. Image bytes are not stored.

## Cases and Reports

- `GET /cases`
- `GET /cases/{id}`
- `DELETE /cases/{id}`
- `GET /reports`
- `POST /reports`
- `GET /reports/{id}`
- `POST /reports/{id}/assign`
- `POST /reports/{id}/status`
- `POST /reports/{id}/notes`
- `GET /export/{id}`

## Dashboards and Analytics

- `GET /analytics`
- `GET /admin/analytics`
- `GET /hotspots`
- `GET /threat-intel`
- `GET /threat-intel/dashboard`
- `GET /threat-intel/incidents`
- `GET /threat-intel/indicators/search?query=...`
- `GET /threat-intel/clusters`
- `GET /threat-intel/clusters/{id}`

## Transactions

- `POST /transactions/analyze`
- `GET /transactions`
- `GET /transactions/{id}`
- `GET /transactions/analytics`

## CyberDost and Awareness

- `POST /chatbot/message`
- `GET /awareness/quiz`
- `POST /awareness/quiz/submit`

## Notes

- All demo data is synthetic.
- Local deterministic risk scoring is authoritative.
- Optional AI is disabled unless backend environment keys are configured and the user explicitly enables AI analysis in supported UI flows.
