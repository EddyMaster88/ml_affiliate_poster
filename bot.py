import os
import time
import requests

# ============================================
#  VARIÁVEIS DE AMBIENTE
# ============================================

MODO_TESTE_SECO = os.getenv("MODO_TESTE_SECO", "True").lower() == "true"
WHATS_DESTINO = os.getenv("WHATS_DESTINO")  # Ex: 5511999999999
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
INTERVALO_MINUTOS = int(os.getenv("INTERVALO_MINUTOS", "60"))  # intervalo entre ciclos


# ============================================
# 1. Busca de produtos no Mercado Livre
# ============================================

def buscar_produtos(
    query,
    limit=30,
    desconto_minimo=25,
    somente_loja_oficial=True,
    frete_gratis=True,
):
    """
    Faz uma busca simples na API pública do Mercado Livre
    e aplica alguns filtros básicos.
    """

    url = f"https://api.mercadolibre.com/sites/MLB/search?q={query}&limit={limit}"
    print(f"[INFO] Buscando produtos no ML: {url}")

    try:
        resp = requests.get(url, timeout=10)

        if resp.status_code != 200:
            print(f"[ERRO] HTTP na busca de produtos: {resp.status_code}")
            print(f"[ERRO] URL chamada: {url}")
            print(f"[ERRO] Corpo da resposta: {resp.text}")
            print("[AVISO] usando produtos mockados")
            return produtos_mockados()

        data = resp.json()

    except Exception as e:
        print(f"[ERRO] Exceção em buscar_produtos: {e}")
        print("[AVISO] usando produtos mockados")
        return produtos_mockados()

    produtos_filtrados = []

    for item in data.get("results", []):
        preco = item.get("price", 0)
        preco_original = item.get("original_price") or preco

        if preco_original:
            desconto = round((1 - (preco / preco_original)) * 100, 2)
        else:
            desconto = 0

        if desconto < desconto_minimo:
            continue

        if somente_loja_oficial and not item.get("official_store_id"):
            continue

        if frete_gratis and not item.get("shipping", {}).get("free_shipping", False):
            continue

        produtos_filtrados.append(
            {
                "title": item.get("title"),
                "price": preco,
                "price_original": preco_original,
                "desconto_pct": desconto,
                "thumbnail": item.get("thumbnail"),
                "permalink": item.get("permalink"),
            }
        )

    print(f"[INFO] Produtos filtrados: {len(produtos_filtrados)}")
    return produtos_filtrados


# ============================================
# 2. Mock – usado quando a API do ML falha
# ============================================

def produtos_mockados():
    print("[AVISO] usando produtos mockados de exemplo")
    return [
        {
            "title": "Sabonete Nivea Suave 90g Kit c/ 3",
            "price": 18.90,
            "price_original": 27.90,
            "desconto_pct": 32,
            "thumbnail": "https://http2.mlstatic.com/D_NQ_NP_2X.webp",
            "permalink": "https://produto.mercadolivre.com.br/MLB-TEST3",
        },
        {
            "title": "Sabonete Nivea Creme Care 90g",
            "price": 6.99,
            "price_original": 9.99,
            "desconto_pct": 30,
            "thumbnail": "https://http2.mlstatic.com/D_NQ_NP_2X.webp",
            "permalink": "https://produto.mercadolivre.com.br/MLB-TEST2",
        },
        {
            "title": "Sabonete Nivea Proteção 90g",
            "price": 5.99,
            "price_original": 8.99,
            "desconto_pct": 31,
            "thumbnail": "https://http2.mlstatic.com/D_NQ_NP_2X.webp",
            "permalink": "https://produto.mercadolivre.com.br/MLB-TEST1",
        },
    ]


# ============================================
# 3. Link de afiliado (placeholder)
# ============================================

def gerar_link_afiliado(link_original: str) -> str:
    """
    Aqui você pluga sua lógica real de afiliado.
    Por enquanto, só adiciona um parâmetro fake.
    """
    return link_original + "?aff=TESTE123"


# ============================================
# 4. Envio via WhatsApp Cloud API
# ============================================

def enviar_oferta_whats(destino: str, produto: dict):
    if not destino:
        print("[ERRO] WHATS_DESTINO não foi configurado (None)")
        return

    texto_msg = (
        f"🛒 *{produto['title']}*\n"
        f"💰 De R$ {produto['price_original']:.2f} por R$ {produto['price']:.2f}\n"
        f"📉 Desconto de {produto['desconto_pct']}%\n"
        f"🔗 {produto['link_afiliado']}"
    )

    print("\n====== Pré-visualização da mensagem ======")
    print(f"Destino: {destino}")
    print(f"Imagem: {produto.get('thumbnail')}")
    print(texto_msg)
    print("==========================================")

    if MODO_TESTE_SECO:
        print("[MODO_TESTE_SECO] Mensagem NÃO enviada. Conteúdo seria o acima.")
        return

    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
        print("[ERRO] WHATSAPP_TOKEN ou WHATSAPP_PHONE_NUMBER_ID não configurados!")
        return

    url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": destino,
        "type": "text",
        "text": {"body": texto_msg},
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"Status Whats: {resp.status_code}")
        print(resp.text)
    except Exception as e:
        print(f"[ERRO] Falha ao enviar mensagem no WhatsApp: {e}")


# ============================================
# 5. Seleção de ofertas
# ============================================

def escolher_ofertas_para_postar():
    produtos = buscar_produtos(
        query="sabonete nivea",
        limit=30,
        desconto_minimo=25,
        somente_loja_oficial=True,
        frete_gratis=True,
    )

    produtos_ordenados = sorted(
        produtos, key=lambda p: p["desconto_pct"], reverse=True
    )
    # top 3
    return produtos_ordenados[:3]


# ============================================
# 6. Execução de um ciclo
# ============================================

def postar_ofertas_no_destino():
    ofertas = escolher_ofertas_para_postar()

    for produto in ofertas:
        produto["link_afiliado"] = gerar_link_afiliado(produto["permalink"])
        enviar_oferta_whats(WHATS_DESTINO, produto)


# ============================================
# 7. LOOP PRINCIPAL (Railway)
# ============================================

def main():
    print("==========================================")
    print("[INFO] Iniciando bot ml_affiliate_poster")
    print(f"[INFO] MODO_TESTE_SECO = {MODO_TESTE_SECO}")
    print(f"[INFO] INTERVALO_MINUTOS = {INTERVALO_MINUTOS}")
    print("==========================================")

    while True:
        print("\n[INFO] ===== Novo ciclo de envio =====")
        try:
            postar_ofertas_no_destino()
            print("[INFO] Ciclo concluído com sucesso.")
        except Exception as e:
            # Nunca deixar o processo morrer
            print(f"[ERRO] Exceção no ciclo principal: {e}")

        print(f"[INFO] Aguardando {INTERVALO_MINUTOS} minutos para o próximo ciclo...")
        time.sleep(INTERVALO_MINUTOS * 60)


if __name__ == "__main__":
    main()
