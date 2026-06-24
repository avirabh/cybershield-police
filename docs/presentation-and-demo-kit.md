# CyberShield Police Presentation and Demo Kit

Hackathon: Prakasam Police Hackathon 2026 - Mission Y4  
Challenge: Challenge 05 - Cybercrime Detection & Digital Fraud  
Tagline: AI-powered cybercrime triage for safer digital communities.

## 12-Slide PPT Structure

### 1. Title Slide

Bullets:
- CyberShield Police
- AI-powered cybercrime triage for safer digital communities
- Prakasam Police Hackathon 2026 - Mission Y4
- Challenge 05: Cybercrime Detection & Digital Fraud

Speaker Notes:
CyberShield Police is a practical cybercrime triage platform for citizens and police. It helps detect scam messages, suspicious URLs, transaction fraud patterns, and threat hotspots using explainable risk scoring and safe optional AI support.

Suggested Visual:
Dark blue command-center background, shield/radar icon, product screenshot of homepage, subtle cyber grid.

### 2. Problem: Rising Cyber Fraud

Bullets:
- Fraud begins with small signals: SMS, WhatsApp, links, QR codes, calls
- Citizens often act before verifying
- Police receive scattered, incomplete reports
- Time-sensitive fraud needs quick triage

Speaker Notes:
Digital fraud is fast, emotional, and often happens before citizens realize they are being manipulated. The first few minutes matter, especially in OTP fraud, UPI fraud, fake KYC, fake customer care, and digital arrest scams.

Suggested Visual:
Fraud funnel diagram: message/call/link -> citizen action -> money loss -> police report.

### 3. Why Existing Systems Are Not Enough

Bullets:
- Reporting portals often start after damage is done
- Citizens need prevention guidance before payment or OTP sharing
- Manual case screening is slow
- Link-only detection misses text-only scams
- Local language awareness is limited

Speaker Notes:
CyberShield Police focuses on prevention plus triage. It does not wait for only formal case filing. It helps citizens understand risk early and gives police structured evidence, priority, category, and summaries.

Suggested Visual:
Before/after comparison: unstructured complaint vs structured CyberShield case.

### 4. Our Solution: CyberShield Police

Bullets:
- Unified citizen + police cyber safety platform
- Explainable risk score from 0 to 100
- Scam category, risk factors, and triage priority
- Gemini-enhanced explanations with Local Safety Mode fallback
- Synthetic-data-only ethical prototype

Speaker Notes:
Our solution combines local rule-based detection, optional AI explanation, case management, transaction monitoring, and threat intelligence into one working prototype. Local deterministic scoring remains authoritative.

Suggested Visual:
Central product map with citizen, AI detector, police dashboard, and hotspot intelligence.

### 5. Five Core Modules

Bullets:
- Citizen Reporting Interface
- URL/UPI Scam Validator
- Transaction Anomaly Detector
- Cyber Threat Intelligence Stream
- Police Investigative Dashboard

Speaker Notes:
These five modules match the challenge directly. A citizen can report suspicious activity, scan links or messages, test transaction patterns, receive CyberDost guidance, and police can triage and investigate from dashboards.

Suggested Visual:
Five module cards with icons: report, link, transaction, radar, dashboard.

### 6. System Architecture

Bullets:
- React + Vite frontend
- FastAPI backend
- SQLite local database
- Explainable detection engines
- Optional AI provider layer
- Synthetic datasets and seed script

Speaker Notes:
The architecture is intentionally simple and realistic for one developer and local police demo use. FastAPI handles analysis and storage, SQLite stores cases and synthetic data, and React provides role-based dashboards.

Suggested Visual:
Architecture diagram: React UI -> FastAPI APIs -> detector services -> SQLite -> dashboards/export.

### 7. AI Scam + Phishing + Screenshot Analysis

Bullets:
- Text-only, URL-only, metadata-only, and hybrid detection
- Phishing and lookalike domain rules
- Screenshot scam analyzer using safe metadata/manual visible text
- Matched patterns and triggered risk factors
- AI explanation does not override local score

