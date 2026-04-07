from __future__ import annotations

import json
import unittest

from cloud_function import handler


class CloudFunctionTests(unittest.TestCase):
    def test_health_endpoint(self) -> None:
        event = {"httpMethod": "GET", "path": "/health"}

        response = handler(event, context=None)
        payload = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(payload, {"status": "ok"})

    def test_get_webhook_info(self) -> None:
        event = {"httpMethod": "GET", "path": "/webhook"}

        response = handler(event, context=None)
        payload = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(payload.get("status"), "ok")
        self.assertIn("POST", payload.get("message", ""))

    def test_post_webhook_dialog_payload(self) -> None:
        payload = {
            "request": {"original_utterance": "старт"},
            "session": {"new": True, "user_id": "cf-test-user"},
        }
        event = {
            "httpMethod": "POST",
            "path": "/webhook",
            "body": json.dumps(payload, ensure_ascii=False),
        }

        response = handler(event, context=None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(body.get("version"), "1.0")
        self.assertIn("response", body)


if __name__ == "__main__":
    unittest.main()
