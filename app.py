"""Flask application wrapper for Yandex Dialogs webhook.

This serves the alice_handler as an HTTP endpoint that can be accessed
by Yandex Dialogs from the public internet.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from flask import Flask, request, jsonify

from alice_handler import handler

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)


@app.route("/webhook", methods=["POST"])
def webhook() -> tuple[Any, int]:
    """Handle Yandex Dialogs webhook requests."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON body"}), 400

        response = handler(data, None)
        return jsonify(response), 200

    except Exception as e:
        logging.error(f"Error processing webhook: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health() -> tuple[dict[str, str], int]:
    """Health check endpoint for deployment monitoring."""
    return {"status": "ok"}, 200


@app.route("/", methods=["GET"])
def index() -> str:
    """Root endpoint for information."""
    return """
    <h1>Петрозаводск Quiz Skill</h1>
    <p>Webhook endpoints:</p>
    <ul>
        <li>POST /webhook — Yandex Dialogs webhook</li>
        <li>GET /health — Health check</li>
    </ul>
    """


if __name__ == "__main__":
    # For local testing. In production, Render uses gunicorn.
    app.run(host="0.0.0.0", port=5000, debug=False)
