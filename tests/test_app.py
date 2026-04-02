from __future__ import annotations

import unittest

from app import app


class FlaskAppTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = app.test_client()

    def test_health_endpoint(self) -> None:
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})

    def test_webhook_rejects_empty_json(self) -> None:
        response = self.client.post("/webhook", data="", content_type="application/json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"error": "No JSON body"})

    def test_webhook_rejects_non_object_json(self) -> None:
        response = self.client.post("/webhook", json=["not", "an", "object"])

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json(),
            {"error": "Invalid JSON payload: expected object"},
        )

    def test_webhook_get_returns_status_message(self) -> None:
        response = self.client.get("/webhook")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload.get("status"), "ok")
        self.assertIn("POST", payload.get("message", ""))

    def test_webhook_accepts_dialogs_payload(self) -> None:
        payload = {
            "request": {"original_utterance": "старт"},
            "session": {
                "new": True,
                "user_id": "app-test-user",
            },
        }

        response = self.client.post("/webhook", json=payload)
        body = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(body.get("version"), "1.0")
        self.assertIn("response", body)
        self.assertIn("text", body["response"])


if __name__ == "__main__":
    unittest.main()
