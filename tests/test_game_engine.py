import unittest
from unittest.mock import patch

from game_engine import GameState, handle_user_input, normalize_text
from landmarks import LANDMARKS


class TestGameEngine(unittest.TestCase):
    def setUp(self) -> None:
        # Fixed order makes tests deterministic.
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
        self.assertIn("Я описываю место", text)
        self.assertIn("Вопрос 1/5", text)
        self.assertNotIn("Подсказка:", text)

    def test_help_before_start_also_starts_game(self) -> None:
        state = GameState()
        with patch("game_engine.random.sample", return_value=self.fixed_landmarks.copy()):
            text, state = handle_user_input("помощь", state)

        self.assertTrue(state.in_progress)
        self.assertIn("Правила игры", text)
        self.assertIn("Вопрос 1/5", text)

    def test_what_can_you_do_before_start_also_shows_help(self) -> None:
        state = GameState()
        with patch("game_engine.random.sample", return_value=self.fixed_landmarks.copy()):
            text, state = handle_user_input("что ты умеешь", state)

        self.assertTrue(state.in_progress)
        self.assertIn("Правила игры", text)
        self.assertIn("Вопрос 1/5", text)

    def test_hint_shown_only_after_first_wrong_answer(self) -> None:
        _, state = self._start_game()

        text, state = handle_user_input("не знаю", state)

        self.assertEqual(state.wrong_attempts_on_current, 1)
        self.assertIn("Первая подсказка", text)
        self.assertIn("Попробуй еще раз", text)

    def test_second_wrong_answer_shows_image_hint(self) -> None:
        _, state = self._start_game()

        handle_user_input("не знаю", state)
        text, state = handle_user_input("совсем не знаю", state)

        self.assertEqual(state.wrong_attempts_on_current, 2)
        self.assertIn("Вторая подсказка (картинка)", text)
        self.assertIn("http", text)

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
        self.assertTrue(state.awaiting_restart_decision)
        self.assertIsNone(state.current_landmark)
        self.assertEqual(state.score, 5)
        self.assertIn("Игра окончена", last_text)
        self.assertIn("5/5", last_text)

    def test_after_finish_non_restart_text_does_not_start_new_game(self) -> None:
        _, state = self._start_game()

        for landmark in self.fixed_landmarks:
            _, state = handle_user_input(landmark["name"], state)

        text, state = handle_user_input("краеведческий", state)

        self.assertFalse(state.in_progress)
        self.assertIn("Игра сейчас не запущена", text)

    def test_after_finish_no_command_exits_waiting_state(self) -> None:
        _, state = self._start_game()

        for landmark in self.fixed_landmarks:
            _, state = handle_user_input(landmark["name"], state)

        text, state = handle_user_input("нет", state)

        self.assertFalse(state.awaiting_restart_decision)
        self.assertIn("Спасибо за игру", text)

    def test_after_finish_typo_zanavo_starts_new_game(self) -> None:
        _, state = self._start_game()

        for landmark in self.fixed_landmarks:
            _, state = handle_user_input(landmark["name"], state)

        with patch("game_engine.random.sample", return_value=self.fixed_landmarks.copy()):
            text, state = handle_user_input("занаво", state)

        self.assertTrue(state.in_progress)
        self.assertFalse(state.awaiting_restart_decision)
        self.assertIn("Вопрос 1/5", text)

    def test_partial_lemma_match_counts_as_correct(self) -> None:
        state = GameState(
            in_progress=True,
            score=0,
            asked_count=0,
            current_landmark={
                "name": "Музыкальный театр Республики Карелия",
                "aliases": ["музыкальный театр", "театр карелии"],
                "description": "",
                "hint": "",
                "location": "",
                "year": "",
            },
            queue=self.fixed_landmarks[1:5],
        )

        text, state = handle_user_input("музыкального", state)

        self.assertEqual(state.score, 1)
        self.assertIn("Верно!", text)


if __name__ == "__main__":
    unittest.main()