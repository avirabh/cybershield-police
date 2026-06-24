from __future__ import annotations

import logging
import os
import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


logger = logging.getLogger("cybershield.ai")

PROVIDER_GEMINI = "Gemini"
PROVIDER_HUGGINGFACE = "Hugging Face"
PROVIDER_OPENROUTER = "OpenRouter"
PROVIDER_GROQ = "Groq"
PROVIDER_MULTI = "Multi AI"
PROVIDER_FALLBACK = "Local Fallback"
DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_HUGGINGFACE_MODEL = "mistralai/Mistral-7B-Instruct-v0.3"
DEFAULT_OPENROUTER_MODEL = "mistralai/mistral-7b-instruct:free"
DEFAULT_GROQ_MODEL = "llama-3.1-8b-instant"
DEFAULT_TIMEOUT_SECONDS = 20
_LAST_PROVIDER_ERROR = ""
_ENV_LOADED = False
_PLACEHOLDER_MARKERS = ("your_", "paste", "placeholder", "demo-key", "replace_me", "example")

SAFE_SYSTEM_NOTE = (
    "You are CyberDost, a calm cyber-safety assistant for a hackathon prototype. "
    "Do not ask for OTP, PIN, passwords, CVV, full bank details, or private evidence. "
    "Do not provide hacking, tracking, revenge, doxxing, malware, credential theft, or illegal advice. "
    "Do not claim to be real police. For urgent cyber fraud, suggest reporting to 1930 and preserving evidence."
)


@dataclass(frozen=True)
class AIResult:
    provider: str
    mode: str
    text: str
    error: str = ""


def load_environment() -> None:
    """Load project-root .env and backend/.env before any provider decision."""
    global _ENV_LOADED
    if _ENV_LOADED:
        return

    backend_dir = Path(__file__).resolve().parents[2]
    project_dir = backend_dir.parent
    env_paths = (backend_dir / ".env", project_dir / ".env")

    try:
        from dotenv import load_dotenv
    except ImportError:
        for path in env_paths:
            _load_plain_env(path)
    else:
        for path in env_paths:
            if path.exists():
                load_dotenv(path, override=False)

    _ENV_LOADED = True
    logger.info("AI provider configured: %s", "yes" if _gemini_key_present() else "no")


def get_ai_status() -> dict[str, Any]:
    load_environment()
    configured_provider = _configured_provider()
    configured_candidates = _provider_candidates(configured_provider)
    provider_used = provider_display_name(configured_candidates[0]) if configured_candidates else PROVIDER_FALLBACK
    enabled = bool(configured_candidates)
    return {
        "provider_configured": enabled,
        "provider_used": provider_used,
        "gemini_key_present": _provider_key_present("gemini"),
        "model": _model_name("gemini"),
        "fallback_available": True,
        "active_provider": configured_provider if enabled else "local_fallback",
        "active_provider_label": PROVIDER_MULTI if configured_provider == "multi" and enabled else provider_used,
        "mode": "multi_ai" if configured_provider == "multi" and enabled else ("optional_ai" if enabled else "local_rule_based"),
        "ai_explanation_available": enabled,
        "local_detector_available": True,
        "api_keys_required": False,
        "ai_enabled": enabled,
        "gemini_available": _provider_key_present("gemini"),
        "openrouter_available": _provider_key_present("openrouter"),
        "groq_available": _provider_key_present("groq"),
        "huggingface_available": _provider_key_present("huggingface"),
        "last_error": _LAST_PROVIDER_ERROR,
        "providers": [
            {
                "name": "gemini",
                "env_var": "GEMINI_API_KEY",
                "configured": _provider_key_present("gemini"),
                "model": _model_name("gemini"),
            },
            {
                "name": "openrouter",
                "env_var": "OPENROUTER_API_KEY",
                "configured": _provider_key_present("openrouter"),
                "model": _model_name("openrouter"),
            },
            {
                "name": "groq",
                "env_var": "GROQ_API_KEY",
                "configured": _provider_key_present("groq"),
                "model": _model_name("groq"),
            },
            {
                "name": "huggingface",
                "env_var": "HUGGINGFACE_API_KEY",
                "configured": _provider_key_present("huggingface"),
                "model": _model_name("huggingface"),
            },
        ],
        "provider_order": configured_candidates,
        "keys_exposed_to_frontend": False,
        "fallback": "Local deterministic scoring and local response templates remain authoritative.",
    }


