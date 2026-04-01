== Развёртывание навыка Петрозаводск Quiz на Render ==

=== Быстрое развёртывание (5 минут) ===

1. **Перейди на https://render.com** и создай аккаунт (через GitHub проще)

2. **В Render:**
   - Нажми "New" → "Web Service"
   - Выбери репозиторий `alice-petrozavodsk-game`
   - Настройки:
     * Name: любое имя (например, `petrozavodsk-quiz`)
     * Runtime: Python 3
     * Build command: `pip install -r requirements.txt`
     * Start command: `gunicorn app:app`
   - Нажми "Deploy"
   - Ждёшь 2-3 минуты, пока развернётся

3. **Когда развёрнется:**
   - Получишь URL вида: `https://petrozavodsk-quiz.onrender.com`
   - Проверь, что работает: https://твой-url.onrender.com/health
   - Должен вернуться статус `{"status": "ok"}`

4. **Webhook URL для Яндекс Диалогов:**
   - `https://твой-url.onrender.com/webhook`

=== Регистрация навыка в Яндекс Диалогах ===

1. **Перейди на https://dialogs.yandex.ru** (вход через Яндекс аккаунт)

2. **Создай новый навык:**
   - "Создать навык"
   - Название: "Петрозаводск Quiz" (или как хочешь)
   - Описание: "Угадай достопримечательности Петрозаводска"
   - Вкус: может быть любым

3. **Настроить webhook:**
   - Раздел "Интеграция" или "Webhook"
   - URL обработчика (HTTPS): `https://твой-url.onrender.com/webhook`
   - Сохрани

4. **Протестировать:**
   - In Yandex Assistant app or web interface: включи навык
   - Скажи "старт" или просто откройся навык
   - Начнётся игра

=== Что передаёшь преподавателю ===

Когда всё готово, дай преподавателю:
- Название навыка (как найти в Яндекс Диалогах)
- Или скриншот работающего навыка в приложении
- Webhook URL: `https://твой-url.onrender.com/webhook` (для проверки)
