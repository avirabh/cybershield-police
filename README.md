# CyberShield Police

CyberShield Police is a complete local prototype for **Mission Y4 Prakasam Police Hackathon 2026 - Challenge 05: Cybercrime Detection & Digital Fraud**. It helps citizens and police triage suspicious scam messages, phishing links, transaction-risk patterns, and synthetic cyber threat intelligence signals for Prakasam / Andhra Pradesh.

The app uses only synthetic demo data and runs locally without paid APIs, secrets, or mandatory external AI services. Optional AI providers can be configured on the backend for explanation refinement, but local deterministic scoring remains authoritative.

## Problem Statement

Digital fraud cases often start with small signals: an urgent SMS, a shortened link, a fake KYC warning, a job registration fee, a QR refund request, or a caller pretending to be an official. Citizens need clear advice before they act, and police teams need structured reports, risk scoring, and analytics to prioritize investigation.

## Features

- Scam analyzer for SMS, WhatsApp, email, Telegram, call notes, suspicious URLs, and metadata-only context
- Screenshot Scam Analyzer for safe image metadata plus pasted visible text from scam screenshots
- Transaction Monitor for synthetic UPI, bank transfer, wallet, and card transaction risk analysis
- Cyber Threat Intelligence dashboard with Prakasam/AP synthetic incident heat, trends, charts, and filters
- Indicator Lookup for masked/demo phones, UPI placeholders, account placeholders, fake domains, demo IPs, and scam keywords
- Case Pattern Analyzer for synthetic linked-case clusters, shared indicators, repeated scripts, and recommended police action
- Strong text-only detection, so scams can be detected even when no URL is present
- Explainable risk score from 0 to 100
- Risk levels: Low, Medium, High, Critical
- Police triage priority: Low Priority, Review Recommended, High Priority, Critical Immediate Triage
- Scam category detection:
  - OTP Fraud
  - UPI Fraud
  - Fake KYC/Bank Alert
  - Phishing
  - Fake Job Scam
  - Work From Home Scam
  - Fake Loan Scam
  - Lottery/Prize Scam
  - Investment Scam
  - Fake Customer Care Scam
  - Courier/Parcel Scam
  - Impersonation Scam
  - Fake Police/Legal Threat
  - QR Code Scam
  - Unknown Suspicious
  - Likely Safe
- Triggered risk factors with weighted scoring
- Matched pattern output for transparent rule explanations
- Detection mode output: text-only, URL-only, metadata-only, or hybrid signals
- Citizen-friendly explanation
- Police-oriented investigation summary
- Short explanation for why the police triage priority was assigned
- Recommended action guidance
- SQLite case storage
- Police dashboard with category, risk level, platform, top risk factor, text-only, URL-based, and high-priority analytics
- Transaction dashboard analytics with risk level distribution, suspicious transaction categories, high-risk transaction count, priority queue, and total monitored synthetic amount
- Case details page with PDF export
- Awareness and safety tips page
- Mock role-based access for Citizen, Police Officer, and Admin/SP demos
- Role-based citizen and police login/registration with simulated police verification
- Homepage role access cards, judge demo credentials, one-click demo login, and current account overview
- Guided citizen incident reporting with step progress, category icons, Prakasam mandal selector, evidence metadata, tracking ID, risk triage, and 1930 guidance
- Police case management with assignment, required case statuses, evidence metadata review, timeline, officer notes, recommended action, and FIR-style summary aid
- Phishing scanner for URL/email checks with trusted-domain false-positive safeguards
- Phishing scanner, screenshot analyzer, and transaction monitor can save high-risk findings into the police triage report workflow
- Optional multi-provider AI layer for explanation refinement with local fallback
- Improved phishing detector for lookalike domains, fake login pages, KYC, result/certificate links, courier links, government notices, UPI refunds, QR scams, digital arrest, and credential harvesting
- Synthetic hotspot map for Prakasam cybercrime heat visualization with filters, area charts, rising locations, and high-risk alerts
- Cyber Dost Prakasam rule-based safety chatbot with quick actions, safer emergency guidance, scam checking, and Telugu/Hinglish-style prevention reminders
- Multilingual citizen UI support for English, Telugu, Hindi, Bengali, Tamil, Kannada, Malayalam, and Marathi
- Telugu-first accessibility on homepage, login, citizen reporting, awareness hub, and CyberDost quick guidance
- Awareness quiz with local result storage
- 300 clearly fake synthetic examples for tests, seeding, dashboard analytics, and presentations

