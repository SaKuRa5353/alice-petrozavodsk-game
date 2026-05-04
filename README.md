# Alice Petrozavodsk Game

![CI](https://github.com/SaKuRa5353/alice-petrozavodsk-game/actions/workflows/ci.yml/badge.svg)

Голосовой учебный навык для Алисы: викторина «Угадай достопримечательность Петрозаводска».

## О проекте

Проект реализует игру на 5 раундов: пользователь получает описание достопримечательности, вводит ответ и получает мгновенную проверку результата.

Архитектура разделена на:
- независимый игровой движок, который можно тестировать локально;
- webhook-обработчик для интеграции с Яндекс Диалогами;
- отдельный entry point для Yandex Cloud Functions.

## Структура репозитория

```text
.
├── .github/workflows/ci.yml    # CI: автозапуск тестов в GitHub Actions
├── alice_handler.py            # Основной webhook-обработчик
├── app.py                      # Flask HTTP-сервер для локальной проверки
├── cloud_function.py           # Entry point для Yandex Cloud Functions
├── demo_cli.py                 # Локальный CLI-запуск
├── game_engine.py              # Игровая логика и состояние
├── landmarks.py                # База достопримечательностей
├── Procfile                    # Локальный запуск для Flask-сервера
├── requirements.txt            # Зависимости
├── runtime.txt                 # Версия Python для облака
├── DEPLOYMENT.md               # Инструкция по развёртыванию
├── PROGRESS.md                 # Журнал прогресса
├── tests/                      # Набор unit-тестов
└── wikiversity_quiz.wiki       # Материал для Викиверситета
```

## Возможности

- 5 случайных вопросов в каждой игре.
- Проверка ответа по основному названию и алиасам.
- Подсчёт итогового результата.
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
- Yandex Cloud Functions

## Условия запуска

- Python 3.11 или выше
- Linux / macOS / Windows
- Для локального CLI не требуются внешние сервисы
- Для публикации навыка рекомендуется Yandex Cloud Functions

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
- webhook-обработчик (`tests/test_alice_handler.py`);
- HTTP-слой Flask (`tests/test_app.py`);
- валидацию качества данных (`tests/test_landmarks_data.py`).

## Развёртывание webhook

### Рекомендуемый вариант: Yandex Cloud Functions

1. Открой https://console.yandex.cloud/ и войди в аккаунт.
2. Создай функцию в разделе Cloud Functions.
3. Загрузите код архивом `.zip` из корня репозитория.
4. Entry point укажи `cloud_function.handler`.
5. Создай HTTP-trigger и получи публичный HTTPS URL.
6. Укажи этот URL как webhook в Яндекс Диалогах.

### Проверка перед отправкой на модерацию

После публикации запусти:

```bash
python verify_webhook.py https://твой-url
```

Ожидается:
- `GET /health` возвращает `{"status":"ok"}`;
- `POST /webhook` принимает JSON и отдаёт корректный ответ формата Алисы.

### Подключение в Яндекс Диалогах

1. Создай навык в https://dialogs.yandex.ru.
2. В поле webhook URL укажи URL функции.
3. Проверь команды `старт`, `помощь`, `сдаюсь`, `заново`.

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
3. Разверните `cloud_function.py` или `alice_handler.py` в облачной функции.
4. Добавьте URL функции в настройках навыка.
5. Проверьте команды `помощь`, `сдаюсь`, `заново`.

## Автор

- Дуденков Семён
- Петрозаводский государственный университет (ПетрГУ)
- Направление: ИМИТ
- Группа: 22304

## Источники данных

Источники по объектам указаны в поле `sources` файла `landmarks.py`.

## Лицензия

Проект распространяется по лицензии MIT. Подробности: `LICENSE`
