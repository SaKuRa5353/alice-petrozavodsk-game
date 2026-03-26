import unittest
from unittest.mock import patch

from game_engine import GameState, handle_user_input, normalize_text
from landmarks import LANDMARKS


class TestGameEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.fixed_landmarks = LANDMARKS[:5]

    def _start_game(self) -> tuple[str, GameState]:
        state = GameState()
        with patch("game_engine.random.sample", return_value=self.fixed_landmarks.copy()):
            text, state = handle_user_input("старт", state)
        return text, state

    def test_normalize_text(self) -> None:
        self.assertEqual(normalize_text("  ЁжИК!!  "), "ежик")
        self.assertEqual(normalize_text("Площадь   Гагарина"), "площадь гагарина")

    def test_start_game_sets_initial_state(self) -> None:
        text, state = self._start_game()

        self.assertTrue(state.in_progress)
        self.assertEqual(state.score, 0)
        self.assertEqual(state.asked_count, 0)
        self.assertIsNotNone(state.current_landmark)
        self.assertIn("Вопрос 1/5", text)

    def test_help_before_start_also_starts_game(self) -> None:
        state = GameState()
        with patch("game_engine.random.sample", return_value=self.fixed_landmarks.copy()):
            text, state = handle_user_input("помощь", state)

        self.assertTrue(state.in_progress)
        self.assertIn("Правила игры", text)
        self.assertIn("Вопрос 1/5", text)

    def test_correct_answer_increases_score_and_moves_to_next_question(self) -> None:
        _, state = self._start_game()
        current_name = state.current_landmark["name"]

        text, state = handle_user_input(current_name, state)

        self.assertEqual(state.score, 1)
        self.assertEqual(state.asked_count, 1)
        self.assertIn("Верно!", text)
        self.assertIn("Вопрос 2/5", text)

    def test_surrender_shows_answer_and_moves_forward(self) -> None:
        _, state = self._start_game()

        text, state = handle_user_input("сдаюсь", state)

        self.assertEqual(state.score, 0)
        self.assertEqual(state.asked_count, 1)
        self.assertIn("Правильный ответ", text)
        self.assertIn("Вопрос 2/5", text)

    def test_game_finishes_after_five_correct_answers(self) -> None:
        _, state = self._start_game()

        last_text = ""
        for landmark in self.fixed_landmarks:
            last_text, state = handle_user_input(landmark["name"], state)

        self.assertFalse(state.in_progress)
        self.assertIsNone(state.current_landmark)
        self.assertEqual(state.score, 5)
        self.assertIn("Игра окончена", last_text)
        self.assertIn("5/5", last_text)


if __name__ == "__main__":
    unittest.main()