## Five Core Modules

1. **Citizen Reporting**: guided complaint workflow with tracking ID, evidence metadata, automated classification, risk score, and police triage priority.
2. **URL/UPI/Screenshot Scam Validator**: checks suspicious URLs, UPI placeholders, SMS, WhatsApp, email content, and screenshot-visible text with trusted-domain safeguards.
3. **Transaction Anomaly Detection**: scores fictional payment behavior for refund scams, QR traps, fake loan fees, prize fees, job registration fees, and repeated transfers.
4. **Cyber Threat Intelligence**: synthetic Prakasam/AP indicators, threat stream cards, linked clusters, hotspot heat, and future-integration notes.
5. **Police Investigation Dashboard**: priority complaints, status buckets, evidence metadata, officer notes, case timeline, FIR draft aid, and workload overview.

Connected demo workflow:

```text
Citizen report -> automated triage -> saved police case -> case management -> hotspot analytics -> threat intelligence context
```

Scanner and transaction results can also be saved into the same police triage workflow so the product feels connected rather than split into separate tools.

## Demo Login Credentials

This prototype uses mock local authentication for presentation only:

| Role | Email | Password |
|---|---|---|
| Citizen | `citizen@example.com` | `citizen123` |
| Police Officer | `officer@example.com` | `officer123` |
| Admin/SP | `admin@example.com` | `admin123` |

Police registration demo verification code:

```text
PRAKASAM-POLICE-DEMO
```

Authentication and police verification are simulated for the hackathon prototype. Do not enter real police ID, real government documents, or sensitive personal information. The verification document field accepts only a demo placeholder filename. Demo passwords are shown only in this README and the homepage judge demo card, not inside the logged-in account overview.

The homepage includes **Access CyberShield Police** role cards and a **Demo Accounts for Judges** card. Judges can use the one-click buttons to continue as Citizen, Police Officer, or Admin/SP after the backend is running.

Role routes:

- Account details: `http://localhost:5173/account`
- Citizen dashboard: `http://localhost:5173/citizen`
- Police dashboard: `http://localhost:5173/police`
- Admin/SP dashboard: `http://localhost:5173/admin`
- Verification pending page: `http://localhost:5173/verification-pending`
- Incident reporting: `http://localhost:5173/report-incident`
- Case management: `http://localhost:5173/case-management`
- Phishing scanner: `http://localhost:5173/phishing-scanner`
- Screenshot analyzer: `http://localhost:5173/screenshot-analyzer`
- Hotspots: `http://localhost:5173/hotspots`
- Cyber Threat Intelligence: `http://localhost:5173/threat-intel`
- Awareness quiz: `http://localhost:5173/awareness`
- Cyber Dost chatbot: `http://localhost:5173/chatbot`

## Tech Stack

- Frontend: React + Vite
- Backend: FastAPI
- Database: SQLite
- Charts: Recharts
- PDF export: Python ReportLab
- Icons: lucide-react

## Architecture