def provider_status() -> dict[str, Any]:
    return get_ai_status()


def generate_ai_text(prompt: str, purpose: str = "general") -> dict[str, Any]:
    global _LAST_PROVIDER_ERROR
    load_environment()

    configured_provider = _configured_provider()
    candidates = _provider_candidates(configured_provider)
    if not candidates:
        _LAST_PROVIDER_ERROR = "No optional AI provider is configured; using local fallback."
        logger.info("AI call skipped for %s; using fallback", _safe_purpose(purpose))
        return _fallback_result(_fallback_text(purpose), _LAST_PROVIDER_ERROR)

    errors: list[str] = []
    for provider in candidates:
        provider_label = provider_display_name(provider)
        logger.info("%s call started for %s", provider_label, _safe_purpose(purpose))
        try:
            text = _clean_ai_text(_call_provider(provider, prompt, _timeout_seconds()))
        except Exception as exc:  # noqa: BLE001 - provider boundary must always fall back safely.
            detail = _safe_error_detail(exc)
            errors.append(f"{provider_label}: {detail}")
            logger.warning("%s call failed: %s", provider_label, detail)
            continue

        if not text:
            errors.append(f"{provider_label}: empty or unsafe response")
            logger.warning("%s call failed: empty or unsafe response", provider_label)
            continue

        _LAST_PROVIDER_ERROR = ""
        logger.info("%s call succeeded for %s", provider_label, _safe_purpose(purpose))
        return {
            "success": True,
            "provider_used": provider_label,
            "text": text,
            "error": None,
        }

    _LAST_PROVIDER_ERROR = "All configured AI providers failed; using local fallback."
    if errors:
        _LAST_PROVIDER_ERROR = f"{_LAST_PROVIDER_ERROR} {' | '.join(errors[:3])}"
    logger.warning("All AI providers failed for %s; using fallback", _safe_purpose(purpose))
    return _fallback_result(_fallback_text(purpose), _LAST_PROVIDER_ERROR)


def optional_ai_summary(
    prompt: str,
    fallback: str,
    *,
    allow_external: bool = False,
    timeout_seconds: int | None = None,
) -> AIResult:
    if not allow_external:
        return AIResult(provider="local_fallback", mode="local_rule_based", text=fallback)

    result = generate_ai_text(prompt, purpose="summary")
    if result["success"]:
        return AIResult(provider=result.get("provider_used", "optional_ai"), mode="optional_ai", text=result["text"])
    return AIResult(
        provider="local_fallback",
        mode="local_rule_based",
        text=fallback,
        error=result.get("error") or "Gemini unavailable.",
    )


def provider_display_name(provider: str | None) -> str:
    if provider == "gemini" or provider == PROVIDER_GEMINI:
        return PROVIDER_GEMINI
    if provider == "openrouter" or provider == PROVIDER_OPENROUTER:
        return PROVIDER_OPENROUTER
    if provider == "groq" or provider == PROVIDER_GROQ:
        return PROVIDER_GROQ
    if provider == "huggingface" or provider == PROVIDER_HUGGINGFACE:
        return PROVIDER_HUGGINGFACE
    if provider == "multi" or provider == PROVIDER_MULTI:
        return PROVIDER_MULTI
    return PROVIDER_FALLBACK


