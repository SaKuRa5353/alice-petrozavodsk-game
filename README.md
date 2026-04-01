# Alice Petrozavodsk Game

![CI](https://github.com/SaKuRa5353/alice-petrozavodsk-game/actions/workflows/ci.yml/badge.svg)

Голосовой учебный навык для Алисы: викторина «Угадай достопримечательность Петрозаводска».

## О проекте

Проект реализует игру на 5 раундов: пользователь получает описание достопримечательности,
вводит ответ и получает мгновенную проверку результата.

Архитектура разделена на:
- независимый игровой движок (можно тестировать локально);
- webhook-обработчик для интеграции с Яндекс Диалогами.

## Структура репозитория

```text
.
├── .github/workflows/ci.yml    # CI: автозапуск тестов в GitHub Actions
├── app.py                      # Flask HTTP-сервер для webhook
├── alice_handler.py            # Webhook для Яндекс Диалогов
├── demo_cli.py                 # Локальный CLI-запуск
├── game_engine.py              # Игровая логика и состояние
├── landmarks.py                # База достопримечательностей
├── Procfile                    # Конфигурация развёртывания (Render)
├── requirements.txt            # Зависимости
├── runtime.txt                 # Версия Python для облака
├── DEPLOYMENT.md               # Инструкция по развёртыванию
├── PROGRESS.md                 # Журнал прогресса
├── tests/                      # Набор unit-тестов
└── wikiversity_quiz.wiki       # Полный курс для Викиверситета
```

## Возможности

- 5 случайных вопросов в каждой игре.
- Проверка ответа по основному названию и алиасам.
- Подсчет итогового результата.
- Команды управления раундом.

### Команды

| Команда | Назначение |
|---|---|
| `помощь` | Показать правила игры |
| `сдаюсь` | Показать правильный ответ и перейти дальше |
| `заново` | Начать новую игру |

## Технологии

- Python 3.11+
- Python Standard Library
- Yandex Dialogs Webhook API

## Условия запуска

- Python 3.11 или выше
- Linux / macOS / Windows
- Для локального CLI не требуются внешние сервисы
- Для webhook-развертывания нужна облачная среда (например, Yandex Cloud Functions)

## Как запускать

### 1. Подготовить окружение

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Запустить локальный CLI

```bash
python demo_cli.py
```

Команда выхода: `exit`.

### 3. Запустить автотесты

```bash
python -m unittest discover -s tests -v
```

Тесты покрывают:
- игровую логику (`tests/test_game_engine.py`);
- webhook-обработчик (`tests/test_alice_handler.py`).
- валидацию качества данных (`tests/test_landmarks_data.py`).

## Развёртывание webhook

Для того чтобы навык работал в Яндекс.Ассистенте, нужно развернуть webhook на публичном сервере.

### Быстрое развёртывание на Render (5 минут)

1. Перейди на https://render.com и залогинься через GitHub
2. Нажми "New" → "Web Service"
3. Выбери этот репозиторий
4. Заполни:
   - Name: `petrozavodsk-quiz`
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn app:app`
5. Нажми "Deploy"
6. Когда готово, получишь URL вида: `https://petrozavodsk-quiz.onrender.com`
7. Webhook URL для Яндекс.Диалогов: `https://твой-url/webhook`

**Полная инструкция:** см. [DEPLOYMENT.md](DEPLOYMENT.md)

### Регистрация навыка в Яндекс.Диалогах

1. https://dialogs.yandex.ru → создай новый навык
2. Укажи webhook URL: `https://твой-url/webhook`
3. Опубликуй и тестируй в Яндекс.Ассистент

## CI

В проекте настроен GitHub Actions workflow (`.github/workflows/ci.yml`),
который автоматически запускает тесты при каждом `push` и `pull request` в `main`.
## Пример сценария

```text
> старт
Начинаем игру: Угадай достопримечательность Петрозаводска!
Вопрос 1/5.
Описание: ...
Подсказка: ...
Что это за достопримечательность?

> набережная
Верно! Отличный ответ.
```

## Интеграция с Яндекс Диалогами

Точка входа webhook: `handler(event, context)` в `alice_handler.py`.

Минимальный входной payload:

```json
{
	"request": {
		"original_utterance": "старт"
	},
	"session": {
		"new": true,
		"user_id": "user-123"
	}
}
```

Шаги подключения:

1. Создайте навык в Яндекс Диалогах.
2. Укажите формат с webhook URL.
3. Разверните `alice_handler.py` в облачной функции.
4. Добавьте URL функции в настройках навыка.
5. Проверьте команды `помощь`, `сдаюсь`, `заново`.

## Автор

- Дуденков Семён
- Петрозаводский государственный университет (ПетрГУ)
- Направление: ПМИКТ
- Группа: 22304

## Источники данных

Источники по объектам указаны в поле `sources` файла `landmarks.py`.

## Лицензия

Проект распространяется по лицензии MIT. Подробности: `LICENSE`.