Speaker Notes:
Many scams have no URL. The detector handles OTP, KYC, UPI refund, fake job, loan, lottery, investment, courier, QR, customer care, impersonation, and legal threat scripts. Screenshot analysis is privacy-preserving.

Suggested Visual:
Risk meter screenshot plus a side panel showing matched rules and explanation.

### 8. CyberDost + Multilingual Citizen Support

Bullets:
- CyberDost chatbot for practical safety guidance
- English, Telugu, Hindi, Bengali, Tamil, Kannada, Malayalam, Marathi
- Telugu-first citizen accessibility
- Quick actions: UPI fraud, digital arrest, phishing, 1930 guidance
- Local fallback when AI is unavailable

Speaker Notes:
CyberDost makes the product citizen-friendly. It gives calm, prevention-focused guidance and reminds users not to share OTP, PIN, password, CVV, UPI PIN, or pay urgent fees without verification.

Suggested Visual:
Chatbot screenshot with language selector and quick action chips.

### 9. Transaction Monitoring + Hotspot Intelligence

Bullets:
- Synthetic transaction risk monitoring
- Detects fake refund, loan fee, lottery fee, job registration, QR traps
- Hotspot analytics for Prakasam/AP demo data
- Risk distribution, category trends, high-priority queues
- Supports Admin/SP overview

Speaker Notes:
Challenge 05 includes transaction monitoring, so CyberShield Police includes a safe synthetic transaction analyzer and district-level hotspot intelligence for police decision support.

Suggested Visual:
Charts: transaction risk distribution, hotspot map, high-priority count.

### 10. Police Workflow

Bullets:
- Report -> Analyze -> Triage -> Investigate -> Warn Public
- Case details with evidence metadata
- Officer notes and status updates
- FIR-style summary aid
- Exportable report

Speaker Notes:
The police workflow is designed for repeated operational use. It converts scattered citizen inputs into structured cases with risk score, category, priority, recommended action, evidence metadata, and summary.

Suggested Visual:
Horizontal workflow diagram with screenshots of case management and report export.

### 11. Practical Impact, Scalability, Privacy & Ethics

Bullets:
- Prevents fraud before citizens act
- Helps police prioritize urgent cases
- Works locally without paid APIs
- No real victim or police data
- Scalable to production databases, OCR, and official integrations

Speaker Notes:
The prototype is safe by design. It uses synthetic data, no real private screenshots, no official logos, and no mandatory external APIs. Future deployment can integrate official cybercrime workflows, secure evidence storage, and audited AI.

Suggested Visual:
Impact triangle: Citizens protected, police efficiency, ethical AI.

### 12. Future Scope + Team

Bullets:
- Official 1930/cybercrime portal integration
- OCR-based screenshot analysis with consent
- Case clustering across districts
- Officer audit logs and secure evidence workflow
- Team Lead / Developer: Anubrata Sarker

Speaker Notes:
CyberShield Police is built as a strong prototype but with a clear path to production: stronger integrations, real deployment governance, native speaker review for translations, and police-approved workflows.

Suggested Visual:
Roadmap timeline and team card.

## 2-3 Minute Demo Video Script

Opening, 0:00-0:15:
This is CyberShield Police, an AI-powered cybercrime triage platform for Challenge 05: Cybercrime Detection and Digital Fraud. It helps citizens detect scams early and helps police prioritize cybercrime reports.

Homepage, 0:15-0:30:
Show the homepage, role cards, and demo accounts. Point out Citizen, Police Officer, and Admin/SP access. Mention that all data is synthetic and no real victim data is used.

Citizen Login, 0:30-0:45:
Click Continue as Citizen. Open the citizen dashboard and report form.

Citizen Report, 0:45-1:05:
Paste a suspicious message such as: "FAKE DEMO: Your bank KYC is blocked. Enter OTP and UPI PIN to reactivate." Submit the report. Show tracking ID, risk score, category, and police triage priority.

Phishing Scanner, 1:05-1:25:
Open phishing scanner. Scan `secure-sbi-kyc-login.xyz` with KYC text. Show Critical/Phishing result, triggered risk factors, local explanation, and optional AI enhanced explanation if available.