def _call_provider(provider: str, prompt: str, timeout_seconds: int) -> str:
    if provider == "gemini":
        return _call_gemini(_provider_key("gemini"), prompt, _model_name("gemini"), timeout_seconds)
    if provider == "openrouter":
        return _call_openai_compatible(
            "https://openrouter.ai/api/v1/chat/completions",
            _provider_key("openrouter"),
            prompt,
            _model_name("openrouter"),
            timeout_seconds,
            provider="openrouter",
        )
    if provider == "groq":
        return _call_openai_compatible(
            "https://api.groq.com/openai/v1/chat/completions",
            _provider_key("groq"),
            prompt,
            _model_name("groq"),
            timeout_seconds,
            provider="groq",
        )
    if provider == "huggingface":
        return _call_huggingface(_provider_key("huggingface"), prompt, _model_name("huggingface"), timeout_seconds)
    raise ValueError(f"Unsupported AI provider: {provider}")


def _call_gemini(api_key: str, prompt: str, model: str, timeout_seconds: int) -> str:
    from google import genai

    del timeout_seconds
    client = genai.Client(api_key=api_key)
    try:
        response = client.models.generate_content(
            model=model,
            contents=f"{SAFE_SYSTEM_NOTE}\n\nUser request:\n{prompt}",
        )
        return getattr(response, "text", "") or ""
    finally:
        close = getattr(client, "close", None)
        if callable(close):
            close()


def _call_openai_compatible(
    endpoint: str,
    api_key: str,
    prompt: str,
    model: str,
    timeout_seconds: int,
    *,
    provider: str,
) -> str:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SAFE_SYSTEM_NOTE},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 360,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if provider == "openrouter":
        headers["X-Title"] = "CyberShield Police"
        headers["HTTP-Referer"] = "http://localhost:5173"

    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        body = json.loads(response.read().decode("utf-8") or "{}")
    choices = body.get("choices") or []
    if not choices:
        return ""
    message = choices[0].get("message") or {}
    return str(message.get("content") or "").strip()


