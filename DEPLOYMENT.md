## Развёртывание навыка Петрозаводск Quiz на Render

### 1. Подготовка перед публикацией

Проверь локально:

```bash
python -m unittest discover -s tests -v
```

Если тесты зелёные, отправь актуальный код в GitHub.

### 2. Публикация Web Service в Render

1. Открой https://render.com и войди через GitHub.
2. Нажми New -> Web Service.
3. Выбери репозиторий alice-petrozavodsk-game.
4. Укажи параметры:
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
5. Нажми Deploy.

Через 2-3 минуты сервис получит адрес вида:
`https://petrozavodsk-quiz.onrender.com`

### 3. Проверка публичного сервиса

Проверь health endpoint:

```bash
curl https://твой-url.onrender.com/health
```

Ожидаемый ответ:

```json
{"status":"ok"}
```

Проверь webhook локальным тестовым запросом:

```bash
curl -X POST https://твой-url.onrender.com/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "request": {"original_utterance": "старт"},
    "session": {"new": true, "user_id": "demo-user"}
  }'
```

Также можно проверить оба endpoint сразу:

```bash
python verify_webhook.py https://твой-url.onrender.com
```

Проверь открытие webhook в браузере (GET):

```bash
curl https://твой-url.onrender.com/webhook
```

Ожидаемый ответ:

```json
{"status":"ok","message":"Webhook is online. Send POST requests from Yandex Dialogs."}
```

### 4. Привязка webhook в Яндекс Диалогах

1. Открой https://dialogs.yandex.ru.
2. Создай навык с внешним webhook.
3. В поле URL обработчика укажи:
   `https://твой-url.onrender.com/webhook`
4. Сохрани и протестируй навык в интерфейсе Диалогов и в приложении Алисы.

### 5. Чеклист готовности к сдаче

- Навык запускается в приложении Алисы.
- Команды `старт`, `помощь`, `сдаюсь`, `заново` работают.
- Публичный `/health` отвечает со статусом ok.
- Публичный `GET /webhook` возвращает JSON со статусом ok.
- Публичный `/webhook` принимает JSON и возвращает корректный ответ формата Алисы.

Перед отправкой на модерацию отправь 1-2 тестовых запроса в `/health` и `/webhook`,
чтобы исключить задержку первого запуска сервиса после простоя.

### 6. Что отправить преподавателю

1. Название навыка или ссылку на карточку навыка в Яндекс Диалогах.
2. Публичный webhook URL.
3. Скриншоты или короткое видео работы навыка в приложении Алисы.
4. Ссылку на страницу курса в Викиверситете.