```text
cybershield-police/
  backend/
    app/
      main.py              FastAPI routes
      database.py          SQLite setup and queries
      scam_detector.py     Explainable scam detection engine
      transaction_detector.py  Explainable transaction risk engine
      services/
        ai_provider.py          Optional AI provider adapter with safe fallback
        screenshot_analyzer.py  Screenshot metadata/manual-text analysis
      data/
        synthetic_scam_dataset.json  300 fictional examples
        synthetic_phishing_dataset.json  620 fictional phishing examples
        synthetic_transaction_dataset.json  150 fictional transaction examples
        synthetic_threat_incidents.json  Prakasam/AP demo incidents
        synthetic_indicators.json        Masked/demo indicators
        synthetic_case_clusters.json     Linked synthetic clusters
      seed_data.py         Synthetic dataset loader
    requirements.txt
    run_backend.py
    seed_demo_data.py      Demo dataset loader
    seed_demo_data.bat
    reset_demo_data.bat
    start_backend.bat      Windows setup and run helper
  frontend/
    src/
      pages/               Landing, analyzer, dashboard, case, safety tips
      components/          Layout, tables, loading state, risk UI
      api.js               API client
      auth.js              Mock role auth helpers
      styles.css           Responsive police-tech UI
    package.json
    start_frontend.bat     Windows setup and run helper
  docs/
    architecture.md
    api.md
    scalability.md
    impact.md
    originality-and-licenses.md
    demo-flow.md
    problem-solution.md
    demo-script.md
```

## Setup Instructions

Prerequisites:

- Python 3.10+ or the Codex bundled Python runtime. If you deleted Python, use `start_backend.bat`; it will try the bundled runtime available on this machine.
- Node.js 18+ with npm

## Run Backend

Open the first terminal:

```powershell
cd C:\Users\anubr\Documents\Codex\2026-06-19\prompt-1-master-build-prompt-you\cybershield-police\backend
.\start_backend.bat
```

The script finds Python, creates `.venv`, installs dependencies, and starts FastAPI. It avoids the common Windows issue where `python` or `uvicorn` is not available on PATH.

Backend URL:

```text
http://localhost:8000
```

API docs:

```text
http://localhost:8000/docs
```

## Run Frontend

Open a second terminal:

```powershell
cd C:\Users\anubr\Documents\Codex\2026-06-19\prompt-1-master-build-prompt-you\cybershield-police\frontend
.\start_frontend.bat
```

The frontend script installs dependencies, builds the production bundle, and serves it with Vite Preview on port 5173. This is the recommended stable mode for hackathon judging and avoids development-server dependency optimizer issues on some Windows setups.

If you are already inside the `backend` folder, this also works:

```powershell
.\start_frontend.bat
```

## Stop And Restart

From the `backend` folder:

```powershell
.\stop_backend.bat
.\stop_frontend.bat
.\start_backend.bat
.\start_frontend.bat
```

Frontend URL:

```text
http://localhost:5173
```

## Hybrid Detector

The detector is offline and explainable. It does not call paid APIs or external AI services.

It combines:

- Text rules for OTP/PIN/CVV/password requests, KYC threats, UPI refunds, fake jobs, loans, prizes, investments, courier scripts, fake customer care, police/legal threats, QR scams, urgency, secrecy, emotional manipulation, payment manipulation, and suspicious grammar.
- URL rules for shorteners, unknown domains, suspicious TLDs, lookalike domains, fake login/payment/verification words, fake result/certificate links, government impersonation, and credential-harvesting patterns.
- Metadata rules for platform, target group, and amount involved.

Each analysis returns the risk score, risk level, detected category, confidence, police triage priority, matched patterns, risk factors, citizen explanation, police summary, citizen action, police action, and signal mode.

False-positive prevention:

- Inputs with risk score `0-25` and no critical scam factor are corrected to `Likely Safe`.
- Trusted domains such as `cisce.org`, `results.cisce.org`, `digilocker.gov.in`, `umang.gov.in`, and `gov.in` domains are not flagged only because words like result, login, exam, certificate, student, verify, or official appear.
- Trusted domains are still flagged if the message asks for OTP, PIN, password, CVV, money, QR payment, urgent private details, or account takeover actions.

## Optional AI Provider Layer

The backend includes an optional AI adapter in `backend/app/services/ai_provider.py`.

