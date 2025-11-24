import os
import requests
from dotenv import load_dotenv

load_dotenv()

# ===== CONFIG GERAL =====
AFILIADO_PARAM = os.getenv("AFILIADO_PARAM")

WHATS_TOKEN = os.getenv("WHATS_TOKEN")
WHATS_PHONE_NUMBER_ID = os.getenv("WHATS_PHONE_NUMBER_ID")
WHATS_DESTINO = os.getenv("WHATS_DESTINO")

BASE_MELI = "https://api.mercadolibre.com"
BASE_WHATS = "https://graph.facebook.com/v19.0"

# Modo teste (apenas imprime ↔ envia real)
MODO_TESTE_SECO = os.getenv("MODO_TESTE_SECO", "true").lower() == "true"


# ===== MOCK DE PRODUTOS =====

def produtos_mockados():
    return [
        {
            "id": "MLBTEST1",
            "titulo": "Sabonete Nivea Creme Care 90g",
            "preco": 6.99,
            "preco_original": 9.99,
            "desconto_pct": 30,
            "categoria_id": "TEST",
            "permalink": "https://produto.mercadolivre.com.br/MLB-TEST1",
            "image_url": "https://http2.mlstatic.com/D_NQ_NP_2X_651980-MLB1234567890_012025-F.webp",
        },
        {
            "id": "MLBTEST2",
            "titulo": "Sabonete Nivea Erva Doce 85g",
            "preco": 5.49,
            "preco_original": 7.99,
            "desconto_pct": 31,
            "categoria_id": "TEST",
            "permalink": "https://produto.mercadolivre.com.br/MLB-TEST2",
            "image_url": "https://http2.mlstatic.com/D_NQ_NP_2X_999999-MLB1234567891_012025-F.webp",
        },
        {
            "id": "MLBTEST3",
            "titulo": "Sabonete Nivea Suave 90g Kit c/ 3",
            "preco": 18.90,
            "preco_original": 27.90,
            "desconto_pct": 32,
            "categoria_id": "TEST",
            "permalink": "https://produto.mercadolivre.com.br/MLB-TEST3",
            "image_url": "https://http2.mlstatic.com/D_NQ_NP_2X_888888-MLB1234567892_012025-F.webp",
        },
    ]


# ===== 1. Busca pública SEM TOKEN =====

def buscar_produtos(
    query=None,
    category_id=None,
    limit=20,
    desconto_minimo=20,
    somente_loja_oficial=False,
    frete_gratis=False,
):
    """
    Busca produtos no /sites/MLB/search SEM token.
    Se der erro (403, etc.), cai no mock.
    """
    url = f"{BASE_MELI}/sites/MLB/search"

    params = {
        "limit": limit,
        "sort": "relevance",
    }

    if query:
        params["q"] = query
    if category_id:
        params["category"] = category_id

    # Header “de gente”, imitando browser
    headers = {
        "Accept": "application/json",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36 ml_affiliate_poster/1.0"
        ),
    }

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)

        if resp.status_code != 200:
            print("[ERRO] HTTP na busca de produtos:", resp.status_code)
            print("[ERRO] URL chamada:", resp.url)
            print("[ERRO] Corpo da resposta:", resp.text)
            # log extra pra investigar com o suporte do ML
            print("[DEBUG] Response headers:", dict(resp.headers))
            print("[DEBUG] Request headers usados:", dict(resp.request.headers))
            print("[AVISO] usando produtos mockados")
            return produtos_mockados()

        data = resp.json()

    except Exception as e:
        print("[ERRO] Falha na chamada ao Mercado Livre:", repr(e))
        print("[AVISO] usando produtos mockados")
        return produtos_mockados()

    resultados = data.get("results", [])
    produtos = []

    for item in resultados:
        price = item.get("price")
        original_price = item.get("original_price") or price
        if not price:
            continue

        # Loja oficial
        if somente_loja_oficial and not item.get("official_store_id"):
            continue

        # Desconto %
        desconto_pct = 0
        if original_price and original_price > price:
            desconto_pct = round((1 - price / original_price) * 100, 1)

        if desconto_pct < desconto_minimo:
            continue

        # Frete grátis — filtrado em código
        if frete_gratis and not item.get("shipping", {}).get("free_shipping"):
            continue

        produtos.append({
            "id": item["id"],
            "titulo": item["title"],
            "preco": price,
            "preco_original": original_price,
            "desconto_pct": desconto_pct,
            "categoria_id": item.get("category_id"),
            "permalink": item.get("permalink"),
            "image_url": item.get("thumbnail"),
            "official_store_id": item.get("official_store_id"),
            "shipping_free": item.get("shipping", {}).get("free_shipping"),
        })

    return produtos if produtos else produtos_mockados()


# ===== 2. Link de afiliado =====

def gerar_link_afiliado(url_produto: str) -> str:
    if not AFILIADO_PARAM:
        return url_produto
    separador = "&" if "?" in url_produto else "?"
    return f"{url_produto}{separador}{AFILIADO_PARAM}"


# ===== 3. Mensagem =====

def montar_mensagem_oferta(produto: dict) -> str:
    return f"""ISSO AQUI EM MUITO LUGAR TÁ BEM MAIS CARO 👀

✅ {produto['titulo']}

🔥 POR R$ {produto['preco']:.2f} (de R$ {produto['preco_original']:.2f})
💸 Desconto de {produto['desconto_pct']:.0f}% OFF

🔗 {produto['link_afiliado']}
"""


# ===== 4. WhatsApp =====

def enviar_oferta_whats(destino: str, produto: dict):

    mensagem = montar_mensagem_oferta(produto)

    if MODO_TESTE_SECO:
        print("[MODO_TESTE_SECO] Mensagem NÃO enviada. Conteúdo seria:")
        print("Destino:", destino)
        print("Imagem:", produto.get("image_url"))
        print(mensagem)
        return

    headers = {
        "Authorization": f"Bearer {WHATS_TOKEN}",
        "Content-Type": "application/json"
    }

    url = f"{BASE_WHATS}/{WHATS_PHONE_NUMBER_ID}/messages"

    if produto.get("image_url"):
        payload = {
            "messaging_product": "whatsapp",
            "to": destino,
            "type": "image",
            "image": {
                "link": produto["image_url"],
                "caption": mensagem
            }
        }
    else:
        payload = {
            "messaging_product": "whatsapp",
            "to": destino,
            "type": "text",
            "text": {"body": mensagem}
        }

    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    print("Status Whats:", resp.status_code, resp.text)


# ===== 5. Seleção =====

def escolher_ofertas_para_postar():
    produtos = buscar_produtos(
        query="sabonete nivea",
        limit=30,
        desconto_minimo=25,
        somente_loja_oficial=True,
        frete_gratis=True,
    )

    produtos_ordenados = sorted(produtos, key=lambda p: p["desconto_pct"], reverse=True)
    return produtos_ordenados[:3]


# ===== 6. Execução =====

def postar_ofertas_no_destino():
    ofertas = escolher_ofertas_para_postar()

    for produto in ofertas:
        produto["link_afiliado"] = gerar_link_afiliado(produto["permalink"])
        enviar_oferta_whats(WHATS_DESTINO, produto)


def main():
    print(f"[INFO] MODO_TESTE_SECO = {MODO_TESTE_SECO}")
    postar_ofertas_no_destino()


if __name__ == "__main__":
    main()