Transaction Monitor, 1:25-1:45:
Open Transaction Monitor. Analyze a fake loan processing fee or QR refund transaction. Show risk score, suspected fraud type, and recommended action.

CyberDost, 1:45-2:00:
Open CyberDost. Ask: "My friend asked me to send Rs. 5000 immediately. What should I do?" Show calm guidance, 1930 reminder, and AI/Local status.

Police Dashboard, 2:00-2:30:
Switch to Police demo. Show dashboard analytics, high-priority cases, category distribution, and recent cases. Open case details and show evidence metadata, summary, and export/report flow.

Admin/SP Intelligence, 2:30-2:50:
Open hotspot or threat intelligence dashboard. Show synthetic Prakasam/AP hotspots, threat stream, and pattern intelligence.

Closing, 2:50-3:00:
CyberShield Police is prevention-focused, explainable, multilingual, privacy-safe, and ready for local police hackathon demonstration.

## 90-Second Judge Presentation Speech

Good morning respected judges and police officials. Our project is CyberShield Police, built for Mission Y4 Prakasam Police Hackathon 2026, Challenge 05: Cybercrime Detection and Digital Fraud.

Cyber fraud often starts with a small message: fake KYC alerts, OTP requests, UPI refund traps, fake jobs, loan fees, phishing links, QR codes, or digital arrest threats. Citizens need guidance before they click, pay, or share OTP. Police teams need structured, prioritized reports instead of scattered screenshots and incomplete complaints.

CyberShield Police solves this with five connected modules: citizen reporting, URL/UPI scam validation, transaction anomaly detection, cyber threat intelligence, and a police investigative dashboard.

The system generates an explainable risk score from 0 to 100, detects scam categories, shows triggered risk factors, gives citizen-friendly advice, and creates police-oriented summaries with triage priority. It also includes CyberDost, a multilingual safety chatbot, and supports English, Telugu, Hindi, Bengali, Tamil, Kannada, Malayalam, and Marathi.

AI is used responsibly. Gemini or other configured AI providers can improve explanations, but the local deterministic detector remains the source of truth. If AI is unavailable, Local Safety Mode continues working.

The prototype uses only synthetic demo data. No real victim data, police records, UPI IDs, phone numbers, or private screenshots are included.

Our goal is simple: prevent fraud earlier, help citizens act safely, and help police prioritize faster.

## 3-Minute Judge Presentation Speech

Good morning respected judges and police officials. I am presenting CyberShield Police, an AI-powered cybercrime triage platform for Prakasam Police Hackathon 2026, Mission Y4, Challenge 05: Cybercrime Detection and Digital Fraud.

The core problem is that cyber fraud does not always begin with a clear crime report. It often starts with a single SMS, WhatsApp message, fake customer care call, phishing link, QR code, job fee request, loan processing fee, or digital arrest threat. Citizens are pressured to act quickly, and by the time they formally report, money or credentials may already be lost.

Existing systems are important, but many workflows begin after the incident. CyberShield Police focuses on early prevention plus structured police triage.

The platform has five core modules. First, a Citizen Reporting Interface where users can submit suspicious messages, URLs, transaction details, and evidence metadata. Second, a URL/UPI Scam Validator that checks phishing links, lookalike domains, UPI-style fraud, and suspicious text. Third, a Transaction Anomaly Detector for synthetic payment risk patterns like fake refund scams, loan fees, QR traps, and lottery processing fees. Fourth, a Cyber Threat Intelligence Stream with synthetic Prakasam/AP hotspot and indicator data. Fifth, a Police Investigative Dashboard for high-priority reports, category analytics, case details, summaries, and officer workflow.

The detection engine is explainable. It produces a risk score from 0 to 100, risk level, scam category, confidence, triggered rules, matched patterns, citizen explanation, police summary, and triage priority. It works for text-only scams, URL-only scans, metadata-only context, and hybrid inputs.

