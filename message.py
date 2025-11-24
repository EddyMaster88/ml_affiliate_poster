from typing import Dict

def format_offer(item: Dict, affiliate_url: str) -> str:
    title = item.get("title","").strip()
    price = item.get("price")
    permalink = affiliate_url or item.get("permalink","")
    currency = item.get("currency_id","BRL")
    thumbnail = item.get("thumbnail") or (item.get("pictures", [{}])[0].get("url","") if item.get("pictures") else "")

    lines = [
        "🔥 *OFERTA QUENTE*",
        f"🛍️ {title}",
    ]
    if price:
        price_fmt = f"R$ {float(price):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        lines.append(f"💰 {price_fmt} ({currency})")
    if thumbnail:
        lines.append(f"🖼️ {thumbnail}")
    lines.append(f"👉 {permalink}")
    lines.append("")
    lines.append("⚡ Estoque limitado | *Aproveite!*")
    return "\n".join(lines)
