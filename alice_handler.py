"""Yandex Dialogs webhook handler for the quiz game.

This file is suitable as a starting point for Yandex Cloud Functions.
Entry point: handler(event, context)
"""

from __future__ import annotations

from typing import Any, Dict

from game_engine import GameState, handle_user_input

# In production, session state should be stored in external storage.
SESSIONS: Dict[str, GameState] = {}


def _as_dict(value: Any) -> Dict[str, Any]:
    """Return dict value or safe empty dict for malformed payloads."""
    return value if isinstance(value, dict) else {}


def _build_response(text: str, end_session: bool = False) -> Dict[str, Any]:
    return {
        "version": "1.0",
        "response": {
            "text": text,
            "end_session": end_session,
        },
    }


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    event_payload = _as_dict(event)
    request = _as_dict(event_payload.get("request"))
    session = _as_dict(event_payload.get("session"))
    application = _as_dict(session.get("application"))

    # Keep a stable key even when user_id is absent in some test/debug payloads.
    user_id = str(session.get("user_id") or application.get("application_id") or "anonymous")
    is_new = bool(session.get("new"))
    raw_text = request.get("original_utterance") or request.get("command") or ""
    user_text = str(raw_text).strip()

    if is_new or user_id not in SESSIONS:
        SESSIONS[user_id] = GameState()

    state = SESSIONS[user_id]

    # Empty utterance often comes from "open skill" events.
    if not user_text:
        user_text = "старт"

    reply_text, updated_state = handle_user_input(user_text, state)
    SESSIONS[user_id] = updated_state

    return _build_response(reply_text, end_session=False)