CyberShield Police also includes CyberDost, a citizen safety chatbot with multilingual support. Telugu and English are prioritized, with additional support for Hindi, Bengali, Tamil, Kannada, Malayalam, and Marathi. The chatbot gives practical guidance such as not sharing OTP, PIN, password, CVV, UPI PIN, not installing remote access apps, and reporting urgent fraud to 1930.

AI is optional and safe. Gemini or other configured AI providers can enhance wording, but the local rule-based detector remains authoritative. If keys are absent or AI fails, Local Safety Mode continues working.

Privacy and ethics are central. The project uses only fictional synthetic data. It contains no real victim data, no real police records, no real UPI IDs, no real phone numbers, no bank accounts, and no private screenshots.

This is a realistic prototype that can run locally, seed demo data, and show meaningful analytics. With production hardening, it can scale into official integrations, secure evidence workflows, OCR with consent, audit logs, and district-level cybercrime intelligence.

CyberShield Police helps citizens avoid fraud before harm, and helps police triage faster after a report. Thank you.

## Top 15 Judge Q&A

1. What problem does this solve?
It helps citizens detect suspicious cyber fraud early and helps police prioritize structured cybercrime reports with explainable risk scoring.

2. What makes it different from a normal reporting portal?
It provides prevention and triage before or during reporting: scam analysis, transaction monitoring, chatbot guidance, and police dashboards.

3. Does it require paid APIs?
No. The core system runs locally with FastAPI, React, SQLite, and deterministic rules. AI and URL reputation APIs are optional.

4. Is AI deciding the final risk score?
No. Local explainable scoring is authoritative. AI only improves explanation text when configured.

5. What happens if Gemini fails?
Local Safety Mode continues working. The app still analyzes scams, produces risk scores, and gives guidance.

6. Can it detect scams without URLs?
Yes. It includes text-only detection for OTP, KYC, UPI refund, fake job, fake loan, lottery, investment, courier, QR, customer care, impersonation, and legal threat scams.

7. How do police benefit?
Police get risk score, category, triage priority, evidence metadata, case details, dashboard analytics, hotspots, and summaries.

8. How do citizens benefit?
Citizens get immediate safety guidance, risk explanations, 1930 awareness, multilingual UI, and report tracking.

9. Is any real data used?
No. All cases, transactions, threat indicators, and datasets are fictional/synthetic.

10. Is it safe to publish on GitHub?
Yes. `.env`, SQLite databases, virtual environments, build output, and secrets are ignored. Only examples and placeholders are committed.

11. How does transaction monitoring work?
It uses explainable rules for amount, timing, first-time receiver, repeated payments, suspicious notes, and fraud patterns like fake refund, job fee, loan fee, and QR scams.

12. How does phishing detection avoid false positives?
Trusted domains like official government and CISCE domains are allowlisted, but still flagged if the message asks for OTP, password, money, QR payment, or private data.

13. How scalable is this?
The prototype can scale to PostgreSQL, role-based production auth, OCR queues, secure evidence storage, audit logs, official API integrations, and district-level analytics.

14. What is the ethical AI approach?
AI is optional, does not override scoring, avoids sensitive data, does not store private screenshots, and falls back safely.

15. What should judges remember?
CyberShield Police connects prevention, reporting, detection, transaction monitoring, chatbot guidance, and police investigation into one working, ethical prototype.

## Final Submission Checklist

- GitHub repo is public and accessible.
- README includes overview, setup, demo credentials, privacy note, and commands.
- Backend starts with `backend\start_backend.bat`.
- Frontend starts with `frontend\start_frontend.bat`.
- Demo data seeds with `python seed_demo_data.py`.
- Backend tests pass.
- Frontend build passes.
- `.env` is not committed.
- Demo credentials are marked as demo-only.
- No real victim/police/private data is included.
- Citizen demo login works.
- Police demo login works.
- Admin/SP demo login works.
- Citizen report flow works.
- Phishing scanner works.
- Transaction monitor works.
- CyberDost works in AI or Local Safety Mode.
- Police dashboard shows seeded analytics.
- Hotspot/threat intelligence pages load.
- Presentation deck and demo script are ready.
