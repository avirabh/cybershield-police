# Originality and License Audit

## Originality Statement

CyberShield Police is a custom hackathon prototype built around Challenge 05: Cybercrime Detection & Digital Fraud. The flows, synthetic datasets, rule-based detectors, transaction monitoring, CyberDost chatbot, screenshot analyzer, dashboards, and documentation are project-specific.

## Synthetic Data Statement

- All datasets are synthetic for demonstration.
- No real victim data is used.
- No real police records, badge documents, FIRs, private evidence, or suspect data are used.
- No real bank accounts, real UPI IDs, real phone numbers, real emails, or private social media data are used.
- No private social media scraping is performed.

## Assets and Logos

- No official police logo is used unless provided separately by organizers.
- UI icons come from the `lucide-react` package.
- The app uses CSS-generated visuals rather than copyrighted images or downloaded templates.

## Third-Party Dependencies

Backend:

- FastAPI
- Uvicorn
- ReportLab

Frontend:

- React
- Vite
- React Router
- Recharts
- Lucide React

These dependencies should be reviewed with their package licenses before public submission. No dependency API keys are bundled in the project.

## Optional AI Providers

Optional AI providers are disabled unless configured through backend environment variables. API keys are not exposed to the frontend. Local deterministic risk scoring remains authoritative even when optional AI explanation is enabled.

## Audit Result

Manual project review found no bundled copyrighted images, no official police/government logo assets, no real personal datasets, and no hardcoded API secrets.

## Limitations

This is an internal manual audit. It cannot guarantee plagiarism-free status without external plagiarism/license scanning tools. Before final public GitHub submission, run dependency license checks and review any newly added assets.
