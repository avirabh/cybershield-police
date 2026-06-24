from __future__ import annotations

import json
import os
import re
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


BASE_DIR = Path(__file__).resolve().parent.parent


def _database_path() -> Path:
    database_url = os.getenv("DATABASE_URL", "").strip()
    if database_url.startswith("sqlite:///"):
        raw_path = database_url.replace("sqlite:///", "", 1)
        path = Path(raw_path)
        return path if path.is_absolute() else BASE_DIR / path
    return BASE_DIR / "cybershield.db"


DB_PATH = _database_path()


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                url TEXT,
                platform TEXT,
                victim_age_group TEXT,
                amount_involved REAL,
                risk_score INTEGER NOT NULL,
                risk_level TEXT NOT NULL,
                confidence_score INTEGER NOT NULL DEFAULT 0,
                category TEXT NOT NULL,
                categories TEXT NOT NULL DEFAULT '[]',
                police_triage_priority TEXT NOT NULL DEFAULT '',
                police_triage_explanation TEXT NOT NULL DEFAULT '',
                signal_sources TEXT NOT NULL DEFAULT '[]',
                detection_mode TEXT NOT NULL DEFAULT '',
                risk_factors TEXT NOT NULL,
                citizen_explanation TEXT NOT NULL,
                police_summary TEXT NOT NULL,
                recommended_police_action TEXT NOT NULL DEFAULT '',
                recommended_citizen_action TEXT NOT NULL DEFAULT '',
                recommended_action TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        _ensure_column(conn, "cases", "confidence_score", "INTEGER NOT NULL DEFAULT 0")
        _ensure_column(conn, "cases", "categories", "TEXT NOT NULL DEFAULT '[]'")
        _ensure_column(conn, "cases", "police_triage_priority", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "cases", "police_triage_explanation", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "cases", "signal_sources", "TEXT NOT NULL DEFAULT '[]'")
        _ensure_column(conn, "cases", "detection_mode", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "cases", "recommended_police_action", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "cases", "recommended_citizen_action", "TEXT NOT NULL DEFAULT ''")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id TEXT NOT NULL,
                amount REAL NOT NULL DEFAULT 0,
                payment_method TEXT NOT NULL DEFAULT '',
                merchant_or_receiver_name TEXT NOT NULL DEFAULT '',
                receiver_upi_or_account_placeholder TEXT NOT NULL DEFAULT '',
                timestamp TEXT NOT NULL DEFAULT '',
                location_or_city TEXT NOT NULL DEFAULT '',
                transaction_note TEXT NOT NULL DEFAULT '',
                user_age_group TEXT NOT NULL DEFAULT '',
                previous_transaction_count INTEGER NOT NULL DEFAULT 0,
                is_first_time_receiver INTEGER NOT NULL DEFAULT 0,
                reported_by_user INTEGER NOT NULL DEFAULT 0,
                risk_score INTEGER NOT NULL,
                risk_level TEXT NOT NULL,
                suspected_fraud_type TEXT NOT NULL,
                risk_factors TEXT NOT NULL,
                police_triage_priority TEXT NOT NULL,
                citizen_explanation TEXT NOT NULL,
                police_summary TEXT NOT NULL,
                recommended_action TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS threat_incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id TEXT NOT NULL UNIQUE,
                location TEXT NOT NULL,
                mandal TEXT NOT NULL,
                district TEXT NOT NULL,
                state TEXT NOT NULL,
                scam_type TEXT NOT NULL,
                amount_lost REAL NOT NULL DEFAULT 0,
                payment_mode TEXT NOT NULL DEFAULT '',
                target_group TEXT NOT NULL DEFAULT '',
                incident_date TEXT NOT NULL DEFAULT '',
                risk_score INTEGER NOT NULL DEFAULT 0,
                risk_level TEXT NOT NULL DEFAULT 'Low',
                summary TEXT NOT NULL DEFAULT '',
                indicators TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS threat_indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                indicator_id TEXT NOT NULL UNIQUE,
                indicator_type TEXT NOT NULL,
                value TEXT NOT NULL,
                risk_score INTEGER NOT NULL DEFAULT 0,
                related_case_count INTEGER NOT NULL DEFAULT 0,
                linked_scam_categories TEXT NOT NULL DEFAULT '[]',
                first_seen TEXT NOT NULL DEFAULT '',
                last_seen TEXT NOT NULL DEFAULT '',
                related_locations TEXT NOT NULL DEFAULT '[]',
                related_indicators TEXT NOT NULL DEFAULT '[]',
                police_triage_priority TEXT NOT NULL DEFAULT '',
                intelligence_summary TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS case_clusters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cluster_id TEXT NOT NULL UNIQUE,
                cluster_name TEXT NOT NULL,
                suspected_fraud_pattern TEXT NOT NULL,
                risk_score INTEGER NOT NULL DEFAULT 0,
                linked_case_count INTEGER NOT NULL DEFAULT 0,
                total_amount_lost REAL NOT NULL DEFAULT 0,
                common_risk_factors TEXT NOT NULL DEFAULT '[]',
                shared_indicators TEXT NOT NULL DEFAULT '[]',
                linked_cases TEXT NOT NULL DEFAULT '[]',
                recommended_police_action TEXT NOT NULL DEFAULT '',
                evidence_summary TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                name TEXT NOT NULL,
                location TEXT NOT NULL DEFAULT '',
                age_group TEXT NOT NULL DEFAULT '',
                rank_designation TEXT NOT NULL DEFAULT '',
                police_station TEXT NOT NULL DEFAULT '',
                district TEXT NOT NULL DEFAULT '',
                badge_id_placeholder TEXT NOT NULL DEFAULT '',
                verification_document_name TEXT NOT NULL DEFAULT '',
                verification_status TEXT NOT NULL DEFAULT 'Verified',
                verification_note TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        _ensure_column(conn, "users", "location", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "users", "age_group", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "users", "rank_designation", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "users", "police_station", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "users", "district", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "users", "badge_id_placeholder", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "users", "verification_document_name", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "users", "verification_status", "TEXT NOT NULL DEFAULT 'Verified'")
        _ensure_column(conn, "users", "verification_note", "TEXT NOT NULL DEFAULT ''")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS incident_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tracking_id TEXT NOT NULL UNIQUE,
                reporter_name TEXT NOT NULL DEFAULT '',
                anonymous INTEGER NOT NULL DEFAULT 0,
                age_group TEXT NOT NULL DEFAULT '',
                contact_placeholder TEXT NOT NULL DEFAULT '',
                location TEXT NOT NULL DEFAULT '',
                category TEXT NOT NULL DEFAULT '',
                description TEXT NOT NULL DEFAULT '',
                suspicious_message TEXT NOT NULL DEFAULT '',
                suspicious_url TEXT NOT NULL DEFAULT '',
                transaction_amount REAL NOT NULL DEFAULT 0,
                payment_mode TEXT NOT NULL DEFAULT '',
                receiver_placeholder TEXT NOT NULL DEFAULT '',
                evidence_metadata TEXT NOT NULL DEFAULT '[]',
                risk_score INTEGER NOT NULL DEFAULT 0,
                risk_level TEXT NOT NULL DEFAULT 'Low',
                confidence_score INTEGER NOT NULL DEFAULT 0,
                detected_category TEXT NOT NULL DEFAULT '',
                police_triage_priority TEXT NOT NULL DEFAULT '',
                citizen_explanation TEXT NOT NULL DEFAULT '',
                police_summary TEXT NOT NULL DEFAULT '',
                recommended_citizen_action TEXT NOT NULL DEFAULT '',
                recommended_police_action TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'New',
                assigned_officer TEXT NOT NULL DEFAULT '',
                evidence_reviewed INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS case_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id INTEGER NOT NULL,
                officer_email TEXT NOT NULL DEFAULT '',
                note TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS awareness_quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL DEFAULT '',
                score INTEGER NOT NULL DEFAULT 0,
                total INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )


def _ensure_column(conn: sqlite3.Connection, table_name: str, column_name: str, column_type: str) -> None:
    existing = {
        row["name"]
        for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    }
    if column_name not in existing:
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")


def row_to_case(row: sqlite3.Row) -> dict[str, Any]:
    data = dict(row)
    data["risk_factors"] = json.loads(data.get("risk_factors") or "[]")
    content_for_matches = f"{data.get('message') or ''} {data.get('url') or ''}"
    for factor in data["risk_factors"]:
        factor["matched_patterns"] = [
            _readable_match(pattern, content_for_matches)
            for pattern in factor.get("matched_patterns", [])
        ]
    data["triggered_rules"] = data["risk_factors"]
    data["matched_patterns"] = [
        {
            "rule": factor.get("label", ""),
            "code": factor.get("code", ""),
            "pattern": pattern,
            "source": factor.get("source", ""),
        }
        for factor in data["risk_factors"]
        for pattern in factor.get("matched_patterns", [])
    ]
    data["categories"] = json.loads(data.get("categories") or "[]")
    if not data["categories"]:
        data["categories"] = [{"name": data.get("category") or "Unknown Suspicious", "score": 0, "confidence": 0}]
    data["signal_sources"] = json.loads(data.get("signal_sources") or "[]")
    if not data["signal_sources"]:
        data["signal_sources"] = _fallback_signal_sources(data)
    data["detection_mode"] = data.get("detection_mode") or _fallback_detection_mode(data)
    data["signal_summary"] = {
        "text": "text" in data["signal_sources"],
        "url": "url" in data["signal_sources"],
        "metadata": "metadata" in data["signal_sources"],
        "mode": data["detection_mode"],
    }
    data["recommended_police_action"] = data.get("recommended_police_action") or data.get("police_summary") or ""
    data["recommended_citizen_action"] = data.get("recommended_citizen_action") or data.get("recommended_action") or ""
    data["confidence_score"] = int(data.get("confidence_score") or 0)
    data["police_triage_priority"] = data.get("police_triage_priority") or _fallback_triage_priority(
        int(data.get("risk_score") or 0),
        data.get("category") or "Unknown Suspicious",
    )
    data["police_triage_explanation"] = data.get("police_triage_explanation") or _fallback_triage_explanation(
        int(data.get("risk_score") or 0),
        data.get("category") or "Unknown Suspicious",
        data["police_triage_priority"],
    )
    return data