Provider priority when `AI_PROVIDER=multi`:

1. Gemini through `GEMINI_API_KEY`
2. OpenRouter through `OPENROUTER_API_KEY`
3. Groq through `GROQ_API_KEY`
4. Hugging Face through `HUGGINGFACE_API_KEY`
5. Local fallback mode

AI is optional and disabled unless backend environment variables are configured. If a provider is missing, fails, times out, or returns an unsafe/empty response, `AI_PROVIDER=multi` tries the next configured provider before falling back to local deterministic text. API keys are never exposed to the frontend.

AI may only refine:

- citizen-friendly explanations
- police summaries
- CyberDost wording
- phishing explanation text
- screenshot visible-text interpretation

Final category and risk score always come from local deterministic scoring.

Check provider status:

```text
http://localhost:8000/ai/status
```

PowerShell optional AI verification:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/ai/test -Method POST -ContentType "application/json" -Body '{"prompt":"Say the active AI provider is working in one sentence."}'
```

CyberDost must return the actual provider in `provider_used` and `ai_enhanced: true` when any configured provider succeeds:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/chatbot/message -Method POST -ContentType "application/json" -Body '{"message":"FAKE DEMO: KYC blocked. Should I share OTP?","language":"en","use_optional_ai":true}'
```

PowerShell multiline form:

```powershell
Invoke-RestMethod `
  -Uri "http://localhost:8000/chatbot/message" `
  -Method POST `
  -Headers @{ "Content-Type" = "application/json" } `
  -Body '{"message":"My friend asked me to send ₹5000 immediately. What shall I do?","language":"en"}'
```