def _call_huggingface(api_key: str, prompt: str, model: str, timeout_seconds: int) -> str:
    payload = {
        "inputs": f"{SAFE_SYSTEM_NOTE}\n\nUser request:\n{prompt}",
        "parameters": {"max_new_tokens": 260, "temperature": 0.2, "return_full_text": False},
        "options": {"wait_for_model": True},
    }
    request = urllib.request.Request(
        f"https://api-inference.huggingface.co/models/{model}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        body = json.loads(response.read().decode("utf-8") or "[]")
    if isinstance(body, list) and body:
        return str(body[0].get("generated_text") or "").strip()
    if isinstance(body, dict):
        return str(body.get("generated_text") or body.get("summary_text") or body.get("error") or "").strip()
    return ""


def _configured_provider() -> str:
    configured = os.getenv("AI_PROVIDER", "gemini").strip().lower()
    aliases = {
        "google": "gemini",
        "hf": "huggingface",
        "hugging_face": "huggingface",
        "local": "local_fallback",
        "none": "local_fallback",
        "all": "multi",
    }
    return aliases.get(configured, configured)


def _provider_candidates(configured_provider: str) -> list[str]:
    if configured_provider in {"local_fallback", ""}:
        return []
    if configured_provider == "multi":
        order = os.getenv("AI_PROVIDER_ORDER", "gemini,openrouter,groq,huggingface")
        requested = [_configured_provider_name(item) for item in order.split(",")]
    else:
        requested = [_configured_provider_name(configured_provider)]
    return [provider for provider in requested if provider in {"gemini", "openrouter", "groq", "huggingface"} and _provider_key_present(provider)]


def _configured_provider_name(provider: str) -> str:
    value = (provider or "").strip().lower()
    aliases = {"google": "gemini", "hf": "huggingface", "hugging_face": "huggingface"}
    return aliases.get(value, value)


def _provider_key(provider: str) -> str:
    env_vars = {
        "gemini": "GEMINI_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
        "groq": "GROQ_API_KEY",
        "huggingface": "HUGGINGFACE_API_KEY",
    }
    return os.getenv(env_vars.get(provider, ""), "").strip()


def _provider_key_present(provider: str) -> bool:
    return _looks_like_real_key(_provider_key(provider))


def _gemini_key_present() -> bool:
    return _provider_key_present("gemini")


def _looks_like_real_key(value: str) -> bool:
    key = (value or "").strip()
    if not key:
        return False
    lowered = key.lower()
    return not any(marker in lowered for marker in _PLACEHOLDER_MARKERS)


def _model_name(provider: str = "gemini") -> str:
    defaults = {
        "gemini": DEFAULT_MODEL,
        "openrouter": DEFAULT_OPENROUTER_MODEL,
        "groq": DEFAULT_GROQ_MODEL,
        "huggingface": DEFAULT_HUGGINGFACE_MODEL,
    }
    env_vars = {
        "gemini": "GEMINI_MODEL",
        "openrouter": "OPENROUTER_MODEL",
        "groq": "GROQ_MODEL",
        "huggingface": "HUGGINGFACE_MODEL",
    }
    default = defaults.get(provider, DEFAULT_MODEL)
    return os.getenv(env_vars.get(provider, "GEMINI_MODEL"), default).strip() or default


def _timeout_seconds() -> int:
    raw_value = os.getenv("AI_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS)).strip()
    try:
        value = int(raw_value)
    except ValueError:
        return DEFAULT_TIMEOUT_SECONDS
    return max(3, min(value, 60))


def _fallback_result(text: str, error: str) -> dict[str, Any]:
    return {
        "success": False,
        "provider_used": PROVIDER_FALLBACK,
        "text": text,
        "error": error,
    }


def _safe_error_detail(exc: Exception) -> str:
    value = " ".join(str(exc).split())
    for provider in ("gemini", "openrouter", "groq", "huggingface"):
        key = _provider_key(provider)
        if key:
            value = value.replace(key, "[redacted]")
    if len(value) > 180:
        value = value[:180].rsplit(" ", 1)[0]
    return f"{exc.__class__.__name__}: {value}" if value else exc.__class__.__name__


def _fallback_text(purpose: str) -> str:
    safe_purpose = _safe_purpose(purpose)
    if safe_purpose == "debug_test":
        return "Local fallback is working. Add GEMINI_API_KEY to enable Gemini responses."
    if safe_purpose == "phishing_explanation":
        return "Local scanner result is available. Gemini explanation is currently unavailable."
    if safe_purpose == "cyberdost":
        return "Local safety guidance is available. Gemini is currently unavailable."
    return "Local fallback is available. Gemini is currently unavailable."


def _clean_ai_text(text: str) -> str:
    value = " ".join((text or "").strip().split())
    if len(value) > 1400:
        value = value[:1400].rsplit(" ", 1)[0] + "."
    if _contains_unsafe_instruction(value.lower()):
        return ""
    return value


def _contains_unsafe_instruction(value: str) -> bool:
    allowed_safety_warnings = (
        "do not share your otp",
        "don't share your otp",
        "never share your otp",
        "do not share your pin",
        "don't share your pin",
        "never share your pin",
        "do not tell",
        "don't tell",
        "never tell",
        "do not send your cvv",
        "don't send your cvv",
        "never send your cvv",
    )
    direct_harmful_requests = (
        "please share your otp",
        "share your otp with me",
        "send your otp",
        "give your otp",
        "share your pin with me",
        "send your pin",
        "give your pin",
        "tell me your password",
        "send your cvv",
        "install malware",
        "build malware",
        "make phishing kit",
        "create phishing kit",
    )
    for warning in allowed_safety_warnings:
        value = value.replace(warning, "")
    return any(fragment in value for fragment in direct_harmful_requests)


def _safe_purpose(purpose: str) -> str:
    value = (purpose or "general").strip().lower()
    return "".join(char for char in value if char.isalnum() or char in {"_", "-"})[:40] or "general"


def _load_plain_env(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key and key not in os.environ:
            os.environ[key] = value.strip().strip('"').strip("'")
