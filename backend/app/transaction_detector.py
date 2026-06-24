from __future__ import annotations

import re
from datetime import datetime
from typing import Any


RISK_LEVELS = [
    (75, "Critical"),
    (55, "High"),
    (28, "Medium"),
    (0, "Low"),
]

TRANSACTION_FRAUD_TYPES = {
    "UPI Refund Scam",
    "Fake Loan Processing Fee",
    "Lottery/Prize Fee Scam",
    "Fake Job Registration Fee",
    "Fake Customer Care Refund Scam",
    "QR Code Scam",
    "Suspicious Transaction Pattern",
    "Likely Safe Transaction",
}


def _as_float(value: Any) -> float:
    try:
        return max(0.0, float(value or 0))
    except (TypeError, ValueError):
        return 0.0


def _as_int(value: Any) -> int:
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError):
        return 0


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"1", "true", "yes", "y"}


def _find(pattern: str, text: str) -> list[str]:
    matches = re.findall(pattern, text, flags=re.IGNORECASE)
    values: list[str] = []
    for match in matches:
        if isinstance(match, tuple):
            match = " ".join(part for part in match if part)
        cleaned = " ".join(str(match).split())
        if cleaned and cleaned.lower() not in {value.lower() for value in values}:
            values.append(cleaned)
    return values[:5]


def _risk_level(score: int) -> str:
    for threshold, level in RISK_LEVELS:
        if score >= threshold:
            return level
    return "Low"


def _triage_priority(score: int, fraud_type: str, reported_by_user: bool) -> str:
    urgent_types = {
        "UPI Refund Scam",
        "Fake Customer Care Refund Scam",
        "QR Code Scam",
    }
    if score >= 82 or (reported_by_user and score >= 70):
        return "Critical Immediate Triage"
    if score >= 60 or fraud_type in urgent_types and score >= 52:
        return "High Priority"
    if score >= 28:
        return "Review Recommended"
    return "Low Priority"


def _parse_hour(timestamp: str) -> int | None:
    value = str(timestamp or "").strip()
    if not value:
        return None
    try:
        normalized = value.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized).hour
    except ValueError:
        match = re.search(r"\b([01]?\d|2[0-3]):[0-5]\d\b", value)
        return int(match.group(1)) if match else None