Phishing Detector must also return the actual `provider_used` and `ai_enhanced: true` while keeping the local risk score/category authoritative:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/phishing/scan -Method POST -ContentType "application/json" -Body '{"url":"https://urgent-kyc-bank.demo.test/login","email_content":"FAKE DEMO: enter OTP and password to avoid account block","use_optional_ai":true}'
```

Environment files:

- `.env.example`
- `backend/.env.example`
- `frontend/.env.example`

Optional backend environment variables:

```text
AI_PROVIDER=multi
AI_PROVIDER_ORDER=gemini,openrouter,groq,huggingface
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash
OPENROUTER_API_KEY=
OPENROUTER_MODEL=mistralai/mistral-7b-instruct:free
GROQ_API_KEY=
GROQ_MODEL=llama-3.1-8b-instant
HUGGINGFACE_API_KEY=
HUGGINGFACE_MODEL=mistralai/Mistral-7B-Instruct-v0.3
```

## Screenshot Scam Analyzer

The Screenshot Scam Analyzer accepts PNG, JPG, JPEG, or WEBP files in the browser, but the prototype sends only metadata to the backend:

- filename
- size
- file type
- upload time

It does not store image bytes, perform face recognition, identify people, or make legal conclusions. If OCR is not available, users paste visible screenshot text manually. That text is sent to the existing scam detector. Optional AI explanation is used only when an AI key is configured and the user explicitly enables the checkbox.

## Demo Data

The project includes safe synthetic datasets and seeded role/case-management records:

- `backend/app/data/synthetic_scam_dataset.json` with 300 fictional scam-message/link examples: 20 examples for each scam category and 20 likely-safe examples.
- `backend/app/data/synthetic_phishing_dataset.json` with 620 fictional phishing/safe examples for detector validation and backend reference. It is cached by the backend and is not loaded into the frontend.
- `backend/app/data/synthetic_transaction_dataset.json` with 150 fictional transaction examples: 30 safe transactions and 20 examples each for UPI refund scams, fake loan processing fees, lottery/prize fees, fake job registration fees, fake customer-care refund patterns, and QR code scams.
- `backend/app/data/synthetic_threat_incidents.json` with fictional Prakasam/AP cyber incident intelligence.
- `backend/app/data/synthetic_indicators.json` with masked/demo-only indicators such as `98XXXXXX21`, `fraudster-demo@upi`, `ACCT-DEMO-4821`, `suspicious-demo-login.example`, and `203.0.113.24`.
- `backend/app/data/synthetic_case_clusters.json` with linked synthetic complaint clusters.
- Demo users and 12 citizen incident reports for the role-based workflow.

They use fake text, fake amounts, placeholders, and reserved `.test` / `.invalid` demo domains when URLs are present. No real phone numbers, real names, real emails, real UPI IDs, real account numbers, or real links are included.

Load missing demo cases and transactions without deleting existing reports:

```powershell
cd C:\Users\anubr\Documents\Codex\2026-06-19\prompt-1-master-build-prompt-you\cybershield-police\backend
.\.venv\Scripts\python.exe seed_demo_data.py
```

If Python is installed globally, this also works:

```powershell
cd C:\Users\anubr\Documents\Codex\2026-06-19\prompt-1-master-build-prompt-you\cybershield-police\backend
python seed_demo_data.py
```

Reset the database to the clean demo dataset:

```powershell
cd C:\Users\anubr\Documents\Codex\2026-06-19\prompt-1-master-build-prompt-you\cybershield-police\backend
.\.venv\Scripts\python.exe seed_demo_data.py --reset
```

The reset command deletes all existing cases, transaction reports, threat incidents, indicators, and clusters in the local SQLite database, then reloads the synthetic demo datasets. Use it before a hackathon demo when you want clean dashboard charts.

## Role-Based Demo Flow

1. Open `http://localhost:5173`.
2. On the homepage, show **Access CyberShield Police** role cards for Citizen, Police Officer, and Admin/SP.
3. Use **Demo Accounts for Judges** and click **Try Citizen Demo**.
4. Return to the homepage to show **Account Overview**, then open the Citizen dashboard.
5. Logout from the homepage or navbar dropdown.
6. Click **Try Police Demo**, open **Case Management**, assign a report, update status, review evidence metadata, add an officer note, and show the FIR-style summary aid.
7. Logout, then click **Try Admin/SP Demo** to show command analytics plus **Police Account Verification Requests**.
8. Open **Dashboard**, **Hotspots**, and **Cyber Threat Intelligence** to show analytics, linked patterns, and synthetic location heat.
9. To test registration, use the homepage **Register Citizen** or **Register Police** buttons. Police registration code `PRAKASAM-POLICE-DEMO` gives instant demo verification; omitting it shows **Verification Pending**.

Role-based dashboard mapping:

- Citizen -> Citizen Dashboard
- Police Officer -> Police Dashboard
- Admin/SP -> Admin Dashboard

## Judge Testing Guide

Recommended 2-minute judge flow:

1. Start at the homepage and explain the one-line pitch: **AI-powered cybercrime triage for safer digital communities.**
2. Show the five-module overview and privacy-safe synthetic data note.
3. Click **Try Citizen Demo**, open **Report Incident**, load the demo complaint, move through the guided steps, and submit.
4. Show the generated tracking ID, risk score, triage priority, citizen guidance, and 1930 warning.
5. Logout and click **Try Police Demo**.
6. Open **Police Dashboard** to show new/under-review/verified/escalated counts, urgent summaries, location intelligence, and high-priority queue.
7. Open the submitted report in **Case Management**, review evidence metadata, update status, add a note, and show the FIR draft aid.
8. Open **Hotspots** and **Cyber Threat Intelligence** to show how cases connect to district-level trends.

Backend routes added for this role flow:

- `POST /auth/login`
- `POST /auth/register/citizen`
- `POST /auth/register/police`
- `GET /auth/me`
- `POST /auth/logout`
- `GET /admin/police-verification-requests`
- `POST /admin/police-verification/{id}/approve`
- `POST /admin/police-verification/{id}/reject`
- `POST /reports`
- `GET /reports`
- `GET /reports/{id}`
- `POST /reports/{id}/assign`
- `POST /reports/{id}/status`
- `POST /reports/{id}/notes`
- `GET /ai/status`
- `POST /phishing/scan`
- `POST /screenshots/analyze`
- `GET /hotspots`
- `GET /threat-intel`
- `GET /admin/analytics`
- `POST /chatbot/message`
- `GET /awareness/quiz`
- `POST /awareness/quiz/submit`