def _readable_match(pattern: str, content: str) -> str:
    value = str(pattern or "").strip()
    if not value:
        return ""

    try:
        if value == r"within\s+\d+\s*(?:hour|hr|day|minute|min)":
            match = re.search(r"within\s+\d+\s*(?:hours?|hrs?|days?|minutes?|mins?)", content, flags=re.IGNORECASE)
            if match:
                return " ".join(match.group(0).strip().split())
        match = re.search(value, content, flags=re.IGNORECASE)
    except re.error:
        match = None
    if match:
        return " ".join(match.group(0).strip().split())

    known_labels = {
        r"within\s+\d+\s*(?:hour|hr|day|minute|min)": "deadline within a short time",
        r"final\s+warning": "final warning",
        r"\burgent\b": "urgent",
        r"\bimmediate(?:ly)?\b": "immediate action",
        r"last\s+chance": "last chance",
        r"expires?\s+(?:today|soon|in)": "expires today or soon",
        r"avoid\s+(?:block|arrest|penalty|fine)": "avoid block, arrest, penalty, or fine",
        r"do\s+not\s+delay": "do not delay",
    }
    if value in known_labels:
        return known_labels[value]

    cleaned = value
    replacements = {
        r"\b": "",
        r"\s+": " ",
        r"\s*": " ",
        r"(?:": "",
        r"\?": "",
        r"\.": ".",
    }
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)
    cleaned = cleaned.replace(")", "").replace("(", "").replace("|", " / ")
    cleaned = cleaned.replace("\\", "")
    return " ".join(cleaned.split())


def _fallback_signal_sources(data: dict[str, Any]) -> list[str]:
    sources: list[str] = []
    if (data.get("message") or "").strip():
        sources.append("text")
    if (data.get("url") or "").strip():
        sources.append("url")
    if data.get("platform") or data.get("victim_age_group") or data.get("amount_involved"):
        sources.append("metadata")
    return sources


def _fallback_detection_mode(data: dict[str, Any]) -> str:
    sources = _fallback_signal_sources(data)
    if not sources:
        return "empty_or_weak_input"
    if sources == ["text"]:
        return "text_only"
    if sources == ["url"]:
        return "url_only"
    if sources == ["metadata"]:
        return "metadata_only"
    return "hybrid_" + "_".join(sources)


def _fallback_triage_priority(score: int, category: str) -> str:
    aliases = {
        "Fake Job Offer": "Fake Job Scam",
        "Impersonation": "Impersonation Scam",
        "Suspicious Link": "Phishing",
    }
    category = aliases.get(category, category)
    immediate_categories = {
        "OTP Fraud",
        "UPI Fraud",
        "Fake KYC/Bank Alert",
        "Fake Customer Care Scam",
        "Fake Police/Legal Threat",
        "QR Code Scam",
        "Impersonation Scam",
    }
    high_attention_categories = immediate_categories | {"Phishing", "Fake Loan Scam", "Investment Scam", "Courier/Parcel Scam"}
    review_categories = high_attention_categories | {
        "Fake Job Scam",
        "Work From Home Scam",
        "Lottery/Prize Scam",
        "Unknown Suspicious",
    }

    if score >= 85 or (score >= 75 and category in immediate_categories):
        return "Critical Immediate Triage"
    if score >= 60 or (score >= 50 and category in high_attention_categories):
        return "High Priority"
    if score >= 30 or category in review_categories:
        return "Review Recommended"
    return "Low Priority"


def _fallback_triage_explanation(score: int, category: str, priority: str) -> str:
    return (
        f"{priority} was assigned from risk score {score}/100 and detected category {category}. "
        "Review the risk factors and submitted evidence before taking action."
    )


