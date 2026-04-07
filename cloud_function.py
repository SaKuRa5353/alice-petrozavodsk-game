"""HTTP adapter entry point for Yandex Cloud Functions.

This module converts YCF HTTP event format into Alice payload handling
and returns HTTP-compatible responses.
"""

from __future__ import annotations

import json
from typing import Any, Dict

from alice_handler import handler as alice_handler


def _json_response(payload: Dict[str, Any], status_code: int = 200) -> Dict[str, Any]:
	return {
		"statusCode": status_code,
		"headers": {"Content-Type": "application/json"},
		"body": json.dumps(payload, ensure_ascii=False),
	}


def _parse_body(event: Dict[str, Any]) -> Dict[str, Any]:
	body = event.get("body")
	if isinstance(body, dict):
		return body
	if isinstance(body, str) and body.strip():
		try:
			parsed = json.loads(body)
			return parsed if isinstance(parsed, dict) else {}
		except json.JSONDecodeError:
			return {}
	return {}


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
	# Direct invocation with pure Alice JSON (without HTTP wrapper).
	if isinstance(event, dict) and "request" in event and "session" in event:
		return alice_handler(event, context)

	if not isinstance(event, dict):
		return _json_response({"error": "Invalid event payload"}, 400)

	method = str(event.get("httpMethod", "")).upper()
	path = str(event.get("path", "") or "")

	if method == "GET" and path.endswith("/health"):
		return _json_response({"status": "ok"}, 200)

	if method == "GET":
		return _json_response(
			{
				"status": "ok",
				"message": "Webhook is online. Send POST requests from Yandex Dialogs.",
			},
			200,
		)

	if method == "POST":
		payload = _parse_body(event)
		if not payload:
			return _json_response({"error": "No JSON body"}, 400)
		if not isinstance(payload, dict):
			return _json_response({"error": "Invalid JSON payload: expected object"}, 400)

		response_payload = alice_handler(payload, context)
		return _json_response(response_payload, 200)

	return _json_response({"error": "Method Not Allowed"}, 405)
