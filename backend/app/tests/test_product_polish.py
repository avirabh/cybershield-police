from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from app.main import (
    AITestRequest,
    ChatbotRequest,
    IncidentReportRequest,
    PhishingScanRequest,
    ScreenshotAnalyzeRequest,
    ai_status,
    ai_test,
    chatbot_message,
    hotspots,
    phishing_scan,
    screenshot_scan,
    startup,
    submit_report,
)
from app.phishing_examples import load_phishing_examples
from app.scam_detector import analyze_scam


PROJECT_ROOT = Path(__file__).resolve().parents[3]
FRONTEND_SRC = PROJECT_ROOT / "frontend" / "src" / "pages"


class ProductPolishTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        startup()

    def test_phishing_dataset_has_many_synthetic_examples(self) -> None:
        examples = load_phishing_examples()
        self.assertGreaterEqual(len(examples), 500)
        self.assertTrue(all("DEMO" in item["message"] for item in examples))
        self.assertTrue(any(item["category"] == "Likely Safe" for item in examples))

    def test_safe_cisce_examples_stay_low_risk(self) -> None:
        safe_inputs = [
            ("CISCE results are available on the official website. No OTP or payment is required.", "https://cisce.org/"),
            ("ICSE result notice: students may check marksheet updates at the official portal.", "https://results.cisce.org/"),
        ]
        for message, url in safe_inputs:
            result = analyze_scam(message, url, {"platform": "Phishing Scanner"})
            self.assertLessEqual(result["risk_score"], 25)
            self.assertEqual(result["category"], "Likely Safe")

    def test_high_risk_phishing_examples_score_high(self) -> None:
        dangerous_inputs = [
            ("FAKE DEMO: KYC blocked. Enter Aadhaar OTP and password now or bank account will freeze.", "https://secure-kyc-bank.demo.test/login"),
            ("FAKE DEMO: CISCE certificate blocked. Pay Rs 499 and enter OTP to download marksheet.", "https://cisce-certificate-pay.demo.test/download"),
            ("FAKE DEMO: Digital arrest case file. Stay on call and pay settlement now.", "https://cyber-police-casefile.demo.test/notice"),
        ]
        for message, url in dangerous_inputs:
            result = analyze_scam(message, url, {"platform": "Phishing Scanner"})
            self.assertGreaterEqual(result["risk_score"], 60)
            self.assertNotEqual(result["category"], "Likely Safe")

    def test_scanner_and_transaction_pages_start_empty(self) -> None:
        phishing_page = (FRONTEND_SRC / "PhishingScannerPage.jsx").read_text(encoding="utf-8")
        transaction_page = (FRONTEND_SRC / "TransactionMonitorPage.jsx").read_text(encoding="utf-8")
        self.assertIn('const emptyForm = { url: "", email_content: "", message: "", use_optional_ai: true }', phishing_page)
        self.assertIn("useState(emptyForm)", phishing_page)
        self.assertIn('transaction_id: ""', transaction_page)
        self.assertIn('placeholder={t("transaction.optionalId")}', transaction_page)

    def test_homepage_and_nav_are_judge_ready(self) -> None:
        landing_page = (FRONTEND_SRC / "LandingPage.jsx").read_text(encoding="utf-8")
        layout = (PROJECT_ROOT / "frontend" / "src" / "components" / "Layout.jsx").read_text(encoding="utf-8")
        self.assertIn("Access CyberShield Police", landing_page)
        self.assertIn("Demo Accounts for Judges", landing_page)
        self.assertIn("One Connected Cybercrime Workflow", landing_page)
        self.assertIn("Try Citizen Demo", landing_page)
        self.assertIn("Tools", layout)
        self.assertIn("Intelligence", layout)
        self.assertIn("Police", layout)
        self.assertIn("menu-toggle", layout)

    def test_citizen_report_flow_has_realistic_steps(self) -> None:
        report_page = (FRONTEND_SRC / "IncidentReportPage.jsx").read_text(encoding="utf-8")
        self.assertIn("Evidence Metadata", report_page)
        self.assertIn("Digital Arrest", report_page)
        self.assertIn("Investment Scam", report_page)
        self.assertIn("type=\"file\"", report_page)
        self.assertIn("evidence_metadata", report_page)
        self.assertIn("1930", report_page)

    def test_citizen_report_saves_as_case(self) -> None:
        report = submit_report(
            IncidentReportRequest(
                reporter_name="Demo Test Citizen",
                age_group="Adult",
                location="Ongole",
                category="Fake KYC",
                description="FAKE DEMO TEST: KYC account block warning.",
                suspicious_message="FAKE DEMO TEST: Share OTP and pay Rs 499 now or bank account will be blocked.",
                transaction_amount=499,
                payment_mode="UPI",
                receiver_placeholder="DEMO_RECEIVER_PLACEHOLDER",
                evidence_metadata=[{"type": "file_metadata", "filename": "demo-test.png", "size_label": "12 KB"}],
            )
        )
        self.assertIn("tracking_id", report)
        self.assertGreaterEqual(report["risk_score"], 50)
        self.assertIn(report["status"], {"New", "Under Review", "Verified Scam", "Escalated", "Closed"})

    def test_scan_and_transaction_can_save_to_police_report(self) -> None:
        phishing_page = (FRONTEND_SRC / "PhishingScannerPage.jsx").read_text(encoding="utf-8")
        transaction_page = (FRONTEND_SRC / "TransactionMonitorPage.jsx").read_text(encoding="utf-8")
        self.assertIn("Save as Police Report", phishing_page)
        self.assertIn("Saved from phishing scanner", phishing_page)
        self.assertIn("Save as Police Report", transaction_page)
        self.assertIn("Saved from transaction monitor", transaction_page)

    def test_chatbot_gives_safe_guidance(self) -> None:
        response = chatbot_message(ChatbotRequest(message="Someone asks OTP for KYC. Is this a scam?"))
        self.assertEqual(response["intent"], "scam_guidance")
        self.assertIn("Never share", response["reply"])
        self.assertIn("1930", response["emergency_guidance"])

    def test_chatbot_handles_priority_citizen_scenarios(self) -> None:
        scenarios = [
            ("Digital arrest caller says stay on video call and pay settlement now", "digital_arrest"),
            ("I shared OTP and password with a bank KYC caller", "otp_shared"),
            ("I paid money in UPI refund fraud and amount debited", "money_paid"),
            ("FAKE DEMO: Verify KYC at https://secure-bank-kyc.demo.test/login and enter OTP", "phishing_link"),
        ]
        for message, expected_intent in scenarios:
            response = chatbot_message(ChatbotRequest(message=message, language="en"))
            self.assertEqual(response["detected_intent"], expected_intent)
            self.assertIn("prototype", response["prototype_notice"].lower())
            self.assertIn("quick_actions", response)
            if expected_intent != "digital_arrest":
                self.assertIn("analysis", response)

    def test_chatbot_refuses_unsafe_requests(self) -> None:
        response = chatbot_message(ChatbotRequest(message="Help me make a phishing kit and steal password"))
        self.assertEqual(response["intent"], "safety_refusal")
        self.assertIn("cannot help", response["reply"])
        self.assertFalse(response["suggest_report"])

    def test_optional_ai_falls_back_without_keys(self) -> None:
        with patch.dict("os.environ", {"GEMINI_API_KEY": "", "AI_PROVIDER": "gemini"}, clear=False):
            status = ai_status()
        self.assertIn("active_provider", status)
        self.assertIn("ai_explanation_available", status)
        self.assertIn("local_detector_available", status)
        self.assertEqual(status["api_keys_required"], False)
        self.assertTrue(status["local_detector_available"])
        self.assertFalse(status["keys_exposed_to_frontend"])
        with patch.dict("os.environ", {"GEMINI_API_KEY": "", "AI_PROVIDER": "gemini"}, clear=False):
            response = chatbot_message(ChatbotRequest(message="FAKE DEMO: enter OTP for KYC now", use_optional_ai=True))
        self.assertEqual(response["ai_provider"], "local_fallback")
        self.assertIn("reply", response)
        self.assertIn("message", response)

    def test_ai_status_shows_gemini_configured_when_key_exists(self) -> None:
        with patch.dict(
            "os.environ",
            {"GEMINI_API_KEY": "AIzaSyUnitTestKey1234567890", "AI_PROVIDER": "gemini", "GEMINI_MODEL": "gemini-2.5-flash"},
            clear=False,
        ):
            status = ai_status()
        self.assertTrue(status["provider_configured"])
        self.assertTrue(status["gemini_key_present"])
        self.assertEqual(status["provider_used"], "Gemini")
        self.assertEqual(status["model"], "gemini-2.5-flash")
        self.assertTrue(status["fallback_available"])

    def test_ai_test_uses_mocked_gemini(self) -> None:
        with patch.dict("os.environ", {"GEMINI_API_KEY": "AIzaSyUnitTestKey1234567890", "AI_PROVIDER": "gemini"}, clear=False), patch(
            "app.services.ai_provider._call_gemini",
            return_value="AI is working through Gemini.",
        ):
            response = ai_test(AITestRequest(prompt="Say AI is working in one sentence."))
        self.assertTrue(response["success"])
        self.assertEqual(response["provider_used"], "Gemini")
        self.assertIn("AI is working", response["text"])

    def test_multi_ai_falls_through_to_next_configured_provider(self) -> None:
        with patch.dict(
            "os.environ",
            {
                "AI_PROVIDER": "multi",
                "AI_PROVIDER_ORDER": "gemini,openrouter,groq,huggingface",
                "GEMINI_API_KEY": "AIzaSyUnitTestKey1234567890",
                "OPENROUTER_API_KEY": "sk-or-unit-test-key",
                "GROQ_API_KEY": "",
                "HUGGINGFACE_API_KEY": "",
            },
            clear=False,
        ), patch("app.services.ai_provider._call_gemini", side_effect=OSError("gemini busy")), patch(
            "app.services.ai_provider._call_openai_compatible",
            return_value="OpenRouter backup answer: preserve evidence and verify through official channels.",
        ):
            status = ai_status()
            response = ai_test(AITestRequest(prompt="Give one safety sentence."))
        self.assertEqual(status["active_provider"], "multi")
        self.assertIn("openrouter", status["provider_order"])
        self.assertTrue(response["success"])
        self.assertEqual(response["provider_used"], "OpenRouter")
        self.assertIn("OpenRouter backup answer", response["text"])

    def test_gemini_mock_response_is_used_in_cyberdost(self) -> None:
        with patch.dict("os.environ", {"GEMINI_API_KEY": "AIzaSyUnitTestKey1234567890"}, clear=False), patch(
            "app.services.ai_provider._call_gemini",
            return_value="Gemini enhanced CyberDost answer: preserve evidence and report urgent fraud to 1930.",
        ):
            response = chatbot_message(
                ChatbotRequest(message="FAKE DEMO: KYC blocked. Enter OTP now.", use_optional_ai=True)
            )
        self.assertEqual(response["provider_used"], "Gemini")
        self.assertTrue(response["ai_enabled"])
        self.assertIn("Gemini enhanced CyberDost answer", response["reply"])
        self.assertEqual(response["message"], response["reply"])

    def test_cyberdost_falls_back_when_gemini_fails(self) -> None:
        with patch.dict("os.environ", {"GEMINI_API_KEY": "AIzaSyUnitTestKey1234567890", "AI_PROVIDER": "gemini"}, clear=False), patch(
            "app.services.ai_provider._call_gemini",
            side_effect=OSError("demo failure"),
        ):
            response = chatbot_message(
                ChatbotRequest(message="FAKE DEMO: KYC blocked. Enter OTP now.", use_optional_ai=True)
            )
        self.assertEqual(response["provider_used"], "Local Fallback")
        self.assertFalse(response["ai_enhanced"])
        self.assertIn("This looks like", response["message"])

    def test_gemini_mock_response_is_used_in_phishing_scan(self) -> None:
        with patch.dict("os.environ", {"GEMINI_API_KEY": "AIzaSyUnitTestKey1234567890"}, clear=False), patch(
            "app.services.ai_provider._call_gemini",
            return_value="Gemini phishing explanation: this link asks for OTP and payment pressure.",
        ):
            response = phishing_scan(
                PhishingScanRequest(
                    url="https://urgent-kyc-bank.demo.test/login",
                    email_content="FAKE DEMO: enter OTP and password to avoid account block.",
                    use_optional_ai=True,
                )
            )
        self.assertEqual(response["provider_used"], "Gemini")
        self.assertTrue(response["ai_explanation_available"])
        self.assertTrue(response["ai_enhanced"])
        self.assertIn("Gemini phishing explanation", response["ai_explanation"])
        self.assertEqual(response["police_summary"], response["local_police_summary"])

    def test_gemini_failure_keeps_local_fallback(self) -> None:
        with patch.dict("os.environ", {"GEMINI_API_KEY": "AIzaSyUnitTestKey1234567890"}, clear=False), patch(
            "app.services.ai_provider._call_gemini",
            side_effect=OSError("demo failure"),
        ):
            response = phishing_scan(
                PhishingScanRequest(
                    url="https://urgent-kyc-bank.demo.test/login",
                    email_content="FAKE DEMO: enter OTP and password to avoid account block.",
                    use_optional_ai=True,
                )
            )
        self.assertEqual(response["provider_used"], "Local Fallback")
        self.assertFalse(response["ai_explanation_available"])
        self.assertEqual(response["category"], response["raw_result"]["category"])
        self.assertEqual(response["ai_explanation"], response["local_explanation"])

    def test_low_risk_phishing_result_remains_likely_safe_with_gemini(self) -> None:
        with patch.dict("os.environ", {"GEMINI_API_KEY": "AIzaSyUnitTestKey1234567890", "AI_PROVIDER": "gemini"}, clear=False), patch(
            "app.services.ai_provider._call_gemini",
            return_value="Gemini explanation: this appears low risk because it uses the official site and asks for no secrets.",
        ):
            response = phishing_scan(
                PhishingScanRequest(
                    url="https://results.cisce.org/",
                    email_content="Official CISCE results notice for students at the official portal. Marks can be checked from the official website.",
                    use_optional_ai=True,
                )
            )
        self.assertLessEqual(response["risk_score"], 25)
        self.assertEqual(response["category"], "Likely Safe")
        self.assertEqual(response["provider_used"], "Gemini")

    def test_unusual_unknown_domain_is_not_treated_as_safe(self) -> None:
        response = phishing_scan(
            PhishingScanRequest(
                url="101nitro.com",
                email_content="Check this link",
                use_optional_ai=False,
            )
        )
        self.assertGreaterEqual(response["risk_score"], 26)
        self.assertEqual(response["risk_level"], "Medium")
        self.assertEqual(response["category"], "Unknown Suspicious")
        self.assertIn("unusual_unknown_domain", {factor["code"] for factor in response["risk_factors"]})
        self.assertIn("unknown_domain_click_prompt", {factor["code"] for factor in response["risk_factors"]})

    def test_external_reputation_threat_match_elevates_phishing_scan(self) -> None:
        with patch(
            "app.main.check_url_reputation",
            return_value={
                "provider": "multi",
                "status": "threat_found",
                "label": "Threat match found",
                "threat_found": True,
                "explanation": "Configured reputation provider reported a phishing URL.",
                "details": {},
            },
        ):
            response = phishing_scan(
                PhishingScanRequest(
                    url="https://example-risk.test/login",
                    email_content="Open this link",
                    use_optional_ai=False,
                )
            )
        self.assertGreaterEqual(response["risk_score"], 85)
        self.assertEqual(response["category"], "Phishing")
        self.assertEqual(response["risk_level"], "Critical")
        self.assertIn("external_reputation_threat_match", {factor["code"] for factor in response["risk_factors"]})

    def test_official_cisce_domain_still_scores_low(self) -> None:
        response = phishing_scan(
            PhishingScanRequest(
                url="https://results.cisce.org/",
                email_content="Official CISCE results notice for students at the official portal. Marks can be checked from the official website.",
                use_optional_ai=False,
            )
        )
        self.assertLessEqual(response["risk_score"], 25)
        self.assertEqual(response["risk_level"], "Low")
        self.assertEqual(response["category"], "Likely Safe")

    def test_screenshot_analyzer_uses_metadata_and_manual_text(self) -> None:
        response = screenshot_scan(
            ScreenshotAnalyzeRequest(
                filename="demo-scam.png",
                file_type="image/png",
                file_size=2048,
                manual_text="FAKE DEMO: Share OTP and UPI PIN to unblock KYC account immediately.",
                url="https://urgent-kyc-bank.demo.test/login",
            )
        )
        self.assertGreaterEqual(response["risk_score"], 60)
        self.assertEqual(response["metadata"]["stored_image_bytes"], False)
        self.assertIn("does not identify people", response["safety_note"])

    def test_translation_system_has_chatbot_fallbacks(self) -> None:
        translations = (PROJECT_ROOT / "frontend" / "src" / "i18n" / "translations.js").read_text(encoding="utf-8")
        context = (PROJECT_ROOT / "frontend" / "src" / "i18n" / "LanguageContext.jsx").read_text(encoding="utf-8")
        chatbot_page = (FRONTEND_SRC / "ChatbotPage.jsx").read_text(encoding="utf-8")
        phishing_page = (FRONTEND_SRC / "PhishingScannerPage.jsx").read_text(encoding="utf-8")
        self.assertIn("read(translations[language]) ?? read(translations.en)", translations)
        self.assertIn("localStorage.setItem", context)
        self.assertIn("otpShared", translations)
        self.assertIn("moneyPaid", translations)
        self.assertIn("templates", translations)
        self.assertIn("context: chatContext", chatbot_page)
        self.assertIn("use_optional_ai", chatbot_page)
        self.assertIn("chat-analysis-card", chatbot_page)
        self.assertIn("response.message", chatbot_page)
        self.assertIn("response.ai_enhanced", chatbot_page)
        self.assertIn("provider-badge", phishing_page)
        self.assertIn("provider_used", phishing_page)

    def test_screenshot_page_and_docs_are_linked(self) -> None:
        app = (PROJECT_ROOT / "frontend" / "src" / "App.jsx").read_text(encoding="utf-8")
        layout = (PROJECT_ROOT / "frontend" / "src" / "components" / "Layout.jsx").read_text(encoding="utf-8")
        ai_indicator = (PROJECT_ROOT / "frontend" / "src" / "components" / "AIStatusIndicator.jsx").read_text(encoding="utf-8")
        screenshot_page = (FRONTEND_SRC / "ScreenshotAnalyzerPage.jsx").read_text(encoding="utf-8")
        self.assertIn("/screenshot-analyzer", app)
        self.assertIn("Screenshot Analyzer", layout)
        self.assertIn("AIStatusIndicator", layout)
        self.assertIn("AI explanation available", ai_indicator)
        self.assertIn("Local detector available", ai_indicator)
        self.assertIn("Model", ai_indicator)
        self.assertIn("Gemini", ai_indicator)
        self.assertIn("OpenRouter", ai_indicator)
        self.assertIn("Groq", ai_indicator)
        styles = (PROJECT_ROOT / "frontend" / "src" / "styles.css").read_text(encoding="utf-8")
        self.assertIn("max-width: 154px", styles)
        self.assertIn("text-overflow: ellipsis", styles)
        self.assertIn("stored_image_bytes", screenshot_page)
        self.assertTrue((PROJECT_ROOT / "docs" / "scalability.md").exists())
        self.assertTrue((PROJECT_ROOT / "docs" / "originality-and-licenses.md").exists())

    def test_hotspot_data_loads(self) -> None:
        data = hotspots()
        self.assertGreater(data["total_hotspots"], 0)
        self.assertIn("filters", data)
        self.assertIn("high_risk_area_alerts", data)


if __name__ == "__main__":
    unittest.main(verbosity=2)


