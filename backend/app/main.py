from __future__ import annotations

from datetime import datetime, timedelta
from io import BytesIO
import re
import logging
import os
from typing import Any
from xml.sax.saxutils import escape

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.database import (
    add_incident_note,
    assign_incident_report,
    authenticate_user,
    create_case,
    create_citizen_user,
    create_incident_report,
    create_police_user,
    create_transaction,
    delete_case,
    get_case_cluster,
    get_case,
    get_incident_report,
    get_transaction,
    get_user_by_email,
    init_db,
    list_case_clusters,
    list_cases,
    list_incident_reports,
    list_police_verification_requests,
    list_threat_incidents,
    list_threat_indicators,
    list_transactions,
    save_quiz_result,
    search_threat_indicators,
    seed_demo_users,
    update_incident_status,
    update_police_verification,
)
from app.phishing_examples import phishing_dataset_summary
from app.scam_detector import analyze_scam, analyze_url_trust, risk_level
from app.seed_data import seed_demo_data
from app.services.ai_provider import generate_ai_text, get_ai_status
from app.services.screenshot_analyzer import analyze_screenshot
from app.services.url_reputation import check_url_reputation
from app.transaction_detector import analyze_transaction


app = FastAPI(
    title="CyberShield Police API",
    description="Rule-based cybercrime and digital fraud detection API for demo use.",
    version="1.0.0",
)

logger = logging.getLogger("cybershield.api")


def _ai_provider_slug(provider_used: str | None) -> str:
    value = (provider_used or "").strip().lower()
    mapping = {
        "gemini": "gemini",
        "openrouter": "openrouter",
        "groq": "groq",
        "hugging face": "huggingface",
        "huggingface": "huggingface",
    }
    return mapping.get(value, "local_fallback")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,http://0.0.0.0:5173",
        ).split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    message: str = Field(default="", max_length=5000)
    url: str = Field(default="", max_length=1000)
    platform: str = Field(default="", max_length=80)
    victim_age_group: str = Field(default="", max_length=80)
    amount_involved: float | None = Field(default=None, ge=0)


class TransactionAnalyzeRequest(BaseModel):
    transaction_id: str = Field(default="", max_length=120)
    amount: float = Field(default=0, ge=0)
    payment_method: str = Field(default="UPI", max_length=80)
    merchant_or_receiver_name: str = Field(default="", max_length=160)
    receiver_upi_or_account_placeholder: str = Field(default="", max_length=160)
    timestamp: str = Field(default="", max_length=80)
    location_or_city: str = Field(default="", max_length=120)
    transaction_note: str = Field(default="", max_length=1000)
    user_age_group: str = Field(default="", max_length=80)
    previous_transaction_count: int = Field(default=0, ge=0)
    is_first_time_receiver: bool = False
    reported_by_user: bool = False


class LoginRequest(BaseModel):
    email: str = Field(max_length=160)
    password: str = Field(max_length=120)


class CitizenRegisterRequest(BaseModel):
    name: str = Field(max_length=160)
    email: str = Field(max_length=160)
    password: str = Field(min_length=4, max_length=120)
    location: str = Field(default="", max_length=120)
    age_group: str = Field(default="", max_length=80)


class PoliceRegisterRequest(BaseModel):
    name: str = Field(max_length=160)
    email: str = Field(max_length=160)
    rank_designation: str = Field(default="", max_length=120)
    police_station: str = Field(default="", max_length=160)
    district: str = Field(default="Prakasam", max_length=120)
    badge_id_placeholder: str = Field(default="", max_length=120)
    verification_document_name: str = Field(default="", max_length=180)
    verification_code: str = Field(default="", max_length=120)
    password: str = Field(min_length=4, max_length=120)


class IncidentReportRequest(BaseModel):
    reporter_name: str = Field(default="", max_length=160)
    anonymous: bool = False
    age_group: str = Field(default="", max_length=80)
    contact_placeholder: str = Field(default="", max_length=120)
    location: str = Field(default="", max_length=120)
    category: str = Field(default="Other", max_length=120)
    description: str = Field(default="", max_length=3000)
    suspicious_message: str = Field(default="", max_length=5000)
    suspicious_url: str = Field(default="", max_length=1000)
    transaction_amount: float = Field(default=0, ge=0)
    payment_mode: str = Field(default="", max_length=80)
    receiver_placeholder: str = Field(default="", max_length=160)
    evidence_metadata: list[dict[str, Any]] = Field(default_factory=list)
    language_preference: str = Field(default="en", max_length=20)


class AssignRequest(BaseModel):
    officer_email: str = Field(max_length=160)


class StatusRequest(BaseModel):
    status: str = Field(max_length=80)
    evidence_reviewed: bool | None = None


class NoteRequest(BaseModel):
    officer_email: str = Field(default="officer@example.com", max_length=160)
    note: str = Field(max_length=2000)


class PhishingScanRequest(BaseModel):
    url: str = Field(default="", max_length=1000)
    email_content: str = Field(default="", max_length=5000)
    message: str = Field(default="", max_length=5000)
    use_optional_ai: bool = True


class ScreenshotAnalyzeRequest(BaseModel):
    filename: str = Field(default="screenshot-demo.png", max_length=180)
    file_type: str = Field(default="", max_length=80)
    file_size: int = Field(default=0, ge=0)
    upload_time: str = Field(default="", max_length=80)
    manual_text: str = Field(default="", max_length=5000)
    url: str = Field(default="", max_length=1000)
    use_optional_ai: bool = False


class AITestRequest(BaseModel):
    prompt: str = Field(default="Say AI is working in one sentence.", max_length=1000)


class ChatbotRequest(BaseModel):
    message: str = Field(max_length=5000)
    language: str = Field(default="en", max_length=20)
    context: dict[str, Any] = Field(default_factory=dict)
    use_optional_ai: bool = True


class QuizSubmitRequest(BaseModel):
    user_email: str = Field(default="", max_length=160)
    answers: dict[str, str] = Field(default_factory=dict)


QUIZ_QUESTIONS = [
    {
        "id": "otp",
        "question": "A caller asks for your OTP to cancel a fake transaction. What should you do?",
        "options": [
            "Share OTP only after asking their name",
            "Never share OTP and report the contact",
            "Share OTP if they claim to be from bank",
            "Send a screenshot of the OTP",
        ],
        "answer": "Never share OTP and report the contact",
    },
    {
        "id": "upi_collect",
        "question": "For receiving a refund through UPI, should you enter your PIN?",
        "options": [
            "Yes, every refund needs PIN",
            "Only if the merchant says urgent",
            "No, entering PIN sends money",
            "Only at night",
        ],
        "answer": "No, entering PIN sends money",
    },
    {
        "id": "digital_arrest",
        "question": "Someone claims you are under digital arrest and demands money. What is safest?",
        "options": [
            "Pay quietly",
            "Stay on the video call",
            "Disconnect, preserve evidence, contact police",
            "Share bank details to verify identity",
        ],
        "answer": "Disconnect, preserve evidence, contact police",
    },
    {
        "id": "job_fee",
        "question": "A job offer asks for a registration fee before an interview. What is the warning sign?",
        "options": [
            "Upfront fee demand",
            "Professional greeting",
            "Office timing",
            "Job title",
        ],
        "answer": "Upfront fee demand",
    },
    {
        "id": "trusted_domain",
        "question": "A message has an official website link but asks for OTP and payment. How should it be treated?",
        "options": [
            "Always safe because the link is official",
            "Suspicious because OTP/payment requests are risky",
            "Safe if it mentions exam results",
            "Ignore risk factors",
        ],
        "answer": "Suspicious because OTP/payment requests are risky",
    },
]


