from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.scam_detector import analyze_scam
from app.services.ai_provider import optional_ai_summary


ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp"}
MAX_DEMO_IMAGE_SIZE = 5 * 1024 * 1024


def analyze_screenshot(payload: dict[str, Any]) -> dict[str, Any]:
    filename = (payload.get("filename") or "screenshot-demo.png").strip()
    file_type = (payload.get("file_type") or "").strip().lower()
    file_size = int(payload.get("file_size") or 0)
    manual_text = (payload.get("manual_text") or "").strip()
    optional_url = (payload.get("url") or "").strip()
    use_optional_ai = bool(payload.get("use_optional_ai"))

    metadata = {
        "filename": filename,
        "file_type": file_type or "unknown",
        "file_size": file_size,
        "upload_time": payload.get("upload_time") or datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "stored_image_bytes": False,
        "privacy_mode": "metadata_only",
    }

    validation_warnings: list[str] = []
    if file_type and file_type not in ALLOWED_IMAGE_TYPES:
        validation_warnings.append("Unsupported image type for demo analysis. Use PNG, JPG, JPEG, or WEBP.")
    if file_size > MAX_DEMO_IMAGE_SIZE:
        validation_warnings.append("Image metadata shows a large file. Keep demo screenshots under 5 MB.")
    if not manual_text and not optional_url:
        validation_warnings.append("No OCR text was provided. Paste visible text from the screenshot for local analysis.")

    detector_input = manual_text or "Screenshot metadata submitted without visible text. Manual text is needed for stronger risk scoring."
    result = analyze_scam(
        detector_input,
        optional_url,
        {"platform": "Screenshot Scam Analyzer", "evidence_type": file_type or "image metadata"},
    )

    image_factors = [
        "Image bytes are not stored in this prototype.",
        "No face recognition or identity matching is performed.",
        "Manual visible text is analyzed with the local scam detector.",
    ] + validation_warnings

    fallback_summary = (
        f"Screenshot analysis found {result['category']} at {result['risk_score']}/100 "
        f"({result['risk_level']}). Main action: {result['recommended_citizen_action']}"
    )
    ai_prompt = (
        "Summarize visible scam indicators from this demo screenshot text. "
        f"Category: {result['category']}. Score: {result['risk_score']}. "
        f"Visible text: {detector_input[:1200]}"
    )
    ai = optional_ai_summary(ai_prompt, fallback_summary, allow_external=use_optional_ai)

    return {
        "metadata": metadata,
        "ocr_status": "manual_text_used" if manual_text else "manual_text_needed",
        "extracted_text_preview": detector_input[:500],
        "risk_score": result["risk_score"],
        "risk_level": result["risk_level"],
        "category": result["category"],
        "confidence_score": result.get("confidence_score", 0),
        "police_triage_priority": result.get("police_triage_priority", "Review Recommended"),
        "image_risk_factors": image_factors,
        "risk_factors": result.get("risk_factors", [])[:8],
        "citizen_explanation": result.get("citizen_explanation", ""),
        "police_summary": result.get("police_summary", ""),
        "recommended_action": result.get("recommended_citizen_action", ""),
        "ai_explanation": ai.text,
        "ai_provider": ai.provider,
        "ai_mode": ai.mode,
        "ai_error": ai.error,
        "safety_note": "This prototype analyzes scam indicators in screenshots. It does not identify people or make legal conclusions.",
    }
