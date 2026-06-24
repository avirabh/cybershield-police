from __future__ import annotations

import json
import unittest
from collections import Counter
from pathlib import Path

from app.scam_detector import analyze_scam


DATASET_PATH = Path(__file__).resolve().parents[1] / "data" / "synthetic_scam_dataset.json"


class ScamDetectorDatasetTest(unittest.TestCase):
    summary: dict[str, float | int] = {}

    @classmethod
    def setUpClass(cls) -> None:
        with DATASET_PATH.open("r", encoding="utf-8") as dataset_file:
            cls.dataset = json.load(dataset_file)

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.summary:
            print(
                "\nDemo accuracy summary: "
                f"{cls.summary['related_accuracy']:.1f}% related-category accuracy, "
                f"{cls.summary['primary_accuracy']:.1f}% primary-category accuracy, "
                f"{cls.summary['score_quality']:.1f}% score-range quality, "
                f"{cls.summary['safe_low_score']:.1f}% safe-low-score rate "
                f"across {cls.summary['total']} examples."
            )

    def test_dataset_has_300_safe_fictional_examples(self) -> None:
        self.assertEqual(len(self.dataset), 300)
        required = {
            "id",
            "message",
            "optional_url",
            "category",
            "risk_level",
            "expected_score_range",
            "platform",
            "target_group",
            "risk_factors",
            "explanation",
        }
        ids = set()
        for item in self.dataset:
            self.assertTrue(required.issubset(item), item)
            self.assertNotIn(item["id"], ids)
            ids.add(item["id"])
            self.assertIn("FAKE DEMO", item["message"])
            self.assertFalse("@" in item["message"])
            self.assertNotRegex(item["message"], r"\b[6-9][0-9]{9}\b")
            if item["optional_url"]:
                self.assertTrue(item["optional_url"].endswith(".demo.test/" + item["optional_url"].rsplit("/", 1)[-1]))

        categories = Counter(item["category"] for item in self.dataset)
        self.assertEqual(categories["Likely Safe"], 20)
        for category, count in categories.items():
            if category != "Likely Safe":
                self.assertEqual(count, 20, category)

    def test_dataset_detection_quality(self) -> None:
        total = len(self.dataset)
        scam_total = 0
        primary_hits = 0
        related_hits = 0
        score_hits = 0
        safe_total = 0
        safe_low = 0
        category_misses: list[str] = []

        for item in self.dataset:
            metadata = {
                "platform": item["platform"],
                "victim_age_group": item["target_group"],
                "target_group": item["target_group"],
                "amount_involved": item.get("amount_involved", 0),
            }
            result = analyze_scam(item["message"], item["optional_url"], metadata)
            expected = item["category"]
            expected_min, expected_max = item["expected_score_range"]
            score = result["risk_score"]
            detected_categories = [category["name"] for category in result.get("categories", [])]

            self.assertIn("risk_score", result)
            self.assertIn("confidence_score", result)
            self.assertIn("police_triage_priority", result)
            self.assertIn("matched_patterns", result)
            self.assertIn("detection_mode", result)
            self.assertTrue(result["signal_sources"])

            if expected == "Likely Safe":
                safe_total += 1
                if score <= expected_max and result["category"] == "Likely Safe":
                    safe_low += 1
                continue

            scam_total += 1
            if result["category"] == expected:
                primary_hits += 1
            if expected in detected_categories:
                related_hits += 1
            else:
                category_misses.append(f"{item['id']} expected {expected}, got {result['category']}")
            if expected_min <= score <= expected_max:
                score_hits += 1

        type(self).summary = {
            "total": total,
            "primary_accuracy": primary_hits / scam_total * 100,
            "related_accuracy": related_hits / scam_total * 100,
            "score_quality": score_hits / scam_total * 100,
            "safe_low_score": safe_low / safe_total * 100,
        }

        self.assertGreaterEqual(self.summary["related_accuracy"], 85.0, category_misses[:10])
        self.assertGreaterEqual(self.summary["score_quality"], 90.0)
        self.assertGreaterEqual(self.summary["safe_low_score"], 90.0)

    def test_text_url_metadata_and_empty_modes(self) -> None:
        text_only = analyze_scam(
            "FAKE DEMO TEST: Demo Bank officer asks for OTP 000111 immediately to stop account block.",
            "",
            {},
        )
        self.assertEqual(text_only["category"], "OTP Fraud")
        self.assertIn("text", text_only["signal_sources"])
        self.assertNotIn("url", text_only["signal_sources"])
        self.assertGreaterEqual(text_only["risk_score"], 60)

        url_only = analyze_scam("", "https://secure-bank-verify.demo.test/login", {})
        self.assertEqual(url_only["category"], "Phishing")
        self.assertEqual(url_only["detection_mode"], "url_only")
        self.assertGreaterEqual(url_only["risk_score"], 30)

        metadata_only = analyze_scam(
            "",
            "",
            {"platform": "WhatsApp", "victim_age_group": "Senior Citizen", "amount_involved": 150000},
        )
        self.assertEqual(metadata_only["detection_mode"], "metadata_only")
        self.assertEqual(metadata_only["category"], "Unknown Suspicious")
        self.assertGreaterEqual(metadata_only["risk_score"], 20)

        empty = analyze_scam("", "", {})
        self.assertEqual(empty["detection_mode"], "empty_or_weak_input")
        self.assertEqual(empty["category"], "Likely Safe")
        self.assertEqual(empty["risk_score"], 0)

    def test_multilingual_keyword_detection(self) -> None:
        examples = [
            ("FAKE DEMO: आपका खाता ब्लॉक होगा। ओटीपी और पिन बताएं।", "OTP Fraud"),
            ("FAKE DEMO: మీ అకౌంట్ బ్లాక్ అవుతుంది. ఓటీపీ మరియు పిన్ చెప్పండి.", "OTP Fraud"),
            ("FAKE DEMO: আপনার অ্যাকাউন্ট ব্লক হবে। ওটিপি এবং পিন দিন।", "OTP Fraud"),
            ("FAKE DEMO: रिफंड पाने के लिए यूपीआई पिन डालें और क्यूआर स्कैन करें।", "UPI Fraud"),
        ]

        for message, expected_category in examples:
            with self.subTest(message=message):
                result = analyze_scam(message, "", {"platform": "WhatsApp"})
                detected_categories = [category["name"] for category in result.get("categories", [])]
                self.assertGreaterEqual(result["risk_score"], 50)
                self.assertIn(expected_category, detected_categories)

    def test_official_result_and_notice_messages_are_not_phishing(self) -> None:
        safe_examples = [
            (
                "CISCE results are available. Students may check the official website https://cisce.org for updates.",
                "https://cisce.org/",
            ),
            (
                "ICSE result declared. Check official website https://results.cisce.org for marksheet updates.",
                "https://results.cisce.org/",
            ),
            (
                "School meeting notice: parents meeting is scheduled tomorrow at 10 AM in the auditorium.",
                "",
            ),
            (
                "Electricity bill has been generated and is available in the official app. No urgent action is required.",
                "",
            ),
            (
                "Your bank statement is now available in the official app for monthly review.",
                "",
            ),
        ]

        for message, url in safe_examples:
            with self.subTest(message=message):
                result = analyze_scam(message, url, {"platform": "SMS", "victim_age_group": "Student"})
                self.assertLessEqual(result["risk_score"], 25)
                self.assertEqual(result["risk_level"], "Low")
                self.assertEqual(result["category"], "Likely Safe")
                self.assertEqual(result["police_triage_priority"], "Low Priority")
                self.assertNotIn("Phishing", [category["name"] for category in result.get("categories", [])])

    def test_result_lookalikes_and_private_data_requests_still_flag(self) -> None:
        suspicious_examples = [
            (
                "CISCE result declared. Check marksheet at https://cisce-results-update.demo.test/result now.",
                "https://cisce-results-update.demo.test/result",
            ),
            (
                "CISCE result blocked. Pay Rs 499 processing fee at https://cisce-result-pay.demo.test to release marksheet.",
                "https://cisce-result-pay.demo.test",
            ),
            (
                "Download CISCE certificate now. Enter OTP to verify student certificate at https://certificate-cisce.demo.test",
                "https://certificate-cisce.demo.test",
            ),
            (
                "DigiLocker CISCE certificate update: share Aadhaar OTP now at https://digilocker-cisce.demo.test",
                "https://digilocker-cisce.demo.test",
            ),
        ]

        for message, url in suspicious_examples:
            with self.subTest(message=message):
                result = analyze_scam(message, url, {"platform": "SMS", "victim_age_group": "Student"})
                self.assertGreaterEqual(result["risk_score"], 50)
                self.assertNotEqual(result["category"], "Likely Safe")
                self.assertIn(result["police_triage_priority"], {"High Priority", "Critical Immediate Triage"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