## Cyber Threat Intelligence

The CTI module is a decision-support prototype. It does not identify real suspects, expose personal data, scrape private groups, scan social media, or connect to real police databases.

Pages:

- **Threat Dashboard**: Prakasam/AP incident heat, scam trends, payment-mode filters, and charts.
- **Hotspots**: filter synthetic location intelligence by scam type, risk level, time range, payment mode, and amount range; view top affected locations, rising areas, incidents over time, and high-risk alerts.
- **Indicator Lookup**: search demo indicators and view risk score, linked categories, locations, related indicators, and triage priority.
- **Case Pattern Analyzer**: view synthetic clusters that share receiver placeholders, fake UPI IDs, domains, scripts, and target groups.

## CyberDost Chatbot

Cyber Dost Prakasam is an offline cyber safety assistant prototype. It can check suspicious text or pasted URLs using the scam detector, show risk score/category/triage priority, and explain OTP fraud, UPI fraud, phishing links, fake KYC, fake customer care, fake jobs, fake loans, fake investment scams, QR scams, and digital arrest scams. It gives short practical guidance, multilingual quick action prompts, a reset button, report/scan/transaction shortcuts, and 1930 emergency reporting guidance.

The chatbot keeps only current-session context in the browser: last scam type, whether the user said money was paid, whether OTP/PIN/password was shared, whether the user wants to report, and selected language. It does not store long-term chat history.

Safety guardrails: CyberDost does not ask for real OTP, PIN, passwords, CVV, bank account details, or private evidence. It refuses hacking, tracking, doxxing, retaliation, malware, phishing-kit, or credential-theft requests. It is a prototype assistant, not official police advice.

## Multilingual Support

CyberShield Police includes a lightweight local translation system in `frontend/src/i18n/translations.js`. The language selector appears in the homepage navbar, login page, citizen dashboard, citizen report flow, awareness hub, and CyberDost chatbot. The selected language is stored in `localStorage`, so switching language does not require a page reload.

Supported demo languages:

- English
- Telugu
- Hindi
- Bengali
- Tamil
- Kannada
- Malayalam
- Marathi

English and Telugu have the richest UI, awareness, and CyberDost response templates. Hindi and Bengali include extra scam-intent support for common citizen phrases. Tamil, Kannada, Malayalam, and Marathi cover key navigation, safety tips, buttons, and chatbot quick responses. The backend still returns investigation summaries in English for police consistency, while frontend headings and citizen-facing labels use the selected language where available. Missing keys safely fall back to English.

The scam detector also includes simple rule-based keyword support for common scam terms in English, Telugu, Hindi, and Bengali, including OTP, PIN, password, KYC, account blocked, loan, prize, refund, police, arrest, payment, UPI, QR code, job, investment, customer care, and digital arrest patterns. No paid translation API or mandatory external AI service is used.

Future integrations could include CERT-In alerts, 1930 complaint data, verified police databases, VirusTotal/AbuseIPDB with legal API keys, and approved public threat feeds.

## Documentation

- `docs/architecture.md` - frontend/backend architecture, services, data flow, and AI fallback.
- `docs/api.md` - important API endpoints.
- `docs/scalability.md` - SQLite to PostgreSQL, service separation, rate limiting, background jobs, privacy, and deployment plan.
- `docs/impact.md` - practical citizen and police impact with synthetic metrics.
- `docs/originality-and-licenses.md` - originality, synthetic data, dependency, asset, and license audit.
- `docs/demo-flow.md` - 3-minute judge demo flow.

## Test The Analyzer

