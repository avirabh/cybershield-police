# Demo Script

Use this script for a 3 to 5 minute hackathon presentation.

## 1. Opening

"CyberShield Police is a local cybercrime triage dashboard for Mission Y4 Prakasam Police Hackathon 2026. It detects cyber fraud even when there is no link, including plain SMS, WhatsApp, email, Telegram, and call-note scams such as OTP fraud, fake KYC, UPI refunds, fake jobs, loans, prize scams, investments, courier scams, QR scams, impersonation, and fake legal threats."

## 2. Landing Page

Show the landing page.

Mention:

- Runs locally
- Uses a 300-example synthetic demo dataset
- No paid APIs
- No real personal data
- Designed for citizen awareness and police triage

## 3. Scam Analyzer

Open the Scam Analyzer page.

Click **Load Demo** or paste this fictional scam sample:

```text
FAKE DEMO: Your bank KYC expires today. Verify PAN and Aadhaar now or account will be blocked. Login at kyc-bank-update.demo.test
```

Use URL:

```text
https://kyc-bank-update.demo.test/login
```

Click **Analyze**.

Show:

- Risk score
- Risk level
- Police triage priority and explanation
- Scam category
- Detection mode and signal sources
- Matched patterns
- Triggered risk factors
- Citizen explanation
- Police summary
- Recommended citizen and police actions

## 4. Police Dashboard

Open the Police Dashboard.

Show:

- Total reports
- High-risk reports
- Critical reports
- Category distribution chart
- Risk level distribution chart
- Top risk factors chart
- Text-only and URL-based scam counts
- High-priority cases
- Platform distribution chart
- Critical alerts
- Recent cases table with police triage priority

## 5. Case Details

Open a recent case.

Show:

- Message and URL
- Metadata
- Risk meter
- Police triage priority
- Investigation summary
- Risk factors
- PDF export button

## 6. Awareness Page

Open Awareness & Safety Tips.

Highlight:

- Never share OTP, PIN, CVV, or passwords
- Verify KYC alerts from official channels
- Do not scan QR codes to receive money
- Avoid advance fees for jobs, loans, or prizes

## 7. Closing

"The prototype is intentionally explainable and realistic for a solo developer build. Future versions can add multilingual support, OCR, domain reputation checks, duplicate scam campaign clustering, officer login, and official workflow integrations."
