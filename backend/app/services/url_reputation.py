from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from urllib.parse import urlencode
from typing import Any

from app.services.ai_provider import load_environment


def check_url_reputation(url: str | None) -> dict[str, Any]:
    """Optional URL reputation lookup.

    Local detector output remains authoritative. This helper only enriches the
    phishing scanner when a legal API key is configured.
    """
    load_environment()
    submitted_url = (url or "").strip()
    provider = os.getenv("URL_CHECK_PROVIDER", "local_only").strip().lower() or "local_only"
    if not submitted_url:
        return _result("No URL submitted", "not_applicable", False, "No URL was submitted.", provider="local_only")
    if provider in {"", "local", "local_only", "none"}:
        return _result(
            "Local rules only",
            "not_configured",
            False,
            "No external URL reputation provider is configured. Local rule-based checks were used.",
            provider="local_only",
        )
    if provider in {"google_safe_browsing", "google", "safe_browsing"}:
        return _google_safe_browsing(submitted_url)
    if provider in {"urlhaus", "abuse_ch", "abusech"}:
        return _urlhaus(submitted_url)
    if provider in {"multi", "all", "google_urlhaus", "google_safe_browsing_urlhaus"}:
        return _multi_reputation(submitted_url)
    return _result(
        "Unsupported provider",
        "not_configured",
        False,
        f"URL_CHECK_PROVIDER={provider} is not supported by this prototype.",
        provider=provider,
    )


def _google_safe_browsing(url: str) -> dict[str, Any]:
    api_key = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY", "").strip()
    if not api_key:
        return _result(
            "Google Safe Browsing not configured",
            "not_configured",
            False,
            "Set GOOGLE_SAFE_BROWSING_API_KEY and URL_CHECK_PROVIDER=google_safe_browsing to enable lookup.",
            provider="google_safe_browsing",
        )

    endpoint = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={api_key}"
    payload = {
        "client": {"clientId": "cybershield-police-demo", "clientVersion": "1.0"},
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}],
        },
    }
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            body = json.loads(response.read().decode("utf-8") or "{}")
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return _result(
            "Lookup unavailable",
            "error",
            False,
            f"External URL reputation lookup failed: {exc.__class__.__name__}. Local checks were used.",
            provider="google_safe_browsing",
        )

    matches = body.get("matches") or []
    if matches:
        threat_types = sorted({match.get("threatType", "UNKNOWN") for match in matches})
        return _result(
            "Threat match found",
            "threat_found",
            True,
            "External reputation provider reported a threat match.",
            provider="google_safe_browsing",
            details={"threat_types": threat_types},
        )
    return _result(
        "No threat match",
        "no_match",
        False,
        "External reputation provider did not report this URL. Continue using local warning signs.",
        provider="google_safe_browsing",
    )


def _urlhaus(url: str) -> dict[str, Any]:
    auth_key = os.getenv("URLHAUS_AUTH_KEY", "").strip()
    if not auth_key:
        return _result(
            "URLhaus not configured",
            "not_configured",
            False,
            "Set URLHAUS_AUTH_KEY and URL_CHECK_PROVIDER=urlhaus or multi to enable URLhaus lookup.",
            provider="urlhaus",
        )

    request = urllib.request.Request(
        "https://urlhaus-api.abuse.ch/v1/url/",
        data=urlencode({"url": url}).encode("utf-8"),
        headers={"Content-Type": "application/x-www-form-urlencoded", "Auth-Key": auth_key},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            body = json.loads(response.read().decode("utf-8") or "{}")
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return _result(
            "URLhaus lookup unavailable",
            "error",
            False,
            f"URLhaus lookup failed: {exc.__class__.__name__}. Local checks were used.",
            provider="urlhaus",
        )

    status = body.get("query_status")
    if status == "ok":
        threat = body.get("threat") or "reported_url"
        url_status = body.get("url_status") or "unknown"
        blacklists = body.get("blacklists") or {}
        return _result(
            "Threat match found",
            "threat_found",
            True,
            f"URLhaus reported this URL as {threat} with URL status {url_status}.",
            provider="urlhaus",
            details={"threat": threat, "url_status": url_status, "blacklists": blacklists},
        )
    if status == "no_results":
        return _result(
            "No URLhaus match",
            "no_match",
            False,
            "URLhaus did not report this URL. Continue using local warning signs.",
            provider="urlhaus",
        )
    return _result(
        "URLhaus lookup inconclusive",
        "error",
        False,
        f"URLhaus returned query_status={status or 'unknown'}. Local checks were used.",
        provider="urlhaus",
    )


def _multi_reputation(url: str) -> dict[str, Any]:
    checks = [_google_safe_browsing(url), _urlhaus(url)]
    threat_checks = [check for check in checks if check.get("threat_found")]
    configured_checks = [check for check in checks if check.get("status") != "not_configured"]
    if threat_checks:
        providers = ", ".join(check["provider"] for check in threat_checks)
        return _result(
            "Threat match found",
            "threat_found",
            True,
            f"At least one configured reputation provider reported this URL: {providers}.",
            provider="multi",
            details={"checks": checks},
        )
    if not configured_checks:
        return _result(
            "No external providers configured",
            "not_configured",
            False,
            "Configure GOOGLE_SAFE_BROWSING_API_KEY and/or URLHAUS_AUTH_KEY to enable external URL reputation.",
            provider="multi",
            details={"checks": checks},
        )
    if any(check.get("status") == "error" for check in configured_checks):
        return _result(
            "Reputation lookup partially unavailable",
            "error",
            False,
            "One or more reputation providers were unavailable. Local checks remain authoritative.",
            provider="multi",
            details={"checks": checks},
        )
    return _result(
        "No threat match",
        "no_match",
        False,
        "Configured reputation providers did not report this URL. This is not a safety guarantee; local rules still apply.",
        provider="multi",
        details={"checks": checks},
    )


def _result(
    label: str,
    status: str,
    threat_found: bool,
    explanation: str,
    *,
    provider: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "provider": provider,
        "status": status,
        "label": label,
        "threat_found": threat_found,
        "explanation": explanation,
        "details": details or {},
    }
