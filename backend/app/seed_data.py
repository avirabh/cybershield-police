from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.database import (
    clear_cases,
    clear_incident_reports,
    clear_threat_intel,
    clear_transactions,
    create_case,
    create_case_cluster,
    create_incident_report,
    create_threat_incident,
    create_threat_indicator,
    create_transaction,
    list_case_clusters,
    list_cases,
    list_incident_reports,
    list_threat_incidents,
    list_threat_indicators,
    list_transactions,
    seed_demo_users,
)
from app.scam_detector import analyze_scam
from app.transaction_detector import analyze_transaction


DATASET_PATH = Path(__file__).resolve().parent / "data" / "synthetic_scam_dataset.json"
TRANSACTION_DATASET_PATH = Path(__file__).resolve().parent / "data" / "synthetic_transaction_dataset.json"
THREAT_INCIDENTS_PATH = Path(__file__).resolve().parent / "data" / "synthetic_threat_incidents.json"
INDICATORS_PATH = Path(__file__).resolve().parent / "data" / "synthetic_indicators.json"
CLUSTERS_PATH = Path(__file__).resolve().parent / "data" / "synthetic_case_clusters.json"


def load_synthetic_dataset() -> list[dict[str, Any]]:
    with DATASET_PATH.open("r", encoding="utf-8") as dataset_file:
        return json.load(dataset_file)


def load_synthetic_transaction_dataset() -> list[dict[str, Any]]:
    with TRANSACTION_DATASET_PATH.open("r", encoding="utf-8") as dataset_file:
        return json.load(dataset_file)


def load_synthetic_threat_incidents() -> list[dict[str, Any]]:
    with THREAT_INCIDENTS_PATH.open("r", encoding="utf-8") as dataset_file:
        return json.load(dataset_file)


def load_synthetic_indicators() -> list[dict[str, Any]]:
    with INDICATORS_PATH.open("r", encoding="utf-8") as dataset_file:
        return json.load(dataset_file)


def load_synthetic_case_clusters() -> list[dict[str, Any]]:
    with CLUSTERS_PATH.open("r", encoding="utf-8") as dataset_file:
        return json.load(dataset_file)


def _payload_from_dataset_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "message": item.get("message") or "",
        "url": item.get("optional_url") or "",
        "platform": item.get("platform") or "",
        "victim_age_group": item.get("target_group") or "",
        "amount_involved": item.get("amount_involved", 0),
    }


def _create_demo_case(item: dict[str, Any]) -> None:
    payload = _payload_from_dataset_item(item)
    metadata = {
        "platform": payload.get("platform"),
        "victim_age_group": payload.get("victim_age_group"),
        "target_group": payload.get("victim_age_group"),
        "amount_involved": payload.get("amount_involved"),
    }
    analysis = analyze_scam(payload["message"], payload.get("url"), metadata)
    create_case(payload, analysis)


def _transaction_payload_from_dataset_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "transaction_id": item.get("id") or "",
        "amount": item.get("amount") or 0,
        "payment_method": item.get("payment_method") or "",
        "merchant_or_receiver_name": item.get("receiver_name") or "",
        "receiver_upi_or_account_placeholder": item.get("receiver_placeholder") or "",
        "timestamp": item.get("timestamp") or "",
        "location_or_city": item.get("city") or "",
        "transaction_note": item.get("note") or "",
        "user_age_group": item.get("user_age_group") or "",
        "previous_transaction_count": item.get("previous_transaction_count", 0),
        "is_first_time_receiver": item.get("is_first_time_receiver", False),
        "reported_by_user": item.get("reported_by_user", False),
    }


def _create_demo_transaction(item: dict[str, Any]) -> None:
    payload = _transaction_payload_from_dataset_item(item)
    analysis = analyze_transaction(payload)
    create_transaction(payload, analysis)


