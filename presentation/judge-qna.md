# CyberShield Police Judge Q&A

1. **What problem does this solve?**  
It helps citizens detect suspicious cyber fraud early and helps police prioritize structured reports with explainable risk scoring.

2. **How is this different from a normal reporting portal?**  
It supports prevention and triage before and during reporting: scam analysis, transaction monitoring, chatbot guidance, and police dashboards.

3. **Does it require paid APIs?**  
No. The core system runs locally with FastAPI, React, SQLite, and deterministic rules. AI and URL reputation APIs are optional.

4. **Is AI deciding the final risk score?**  
No. Local explainable scoring is authoritative. AI only improves explanation text when configured.

5. **What happens if Gemini fails?**  
Local Safety Mode continues working. The app still analyzes scams, produces risk scores, and gives guidance.

6. **Can it detect scams without URLs?**  
Yes. It detects text-only OTP, KYC, UPI refund, fake job, fake loan, lottery, investment, courier, QR, customer care, impersonation, and legal threat scams.

7. **How do police benefit?**  
Police get risk score, category, triage priority, evidence metadata, case summaries, dashboard analytics, and hotspot intelligence.

8. **How do citizens benefit?**  
Citizens get immediate safety guidance, scam explanations, 1930 awareness, multilingual UI, and report tracking.

9. **Is any real data used?**  
No. All cases, transactions, threat indicators, and datasets are fictional/synthetic.

10. **Is it safe to publish on GitHub?**  
Yes. `.env`, databases, virtual environments, build output, and secrets are ignored. Only placeholders and synthetic examples are committed.

11. **How does transaction monitoring work?**  
It uses explainable rules for amount, timing, first-time receivers, repeated payments, suspicious notes, and fraud patterns.

12. **How does phishing detection avoid false positives?**  
Trusted official domains are allowlisted, but still flagged if the message asks for OTP, password, money, QR payment, or private data.

13. **How scalable is this?**  
It can scale to PostgreSQL, production auth, secure evidence storage, audit logs, OCR queues, and official cybercrime integrations.

14. **What is the ethical AI approach?**  
AI is optional, does not override scoring, avoids sensitive data, and falls back safely.

15. **What should judges remember?**  
CyberShield Police connects prevention, reporting, detection, transaction monitoring, chatbot guidance, and police investigation into one working ethical prototype.