def create_case(payload: dict[str, Any], analysis: dict[str, Any]) -> dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO cases (
                message, url, platform, victim_age_group, amount_involved,
                risk_score, risk_level, confidence_score, category, categories,
                police_triage_priority, police_triage_explanation, signal_sources,
                detection_mode, risk_factors,
                citizen_explanation, police_summary, recommended_police_action,
                recommended_citizen_action, recommended_action
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.get("message") or "",
                payload.get("url") or "",
                payload.get("platform") or "",
                payload.get("victim_age_group") or "",
                payload.get("amount_involved"),
                analysis["risk_score"],
                analysis["risk_level"],
                analysis.get("confidence_score", 0),
                analysis["category"],
                json.dumps(analysis.get("categories", [])),
                analysis.get("police_triage_priority", ""),
                analysis.get("police_triage_explanation", ""),
                json.dumps(analysis.get("signal_sources", [])),
                analysis.get("detection_mode", ""),
                json.dumps(analysis["risk_factors"]),
                analysis["citizen_explanation"],
                analysis["police_summary"],
                analysis.get("recommended_police_action", ""),
                analysis.get("recommended_citizen_action", analysis.get("recommended_action", "")),
                analysis["recommended_action"],
            ),
        )
        case_id = cursor.lastrowid
        row = conn.execute("SELECT * FROM cases WHERE id = ?", (case_id,)).fetchone()
        return row_to_case(row)


def list_cases(limit: int = 100) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM cases ORDER BY datetime(created_at) DESC, id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [row_to_case(row) for row in rows]


def get_case(case_id: int) -> dict[str, Any] | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM cases WHERE id = ?", (case_id,)).fetchone()
        return row_to_case(row) if row else None


def delete_case(case_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM cases WHERE id = ?", (case_id,))
        return cursor.rowcount > 0


def clear_cases() -> int:
    with get_connection() as conn:
        deleted = conn.execute("DELETE FROM cases").rowcount
        conn.execute("DELETE FROM sqlite_sequence WHERE name = 'cases'")
        return int(deleted)


def count_cases() -> int:
    with get_connection() as conn:
        return int(conn.execute("SELECT COUNT(*) FROM cases").fetchone()[0])


def row_to_transaction(row: sqlite3.Row) -> dict[str, Any]:
    data = dict(row)
    data["risk_factors"] = json.loads(data.get("risk_factors") or "[]")
    data["is_first_time_receiver"] = bool(data.get("is_first_time_receiver"))
    data["reported_by_user"] = bool(data.get("reported_by_user"))
    data["triggered_rules"] = data["risk_factors"]
    data["matched_patterns"] = [
        {
            "rule": factor.get("label", ""),
            "code": factor.get("code", ""),
            "pattern": pattern,
            "source": factor.get("source", "transaction"),
        }
        for factor in data["risk_factors"]
        for pattern in factor.get("matched_patterns", [])
    ]
    return data


def create_transaction(payload: dict[str, Any], analysis: dict[str, Any]) -> dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO transactions (
                transaction_id, amount, payment_method, merchant_or_receiver_name,
                receiver_upi_or_account_placeholder, timestamp, location_or_city,
                transaction_note, user_age_group, previous_transaction_count,
                is_first_time_receiver, reported_by_user, risk_score, risk_level,
                suspected_fraud_type, risk_factors, police_triage_priority,
                citizen_explanation, police_summary, recommended_action
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.get("transaction_id") or "",
                payload.get("amount") or 0,
                payload.get("payment_method") or "",
                payload.get("merchant_or_receiver_name") or "",
                payload.get("receiver_upi_or_account_placeholder") or "",
                payload.get("timestamp") or "",
                payload.get("location_or_city") or "",
                payload.get("transaction_note") or "",
                payload.get("user_age_group") or "",
                int(payload.get("previous_transaction_count") or 0),
                int(bool(payload.get("is_first_time_receiver"))),
                int(bool(payload.get("reported_by_user"))),
                analysis["risk_score"],
                analysis["risk_level"],
                analysis["suspected_fraud_type"],
                json.dumps(analysis["risk_factors"]),
                analysis["police_triage_priority"],
                analysis["citizen_explanation"],
                analysis["police_summary"],
                analysis["recommended_action"],
            ),
        )
        row = conn.execute("SELECT * FROM transactions WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return row_to_transaction(row)


def list_transactions(limit: int = 100) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM transactions ORDER BY datetime(created_at) DESC, id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [row_to_transaction(row) for row in rows]


def get_transaction(transaction_db_id: int) -> dict[str, Any] | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM transactions WHERE id = ?", (transaction_db_id,)).fetchone()
        return row_to_transaction(row) if row else None


def clear_transactions() -> int:
    with get_connection() as conn:
        deleted = conn.execute("DELETE FROM transactions").rowcount
        conn.execute("DELETE FROM sqlite_sequence WHERE name = 'transactions'")
        return int(deleted)


def count_transactions() -> int:
    with get_connection() as conn:
        return int(conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0])


