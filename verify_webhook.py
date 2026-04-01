"""Quick verification tool for public Alice webhook deployment.

Usage:
    python verify_webhook.py https://your-service.onrender.com
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request


def _fail(message: str) -> int:
    print(f"[FAIL] {message}")
    return 1


def _ok(message: str) -> None:
    print(f"[OK] {message}")


def check_health(base_url: str) -> int:
    health_url = f"{base_url}/health"
    try:
        with urllib.request.urlopen(health_url, timeout=15) as response:
            status = response.status
            body = response.read().decode("utf-8")
    except (urllib.error.URLError, TimeoutError) as exc:
        return _fail(f"Не удалось запросить {health_url}: {exc}")

    if status != 200:
        return _fail(f"{health_url} вернул статус {status}, ожидался 200")

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return _fail(f"{health_url} вернул не JSON: {body}")

    if payload.get("status") != "ok":
        return _fail(f"{health_url} вернул JSON без status=ok: {payload}")

    _ok(f"Health endpoint работает: {payload}")
    return 0


def check_webhook(base_url: str) -> int:
    webhook_url = f"{base_url}/webhook"
    payload = {
        "request": {"original_utterance": "старт"},
        "session": {"new": True, "user_id": "verify-user"},
    }
    body = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        webhook_url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            status = response.status
            response_body = response.read().decode("utf-8")
    except (urllib.error.URLError, TimeoutError) as exc:
        return _fail(f"Не удалось запросить {webhook_url}: {exc}")

    if status != 200:
        return _fail(f"{webhook_url} вернул статус {status}, ожидался 200")

    try:
        payload = json.loads(response_body)
    except json.JSONDecodeError:
        return _fail(f"{webhook_url} вернул не JSON: {response_body}")

    if payload.get("version") != "1.0":
        return _fail(f"Ответ webhook без version=1.0: {payload}")

    response = payload.get("response", {})
    if not isinstance(response.get("text"), str) or not response.get("text"):
        return _fail(f"Ответ webhook без текстовой реплики: {payload}")

    _ok("Webhook endpoint принимает запросы Яндекс Диалогов")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Использование: python verify_webhook.py https://your-service.onrender.com")
        return 2

    base_url = argv[1].strip().rstrip("/")
    if not base_url.startswith("http://") and not base_url.startswith("https://"):
        return _fail("URL должен начинаться с http:// или https://")

    result_health = check_health(base_url)
    result_webhook = check_webhook(base_url)

    if result_health == 0 and result_webhook == 0:
        print("\nГотово: публичный сервис можно подключать к навыку в Алисе.")
        return 0

    print("\nПроверка не пройдена. Исправь ошибки и запусти скрипт снова.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
