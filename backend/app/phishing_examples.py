from __future__ import annotations

import json
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any


PHISHING_DATASET_PATH = Path(__file__).resolve().parent / "data" / "synthetic_phishing_dataset.json"


@lru_cache(maxsize=1)
def load_phishing_examples() -> list[dict[str, Any]]:
    with PHISHING_DATASET_PATH.open("r", encoding="utf-8") as dataset_file:
        return json.load(dataset_file)


def phishing_dataset_summary() -> dict[str, Any]:
    examples = load_phishing_examples()
    categories = Counter(item.get("category") or "Unknown" for item in examples)
    platforms = Counter(item.get("platform") or "Unknown" for item in examples)
    risk_levels = Counter(item.get("risk_level") or "Unknown" for item in examples)
    return {
        "example_count": len(examples),
        "category_distribution": dict(sorted(categories.items())),
        "platform_distribution": dict(sorted(platforms.items())),
        "risk_level_distribution": dict(sorted(risk_levels.items())),
    }