def row_to_threat_incident(row: sqlite3.Row) -> dict[str, Any]:
    data = dict(row)
    data["indicators"] = json.loads(data.get("indicators") or "[]")
    return data


def row_to_indicator(row: sqlite3.Row) -> dict[str, Any]:
    data = dict(row)
    data["linked_scam_categories"] = json.loads(data.get("linked_scam_categories") or "[]")
    data["related_locations"] = json.loads(data.get("related_locations") or "[]")
    data["related_indicators"] = json.loads(data.get("related_indicators") or "[]")
    return data


def row_to_case_cluster(row: sqlite3.Row) -> dict[str, Any]:
    data = dict(row)
    data["common_risk_factors"] = json.loads(data.get("common_risk_factors") or "[]")
    data["shared_indicators"] = json.loads(data.get("shared_indicators") or "[]")
    data["linked_cases"] = json.loads(data.get("linked_cases") or "[]")
    return data


def create_threat_incident(item: dict[str, Any]) -> dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT OR IGNORE INTO threat_incidents (
                incident_id, location, mandal, district, state, scam_type,
                amount_lost, payment_mode, target_group, incident_date,
                risk_score, risk_level, summary, indicators
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item.get("incident_id") or item.get("id") or "",
                item.get("location") or "",
                item.get("mandal") or "",
                item.get("district") or "Prakasam",
                item.get("state") or "Andhra Pradesh",
                item.get("scam_type") or "",
                item.get("amount_lost") or 0,
                item.get("payment_mode") or "",
                item.get("target_group") or "",
                item.get("incident_date") or "",
                item.get("risk_score") or 0,
                item.get("risk_level") or "Low",
                item.get("summary") or "",
                json.dumps(item.get("indicators") or []),
            ),
        )
        incident_id = cursor.lastrowid
        if not incident_id:
            row = conn.execute(
                "SELECT * FROM threat_incidents WHERE incident_id = ?",
                (item.get("incident_id") or item.get("id") or "",),
            ).fetchone()
        else:
            row = conn.execute("SELECT * FROM threat_incidents WHERE id = ?", (incident_id,)).fetchone()
        return row_to_threat_incident(row)


def create_threat_indicator(item: dict[str, Any]) -> dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT OR IGNORE INTO threat_indicators (
                indicator_id, indicator_type, value, risk_score, related_case_count,
                linked_scam_categories, first_seen, last_seen, related_locations,
                related_indicators, police_triage_priority, intelligence_summary
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item.get("indicator_id") or item.get("id") or "",
                item.get("indicator_type") or "",
                item.get("value") or "",
                item.get("risk_score") or 0,
                item.get("related_case_count") or 0,
                json.dumps(item.get("linked_scam_categories") or []),
                item.get("first_seen") or "",
                item.get("last_seen") or "",
                json.dumps(item.get("related_locations") or []),
                json.dumps(item.get("related_indicators") or []),
                item.get("police_triage_priority") or "",
                item.get("intelligence_summary") or "",
            ),
        )
        indicator_id = cursor.lastrowid
        if not indicator_id:
            row = conn.execute(
                "SELECT * FROM threat_indicators WHERE indicator_id = ?",
                (item.get("indicator_id") or item.get("id") or "",),
            ).fetchone()
        else:
            row = conn.execute("SELECT * FROM threat_indicators WHERE id = ?", (indicator_id,)).fetchone()
        return row_to_indicator(row)


def create_case_cluster(item: dict[str, Any]) -> dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT OR IGNORE INTO case_clusters (
                cluster_id, cluster_name, suspected_fraud_pattern, risk_score,
                linked_case_count, total_amount_lost, common_risk_factors,
                shared_indicators, linked_cases, recommended_police_action,
                evidence_summary
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item.get("cluster_id") or item.get("id") or "",
                item.get("cluster_name") or "",
                item.get("suspected_fraud_pattern") or "",
                item.get("risk_score") or 0,
                item.get("linked_case_count") or 0,
                item.get("total_amount_lost") or 0,
                json.dumps(item.get("common_risk_factors") or []),
                json.dumps(item.get("shared_indicators") or []),
                json.dumps(item.get("linked_cases") or []),
                item.get("recommended_police_action") or "",
                item.get("evidence_summary") or "",
            ),
        )
        cluster_row_id = cursor.lastrowid
        if not cluster_row_id:
            row = conn.execute(
                "SELECT * FROM case_clusters WHERE cluster_id = ?",
                (item.get("cluster_id") or item.get("id") or "",),
            ).fetchone()
        else:
            row = conn.execute("SELECT * FROM case_clusters WHERE id = ?", (cluster_row_id,)).fetchone()
        return row_to_case_cluster(row)