1. Start the backend and frontend.
2. Open `http://127.0.0.1:5173`.
3. Go to **Scam Analyzer**.
4. Paste this fictional scam sample:

```text
FAKE DEMO TEST: Bank KYC expires today. Share OTP 000111 and verify PAN at https://kyc-bank-update.demo.test/login or account will be blocked.
```

5. Click **Analyze**.
6. Confirm that the result shows a high or critical risk score, confidence score, multiple detected categories, triggered rules, citizen action, and police action.
7. Open **Dashboard** to confirm category and platform charts are populated after seeding.

## Test Transaction Monitoring

1. Start the backend and frontend.
2. Open `http://127.0.0.1:5173`.
3. Go to **Transactions**.
4. Click **Load Demo** or paste this fictional transaction note:

```text
FAKE DEMO: scan QR and enter UPI PIN to receive urgent refund now. Approve request immediately.
```

5. Set payment method to `UPI`, amount to `2499`, first-time receiver to `Yes`, user age group to `Senior Citizen`, previous transaction count to `6`, and reported by user to `Yes`.
6. Click **Analyze Transaction**.
7. Confirm that the result shows risk score, suspected fraud type, triggered transaction risk factors, police triage priority, citizen explanation, police summary, and recommended action.
8. Open **Dashboard** to confirm transaction risk charts and high-priority transaction tables are populated.

Text-only examples to try:

```text
FAKE DEMO TEST: Demo Bank officer asks for OTP 000111 immediately to stop account block.
```

```text
FAKE DEMO TEST: Work from home rating job gives daily income after prepaid task deposit.
```

```text
FAKE DEMO TEST: Cyber cell officer says case file opened and security deposit must be transferred today.
```

## Run Tests

The detector tests load all 300 synthetic examples, run the analyzer, check category and score quality, verify safe examples score low, and print a demo accuracy summary.

```powershell
cd C:\Users\anubr\Documents\Codex\2026-06-19\prompt-1-master-build-prompt-you\cybershield-police\backend
.\.venv\Scripts\python.exe -m unittest app.tests.test_scam_detector app.tests.test_product_polish -v
```

To include the authentication and police verification tests:

```powershell
cd C:\Users\anubr\Documents\Codex\2026-06-19\prompt-1-master-build-prompt-you\cybershield-police\backend
.\.venv\Scripts\python.exe -m unittest app.tests.test_auth_flow app.tests.test_product_polish app.tests.test_scam_detector -v
```

## API Endpoints

- `POST /analyze`
- `POST /auth/login`
- `POST /auth/register/citizen`
- `POST /auth/register/police`
- `GET /auth/me`
- `POST /auth/logout`
- `GET /admin/police-verification-requests`
- `POST /admin/police-verification/{id}/approve`
- `POST /admin/police-verification/{id}/reject`
- `GET /cases`
- `GET /cases/{id}`
- `GET /analytics`
- `GET /export/{id}`
- `DELETE /cases/{id}`
- `POST /transactions/analyze`
- `GET /transactions`
- `GET /transactions/{id}`
- `GET /transactions/analytics`
- `GET /threat-intel/dashboard`
- `GET /threat-intel/incidents`
- `GET /threat-intel/indicators/search?query=`
- `GET /threat-intel/clusters`
- `GET /threat-intel/clusters/{id}`
- `GET /ai/status`
- `POST /phishing/scan`
- `POST /screenshots/analyze`
- `GET /hotspots`
- `POST /chatbot/message`
- `GET /awareness/quiz`
- `POST /awareness/quiz/submit`

## Screenshots

Add screenshots here after running the app:

- Landing Page
- Scam Analyzer
- Police Dashboard
- Case Details
- Awareness & Safety Tips

## Demo Video

Add a 2-3 minute walkthrough link here after recording:

```text
Demo video URL: <PASTE_DEMO_VIDEO_LINK_HERE>
```

## Judge Pitch Deck And Demo Materials

