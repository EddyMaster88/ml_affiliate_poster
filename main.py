from typing import List, Dict
from pathlib import Path

from .config import Config
from .ml_api import top_sellers_by_category, get_item_details
from .linkbuilder_selenium import LinkBuilder
from .message import format_offer
from .publishers import telegram as tg
from .publishers import whatsapp as wa
from .publishers import x_poster
from .media import download_image
from .seen import SeenDB

def build_and_publish():
    cfg = Config.load()
    if not cfg.categories:
        raise SystemExit("Defina ML_CATEGORIES no .env, ex: MLB1051,MLB1648")

    seen = SeenDB(Path(cfg.seen_path))

    # Instancia LinkBuilder
    lb = LinkBuilder(headless=cfg.headless, user_data_dir=cfg.chrome_user_data_dir, chrome_binary_path=cfg.chrome_binary_path)
    lb.ensure_logged_in()

    exported_rows: List[Dict] = []
    media_dir = Path(__file__).resolve().parent.parent / "data" / "media"

    try:
        for cat in cfg.categories:
            items = top_sellers_by_category(cat, cfg.top_n)
            for it in items:
                item_id = it.get("id")
                if not item_id or seen.has(item_id):
                    continue

                full = get_item_details(item_id)
                product_url = full.get("permalink") or it.get("permalink")
                if not product_url:
                    continue

                # Gera link afiliado (com fallback)
                try:
                    aff = lb.build_affiliate(product_url)
                except Exception as e:
                    aff = product_url
                    print(f"[WARN] Afiliado falhou para {item_id}: {e}")

                msg = format_offer(full or it, aff)

                # Imagem (URL → local para WhatsApp)
                thumb_url = None
                try:
                    thumb_url = full.get("pictures", [{}])[0].get("url") or it.get("thumbnail")
                except Exception:
                    pass

                local_img = None
                if cfg.download_images and thumb_url:
                    try:
                        local_img = str(download_image(thumb_url, media_dir))
                    except Exception as e:
                        print(f"[WARN] Falha ao baixar imagem: {e}")

                # Publicação (respeita DRY_RUN)
                if cfg.dry_run:
                    print("---- DRY_RUN ----")
                    print(msg)
                    print(f"(TG chat={cfg.telegram_chat_id}) (WA={cfg.whatsapp_number}) (IMG={local_img})")
                else:
                    # Telegram
                    if cfg.telegram_bot_token and cfg.telegram_chat_id:
                        try:
                            if thumb_url:
                                tg.send_photo(cfg.telegram_bot_token, cfg.telegram_chat_id, photo_url=thumb_url, caption=msg)
                            else:
                                tg.send_message(cfg.telegram_bot_token, cfg.telegram_chat_id, msg)
                        except Exception as e:
                            print(f"[WARN] Telegram: {e}")

                    # WhatsApp
                    if cfg.whatsapp_number:
                        try:
                            wa.send_whatsapp(cfg.whatsapp_number, msg, image_path=local_img)
                        except Exception as e:
                            print(f"[WARN] WhatsApp: {e}")

                # Export / mark seen
                exported_rows.append({
                    "category": cat,
                    "item_id": item_id,
                    "title": full.get("title"),
                    "price": full.get("price"),
                    "affiliate_url": aff,
                    "permalink": product_url
                })
                seen.add(item_id)

    finally:
        lb.close()
        seen.save()

    out = Path(__file__).resolve().parent.parent / "data" / "exports" / "ml_offers.csv"
    x_poster.export_to_csv(exported_rows, out)
    print(f"Export salvo em: {out}")

if __name__ == "__main__":
    build_and_publish()
