from dataclasses import dataclass
from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

def _as_bool(v: Optional[str], default=False):
    if v is None:
        return default
    return v.strip().lower() in {"1","true","yes","y","on"}

@dataclass(frozen=True)
class Config:
    categories: List[str]
    top_n: int
    telegram_bot_token: Optional[str]
    telegram_chat_id: Optional[str]
    whatsapp_number: Optional[str]
    headless: bool
    chrome_user_data_dir: Optional[str]
    chrome_binary_path: Optional[str]
    download_images: bool
    dry_run: bool
    seen_path: str

    @staticmethod
    def load() -> "Config":
        cats = [c.strip() for c in os.getenv("ML_CATEGORIES","").split(",") if c.strip()]
        return Config(
            categories=cats,
            top_n=int(os.getenv("TOP_N","5")),
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
            telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID"),
            whatsapp_number=os.getenv("WHATSAPP_NUMBER"),
            headless=_as_bool(os.getenv("HEADLESS","true"), True),
            chrome_user_data_dir=os.getenv("CHROME_USER_DATA_DIR"),
            chrome_binary_path=os.getenv("CHROME_BINARY_PATH"),
            download_images=_as_bool(os.getenv("DOWNLOAD_IMAGES","true"), True),
            dry_run=_as_bool(os.getenv("DRY_RUN","false"), False),
            seen_path=os.getenv("SEEN_PATH","data/seen.json"),
        )
