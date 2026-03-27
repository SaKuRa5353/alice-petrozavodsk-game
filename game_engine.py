"""Core mechanics for the Petrozavodsk landmark quiz game."""

from __future__ import annotations

import random
import re
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from landmarks import LANDMARKS

TOTAL_QUESTIONS = 5


@dataclass
class GameState:
    in_progress: bool = False
    score: int = 0
    asked_count: int = 0
    current_landmark: Dict | None = None
    queue: List[Dict] = field(default_factory=list)


def normalize_text(text: str) -> str:
    # Normalize punctuation and spacing so free-form user input is easier to match.
    text = text.lower().strip()
    text = text.replace("ё", "е")
    text = re.sub(r"[^a-zа-я0-9\s-]", "", text)
    return re.sub(r"\s+", " ", text)


def _is_correct_answer(user_text: str, landmark: Dict) -> bool:
    normalized = normalize_text(user_text)
    candidates = [landmark["name"], *landmark.get("aliases", [])]
    normalized_candidates = [normalize_text(c) for c in candidates]

    # Accept exact alias match or full title contained in user text.
    for candidate in normalized_candidates:
        if normalized == candidate or candidate in normalized:
            return True
    return False


def build_question(landmark: Dict, number: int) -> str:
    return (
        f"Вопрос {number}/{TOTAL_QUESTIONS}.\\n"
        f"Описание: {landmark['description']}\\n"
        f"Подсказка: {landmark['hint']}\\n"
        "Что это за достопримечательность?"
    )


def help_text() -> str:
    return (
        "Правила игры: угадай 5 достопримечательностей Петрозаводска.\\n"
        "Команды: \\n"
        "- помощь: показать правила\\n"
        "- сдаюсь: показать ответ и перейти дальше\\n"
        "- заново: начать новую игру\\n"
        "Отправь название достопримечательности текстом."
    )


def _start_new_game(state: GameState) -> Tuple[str, GameState]:
    state.in_progress = True
    state.score = 0
    state.asked_count = 0
    state.queue = random.sample(LANDMARKS, k=min(TOTAL_QUESTIONS, len(LANDMARKS)))
    # Move one landmark from queue into the current round.
    state.current_landmark = state.queue.pop(0)

    text = (
        "Начинаем игру: Угадай достопримечательность Петрозаводска!\\n"
        + build_question(state.current_landmark, 1)
    )
    return text, state


def _next_question_or_finish(state: GameState) -> str:
    if state.asked_count >= TOTAL_QUESTIONS:
        state.in_progress = False
        state.current_landmark = None
        return (
            f"Игра окончена. Твой результат: {state.score}/{TOTAL_QUESTIONS}.\\n"
            "Чтобы сыграть снова, напиши: заново"
        )

    if not state.queue:
        state.in_progress = False
        state.current_landmark = None
        return "Недостаточно данных для продолжения игры."

    # Advance to the next prepared landmark.
    state.current_landmark = state.queue.pop(0)
    return build_question(state.current_landmark, state.asked_count + 1)


def handle_user_input(raw_text: str, state: GameState) -> Tuple[str, GameState]:
    text = normalize_text(raw_text)

    if text in {"помощь", "help"}:
        if not state.in_progress:
            start_text, state = _start_new_game(state)
            return help_text() + "\\n\\n" + start_text, state
        return help_text(), state

    if text in {"заново", "начать заново", "start", "старт"}:
        return _start_new_game(state)

    if not state.in_progress:
        return _start_new_game(state)

    if text == "сдаюсь":
        current = state.current_landmark
        state.asked_count += 1
        answer_text = (
            f"Правильный ответ: {current['name']}.\\n"
            f"Локация: {current['location']}. Год: {current['year']}."
        )
        return answer_text + "\\n\\n" + _next_question_or_finish(state), state

    current = state.current_landmark
    if _is_correct_answer(raw_text, current):
        state.score += 1
        state.asked_count += 1
        return "Верно! Отличный ответ.\\n\\n" + _next_question_or_finish(state), state

    return (
        "Пока не угадал. Попробуй еще раз или напиши 'сдаюсь'."
    ), state