def seed_demo_data(reset: bool = False) -> dict[str, int]:
    dataset = load_synthetic_dataset()
    transaction_dataset = load_synthetic_transaction_dataset()
    incident_dataset = load_synthetic_threat_incidents()
    indicator_dataset = load_synthetic_indicators()
    cluster_dataset = load_synthetic_case_clusters()
    if reset:
        deleted = clear_cases()
        transactions_deleted = clear_transactions()
        threat_deleted = clear_threat_intel()
        report_deleted = clear_incident_reports()
        existing_messages: set[str] = set()
        existing_transaction_ids: set[str] = set()
        existing_incident_ids: set[str] = set()
        existing_indicator_ids: set[str] = set()
        existing_cluster_ids: set[str] = set()
        existing_report_descriptions: set[str] = set()
    else:
        deleted = 0
        transactions_deleted = 0
        threat_deleted = {
            "threat_incidents_deleted": 0,
            "threat_indicators_deleted": 0,
            "case_clusters_deleted": 0,
        }
        report_deleted = {
            "incident_reports_deleted": 0,
            "case_notes_deleted": 0,
            "quiz_results_deleted": 0,
        }
        existing_messages = {case["message"] for case in list_cases(limit=1000)}
        existing_transaction_ids = {
            transaction["transaction_id"] for transaction in list_transactions(limit=10000)
        }
        existing_incident_ids = {incident["incident_id"] for incident in list_threat_incidents(limit=10000)}
        existing_indicator_ids = {indicator["indicator_id"] for indicator in list_threat_indicators(limit=10000)}
        existing_cluster_ids = {cluster["cluster_id"] for cluster in list_case_clusters(limit=10000)}
        existing_report_descriptions = {report["description"] for report in list_incident_reports(limit=10000)}

    added = 0
    for item in dataset:
        message = item.get("message") or ""
        if message in existing_messages:
            continue
        _create_demo_case(item)
        added += 1

    transactions_added = 0
    for item in transaction_dataset:
        transaction_id = item.get("id") or ""
        if transaction_id in existing_transaction_ids:
            continue
        _create_demo_transaction(item)
        transactions_added += 1

    threat_incidents_added = 0
    for item in incident_dataset:
        incident_id = item.get("incident_id") or item.get("id") or ""
        if incident_id in existing_incident_ids:
            continue
        create_threat_incident(item)
        threat_incidents_added += 1

    indicators_added = 0
    for item in indicator_dataset:
        indicator_id = item.get("indicator_id") or item.get("id") or ""
        if indicator_id in existing_indicator_ids:
            continue
        create_threat_indicator(item)
        indicators_added += 1

    clusters_added = 0
    for item in cluster_dataset:
        cluster_id = item.get("cluster_id") or item.get("id") or ""
        if cluster_id in existing_cluster_ids:
            continue
        create_case_cluster(item)
        clusters_added += 1

    users_added = seed_demo_users()
    reports_added = 0
    report_locations = ["Ongole", "Chirala", "Markapur", "Kandukur", "Darsi", "Podili"]
    for index, item in enumerate(dataset[:12], start=1):
        description = f"Demo citizen report based on {item.get('category')} pattern {index}."
        if description in existing_report_descriptions:
            continue
        payload = {
            "reporter_name": "Anonymous Demo Citizen" if index % 3 == 0 else "Demo Citizen",
            "anonymous": index % 3 == 0,
            "age_group": item.get("target_group") or "Adult",
            "contact_placeholder": f"CONTACT-DEMO-{index:03d}",
            "location": report_locations[index % len(report_locations)],
            "category": item.get("category") or "Other",
            "description": description,
            "suspicious_message": item.get("message") or "",
            "suspicious_url": item.get("optional_url") or "",
            "transaction_amount": item.get("amount_involved", 0),
            "payment_mode": "UPI" if index % 2 else "bank transfer",
            "receiver_placeholder": f"RECEIVER-DEMO-{index:03d}",
            "evidence_metadata": [{"filename": f"demo-evidence-{index:03d}.png", "type": "image/png", "note": "Synthetic metadata only"}],
            "assigned_officer": "officer@example.com" if index % 2 == 0 else "",
            "status": "Under Review" if index % 2 == 0 else "New",
        }
        analysis = analyze_scam(payload["suspicious_message"], payload["suspicious_url"], {
            "platform": item.get("platform"),
            "victim_age_group": item.get("target_group"),
            "amount_involved": item.get("amount_involved", 0),
        })
        create_incident_report(payload, analysis)
        reports_added += 1

    return {
        "dataset_size": len(dataset),
        "added": added,
        "deleted": deleted,
        "transaction_dataset_size": len(transaction_dataset),
        "transactions_added": transactions_added,
        "transactions_deleted": transactions_deleted,
        "threat_incident_dataset_size": len(incident_dataset),
        "threat_incidents_added": threat_incidents_added,
        "threat_incidents_deleted": threat_deleted["threat_incidents_deleted"],
        "indicator_dataset_size": len(indicator_dataset),
        "indicators_added": indicators_added,
        "indicators_deleted": threat_deleted["threat_indicators_deleted"],
        "cluster_dataset_size": len(cluster_dataset),
        "clusters_added": clusters_added,
        "clusters_deleted": threat_deleted["case_clusters_deleted"],
        "users_added": users_added,
        "incident_reports_added": reports_added,
        "incident_reports_deleted": report_deleted["incident_reports_deleted"],
    }


def reset_demo_data() -> dict[str, int]:
    return seed_demo_data(reset=True)