def analyze_transaction(payload: dict[str, Any]) -> dict[str, Any]:
    amount = _as_float(payload.get("amount"))
    previous_count = _as_int(payload.get("previous_transaction_count"))
    first_time_receiver = _as_bool(payload.get("is_first_time_receiver"))
    reported_by_user = _as_bool(payload.get("reported_by_user"))
    payment_method = str(payload.get("payment_method") or "").strip()
    receiver = str(payload.get("merchant_or_receiver_name") or "").strip()
    placeholder = str(payload.get("receiver_upi_or_account_placeholder") or "").strip()
    timestamp = str(payload.get("timestamp") or "").strip()
    city = str(payload.get("location_or_city") or "").strip()
    note = str(payload.get("transaction_note") or "").strip()
    age_group = str(payload.get("user_age_group") or "").strip()

    combined = " ".join([payment_method, receiver, placeholder, city, note, age_group]).lower()
    text_signals = " ".join([payment_method, receiver, placeholder, city, note]).lower()
    risk_factors: list[dict[str, Any]] = []
    category_scores: dict[str, int] = {}

    def add_factor(
        code: str,
        label: str,
        weight: int,
        evidence: str,
        fraud_type: str = "Suspicious Transaction Pattern",
        matches: list[str] | None = None,
    ) -> None:
        risk_factors.append(
            {
                "code": code,
                "label": label,
                "weight": weight,
                "evidence": evidence,
                "matched_patterns": matches or [],
                "source": "transaction",
            }
        )
        category_scores[fraud_type] = category_scores.get(fraud_type, 0) + weight

    urgent_matches = _find(r"\b(urgent|immediate|today|now|within\s+\d+\s+hours?|avoid|blocked|last chance)\b", text_signals)
    refund_matches = _find(r"\b(refund|chargeback|cashback|reversal|money return|failed payment)\b", text_signals)
    qr_matches = _find(r"\b(qr|scan|upi pin|approve request)\b", text_signals)
    collect_request_matches = _find(r"\b(collect request|approve collect request|receive money back)\b", text_signals)
    customer_care_matches = _find(r"\b(customer care|helpline|support desk|refund desk|service center)\b", text_signals)
    loan_matches = _find(r"\b(loan|processing fee|approval fee|disbursal|file charge|verification fee)\b", text_signals)
    lottery_matches = _find(r"\b(lottery|prize|winner|reward|claim fee|release fee|gift)\b", text_signals)
    job_matches = _find(r"\b(job|registration fee|interview fee|work from home|task fee|training fee)\b", text_signals)
    suspicious_matches = _find(
        r"\b(otp|pin|cvv|password|security deposit|processing fee|pay now|verify|activation|unlock|hold amount)\b",
        text_signals,
    )

    has_any_input = any(
        [
            amount,
            payment_method,
            receiver,
            placeholder,
            timestamp,
            city,
            note,
            age_group,
            previous_count,
            first_time_receiver,
            reported_by_user,
        ]
    )

    if not has_any_input:
        add_factor(
            "weak_transaction_input",
            "Weak or empty transaction input",
            5,
            "Very little transaction context was supplied, so the system keeps the score low and requests more evidence.",
            "Likely Safe Transaction",
        )

    if amount >= 100000:
        add_factor(
            "very_high_amount",
            "Very high transaction amount",
            28,
            f"Amount Rs. {amount:,.0f} is unusually high for a demo suspicious transaction review.",
        )
    elif amount >= 50000:
        add_factor(
            "high_amount",
            "High transaction amount",
            18,
            f"Amount Rs. {amount:,.0f} is high enough to require careful verification.",
        )

    if previous_count >= 6 and amount <= 1000:
        add_factor(
            "many_small_repeated",
            "Many small repeated transactions",
            20,
            f"{previous_count} previous transactions with a small current amount may indicate staged transfers.",
        )

    if first_time_receiver and urgent_matches:
        add_factor(
            "first_time_receiver_urgent",
            "First-time receiver with urgent note",
            18,
            "The receiver is new and the note uses urgency or fear pressure.",
            matches=urgent_matches,
        )

    if refund_matches:
        add_factor(
            "refund_chargeback_pattern",
            "Refund or chargeback scam language",
            20,
            "The transaction note references refund, cashback, reversal, or failed-payment recovery language.",
            "UPI Refund Scam",
            refund_matches,
        )

    if refund_matches and collect_request_matches:
        add_factor(
            "upi_collect_refund_pattern",
            "UPI collect-request refund pattern",
            20,
            "Refund wording is combined with a collect-request or receive-money-back instruction.",
            "UPI Refund Scam",
            refund_matches + collect_request_matches,
        )

    if qr_matches:
        add_factor(
            "qr_payment_pattern",
            "QR code payment scam pattern",
            24,
            "The note suggests scanning or approving a payment request, which is risky for receiving money.",
            "QR Code Scam",
            qr_matches,
        )

    if customer_care_matches and refund_matches:
        add_factor(
            "fake_customer_care_refund",
            "Fake customer care refund pattern",
            24,
            "Customer-care wording is combined with refund or reversal language.",
            "Fake Customer Care Refund Scam",
            customer_care_matches + refund_matches,
        )
    elif customer_care_matches:
        add_factor(
            "customer_care_impersonation",
            "Possible fake customer care receiver",
            14,
            "The receiver or note uses customer support wording that should be verified from official channels.",
            "Fake Customer Care Refund Scam",
            customer_care_matches,
        )

    if loan_matches:
        add_factor(
            "loan_processing_fee",
            "Loan processing fee pattern",
            24,
            "Loan approval or disbursal wording is paired with fee language.",
            "Fake Loan Processing Fee",
            loan_matches,
        )

    if lottery_matches:
        add_factor(
            "lottery_prize_fee",
            "Lottery or prize processing fee pattern",
            24,
            "Prize, reward, winner, or claim-fee language is present.",
            "Lottery/Prize Fee Scam",
            lottery_matches,
        )

    if job_matches:
        add_factor(
            "job_registration_fee",
            "Job registration or task fee pattern",
            24,
            "Job, training, interview, or work-from-home wording is paired with payment demand language.",
            "Fake Job Registration Fee",
            job_matches,
        )

    hour = _parse_hour(timestamp)
    if hour is not None and 0 <= hour <= 5 and (amount >= 1000 or suspicious_matches):
        add_factor(
            "late_night_transfer",
            "Late-night suspicious transfer",
            10,
            f"Timestamp hour {hour:02d}:00 falls in a late-night review window.",
        )

    if suspicious_matches:
        add_factor(
            "suspicious_note_keywords",
            "Suspicious keywords in transaction note",
            14,
            "The note contains sensitive-payment, verification, activation, or fee pressure wording.",
            matches=suspicious_matches,
        )

    if previous_count >= 4 and amount <= 3000:
        add_factor(
            "multiple_short_interval_payments",
            "Multiple payments pattern",
            12,
            f"{previous_count} previous transactions may indicate repeated transfers to the same receiver or campaign.",
        )

    if "senior" in age_group.lower() and first_time_receiver and urgent_matches:
        add_factor(
            "senior_urgent_first_time",
            "Senior citizen with urgent first-time payment",
            18,
            "Senior-citizen targeting combined with a first-time receiver and urgency needs quick triage.",
            matches=urgent_matches,
        )

    if any(word in age_group.lower() for word in ["student", "job seeker"]) and job_matches:
        add_factor(
            "student_job_fee",
            "Student or job seeker payment demand",
            16,
            "Student/job-seeker context combined with registration, training, or task fee language is suspicious.",
            "Fake Job Registration Fee",
            job_matches,
        )

    if reported_by_user:
        add_factor(
            "reported_by_user",
            "User reported the transaction as suspicious",
            12,
            "Citizen concern is treated as a triage signal and should be reviewed with the other evidence.",
        )

    score = min(100, sum(int(factor["weight"]) for factor in risk_factors))
    if not risk_factors:
        score = 5
    risk_level = _risk_level(score)
    specific_scores = {
        name: score
        for name, score in category_scores.items()
        if name not in {"Suspicious Transaction Pattern", "Likely Safe Transaction"}
    }
    suspected_fraud_type = (
        max((specific_scores or category_scores).items(), key=lambda item: item[1])[0]
        if category_scores
        else "Likely Safe Transaction"
    )
    if score < 20 and suspected_fraud_type == "Suspicious Transaction Pattern":
        suspected_fraud_type = "Likely Safe Transaction"

    priority = _triage_priority(score, suspected_fraud_type, reported_by_user)
    strongest = ", ".join(factor["label"] for factor in risk_factors[:3]) or "no strong suspicious pattern"

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "suspected_fraud_type": suspected_fraud_type,
        "risk_factors": risk_factors,
        "police_triage_priority": priority,
        "citizen_explanation": (
            f"This synthetic transaction is rated {risk_level} risk because it shows {strongest}. "
            "Do not repeat payment or share OTP/PIN/CVV while the receiver is being verified."
        ),
        "police_summary": (
            f"Review transaction {payload.get('transaction_id') or 'without ID'} for {suspected_fraud_type}. "
            f"Amount Rs. {amount:,.0f}, method {payment_method or 'unknown'}, receiver {receiver or 'unknown'}, "
            f"city {city or 'unknown'}. Priority: {priority}."
        ),
        "recommended_action": _recommended_action(score, suspected_fraud_type),
    }


def _recommended_action(score: int, fraud_type: str) -> str:
    if score >= 75:
        return (
            "Pause further payments, preserve screenshots and transaction references, contact the bank/payment app "
            "through official channels, and escalate for immediate police triage."
        )
    if score >= 55:
        return (
            "Verify the receiver independently, preserve evidence, avoid additional transfers, and review linked "
            "messages or calls for a coordinated scam pattern."
        )
    if score >= 28:
        return (
            "Review the receiver, transaction note, and recent payment history before approving or repeating payment."
        )
    return "No strong fraud pattern was detected, but use official channels and keep transaction records."
