from __future__ import annotations

import time
import unittest

from app.main import (
    CitizenRegisterRequest,
    LoginRequest,
    PoliceRegisterRequest,
    approve_police_account,
    login,
    police_verification_requests,
    register_citizen,
    register_police,
    reject_police_account,
    startup,
)


class AuthFlowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        startup()
        cls.suffix = str(int(time.time() * 1000))

    def test_demo_login_credentials_work(self) -> None:
        citizen = login(LoginRequest(email="citizen@example.com", password="citizen123"))
        officer = login(LoginRequest(email="officer@example.com", password="officer123"))
        admin = login(LoginRequest(email="admin@example.com", password="admin123"))
        self.assertEqual(citizen["user"]["role"], "Citizen")
        self.assertEqual(officer["user"]["verification_status"], "Verified")
        self.assertEqual(admin["user"]["role"], "Admin/SP")

    def test_citizen_registration(self) -> None:
        payload = register_citizen(
            CitizenRegisterRequest(
                name="Demo Registered Citizen",
                email=f"citizen-{self.suffix}@example.com",
                password="citizen123",
                location="Ongole",
                age_group="Adult",
            )
        )
        self.assertEqual(payload["user"]["role"], "Citizen")
        self.assertEqual(payload["user"]["verification_status"], "Verified")

    def test_police_registration_with_code_is_verified(self) -> None:
        payload = register_police(
            PoliceRegisterRequest(
                name="Demo Verified Officer",
                email=f"verified-officer-{self.suffix}@example.com",
                password="officer123",
                rank_designation="Sub Inspector",
                police_station="Ongole Cyber Desk",
                district="Prakasam",
                badge_id_placeholder="DEMO-BADGE-VERIFY",
                verification_document_name="demo-verification-placeholder.pdf",
                verification_code="PRAKASAM-POLICE-DEMO",
            )
        )
        self.assertEqual(payload["user"]["verification_status"], "Verified")
        self.assertFalse(payload["requires_verification"])

    def test_pending_police_can_be_approved_and_rejected(self) -> None:
        pending = register_police(
            PoliceRegisterRequest(
                name="Demo Pending Officer",
                email=f"pending-officer-{self.suffix}@example.com",
                password="officer123",
                rank_designation="Constable",
                police_station="Chirala Demo Unit",
                district="Prakasam",
                badge_id_placeholder="DEMO-BADGE-PENDING",
                verification_document_name="demo-pending-placeholder.pdf",
                verification_code="",
            )
        )
        self.assertTrue(pending["requires_verification"])
        self.assertEqual(pending["user"]["verification_status"], "Pending Verification")
        requests = police_verification_requests()
        self.assertTrue(any(item["id"] == pending["user"]["id"] for item in requests))

        approved = approve_police_account(pending["user"]["id"])
        self.assertEqual(approved["verification_status"], "Verified")

        rejected = reject_police_account(pending["user"]["id"])
        self.assertEqual(rejected["verification_status"], "Rejected")


if __name__ == "__main__":
    unittest.main(verbosity=2)