Open the final PowerPoint deck:

```text
presentation/CyberShield_Police_Hackathon_Pitch.pptx
```

Supporting presentation files:

- `presentation/demo-video-script.md`
- `presentation/judge-speech.md`
- `presentation/judge-qna.md`
- `docs/presentation-and-demo-kit.md`

These files are included so judges can quickly review the project story, demo flow, speeches, and Q&A.

## Deployment Notes

For split deployment, use Render for the backend and Vercel for the frontend. See:

```text
docs/deployment.md
```

Key deployment environment variables:

```text
GEMINI_API_KEY=your_gemini_key_here
GEMINI_MODEL=gemini-2.5-flash
AI_PROVIDER=multi
AI_PROVIDER_ORDER=gemini,openrouter,groq,huggingface
AI_TIMEOUT_SECONDS=20
OPENROUTER_API_KEY=your_openrouter_key_here
OPENROUTER_MODEL=mistralai/mistral-7b-instruct:free
GROQ_API_KEY=your_groq_key_here
GROQ_MODEL=llama-3.1-8b-instant
HUGGINGFACE_API_KEY=your_huggingface_key_here
HUGGINGFACE_MODEL=mistralai/Mistral-7B-Instruct-v0.3
DEMO_MODE=true
DATABASE_URL=sqlite:///./cybershield_demo.db
VITE_API_BASE_URL=https://YOUR-BACKEND-URL
CORS_ORIGINS=https://YOUR-FRONTEND-URL
URL_CHECK_PROVIDER=local_only
GOOGLE_SAFE_BROWSING_API_KEY=your_google_safe_browsing_key_here
URLHAUS_AUTH_KEY=your_urlhaus_auth_key_here
```

The app works without `GEMINI_API_KEY`; it will show Local Safety Mode.
The phishing scanner also works without any URL reputation API. For stronger URL checking, set `URL_CHECK_PROVIDER=multi` and legally configure `GOOGLE_SAFE_BROWSING_API_KEY` and/or `URLHAUS_AUTH_KEY`. A provider threat match raises the scan to high-priority phishing, but a provider `no_match` is never treated as proof that a URL is safe; local URL heuristics remain authoritative.

## GitHub Submission Commands

Replace `<MY_GITHUB_REPO_URL>` with the HTTPS URL of your empty GitHub repository, for example:

```text
https://github.com/your-username/cybershield-police.git
```

Then run:

```powershell
git init
git status
git add .
git commit -m "Final hackathon submission: CyberShield Police"
git branch -M main
git remote add origin <MY_GITHUB_REPO_URL>
git push -u origin main
```

Before pushing, confirm `.env`, `*.db`, `.venv`, `node_modules`, and `dist` are not staged.

## Future Scope

- Add native-speaker reviewed translations and richer voice/audio accessibility.
- Add production-grade local OCR for screenshot-based scam reports.
- Add domain age and reputation checks using approved public sources.
- Add phone number and UPI handle pattern extraction.
- Add duplicate campaign clustering for repeated scam templates.
- Add optional offline TF-IDF classifier trained only on the synthetic dataset.
- Add officer login, role-based access, and audit logs.
- Add offline awareness handout generation.

## Privacy and Ethical AI Note

This prototype does not use real personal data, real victim evidence, real police identity documents, real bank data, real UPI IDs, real account numbers, real suspect data, scraped social media, private social media scraping, or mandatory paid AI APIs. It stores only locally submitted demo reports and fictional intelligence records in SQLite. External AI providers are optional and disabled unless configured on the backend. Login/registration and police verification are simulated only. Automated scoring is decision support only and should never be treated as a final legal conclusion.

All datasets are synthetic for demonstration. No real victim data is used. No private social media scraping is performed. No official police logo is used unless provided by organizers.

## Team

- Team Lead / Developer: Anubrata Sarker
- Member 2: Arkaprabha De
- Member 3: Abhirup Goutam
