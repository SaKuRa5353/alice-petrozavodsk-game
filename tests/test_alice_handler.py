import unittest

from alice_handler import SESSIONS, GameState, _build_response, handler


class TestAliceHandler(unittest.TestCase):
    def setUp(self) -> None:
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


if __name__ == "__main__":
    unittest.main()