def list_threat_incidents(limit: int = 10000) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM threat_incidents ORDER BY incident_date DESC, id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [row_to_threat_incident(row) for row in rows]


def list_threat_indicators(limit: int = 10000) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM threat_indicators ORDER BY risk_score DESC, related_case_count DESC, id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [row_to_indicator(row) for row in rows]


def search_threat_indicators(query: str, limit: int = 25) -> list[dict[str, Any]]:
    value = f"%{str(query or '').strip().lower()}%"
    if value == "%%":
        return list_threat_indicators(limit=limit)
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM threat_indicators
            WHERE lower(value) LIKE ?
               OR lower(indicator_type) LIKE ?
               OR lower(linked_scam_categories) LIKE ?
               OR lower(related_locations) LIKE ?
               OR lower(related_indicators) LIKE ?
               OR lower(intelligence_summary) LIKE ?
            ORDER BY risk_score DESC, related_case_count DESC, id DESC
            LIMIT ?
            """,
            (value, value, value, value, value, value, limit),
        ).fetchall()
        return [row_to_indicator(row) for row in rows]


def list_case_clusters(limit: int = 10000) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM case_clusters ORDER BY risk_score DESC, total_amount_lost DESC, id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [row_to_case_cluster(row) for row in rows]


def get_case_cluster(cluster_id: str) -> dict[str, Any] | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM case_clusters WHERE cluster_id = ? OR id = ?",
            (cluster_id, int(cluster_id) if str(cluster_id).isdigit() else -1),
        ).fetchone()
        return row_to_case_cluster(row) if row else None


def clear_threat_intel() -> dict[str, int]:
    with get_connection() as conn:
        incidents = conn.execute("DELETE FROM threat_incidents").rowcount
        indicators = conn.execute("DELETE FROM threat_indicators").rowcount
        clusters = conn.execute("DELETE FROM case_clusters").rowcount
        conn.execute("DELETE FROM sqlite_sequence WHERE name IN ('threat_incidents', 'threat_indicators', 'case_clusters')")
        return {
            "threat_incidents_deleted": int(incidents),
            "threat_indicators_deleted": int(indicators),
            "case_clusters_deleted": int(clusters),
        }


def count_threat_incidents() -> int:
    with get_connection() as conn:
        return int(conn.execute("SELECT COUNT(*) FROM threat_incidents").fetchone()[0])


def count_threat_indicators() -> int:
    with get_connection() as conn:
        return int(conn.execute("SELECT COUNT(*) FROM threat_indicators").fetchone()[0])


def count_case_clusters() -> int:
    with get_connection() as conn:
        return int(conn.execute("SELECT COUNT(*) FROM case_clusters").fetchone()[0])


DEMO_USERS = [
    {
        "email": "citizen@example.com",
        "password": "citizen123",
        "role": "Citizen",
        "name": "Demo Citizen",
        "location": "Ongole",
        "age_group": "Adult",
        "verification_status": "Verified",
    },
    {
        "email": "officer@example.com",
        "password": "officer123",
        "role": "Police Officer",
        "name": "Demo Officer",
        "rank_designation": "Sub Inspector",
        "police_station": "Ongole Cyber Desk",
        "district": "Prakasam",
        "badge_id_placeholder": "DEMO-BADGE-001",
        "verification_status": "Verified",
    },
    {
        "email": "admin@example.com",
        "password": "admin123",
        "role": "Admin/SP",
        "name": "Demo Admin SP",
        "rank_designation": "Admin/SP",
        "police_station": "District Command Demo Unit",
        "district": "Prakasam",
        "badge_id_placeholder": "DEMO-ADMIN-001",
        "verification_status": "Verified",
    },
]


def seed_demo_users() -> int:
    added = 0
    with get_connection() as conn:
        for user in DEMO_USERS:
            cursor = conn.execute(
                """
                INSERT OR IGNORE INTO users (
                    email, password, role, name, location, age_group,
                    rank_designation, police_station, district, badge_id_placeholder,
                    verification_status, verification_note
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user["email"],
                    user["password"],
                    user["role"],
                    user["name"],
                    user.get("location", ""),
                    user.get("age_group", ""),
                    user.get("rank_designation", ""),
                    user.get("police_station", ""),
                    user.get("district", ""),
                    user.get("badge_id_placeholder", ""),
                    user.get("verification_status", "Verified"),
                    "Seeded demo account",
                ),
            )
            added += int(cursor.rowcount > 0)
            conn.execute(
                """
                UPDATE users
                SET verification_status = ?, verification_note = ?
                WHERE lower(email) = lower(?)
                """,
                (user.get("verification_status", "Verified"), "Seeded demo account", user["email"]),
            )
    return added