@app.on_event("startup")
def startup() -> None:
    init_db()
    seed_demo_users()
    seed_demo_data()


@app.get("/")
def root() -> dict[str, str]:
    return {"name": "CyberShield Police API", "status": "running"}


@app.get("/ai/status")
def ai_status() -> dict[str, Any]:
    return get_ai_status()


@app.post("/ai/test")
def ai_test(payload: AITestRequest) -> dict[str, Any]:
    return generate_ai_text(payload.prompt, purpose="debug_test")


@app.post("/auth/login")
def login(payload: LoginRequest) -> dict[str, Any]:
    user = authenticate_user(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid demo login credentials.")
    token = f"demo-token::{user['email']}::{user['role']}"
    return {
        "token": token,
        "user": user,
        "requires_verification": user["role"] == "Police Officer" and user.get("verification_status") != "Verified",
    }


@app.get("/auth/me")
def auth_me(email: str = "") -> dict[str, Any]:
    user = get_user_by_email(email or "citizen@example.com")
    if not user:
        raise HTTPException(status_code=404, detail="Demo user not found.")
    return user


@app.post("/auth/logout")
def logout() -> dict[str, bool]:
    return {"ok": True}


@app.post("/auth/register/citizen")
def register_citizen(payload: CitizenRegisterRequest) -> dict[str, Any]:
    try:
        user = create_citizen_user(payload.model_dump() if hasattr(payload, "model_dump") else payload.dict())
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {
        "token": f"demo-token::{user['email']}::{user['role']}",
        "user": user,
        "message": "Citizen demo account created.",
    }


@app.post("/auth/register/police")
def register_police(payload: PoliceRegisterRequest) -> dict[str, Any]:
    try:
        user = create_police_user(payload.model_dump() if hasattr(payload, "model_dump") else payload.dict())
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {
        "token": f"demo-token::{user['email']}::{user['role']}",
        "user": user,
        "requires_verification": user.get("verification_status") != "Verified",
        "message": (
            "Police demo account auto-verified."
            if user.get("verification_status") == "Verified"
            else "Police demo account submitted for Admin/SP verification."
        ),
    }


@app.get("/admin/police-verification-requests")
def police_verification_requests() -> list[dict[str, Any]]:
    return list_police_verification_requests()


@app.post("/admin/police-verification/{user_id}/approve")
def approve_police_account(user_id: int) -> dict[str, Any]:
    user = update_police_verification(user_id, "Verified", "Approved by Admin/SP in demo verification workflow.")
    if not user:
        raise HTTPException(status_code=404, detail="Police account not found.")
    return user


@app.post("/admin/police-verification/{user_id}/reject")
def reject_police_account(user_id: int) -> dict[str, Any]:
    user = update_police_verification(user_id, "Rejected", "Rejected by Admin/SP in demo verification workflow.")
    if not user:
        raise HTTPException(status_code=404, detail="Police account not found.")
    return user


@app.post("/analyze")
def analyze(payload: AnalyzeRequest) -> dict[str, Any]:
    metadata = {
        "platform": payload.platform,
        "victim_age_group": payload.victim_age_group,
        "amount_involved": payload.amount_involved,
    }
    analysis = analyze_scam(payload.message, payload.url, metadata)
    payload_data = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()
    return create_case(payload_data, analysis)


@app.post("/reports")
def submit_report(payload: IncidentReportRequest) -> dict[str, Any]:
    payload_data = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()
    text = "\n".join(
        value
        for value in [payload.description, payload.suspicious_message]
        if value
    )
    analysis = analyze_scam(
        text,
        payload.suspicious_url,
        {
            "platform": "Citizen Report",
            "victim_age_group": payload.age_group,
            "amount_involved": payload.transaction_amount,
        },
    )
    return create_incident_report(payload_data, analysis)


@app.get("/reports")
def reports() -> list[dict[str, Any]]:
    return list_incident_reports()


@app.get("/reports/{report_id}")
def report_details(report_id: int) -> dict[str, Any]:
    report = get_incident_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    return report


@app.post("/reports/{report_id}/assign")
def assign_report(report_id: int, payload: AssignRequest) -> dict[str, Any]:
    report = assign_incident_report(report_id, payload.officer_email)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    return report


@app.post("/reports/{report_id}/status")
def update_report_status(report_id: int, payload: StatusRequest) -> dict[str, Any]:
    report = update_incident_status(report_id, payload.status, payload.evidence_reviewed)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    return report


@app.post("/reports/{report_id}/notes")
def add_report_note(report_id: int, payload: NoteRequest) -> dict[str, Any]:
    report = add_incident_note(report_id, payload.officer_email, payload.note)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    return report


@app.post("/phishing/scan")
def phishing_scan(payload: PhishingScanRequest) -> dict[str, Any]:
    text = "\n".join(value for value in [payload.email_content, payload.message] if value)
    result = analyze_scam(text, payload.url, {"platform": "Phishing Scanner"})
    trust_check = analyze_url_trust(payload.url, result.get("risk_factors", []))
    reputation_check = check_url_reputation(payload.url)
    if reputation_check.get("threat_found"):
        reputation_factor = {
            "code": "external_reputation_threat_match",
            "label": "External URL reputation threat match",
            "weight": 42,
            "evidence": reputation_check.get("explanation") or "A configured URL reputation provider reported this URL.",
            "categories": ["Phishing"],
            "matched_patterns": [str(payload.url or "")],
            "source": "url_reputation",
        }
        result["risk_factors"] = [reputation_factor, *result.get("risk_factors", [])]
        result["triggered_rules"] = [reputation_factor, *result.get("triggered_rules", [])]
        result["matched_patterns"] = [reputation_factor, *result.get("matched_patterns", [])]
        result["risk_score"] = max(int(result.get("risk_score") or 0), 85)
        result["risk_level"] = risk_level(result["risk_score"])
        result["category"] = "Phishing"
        result["confidence_score"] = max(int(result.get("confidence_score") or 0), 88)
        result["citizen_explanation"] = (
            "This URL is treated as high risk because a configured external reputation provider reported a threat match. "
            "Do not open the link or enter OTP, PIN, password, CVV, UPI PIN, or private details."
        )
        result["police_summary"] = (
            f"External URL reputation provider reported a threat match for {payload.url}. "
            "Treat as high-priority phishing triage, preserve the URL, message text, timestamps, sender details, and any transaction context."
        )
        result["recommended_action"] = (
            "Do not open this URL. Preserve the message and report through official cybercrime or police channels if money or credentials were involved."
        )
    domain = trust_check.get("domain") or "No URL submitted"
    risk_factors = result.get("risk_factors", [])
    has_critical_factor = any(int(factor.get("weight") or 0) >= 35 for factor in risk_factors)
    category = "Likely Safe" if result["risk_score"] <= 25 and not has_critical_factor else result["category"]
    local_explanation = result["citizen_explanation"]
    local_police_summary = result["police_summary"]

    if payload.use_optional_ai:
        logger.info("Phishing Detector: attempting Gemini")
        ai = generate_ai_text(
            (
                "Write 3 short citizen-friendly sentences about this URL safety scan. "
                "Do not change the local score or category. "
                f"Score: {result['risk_score']}/100. Category: {category}. Level: {result['risk_level']}. "
                f"Trusted-domain status: {trust_check.get('status', 'No URL')}. "
                f"URL reputation status: {reputation_check.get('label')}. "
                f"Main local warning signs: {', '.join(factor.get('label', '') for factor in risk_factors[:4]) or 'none'}. "
                "Advise verifying through the official app or typed official website before entering private details."
            ),
            purpose="phishing_explanation",
        )
        if ai.get("success"):
            logger.info("Phishing Detector: Gemini success")
        else:
            logger.info("Phishing Detector: Gemini failed, using fallback")
    else:
        ai = {
            "success": False,
            "provider_used": "Local Fallback",
            "text": local_explanation,
            "error": "Optional AI disabled.",
        }

    ai_enhanced = bool(ai.get("success"))
    provider_used = ai.get("provider_used") or "Local Fallback"
    ai_explanation = ai["text"] if ai_enhanced else local_explanation
    logger.info("Phishing provider_used=%s", provider_used)
    return {
        "risk_score": result["risk_score"],
        "phishing_risk_score": result["risk_score"],
        "risk_level": result["risk_level"],
        "detected_type": category,
        "category": category,
        "confidence": result["confidence_score"],
        "trusted_domain_check": trust_check,
        "url_reputation": reputation_check,
        "domain_analysis": {
            "domain": domain,
            "trusted_domain_handling": "Trusted domains are allowed unless OTP, PIN, password, money, QR, or private-data requests appear.",
            "url_reputation_handling": "External URL reputation is optional. Local scoring remains authoritative when no URL-check API is configured.",
            "lookalike_warning": any(match.get("code", "").endswith("domain_mismatch") for match in result.get("matched_patterns", [])),
        },
        "suspicious_keyword_analysis": risk_factors,
        "triggered_risk_factors": risk_factors,
        "matched_suspicious_patterns": result.get("matched_patterns", []),
        "warnings": [factor["label"] for factor in risk_factors],
        "risk_factors": risk_factors,
        "local_explanation": local_explanation,
        "explanation": local_explanation,
        "citizen_explanation": local_explanation,
        "ai_explanation": ai_explanation,
        "ai_explanation_available": ai_enhanced,
        "ai_provider": _ai_provider_slug(provider_used) if ai_enhanced else "local_fallback",
        "ai_mode": "optional_ai" if ai_enhanced else "local_rule_based",
        "ai_error": ai.get("error"),
        "provider_used": provider_used,
        "ai_enabled": ai_enhanced,
        "ai_enhanced": ai_enhanced,
        "local_police_summary": local_police_summary,
        "police_summary": local_police_summary,
        "recommended_action": result["recommended_action"],
        "phishing_dataset": phishing_dataset_summary(),
        "future_integrations": ["Google Safe Browsing", "VirusTotal with legal API key", "urlscan.io with legal API key", "PhishTank/OpenPhish feeds"],
        "raw_result": result,
    }


@app.post("/screenshots/analyze")
def screenshot_scan(payload: ScreenshotAnalyzeRequest) -> dict[str, Any]:
    data = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()
    return analyze_screenshot(data)


def _parse_incident_date(value: str | None) -> datetime | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


@app.get("/hotspots")
def hotspots(
    scam_type: str = "All",
    risk_level: str = "All",
    time_range: str = "All",
    payment_mode: str = "All",
    min_amount: float = 0,
    max_amount: float = 0,
) -> dict[str, Any]:
    incidents = list_threat_incidents()
    parsed_dates = [date for date in (_parse_incident_date(item.get("incident_date")) for item in incidents) if date]
    latest_date = max(parsed_dates) if parsed_dates else None

    def include(item: dict[str, Any]) -> bool:
        amount = float(item.get("amount_lost") or 0)
        if scam_type != "All" and item.get("scam_type") != scam_type:
            return False
        if risk_level != "All" and item.get("risk_level") != risk_level:
            return False
        if payment_mode != "All" and item.get("payment_mode") != payment_mode:
            return False
        if min_amount and amount < min_amount:
            return False
        if max_amount and amount > max_amount:
            return False
        if latest_date and time_range != "All":
            days = 7 if time_range == "Last 7 days" else 30 if time_range == "Last 30 days" else 90
            item_date = _parse_incident_date(item.get("incident_date"))
            if not item_date or item_date < latest_date - timedelta(days=days):
                return False
        return True

    filtered_incidents = [incident for incident in incidents if include(incident)]
    heat: dict[str, dict[str, Any]] = {}
    for incident in filtered_incidents:
        location = incident.get("location") or "Unknown"
        current = heat.setdefault(
            location,
            {
                "location": location,
                "mandal": incident.get("mandal") or "",
                "district": incident.get("district") or "Prakasam",
                "incident_count": 0,
                "total_amount_lost": 0.0,
                "max_risk_score": 0,
                "top_categories": {},
            },
        )
        current["incident_count"] += 1
        current["total_amount_lost"] += float(incident.get("amount_lost") or 0)
        current["max_risk_score"] = max(current["max_risk_score"], int(incident.get("risk_score") or 0))
        category = incident.get("scam_type") or "Unknown"
        current["top_categories"][category] = current["top_categories"].get(category, 0) + 1

    hotspot_items = []
    for item in heat.values():
        category_counts = item.pop("top_categories")
        item["total_amount_lost"] = round(item["total_amount_lost"], 2)
        item["heat_level"] = (
            "Critical"
            if item["max_risk_score"] >= 85 or item["incident_count"] >= 5
            else "High"
            if item["max_risk_score"] >= 70 or item["incident_count"] >= 3
            else "Moderate"
        )
        item["top_category"] = max(category_counts.items(), key=lambda pair: pair[1])[0] if category_counts else "Unknown"
        hotspot_items.append(item)

    hotspot_items.sort(key=lambda item: (item["incident_count"], item["max_risk_score"]), reverse=True)
    incidents_over_time = _incident_trend(filtered_incidents)
    amount_by_area = _amount_distribution(filtered_incidents, "location")
    scam_types = sorted({incident.get("scam_type") for incident in incidents if incident.get("scam_type")})
    risk_levels = sorted({incident.get("risk_level") for incident in incidents if incident.get("risk_level")})
    payment_modes = sorted({incident.get("payment_mode") for incident in incidents if incident.get("payment_mode")})
    rising_locations = [
        {
            "location": item["location"],
            "insight": f"{item['top_category']} reports are prominent in {item['location']}.",
            "incident_count": item["incident_count"],
            "heat_level": item["heat_level"],
        }
        for item in hotspot_items[:5]
    ]
    high_risk_area_alerts = [
        f"{item['location']} has {item['incident_count']} synthetic {item['top_category']} reports with {item['heat_level']} heat."
        for item in hotspot_items
        if item["heat_level"] in {"High", "Critical"}
    ][:6]
    insights = [
        f"{hotspot_items[0]['location']} has the highest number of {hotspot_items[0]['top_category']} reports."
        if hotspot_items
        else "No hotspot data matched the selected filters.",
        "UPI refund scams are rising in Chirala in the synthetic demo data.",
        "Digital arrest reports increased this week in the synthetic police-intelligence feed.",
    ]
    return {
        "total_hotspots": len(hotspot_items),
        "total_incidents": len(filtered_incidents),
        "total_synthetic_amount_lost": round(sum(float(item.get("amount_lost") or 0) for item in filtered_incidents), 2),
        "hotspots": hotspot_items,
        "top_affected_locations": hotspot_items[:6],
        "rising_locations": rising_locations,
        "incidents_over_time": incidents_over_time,
        "amount_lost_by_area": amount_by_area,
        "high_risk_area_alerts": high_risk_area_alerts,
        "insights": insights,
        "filters": {
            "scam_types": ["All"] + scam_types,
            "risk_levels": ["All"] + risk_levels,
            "payment_modes": ["All"] + payment_modes,
            "time_ranges": ["All", "Last 7 days", "Last 30 days", "Last 90 days"],
            "selected": {
                "scam_type": scam_type,
                "risk_level": risk_level,
                "time_range": time_range,
                "payment_mode": payment_mode,
                "min_amount": min_amount,
                "max_amount": max_amount,
            },
        },
        "note": "All hotspots are based on fictional synthetic demo incidents.",
    }


@app.get("/threat-intel")
def threat_intel_alias() -> dict[str, Any]:
    return threat_intel_dashboard()


@app.get("/admin/analytics")
def admin_analytics() -> dict[str, Any]:
    reports = list_incident_reports(limit=10000)
    cases_data = analytics()
    transactions_data = transaction_analytics()
    threat_data = threat_intel_dashboard()

    status_counts: dict[str, int] = {}
    priority_counts: dict[str, int] = {}
    officer_counts: dict[str, int] = {}
    for report in reports:
        status = report.get("status") or "New"
        priority = report.get("police_triage_priority") or "Review Recommended"
        officer = report.get("assigned_officer") or "Unassigned"
        status_counts[status] = status_counts.get(status, 0) + 1
        priority_counts[priority] = priority_counts.get(priority, 0) + 1
        officer_counts[officer] = officer_counts.get(officer, 0) + 1

    return {
        "total_incident_reports": len(reports),
        "total_scam_cases": cases_data["total_reports"],
        "total_transactions": transactions_data["total_transactions"],
        "total_threat_incidents": threat_data["total_incidents"],
        "critical_queue_count": sum(
            1 for report in reports if report.get("police_triage_priority") == "Critical Immediate Triage"
        ),
        "status_distribution": [{"name": key, "value": value} for key, value in sorted(status_counts.items())],
        "priority_distribution": [{"name": key, "value": value} for key, value in sorted(priority_counts.items())],
        "officer_workload": [{"name": key, "value": value} for key, value in sorted(officer_counts.items())],
        "top_location": threat_data["top_affected_location"],
        "top_scam_category": threat_data["top_scam_category"],
        "high_priority_reports": [
            report
            for report in reports
            if report.get("police_triage_priority") in {"High Priority", "Critical Immediate Triage"}
        ][:8],
        "system_health": {
            "database": "SQLite local demo",
            "external_api_dependency": "None",
            "data_policy": "Synthetic only",
        },
    }


def _generate_cyberdost_ai_text(
    *,
    user_message: str,
    language: str,
    detected_intent: str,
    category: str | None,
    risk_score: int | None,
    local_guidance: str,
) -> dict[str, Any]:
    del user_message, detected_intent, category, risk_score, local_guidance
    prompt = (
        "Write 3 short citizen safety sentences in English. "
        "Advice: verify before sending money, do not rush under pressure, save screenshots and transaction details, "
        "and call 1930 if money was already lost."
    )
    result = generate_ai_text(prompt, purpose="cyberdost")
    if result.get("success"):
        return result

    logger.info("Chatbot Gemini retry with compact prompt after: %s", result.get("error") or "unknown error")
    compact_prompt = (
        "Say: Verify before sending money. Do not rush. Save evidence and call 1930 if money was lost."
    )
    retry = generate_ai_text(compact_prompt, purpose="cyberdost")
    return retry if retry.get("success") else result


@app.post("/chatbot/message")
def chatbot_message(payload: ChatbotRequest) -> dict[str, Any]:
    logger.info("Chatbot route called")
    message = payload.message.strip()
    lowered = message.lower()
    language = (payload.language or "en").lower()
    context = payload.context or {}
    quick_actions = [
        "Check this message",
        "Report incident",
        "I shared OTP",
        "I paid money",
        "Call 1930 guidance",
        "UPI fraud help",
        "Digital arrest help",
        "Phishing link help",
        "Fake job scam help",
        "Investment scam help",
    ]
    prototype_notice = (
        "I am a cyber safety assistant prototype. For urgent cyber fraud, report to 1930 and follow official police guidance."
    )
    emergency_guidance = (
        "If money was just lost or payment credentials were shared, preserve screenshots, transaction IDs, sender details, "
        "and contact the cyber fraud helpline 1930 or the official cybercrime portal as soon as possible."
    )

    def local_chat_response(
        text: str,
        *,
        intent: str,
        detected: str,
        category: str | None = None,
        risk_score: int | None = None,
        recommended_action: str = "",
        suggest_report: bool = False,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        response = {
            "message": text,
            "reply": text,
            "provider_used": "Local Fallback",
            "ai_enhanced": False,
            "ai_enabled": False,
            "ai_provider": "local_fallback",
            "ai_mode": "local_rule_based",
            "ai_error": None,
            "intent": intent,
            "detected_intent": detected,
            "category": category,
            "risk_score": risk_score,
            "quick_actions": quick_actions,
            "emergency_guidance": emergency_guidance,
            "prototype_notice": prototype_notice,
            "recommended_action": recommended_action,
            "suggest_report": suggest_report,
        }
        if extra:
            response.update(extra)
        return response

    def maybe_enhance_chat_response(response: dict[str, Any], prompt_context: str) -> dict[str, Any]:
        if not payload.use_optional_ai:
            logger.info("CyberDost provider_used = Local Fallback")
            return response
        logger.info("Chatbot attempting Gemini")
        ai = _generate_cyberdost_ai_text(
            user_message=prompt_context,
            language=language,
            detected_intent=response.get("detected_intent") or response.get("intent") or "general_awareness",
            category=response.get("category"),
            risk_score=response.get("risk_score"),
            local_guidance=response.get("message") or response.get("reply") or "",
        )
        ai_enhanced = bool(ai.get("success"))
        provider_used = ai.get("provider_used") if ai_enhanced else "Local Fallback"
        if ai_enhanced:
            logger.info("Chatbot Gemini success")
        else:
            logger.info("Chatbot Gemini failed: %s", ai.get("error") or "unknown error")
        logger.info("Chatbot provider_used = %s", provider_used)
        if ai_enhanced:
            response.update(
                {
                    "message": ai.get("text") or response.get("message"),
                    "reply": ai.get("text") or response.get("reply"),
                    "provider_used": provider_used,
                    "ai_enhanced": True,
                    "ai_enabled": True,
                    "ai_provider": _ai_provider_slug(provider_used),
                    "ai_mode": "ai_enhanced",
                    "ai_error": None,
                }
            )
        else:
            response.update(
                {
                    "provider_used": "Local Fallback",
                    "ai_enhanced": False,
                    "ai_enabled": False,
                    "ai_provider": "local_fallback",
                    "ai_mode": "local_rule_based",
                    "ai_error": ai.get("error"),
                }
            )
        return response

    blocked_terms = [
        "hack into",
        "hack account",
        "steal password",
        "bypass otp",
        "phishing kit",
        "make phishing",
        "create phishing",
        "malware",
        "keylogger",
        "spy app",
        "doxx",
        "track location",
        "track someone",
        "revenge",
        "clone whatsapp",
        "read private messages",
    ]
    if any(term in lowered for term in blocked_terms):
        return local_chat_response(
            (
                "I can help with prevention, reporting, and evidence preservation, but I cannot help with hacking, "
                "credential theft, malware, tracking, doxxing, or retaliation. "
                + prototype_notice
            ),
            intent="safety_refusal",
            detected="unsafe_request",
            recommended_action="Preserve evidence and contact the cybercrime helpline or local police for lawful help.",
        )

    url_match = re.search(r"(?:https?://|www\.)[^\s<>()]+", message, flags=re.IGNORECASE)
    extracted_url = url_match.group(0).rstrip(".,;)]}") if url_match else ""

    intent_terms = {
        "otp_shared": [
            "i shared otp",
            "shared otp",
            "gave otp",
            "told otp",
            "entered otp",
            "otp share",
            "pin shared",
            "shared pin",
            "password shared",
            "cvv shared",
            "ఓటీపీ ఇచ్చాను",
            "ओटीपी बताया",
            "ওটিপি দিয়েছি",
        ],
        "money_paid": [
            "i paid",
            "paid money",
            "money lost",
            "amount debited",
            "sent money",
            "transferred money",
            "payment done",
            "upi pin entered",
            "డబ్బు పంపాను",
            "पैसे भेजे",
            "টাকা পাঠিয়েছি",
        ],
        "digital_arrest": [
            "digital arrest",
            "video call arrest",
            "arrest warrant",
            "police case",
            "cyber cell",
            "stay on call",
            "settlement amount",
            "అరెస్ట్",
            "పోలీస్",
            "गिरफ्तार",
            "पुलिस",
            "গ্রেফতার",
            "পুলিশ",
        ],
        "upi_fraud": ["upi", "refund", "collect request", "qr", "scan qr", "cashback", "యూపీఐ", "यूपीआई", "ইউপিআই"],
        "phishing_link": ["phishing", "link", "login", "website", "url", "domain", "లింక్", "लिंक", "লিংক"],
        "fake_kyc": ["kyc", "account blocked", "account freeze", "aadhaar", "pan", "కేవైసీ", "केवाईसी", "কেওয়াইসি"],
        "fake_job": ["job", "work from home", "registration fee", "joining fee", "offer letter", "ఉద్యోగం", "नौकरी", "চাকরি"],
        "fake_loan": ["loan", "processing fee", "instant loan", "pre approved", "లోన్", "लोन", "ঋণ"],
        "investment_scam": ["investment", "trading", "crypto", "guaranteed profit", "double money", "పెట్టుబడి", "निवेश", "বিনিয়োগ"],
        "fake_customer_care": ["customer care", "helpline", "support agent", "remote access", "anydesk", "refund team"],
        "qr_code": ["qr code", "scan and receive", "merchant qr", "క్యూ ఆర్", "क्यूआर", "কিউআর"],
        "report_guidance": ["report", "complaint", "1930", "cybercrime portal", "fir", "రిపోర్ట్", "शिकायत", "অভিযোগ"],
    }

    def has_any(intent: str) -> bool:
        return any(term in lowered for term in intent_terms[intent])

    detected_intent = "general_awareness"
    if has_any("otp_shared"):
        detected_intent = "otp_shared"
    elif has_any("money_paid"):
        detected_intent = "money_paid"
    elif has_any("digital_arrest"):
        detected_intent = "digital_arrest"
    elif has_any("upi_fraud"):
        detected_intent = "upi_fraud"
    elif has_any("phishing_link") or extracted_url:
        detected_intent = "phishing_link"
    elif has_any("fake_kyc"):
        detected_intent = "fake_kyc"
    elif has_any("fake_job"):
        detected_intent = "fake_job"
    elif has_any("fake_loan"):
        detected_intent = "fake_loan"
    elif has_any("investment_scam"):
        detected_intent = "investment_scam"
    elif has_any("fake_customer_care"):
        detected_intent = "fake_customer_care"
    elif has_any("qr_code"):
        detected_intent = "qr_code"
    elif has_any("report_guidance"):
        detected_intent = "report_guidance"

    minimal_known_terms = {"otp", "upi", "kyc", "link", "fraud", "scam", "arrest", "1930", "report"}
    if len(lowered.split()) <= 4 and not extracted_url and not any(term in lowered for term in minimal_known_terms):
        return maybe_enhance_chat_response(local_chat_response(
            "I can help. Please paste the suspicious message/link or tell me what happened: money paid, OTP shared, UPI PIN entered, or only a warning message received?",
            intent="follow_up_needed",
            detected="follow_up_needed",
            extra={
                "follow_up_questions": [
                    "Did the message ask for OTP, PIN, password, CVV, or Aadhaar/PAN?",
                    "Was money paid or a UPI collect/QR request approved?",
                    "Was there a link, app install request, or digital arrest threat?",
                ]
            },
        ), message)

    scam_terms = [
        "otp",
        "kyc",
        "upi",
        "refund",
        "loan",
        "lottery",
        "digital arrest",
        "qr",
        "password",
        "pin",
        "link",
        "is this a scam",
        "scam",
        "fraud",
        "phishing",
        "customer care",
        "investment",
        "job",
        "telugu",
        "cheppakandi",
    ]
    should_analyze = (
        bool(extracted_url)
        or any(term in lowered for term in scam_terms)
        or detected_intent not in {"general_awareness", "report_guidance", "follow_up_needed"}
    )
    if should_analyze:
        result = analyze_scam(
            message,
            extracted_url,
            {"platform": "Cyber Dost Chatbot", "language": language, "chat_context": context},
        )
        if detected_intent == "digital_arrest":
            guidance = "Digital arrest is a scam pattern. Real police do not arrest citizens over video calls or demand money to avoid arrest."
        elif detected_intent == "upi_fraud":
            guidance = "For UPI, entering PIN sends money. Refunds do not require UPI PIN, QR scanning, or collect-request approval."
        elif detected_intent == "otp_shared" or any(term in lowered for term in ["otp", "pin", "password", "cvv"]):
            guidance = "Never share OTP, PIN, password, CVV, or verification code. If already shared, secure the account and report quickly."
        elif detected_intent == "fake_job":
            guidance = "Real recruitment should not require urgent registration, training, or security fees before verification."
        elif detected_intent == "investment_scam":
            guidance = "Guaranteed profit, daily return, or secret trading groups are high-risk investment scam signals."
        elif detected_intent == "fake_kyc":
            guidance = "Verify KYC only inside the official bank app, website, branch, or helpline. Do not use unsolicited links."
        elif detected_intent == "fake_customer_care":
            guidance = "Use official support inside the official app or website. Do not install remote-access apps for refunds."
        elif detected_intent == "fake_loan":
            guidance = "Do not pay processing, insurance, or verification fees before confirming a lender through official channels."
        elif detected_intent == "money_paid":
            guidance = "Act quickly: preserve transaction IDs, screenshots, receiver details, and contact 1930 as soon as possible."
        else:
            guidance = "Treat unsolicited links, payment pressure, and private-data requests carefully. Verify through official channels before acting."
        risk_payload = {
            "risk_score": result["risk_score"],
            "risk_level": result["risk_level"],
            "category": result["category"],
            "confidence_score": result.get("confidence_score", 0),
            "police_triage_priority": result.get("police_triage_priority", "Review Recommended"),
            "risk_factors": result["risk_factors"][:5],
            "matched_patterns": result.get("matched_patterns", [])[:8],
            "citizen_explanation": result.get("citizen_explanation", ""),
            "recommended_citizen_action": result.get("recommended_citizen_action", ""),
            "signal_sources": result.get("signal_sources", []),
        }
        local_reply = (
            f"This looks like {result['category']} with risk score {result['risk_score']}/100 "
            f"({result['risk_level']}). {guidance} {result['recommended_citizen_action']} {prototype_notice}"
        )
        ai = {
            "success": False,
            "provider_used": "Local Fallback",
            "text": local_reply,
            "error": "Optional AI disabled.",
        }
        if payload.use_optional_ai:
            logger.info("Chatbot attempting Gemini")
            ai = _generate_cyberdost_ai_text(
                user_message=message,
                language=language,
                detected_intent=detected_intent,
                category=result["category"],
                risk_score=result["risk_score"],
                local_guidance=f"{guidance} {result['recommended_citizen_action']}",
            )
            if ai.get("success"):
                logger.info("Chatbot Gemini success")
            else:
                logger.info("Chatbot Gemini failed: %s", ai.get("error") or "unknown error")
        ai_enhanced = bool(ai.get("success"))
        provider_used = ai.get("provider_used") if ai_enhanced else "Local Fallback"
        reply_text = ai.get("text") if ai_enhanced else local_reply
        logger.info("Chatbot provider_used = %s", provider_used)
        return {
            "message": reply_text,
            "reply": reply_text,
            "intent": "scam_guidance",
            "detected_intent": detected_intent,
            "risk_score": result["risk_score"],
            "risk_level": result["risk_level"],
            "category": result["category"],
            "risk_factors": result["risk_factors"][:5],
            "analysis": risk_payload,
            "quick_actions": quick_actions,
            "emergency_guidance": emergency_guidance,
            "prototype_notice": prototype_notice,
            "recommended_action": result.get("recommended_citizen_action", guidance),
            "suggest_report": detected_intent in {"money_paid", "otp_shared"} or result["risk_score"] >= 51,
            "ai_provider": _ai_provider_slug(provider_used) if ai_enhanced else "local_fallback",
            "ai_error": ai.get("error"),
            "provider_used": provider_used,
            "ai_enabled": ai_enhanced,
            "ai_enhanced": ai_enhanced,
            "ai_mode": "ai_enhanced" if ai_enhanced else "local_rule_based",
            "safety_note": prototype_notice,
        }

    if detected_intent == "report_guidance" or context.get("wantsReport"):
        return maybe_enhance_chat_response(local_chat_response(
            (
                "To report, keep screenshots, sender IDs, URLs, transaction IDs, time, and receiver placeholders. "
                "Use the Citizen Report form in this prototype, and use 1930 for urgent financial cyber fraud. "
                + prototype_notice
            ),
            intent="report_guidance",
            detected="report_guidance",
            recommended_action="Open the incident reporting form and preserve evidence before deleting any messages.",
            suggest_report=True,
        ), message)

    return maybe_enhance_chat_response(local_chat_response(
        (
            "Cyber Dost Prakasam can help you check suspicious messages, learn safe UPI practices, "
            "prepare a report, and preserve evidence. Never share OTP, PIN, passwords, or pay urgent fees without verification. "
            + prototype_notice
        ),
        intent="general_awareness",
        detected=detected_intent,
        recommended_action="Use the Scam Analyzer or Citizen Report page if you have a suspicious message.",
    ), message)


@app.get("/awareness/quiz")
def awareness_quiz() -> dict[str, Any]:
    return {
        "questions": [
            {key: value for key, value in question.items() if key != "answer"}
            for question in QUIZ_QUESTIONS
        ]
    }


@app.post("/awareness/quiz/submit")
def awareness_quiz_submit(payload: QuizSubmitRequest) -> dict[str, Any]:
    answer_key = {question["id"]: question["answer"] for question in QUIZ_QUESTIONS}
    score = sum(1 for question_id, answer in payload.answers.items() if answer_key.get(question_id) == answer)
    result = save_quiz_result(payload.user_email, score, len(QUIZ_QUESTIONS))
    return {
        "score": score,
        "total": len(QUIZ_QUESTIONS),
        "percentage": round((score / len(QUIZ_QUESTIONS)) * 100),
        "passed": score >= 4,
        "result": result,
        "message": "Great prevention awareness." if score >= 4 else "Review the safety tips and retake the quiz.",
    }



@app.get("/cases")
def cases() -> list[dict[str, Any]]:
    return list_cases()


@app.get("/cases/{case_id}")
def case_details(case_id: int) -> dict[str, Any]:
    case = get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")
    return case


@app.delete("/cases/{case_id}")
def remove_case(case_id: int) -> dict[str, Any]:
    deleted = delete_case(case_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Case not found.")
    return {"deleted": True, "id": case_id}


@app.get("/analytics")
def analytics() -> dict[str, Any]:
    all_cases = list_cases(limit=10000)
    category_counts: dict[str, int] = {}
    platform_counts: dict[str, int] = {}
    risk_level_counts: dict[str, int] = {}
    factor_counts: dict[str, int] = {}
    text_only_count = 0
    url_based_count = 0
    for case in all_cases:
        category_counts[case["category"]] = category_counts.get(case["category"], 0) + 1
        platform = case.get("platform") or "Unknown"
        platform_counts[platform] = platform_counts.get(platform, 0) + 1
        risk_level = case.get("risk_level") or "Low"
        risk_level_counts[risk_level] = risk_level_counts.get(risk_level, 0) + 1
        sources = set(case.get("signal_sources") or [])
        is_scam_like = case.get("category") != "Likely Safe" and case.get("risk_score", 0) >= 30
        if is_scam_like and "text" in sources and "url" not in sources:
            text_only_count += 1
        if is_scam_like and "url" in sources:
            url_based_count += 1
        for factor in case.get("risk_factors", []):
            label = factor.get("label") or factor.get("code") or "Unknown"
            factor_counts[label] = factor_counts.get(label, 0) + 1

    high_risk = [case for case in all_cases if case["risk_score"] >= 60]
    critical = [case for case in all_cases if case["risk_score"] >= 80]
    high_priority = [
        case
        for case in all_cases
        if case.get("police_triage_priority") in {"High Priority", "Critical Immediate Triage"}
    ]
    average_confidence = (
        round(sum(case.get("confidence_score", 0) for case in all_cases) / len(all_cases))
        if all_cases
        else 0
    )

    return {
        "total_reports": len(all_cases),
        "high_risk_reports": len(high_risk),
        "critical_reports": len(critical),
        "average_confidence": average_confidence,
        "category_distribution": [
            {"name": name, "value": value} for name, value in sorted(category_counts.items())
        ],
        "risk_level_distribution": [
            {"name": name, "value": risk_level_counts.get(name, 0)}
            for name in ["Low", "Medium", "High", "Critical"]
            if risk_level_counts.get(name, 0)
        ],
        "platform_distribution": [
            {"name": name, "value": value} for name, value in sorted(platform_counts.items())
        ],
        "top_risk_factors": [
            {"name": name, "value": value}
            for name, value in sorted(factor_counts.items(), key=lambda item: item[1], reverse=True)[:8]
        ],
        "text_only_scam_count": text_only_count,
        "url_based_scam_count": url_based_count,
        "high_priority_cases": high_priority[:8],
        "recent_cases": all_cases[:8],
        "critical_alerts": critical[:5],
    }


@app.post("/transactions/analyze")
def analyze_transaction_route(payload: TransactionAnalyzeRequest) -> dict[str, Any]:
    payload_data = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()
    analysis = analyze_transaction(payload_data)
    return create_transaction(payload_data, analysis)


@app.get("/transactions")
def transactions() -> list[dict[str, Any]]:
    return list_transactions()


@app.get("/transactions/analytics")
def transaction_analytics() -> dict[str, Any]:
    all_transactions = list_transactions(limit=10000)
    risk_level_counts: dict[str, int] = {}
    fraud_type_counts: dict[str, int] = {}
    factor_counts: dict[str, int] = {}
    payment_method_counts: dict[str, int] = {}
    total_amount = 0.0

    for transaction in all_transactions:
        risk_level = transaction.get("risk_level") or "Low"
        fraud_type = transaction.get("suspected_fraud_type") or "Likely Safe Transaction"
        payment_method = transaction.get("payment_method") or "Unknown"
        amount = float(transaction.get("amount") or 0)
        risk_level_counts[risk_level] = risk_level_counts.get(risk_level, 0) + 1
        if fraud_type != "Likely Safe Transaction":
            fraud_type_counts[fraud_type] = fraud_type_counts.get(fraud_type, 0) + 1
        payment_method_counts[payment_method] = payment_method_counts.get(payment_method, 0) + 1
        total_amount += amount
        for factor in transaction.get("risk_factors", []):
            label = factor.get("label") or factor.get("code") or "Unknown"
            factor_counts[label] = factor_counts.get(label, 0) + 1

    high_risk = [transaction for transaction in all_transactions if transaction.get("risk_score", 0) >= 55]
    critical = [transaction for transaction in all_transactions if transaction.get("risk_score", 0) >= 75]
    high_priority = [
        transaction
        for transaction in all_transactions
        if transaction.get("police_triage_priority") in {"High Priority", "Critical Immediate Triage"}
    ]

    return {
        "total_transactions": len(all_transactions),
        "high_risk_transaction_count": len(high_risk),
        "critical_transaction_count": len(critical),
        "high_priority_transaction_count": len(high_priority),
        "total_monitored_amount": round(total_amount, 2),
        "risk_level_distribution": [
            {"name": name, "value": risk_level_counts.get(name, 0)}
            for name in ["Low", "Medium", "High", "Critical"]
            if risk_level_counts.get(name, 0)
        ],
        "suspicious_transaction_categories": [
            {"name": name, "value": value}
            for name, value in sorted(fraud_type_counts.items(), key=lambda item: item[1], reverse=True)
        ],
        "payment_method_distribution": [
            {"name": name, "value": value} for name, value in sorted(payment_method_counts.items())
        ],
        "top_transaction_risk_factors": [
            {"name": name, "value": value}
            for name, value in sorted(factor_counts.items(), key=lambda item: item[1], reverse=True)[:8]
        ],
        "high_priority_transactions": high_priority[:8],
        "recent_transactions": all_transactions[:8],
    }


@app.get("/transactions/{transaction_db_id}")
def transaction_details(transaction_db_id: int) -> dict[str, Any]:
    transaction = get_transaction(transaction_db_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found.")
    return transaction


def _distribution(items: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    counts: dict[str, int] = {}
    for item in items:
        name = item.get(key) or "Unknown"
        counts[name] = counts.get(name, 0) + 1
    return [{"name": name, "value": value} for name, value in sorted(counts.items(), key=lambda pair: pair[1], reverse=True)]


def _amount_distribution(items: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    totals: dict[str, float] = {}
    for item in items:
        name = item.get(key) or "Unknown"
        totals[name] = totals.get(name, 0.0) + float(item.get("amount_lost") or 0)
    return [
        {"name": name, "value": round(value, 2)}
        for name, value in sorted(totals.items(), key=lambda pair: pair[1], reverse=True)
    ]


def _incident_trend(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: dict[str, int] = {}
    for item in items:
        day = str(item.get("incident_date") or "Unknown")
        counts[day] = counts.get(day, 0) + 1
    return [{"name": day, "value": counts[day]} for day in sorted(counts)]


@app.get("/threat-intel/incidents")
def threat_incidents() -> list[dict[str, Any]]:
    return list_threat_incidents()


@app.get("/threat-intel/dashboard")
def threat_intel_dashboard() -> dict[str, Any]:
    incidents = list_threat_incidents()
    indicators = list_threat_indicators()
    clusters = list_case_clusters()
    category_distribution = _distribution(incidents, "scam_type")
    location_distribution = _distribution(incidents, "location")
    amount_by_scam_type = _amount_distribution(incidents, "scam_type")
    payment_mode_distribution = _distribution(incidents, "payment_mode")
    target_group_distribution = _distribution(incidents, "target_group")
    high_risk_indicators = [indicator for indicator in indicators if int(indicator.get("risk_score") or 0) >= 75]
    active_clusters = [cluster for cluster in clusters if int(cluster.get("risk_score") or 0) >= 75]
    top_scam_category = category_distribution[0]["name"] if category_distribution else "None"
    top_location = location_distribution[0]["name"] if location_distribution else "None"
    most_targeted_group = target_group_distribution[0]["name"] if target_group_distribution else "None"

    heat_indicators = []
    for location_item in location_distribution:
        location_incidents = [incident for incident in incidents if incident.get("location") == location_item["name"]]
        total_amount = sum(float(incident.get("amount_lost") or 0) for incident in location_incidents)
        max_score = max((int(incident.get("risk_score") or 0) for incident in location_incidents), default=0)
        heat_indicators.append(
            {
                "location": location_item["name"],
                "incidents": location_item["value"],
                "total_amount": round(total_amount, 2),
                "heat": "Critical" if max_score >= 85 else "High" if max_score >= 70 else "Moderate",
            }
        )

    trend_cards = [
        {
            "title": "KYC scams increased this week",
            "value": f"{sum(1 for incident in incidents if 'KYC' in incident.get('scam_type', ''))} synthetic reports",
            "detail": "Demo trend based on seeded Prakasam intelligence records.",
        },
        {
            "title": "UPI refund fraud rising",
            "value": f"{sum(1 for incident in incidents if 'UPI' in incident.get('scam_type', ''))} synthetic reports",
            "detail": "Refund and collect-request scripts are visible in the demo dataset.",
        },
        {
            "title": "Top affected area",
            "value": top_location,
            "detail": "Location with the highest synthetic incident count.",
        },
        {
            "title": "Most targeted group",
            "value": most_targeted_group,
            "detail": "Target group most frequently represented in synthetic records.",
        },
    ]

    return {
        "total_incidents": len(incidents),
        "total_amount_lost": round(sum(float(incident.get("amount_lost") or 0) for incident in incidents), 2),
        "high_risk_indicators_count": len(high_risk_indicators),
        "active_clusters_count": len(active_clusters),
        "top_scam_category": top_scam_category,
        "top_affected_location": top_location,
        "weekly_trend_insight": f"{top_scam_category} is the leading synthetic trend in {top_location}.",
        "trend_cards": trend_cards,
        "heat_indicators": heat_indicators,
        "incidents_by_location": location_distribution,
        "incidents_by_scam_category": category_distribution,
        "incidents_over_time": _incident_trend(incidents),
        "amount_lost_by_scam_type": amount_by_scam_type,
        "payment_mode_distribution": payment_mode_distribution,
        "target_group_distribution": target_group_distribution,
        "high_risk_indicators": high_risk_indicators[:8],
        "linked_case_clusters": active_clusters[:8],
        "recent_incidents": incidents[:10],
    }


@app.get("/threat-intel/indicators/search")
def indicator_search(query: str = "") -> dict[str, Any]:
    results = search_threat_indicators(query)
    primary = results[0] if results else None
    return {
        "query": query,
        "count": len(results),
        "primary_result": primary,
        "results": results,
        "future_integrations": [
            "CERT-In alerts",
            "1930 cybercrime complaint data",
            "Verified police databases",
            "VirusTotal or AbuseIPDB with legal API keys",
            "Approved public threat feeds",
        ],
    }


@app.get("/threat-intel/clusters")
def threat_clusters() -> list[dict[str, Any]]:
    return list_case_clusters()


@app.get("/threat-intel/clusters/{cluster_id}")
def threat_cluster_details(cluster_id: str) -> dict[str, Any]:
    cluster = get_case_cluster(cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found.")
    return cluster


def _build_case_pdf(case: dict[str, Any]) -> BytesIO:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=42, leftMargin=42, topMargin=42, bottomMargin=42)
    styles = getSampleStyleSheet()
    story: list[Any] = []

    story.append(Paragraph("CyberShield Police Case Report", styles["Title"]))
    story.append(Paragraph("Synthetic demo report for cybercrime triage and awareness.", styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))

    summary_rows = [
        ["Case ID", str(case["id"])],
        ["Created", case["created_at"]],
        ["Risk", f"{case['risk_score']}/100 - {case['risk_level']}"],
        ["Confidence", f"{case.get('confidence_score', 0)}%"],
        ["Category", case["category"]],
        ["Related Categories", ", ".join(category.get("name", "") for category in case.get("categories", [])[:4])],
        ["Police Triage Priority", case.get("police_triage_priority") or "Review Recommended"],
        ["Detection Mode", case.get("detection_mode") or "unknown"],
        ["Signal Sources", ", ".join(case.get("signal_sources", [])) or "None"],
        ["Platform", case.get("platform") or "Unknown"],
        ["Victim Age Group", case.get("victim_age_group") or "Not provided"],
        ["Amount Involved", f"Rs. {case.get('amount_involved') or 0:,.2f}"],
        ["URL", case.get("url") or "Not provided"],
    ]
    table = Table(summary_rows, colWidths=[1.7 * inch, 4.6 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e8eef8")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#16233a")),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#aab7c8")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 0.22 * inch))

    sections = [
        ("Submitted Message", case["message"]),
        ("Citizen Explanation", case["citizen_explanation"]),
        ("Police Investigation Summary", case["police_summary"]),
        ("Police Triage Priority", case.get("police_triage_priority") or "Review Recommended"),
        (
            "Police Triage Explanation",
            case.get("police_triage_explanation") or "Priority was assigned from the risk score and detected category.",
        ),
        ("Detection Signals", f"{case.get('detection_mode') or 'unknown'} using {', '.join(case.get('signal_sources', [])) or 'no'} signals."),
        ("Recommended Citizen Action", case.get("recommended_citizen_action") or case["recommended_action"]),
        ("Recommended Police Action", case.get("recommended_police_action") or "Preserve evidence and review triggered rules."),
    ]
    for title, body in sections:
        story.append(Paragraph(title, styles["Heading2"]))
        safe_body = escape(str(body)).replace("\n", "<br />")
        story.append(Paragraph(safe_body, styles["BodyText"]))
        story.append(Spacer(1, 0.12 * inch))

    story.append(Paragraph("Triggered Risk Factors", styles["Heading2"]))
    if case.get("risk_factors"):
        for factor in case["risk_factors"]:
            story.append(
                Paragraph(
                    f"<b>{escape(str(factor['label']))}</b> ({factor['weight']} pts): {escape(str(factor['evidence']))}",
                    styles["BodyText"],
                )
            )
    else:
        story.append(Paragraph("No high-confidence risk factors were detected.", styles["BodyText"]))

    if case.get("matched_patterns"):
        story.append(Spacer(1, 0.12 * inch))
        story.append(Paragraph("Matched Patterns", styles["Heading2"]))
        for match in case["matched_patterns"][:12]:
            story.append(
                Paragraph(
                    f"<b>{escape(str(match.get('source', '')))}</b> - {escape(str(match.get('rule', '')))}: {escape(str(match.get('pattern', '')))}",
                    styles["BodyText"],
                )
            )

    doc.build(story)
    buffer.seek(0)
    return buffer


@app.get("/export/{case_id}")
def export_case(case_id: int) -> StreamingResponse:
    case = get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")
    pdf = _build_case_pdf(case)
    headers = {"Content-Disposition": f'attachment; filename="cybershield-case-{case_id}.pdf"'}
    return StreamingResponse(pdf, media_type="application/pdf", headers=headers)
