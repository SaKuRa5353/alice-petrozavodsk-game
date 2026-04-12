import unittest

from alice_handler import SESSIONS, GameState, _build_response, handler


class TestAliceHandler(unittest.TestCase):
    def setUp(self) -> None:
        # Keep tests isolated from each other.
        SESSIONS.clear()

    def test_build_response_shape(self) -> None:
        response = _build_response("ok", end_session=False)

        self.assertEqual(response["version"], "1.0")
        self.assertEqual(response["response"]["text"], "ok")
        self.assertFalse(response["response"]["end_session"])

    def test_new_session_with_empty_utterance_starts_game(self) -> None:
        event = {
            "request": {"original_utterance": ""},
            "session": {"new": True, "user_id": "u1"},
        }

        response = handler(event, context=None)

        self.assertIn("u1", SESSIONS)
        self.assertIn("Вопрос 1/5", response["response"]["text"])
        self.assertFalse(response["response"]["end_session"])

    def test_same_user_session_is_reused(self) -> None:
        first_event = {
            "request": {"original_utterance": "старт"},
            "session": {"new": True, "user_id": "u2"},
        }
        second_event = {
            "request": {"original_utterance": "сдаюсь"},
            "session": {"new": False, "user_id": "u2"},
        }

        handler(first_event, context=None)
        state_after_start = SESSIONS["u2"]
        self.assertIsInstance(state_after_start, GameState)

        response = handler(second_event, context=None)

        self.assertIn("Правильный ответ", response["response"]["text"])
        self.assertEqual(SESSIONS["u2"].asked_count, 1)

    def test_fallback_to_application_id_when_user_id_missing(self) -> None:
        event = {
            "request": {"original_utterance": "старт"},
            "session": {
                "new": True,
                "application": {"application_id": "app-123"},
            },
        }

        handler(event, context=None)

        self.assertIn("app-123", SESSIONS)

    def test_handler_tolerates_null_request_and_session(self) -> None:
        event = {
            "request": None,
            "session": None,
        }

        response = handler(event, context=None)

        self.assertEqual(response["version"], "1.0")
        self.assertIn("response", response)
        self.assertIn("text", response["response"])

    def test_handler_uses_request_command_when_original_utterance_missing(self) -> None:
        event = {
            "request": {"command": "старт"},
            "session": {"new": True, "user_id": "u3"},
        }

        response = handler(event, context=None)

        self.assertIn("u3", SESSIONS)
        self.assertIn("Вопрос 1/5", response["response"]["text"])

    def test_handler_answers_what_can_you_do_with_instructions(self) -> None:
        event = {
            "request": {"original_utterance": "Что ты умеешь"},
            "session": {"new": True, "user_id": "u4"},
        }

        response = handler(event, context=None)

        self.assertIn("u4", SESSIONS)
        self.assertIn("Правила игры", response["response"]["text"])

    def test_handler_restores_state_from_session_state_payload(self) -> None:
        first = {
            "request": {"original_utterance": "старт"},
            "session": {"new": True, "user_id": "u5"},
        }
        first_response = handler(first, context=None)

        second = {
            "request": {"original_utterance": "сдаюсь"},
            "session": {"new": False, "user_id": "u5"},
            "state": {"session": first_response.get("session_state", {})},
        }
        second_response = handler(second, context=None)

        self.assertIn("Правильный ответ", second_response["response"]["text"])

    def test_handler_returns_big_image_card_on_second_hint_when_image_id_exists(self) -> None:
        event = {
            "request": {"original_utterance": "абракадабра"},
            "session": {"new": False, "user_id": "u6"},
            "state": {
                "session": {
                    "in_progress": True,
                    "score": 0,
                    "asked_count": 0,
                    "wrong_attempts_on_current": 1,
                    "awaiting_restart_decision": False,
                    "current_landmark": {
                        "name": "Тестовая достопримечательность",
                        "aliases": ["тест"],
                        "description": "desc",
                        "hint": "hint",
                        "location": "loc",
                        "year": "2020",
                        "image_hint_url": "https://example.com/pic",
                        "image_id": "123/abc",
                    },
                    "queue": [],
                }
            },
        }

        response = handler(event, context=None)
        card = response["response"].get("card")

        self.assertIsNotNone(card)
        self.assertEqual(card.get("type"), "BigImage")
        self.assertEqual(card.get("image_id"), "123/abc")


if __name__ == "__main__":
    unittest.main()
