from __future__ import annotations

import argparse
import sys

from app.database import count_case_clusters, count_cases, count_incident_reports, count_threat_incidents, count_threat_indicators, count_transactions, init_db
from app.seed_data import reset_demo_data, seed_demo_data


def main() -> int:
    parser = argparse.ArgumentParser(description="Load CyberShield Police synthetic demo cases.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete existing cases and transactions before loading the synthetic demo datasets.",
    )
    args = parser.parse_args()

    init_db()
    result = reset_demo_data() if args.reset else seed_demo_data(reset=False)
    total = count_cases()
    transaction_total = count_transactions()
    threat_incident_total = count_threat_incidents()
    indicator_total = count_threat_indicators()
    cluster_total = count_case_clusters()
    report_total = count_incident_reports()

    print("CyberShield Police demo data loader")
    print(f"Scam message dataset size: {result['dataset_size']}")
    print(f"Scam cases added: {result['added']}")
    print(f"Scam cases deleted: {result['deleted']}")
    print(f"Total cases in database: {total}")
    print(f"Transaction dataset size: {result['transaction_dataset_size']}")
    print(f"Transactions added: {result['transactions_added']}")
    print(f"Transactions deleted: {result['transactions_deleted']}")
    print(f"Total transactions in database: {transaction_total}")
    print(f"Threat incident dataset size: {result['threat_incident_dataset_size']}")
    print(f"Threat incidents added: {result['threat_incidents_added']}")
    print(f"Threat incidents deleted: {result['threat_incidents_deleted']}")
    print(f"Total threat incidents in database: {threat_incident_total}")
    print(f"Indicator dataset size: {result['indicator_dataset_size']}")
    print(f"Indicators added: {result['indicators_added']}")
    print(f"Indicators deleted: {result['indicators_deleted']}")
    print(f"Total indicators in database: {indicator_total}")
    print(f"Cluster dataset size: {result['cluster_dataset_size']}")
    print(f"Clusters added: {result['clusters_added']}")
    print(f"Clusters deleted: {result['clusters_deleted']}")
    print(f"Total clusters in database: {cluster_total}")
    print(f"Demo users added: {result['users_added']}")
    print(f"Incident reports added: {result['incident_reports_added']}")
    print(f"Incident reports deleted: {result['incident_reports_deleted']}")
    print(f"Total incident reports in database: {report_total}")
    print("All demo cases and transactions are fictional and use placeholders only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
