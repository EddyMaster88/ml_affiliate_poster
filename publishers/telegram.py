import requests
from typing import Optional

def send_message(bot_token: str, chat_id: str, text: str, parse_mode: str = "Markdown") -> None:
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode, "disable_web_page_preview": False}
    r = requests.post(url, json=data, timeout=20)
    r.raise_for_status()

def send_photo(bot_token: str, chat_id: str, photo_url: str, caption: Optional[str] = None, parse_mode: str = "Markdown") -> None:
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    data = {"chat_id": chat_id, "photo": photo_url}
    if caption:
        data["caption"] = caption
        data["parse_mode"] = parse_mode
    r = requests.post(url, json=data, timeout=20)
    r.raise_for_status()
