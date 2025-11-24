import requests
from bs4 import BeautifulSoup

from linkbuilder_selenium import gerar_link_afiliado
from whatsapp_cloud_api import enviar_whatsapp_imagem, enviar_whatsapp_texto


def extrair_dados_produto(url_produto: str) -> dict:
    """
    Acessa a página do produto e tenta pegar:
      - título
      - imagem principal
      - preço (simples)

    Primeiro tenta via requests; se der erro, devolve dados mínimos.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        resp = requests.get(url_produto, headers=headers, timeout=20)
        resp.raise_for_status()
    except Exception:
        # Se der erro, devolve um "fallback"
        print("[PRODUTO] Não consegui baixar HTML via requests, usando dados mínimos.")
        return {
            "titulo": "Oferta no Mercado Livre",
            "img_url": "",
            "preco": "",
            "url": url_produto,
        }

    soup = BeautifulSoup(resp.text, "html.parser")

    # Título
    titulo_el = soup.select_one("h1.ui-pdp-title")
    titulo = titulo_el.get_text(strip=True) if titulo_el else "Oferta no Mercado Livre"

    # Imagem principal (prefere og:image)
    og_img = soup.select_one('meta[property="og:image"]')
    if og_img and og_img.get("content"):
        img_url = og_img["content"]
    else:
        img_el = soup.select_one("img.ui-pdp-image")
        img_url = img_el["src"] if img_el and img_el.get("src") else ""

    # Preço (bem simples)
    preco_el = soup.select_one("span.andes-money-amount__fraction")
    preco = preco_el.get_text(strip=True) if preco_el else ""

    return {
        "titulo": titulo,
        "img_url": img_url,
        "preco": preco,
        "url": url_produto,
    }


def montar_texto_oferta(produto: dict, link_afiliado: str) -> str:
    """
    Monta o texto bonitinho pra postar no WhatsApp.
    """
    titulo = produto.get("titulo", "Oferta no Mercado Livre")
    preco = produto.get("preco", "")
    url = link_afiliado or produto.get("url", "")

    texto = f"""🟡 *{titulo}*

🔥 Oferta especial no Mercado Livre!

💰 Preço: R$ {preco} (ver no anúncio)

🔗 Meu link de afiliado:
{url}

⚠️ Preço e estoque podem mudar a qualquer momento.
"""
    return texto


def postar_oferta_whatsapp(url_produto: str, link_afiliado: str | None = None):
    """
    Fluxo completo:
      1. Gera link de afiliado (usando Selenium no Link Builder).
      2. Lê a página do produto e pega título, imagem, preço.
      3. Monta texto da oferta.
      4. Envia IMAGEM + TEXTO via WhatsApp (ou só texto se não achar imagem).
    """
    print(f"\n🚀 Processando produto: {url_produto}")

    # 1) Gera link afiliado se ainda não veio pronto
    if not link_afiliado:
        link_afiliado = gerar_link_afiliado(url_produto)

    if not link_afiliado:
        print("[ERRO] Não foi possível gerar o link afiliado. Abortando envio.")
        return

    # 2) Extrai dados do produto
    produto = extrair_dados_produto(url_produto)

    # 3) Monta texto
    texto = montar_texto_oferta(produto, link_afiliado)
    img_url = produto.get("img_url") or None

    # 4) Envia pro WhatsApp
    if img_url:
        print("[WHATSAPP] Enviando IMAGEM + TEXTO para o WhatsApp...")
        enviar_whatsapp_imagem(img_url, texto)
    else:
        print("[WHATSAPP] Não encontrei imagem. Enviando apenas TEXTO...")
        enviar_whatsapp_texto(texto)

    print("✅ Oferta enviada para o WhatsApp!")


if __name__ == "__main__":
    # TESTE: coloque aqui uma URL REAL de produto (pode ser a curtinha mesmo)
    url_teste = "https://produto.mercadolivre.com.br/MLB2518344642-ps5-slim-console-1tb"
    postar_oferta_whatsapp(url_teste)