def row_to_user(row: sqlite3.Row) -> dict[str, Any]:
    data = dict(row)
    data.pop("password", None)
    data["is_verified"] = data.get("verification_status") == "Verified"
    return data


def authenticate_user(email: str, password: str) -> dict[str, Any] | None:
    seed_demo_users()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE lower(email) = lower(?) AND password = ?",
            (email, password),
        ).fetchone()
        return row_to_user(row) if row else None


def get_user_by_email(email: str) -> dict[str, Any] | None:
    seed_demo_users()
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM users WHERE lower(email) = lower(?)", (email,)).fetchone()
        return row_to_user(row) if row else None


def create_citizen_user(payload: dict[str, Any]) -> dict[str, Any]:
    with get_connection() as conn:
        try:
            cursor = conn.execute(
                """
                INSERT INTO users (
                    email, password, role, name, location, age_group,
                    verification_status, verification_note
                )
                VALUES (?, ?, 'Citizen', ?, ?, ?, 'Verified', 'Citizen demo registration')
                """,
                (
                    payload.get("email", "").strip().lower(),
                    payload.get("password", ""),
                    payload.get("name", "").strip(),
                    payload.get("location", "").strip(),
                    payload.get("age_group", "").strip(),
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise ValueError("An account with this email already exists.") from exc
        row = conn.execute("SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return row_to_user(row)


def create_police_user(payload: dict[str, Any]) -> dict[str, Any]:
    verification_code = str(payload.get("verification_code") or "").strip()
    status = "Verified" if verification_code == "PRAKASAM-POLICE-DEMO" else "Pending Verification"
    note = (
        "Auto-verified with demo verification code"
        if status == "Verified"
        else "Pending Admin/SP review. No real police verification is performed."
    )
    with get_connection() as conn:
        try:
            cursor = conn.execute(
                """
                INSERT INTO users (
                    email, password, role, name, rank_designation, police_station,
                    district, badge_id_placeholder, verification_document_name,
                    verification_status, verification_note
                )
                VALUES (?, ?, 'Police Officer', ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload.get("email", "").strip().lower(),
                    payload.get("password", ""),
                    payload.get("name", "").strip(),
                    payload.get("rank_designation", "").strip(),
                    payload.get("police_station", "").strip(),
                    payload.get("district", "").strip(),
                    payload.get("badge_id_placeholder", "").strip(),
                    payload.get("verification_document_name", "").strip(),
                    status,
                    note,
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise ValueError("An account with this email already exists.") from exc
        row = conn.execute("SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return row_to_user(row)


def list_police_verification_requests() -> list[dict[str, Any]]:
    seed_demo_users()
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM users
            WHERE role = 'Police Officer'
            ORDER BY
                CASE verification_status
                    WHEN 'Pending Verification' THEN 0
                    WHEN 'Verified' THEN 1
                    ELSE 2
                END,
                datetime(created_at) DESC,
                id DESC
            """
        ).fetchall()
        return [row_to_user(row) for row in rows]


def update_police_verification(user_id: int, status: str, note: str = "") -> dict[str, Any] | None:
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE users
            SET verification_status = ?, verification_note = ?
            WHERE id = ? AND role = 'Police Officer'
            """,
            (status, note, user_id),
        )
        row = conn.execute("SELECT * FROM users WHERE id = ? AND role = 'Police Officer'", (user_id,)).fetchone()
        return row_to_user(row) if row else None


def _incident_notes(conn: sqlite3.Connection, report_id: int) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT * FROM case_notes WHERE report_id = ? ORDER BY datetime(created_at) DESC, id DESC",
        (report_id,),
    ).fetchall()
    return [dict(row) for row in rows]


def row_to_incident_report(row: sqlite3.Row, include_notes: bool = True) -> dict[str, Any]:
    data = dict(row)
    data["anonymous"] = bool(data.get("anonymous"))
    data["evidence_reviewed"] = bool(data.get("evidence_reviewed"))
    data["evidence_metadata"] = json.loads(data.get("evidence_metadata") or "[]")
    if include_notes:
        with get_connection() as conn:
            data["notes"] = _incident_notes(conn, int(data["id"]))
    else:
        data["notes"] = []
    return data


def create_incident_report(payload: dict[str, Any], analysis: dict[str, Any]) -> dict[str, Any]:
    with get_connection() as conn:
        next_id = int(conn.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM incident_reports").fetchone()[0])
        tracking_id = f"CSP-PRK-{next_id:05d}"
        cursor = conn.execute(
            """
            INSERT INTO incident_reports (
                tracking_id, reporter_name, anonymous, age_group, contact_placeholder,
                location, category, description, suspicious_message, suspicious_url,
                transaction_amount, payment_mode, receiver_placeholder, evidence_metadata,
                risk_score, risk_level, confidence_score, detected_category,
                police_triage_priority, citizen_explanation, police_summary,
                recommended_citizen_action, recommended_police_action, status,
                assigned_officer, evidence_reviewed
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                tracking_id,
                payload.get("reporter_name") or "",
                int(bool(payload.get("anonymous"))),
                payload.get("age_group") or "",
                payload.get("contact_placeholder") or "",
                payload.get("location") or "",
                payload.get("category") or "",
                payload.get("description") or "",
                payload.get("suspicious_message") or "",
                payload.get("suspicious_url") or "",
                payload.get("transaction_amount") or 0,
                payload.get("payment_mode") or "",
                payload.get("receiver_placeholder") or "",
                json.dumps(payload.get("evidence_metadata") or []),
                analysis.get("risk_score", 0),
                analysis.get("risk_level", "Low"),
                analysis.get("confidence_score", 0),
                analysis.get("category", "Unknown Suspicious"),
                analysis.get("police_triage_priority", "Review Recommended"),
                analysis.get("citizen_explanation", ""),
                analysis.get("police_summary", ""),
                analysis.get("recommended_citizen_action", analysis.get("recommended_action", "")),
                analysis.get("recommended_police_action", ""),
                payload.get("status") or "New",
                payload.get("assigned_officer") or "",
                int(bool(payload.get("evidence_reviewed"))),
            ),
        )
        row = conn.execute("SELECT * FROM incident_reports WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return row_to_incident_report(row)


def list_incident_reports(limit: int = 1000) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM incident_reports ORDER BY datetime(created_at) DESC, id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [row_to_incident_report(row, include_notes=False) for row in rows]


def get_incident_report(report_id: int) -> dict[str, Any] | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM incident_reports WHERE id = ?", (report_id,)).fetchone()
        return row_to_incident_report(row) if row else None


def assign_incident_report(report_id: int, officer_email: str) -> dict[str, Any] | None:
    with get_connection() as conn:
        conn.execute("UPDATE incident_reports SET assigned_officer = ? WHERE id = ?", (officer_email, report_id))
        row = conn.execute("SELECT * FROM incident_reports WHERE id = ?", (report_id,)).fetchone()
        return row_to_incident_report(row) if row else None


def update_incident_status(report_id: int, status: str, evidence_reviewed: bool | None = None) -> dict[str, Any] | None:
    with get_connection() as conn:
        if evidence_reviewed is None:
            conn.execute("UPDATE incident_reports SET status = ? WHERE id = ?", (status, report_id))
        else:
            conn.execute(
                "UPDATE incident_reports SET status = ?, evidence_reviewed = ? WHERE id = ?",
                (status, int(bool(evidence_reviewed)), report_id),
            )
        row = conn.execute("SELECT * FROM incident_reports WHERE id = ?", (report_id,)).fetchone()
        return row_to_incident_report(row) if row else None


def add_incident_note(report_id: int, officer_email: str, note: str) -> dict[str, Any] | None:
    with get_connection() as conn:
        exists = conn.execute("SELECT id FROM incident_reports WHERE id = ?", (report_id,)).fetchone()
        if not exists:
            return None
        conn.execute(
            "INSERT INTO case_notes (report_id, officer_email, note) VALUES (?, ?, ?)",
            (report_id, officer_email, note),
        )
        row = conn.execute("SELECT * FROM incident_reports WHERE id = ?", (report_id,)).fetchone()
        return row_to_incident_report(row)


def save_quiz_result(user_email: str, score: int, total: int) -> dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO awareness_quiz_results (user_email, score, total) VALUES (?, ?, ?)",
            (user_email, score, total),
        )
        row = conn.execute("SELECT * FROM awareness_quiz_results WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return dict(row)


def clear_incident_reports() -> dict[str, int]:
    with get_connection() as conn:
        notes = conn.execute("DELETE FROM case_notes").rowcount
        reports = conn.execute("DELETE FROM incident_reports").rowcount
        quiz = conn.execute("DELETE FROM awareness_quiz_results").rowcount
        conn.execute("DELETE FROM sqlite_sequence WHERE name IN ('incident_reports', 'case_notes', 'awareness_quiz_results')")
        return {
            "incident_reports_deleted": int(reports),
            "case_notes_deleted": int(notes),
            "quiz_results_deleted": int(quiz),
        }


def count_incident_reports() -> int:
    with get_connection() as conn:
        return int(conn.execute("SELECT COUNT(*) FROM incident_reports").fetchone()[0])
