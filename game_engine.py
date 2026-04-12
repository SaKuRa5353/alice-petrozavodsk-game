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
    wrong_attempts_on_current: int = 0
    awaiting_restart_decision: bool = False


def normalize_text(text: str) -> str:
    # Normalize punctuation and spacing so free-form user input is easier to match.
    text = text.lower().strip()
    text = text.replace("ё", "е")
    text = re.sub(r"[^a-zа-я0-9\s-]", "", text)
    return re.sub(r"\s+", " ", text)


def _stem_token(token: str) -> str:
    """A lightweight Russian token stemmer for tolerant answer matching."""
    token = normalize_text(token)
    if len(token) <= 3:
        return token

    for suffix in (
        "иями",
        "ями",
        "ами",
        "ого",
        "его",
        "ому",
        "ему",
        "ыми",
        "ими",
        "ая",
        "яя",
        "ое",
        "ее",
        "ый",
        "ий",
        "ой",
        "ам",
        "ям",
        "ах",
        "ях",
        "ом",
        "ем",
        "у",
        "ю",
        "а",
        "я",
        "ы",
        "и",
        "о",
        "е",
    ):
        if token.endswith(suffix) and len(token) > len(suffix) + 2:
            return token[: -len(suffix)]
    return token


def _token_stems(text: str) -> set[str]:
    normalized = normalize_text(text)
    tokens = [t for t in normalized.split() if t]
    return {_stem_token(token) for token in tokens if token}


def _is_correct_answer(user_text: str, landmark: Dict) -> bool:
    normalized = normalize_text(user_text)
    candidates = [landmark["name"], *landmark.get("aliases", [])]
    normalized_candidates = [normalize_text(c) for c in candidates]

    # Accept exact alias match or full title contained in user text.
    for candidate in normalized_candidates:
        if normalized == candidate or candidate in normalized:
            return True

    # Fallback: if at least one stemmed token overlaps, accept as near match.
    user_stems = _token_stems(user_text)
    for candidate in candidates:
        if user_stems & _token_stems(candidate):
            return True
    return False


def build_question(landmark: Dict, number: int) -> str:
    return (
        f"Вопрос {number}/{TOTAL_QUESTIONS}.\\n"
        f"Описание: {landmark['description']}\\n"
        "Что это за достопримечательность?"
    )


def help_text() -> str:
    return (
        "Это викторина о достопримечательностях Петрозаводска.\\n"
        "Правила игры: угадай 5 достопримечательностей Петрозаводска.\\n"
        "Команды: \\n"
        "- помощь: показать правила\\n"
        "- сдаюсь: показать ответ и перейти дальше\\n"
        "- заново: начать новую игру\\n"
        "Отправь название достопримечательности текстом."
    )


def _start_new_game(state: GameState) -> Tuple[str, GameState]:
    state.in_progress = True
    state.awaiting_restart_decision = False
    state.score = 0
    state.asked_count = 0
    state.wrong_attempts_on_current = 0
    state.queue = random.sample(LANDMARKS, k=min(TOTAL_QUESTIONS, len(LANDMARKS)))
    # Move one landmark from queue into the current round.
    state.current_landmark = state.queue.pop(0)

    text = (
        "Начинаем игру: Угадай достопримечательность Петрозаводска!\\n"
        "Я описываю место, а ты называешь его. Подсказки даю после ошибок.\\n\\n"
        + build_question(state.current_landmark, 1)
    )
    return text, state


def _next_question_or_finish(state: GameState) -> str:
    if state.asked_count >= TOTAL_QUESTIONS:
        state.in_progress = False
        state.awaiting_restart_decision = True
        state.current_landmark = None
        state.wrong_attempts_on_current = 0
        return (
            f"Игра окончена. Твой результат: {state.score}/{TOTAL_QUESTIONS}.\\n"
            "Хочешь сыграть еще? Напиши: заново. Если нет, напиши: нет"
        )

    if not state.queue:
        state.in_progress = False
        state.awaiting_restart_decision = True
        state.current_landmark = None
        state.wrong_attempts_on_current = 0
        return "Недостаточно данных для продолжения игры."

    # Advance to the next prepared landmark.
    state.current_landmark = state.queue.pop(0)
    state.wrong_attempts_on_current = 0
    return build_question(state.current_landmark, state.asked_count + 1)


def handle_user_input(raw_text: str, state: GameState) -> Tuple[str, GameState]:
    text = normalize_text(raw_text)

    if state.awaiting_restart_decision and text in {"нет", "не хочу", "хватит", "стоп", "выход"}:
        state.awaiting_restart_decision = False
        return (
            "Спасибо за игру! Если захочешь вернуться, напиши: старт или заново.",
            state,
        )

    if text in {"помощь", "help", "что ты умеешь", "что умеешь"}:
        if not state.in_progress:
            start_text, state = _start_new_game(state)
            return help_text() + "\\n\\n" + start_text, state
        return help_text(), state

    if text in {"заново", "занаво", "начать заново", "start", "старт"}:
        return _start_new_game(state)

    if not state.in_progress:
        return (
            "Игра сейчас не запущена. Напиши: старт, чтобы начать новую викторину.",
            state,
        )

    if text == "сдаюсь":
        current = state.current_landmark
        state.asked_count += 1
        state.wrong_attempts_on_current = 0
        answer_text = (
            f"Правильный ответ: {current['name']}.\\n"
            f"Локация: {current['location']}. Год: {current['year']}."
        )
        return answer_text + "\\n\\n" + _next_question_or_finish(state), state

    current = state.current_landmark
    if _is_correct_answer(raw_text, current):
        state.score += 1
        state.asked_count += 1
        state.wrong_attempts_on_current = 0
        return "Верно! Отличный ответ.\\n\\n" + _next_question_or_finish(state), state

    state.wrong_attempts_on_current += 1
    if state.wrong_attempts_on_current == 1:
        return (
            "Пока не угадал. Первая подсказка:\\n"
            f"{current['hint']}\\n"
            "Попробуй еще раз или напиши 'сдаюсь'."
        ), state

    if state.wrong_attempts_on_current == 2:
        image_hint = current.get("image_hint_url")
        if image_hint:
            return (
                "Пока не угадал. Вторая подсказка (картинка):\\n"
                f"{image_hint}\\n"
                "Попробуй еще раз или напиши 'сдаюсь'."
            ), state

    return ("Пока не угадал. Попробуй еще раз или напиши 'сдаюсь'."), state
