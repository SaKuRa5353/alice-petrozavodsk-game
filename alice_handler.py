"""Yandex Dialogs webhook handler for the quiz game.

This file is suitable as a starting point for Yandex Cloud Functions.
Entry point: handler(event, context)
"""

from __future__ import annotations

from typing import Any, Dict

from game_engine import GameState, handle_user_input

# In production, session state should be stored in external storage.
SESSIONS: Dict[str, GameState] = {}


def _build_response(text: str, end_session: bool = False) -> Dict[str, Any]:
    return {
        "version": "1.0",
        "response": {
            "text": text,
            "end_session": end_session,
        },
    }


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    request = event.get("request", {})
    session = event.get("session", {})

    user_id = session.get("user_id") or session.get("application", {}).get("application_id", "anonymous")
    is_new = bool(session.get("new"))
    user_text = request.get("original_utterance", "").strip()

    if is_new or user_id not in SESSIONS:
        SESSIONS[user_id] = GameState()

    state = SESSIONS[user_id]

    if not user_text:
        user_text = "старт"

    reply_text, updated_state = handle_user_input(user_text, state)
    SESSIONS[user_id] = updated_state

    return _build_response(reply_text, end_session=False)
