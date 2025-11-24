# bot_ofertas.py
from typing import List, Dict

from linkbuilder_selenium import conectar_chrome, gerar_link_afiliado
from whatsapp import abrir_whatsapp, abrir_conversa, enviar_mensagem

# Nome do grupo / conversa no WhatsApp Business Web
# (texto que aparece dentro do título e NÃO precisa de emoji)
NOME_CONVERSA = "Ofertas Mercado Livre"

# Lista de produtos de exemplo
# Depois você pode carregar isso de um CSV, banco, API etc.
PRODUTOS: List[Dict[str, str]] = [
    {
        "nome": "Console PlayStation 5 Slim Digital 825GB - Branco",
        "preco": "R$ 3.499,00",
        "url": "https://www.mercadolivre.com.br/console-playstation-5-slim-digital-825gb-branco/p/MLB57081243?pdp_filters=item_id%3AMLB4214670787#polycard_client=affiliates&wid=MLB4214670787&sid=affiliates"
    },
]

def montar_mensagem(produto: Dict[str, str], link_afiliado: str) -> str:
    """
    Monta a mensagem que será enviada no grupo.

    OBS: o whatsapp.py já remove emojis fora do BMP,
    então aqui você pode até usar emoji simples se quiser.
    """
    nome = produto.get("nome", "Oferta")
    preco = produto.get("preco", "").strip()
    preco_str = f"\nPreço: {preco}" if preco else ""

    msg = (
    f"OFERTA\n\n"  # ou "OFERTA 🔥" se você quiser deixar e confiar no filtro
)

    return msg


def enviar_ofertas(produtos: List[Dict[str, str]]) -> None:
    """
    - Conecta no Chrome em modo debug
    - Gera link de afiliado para cada produto
    - Abre WhatsApp
    - Abre o grupo
    - Envia uma mensagem por produto
    """
    # 1) Conectar no Chrome já aberto em debug
    driver = conectar_chrome()

    for idx, produto in enumerate(produtos, start=1):
        print(f"\n========== PRODUTO {idx} ==========")
        url_produto = produto["url"]
        print(f"[BOT] Gerando link afiliado para: {url_produto}")

        # 2) Gerar link no Mercado Livre (isso navega para outras páginas)
        link_afiliado = gerar_link_afiliado(url_produto, driver=driver)

        if not link_afiliado:
            print("[BOT] ERRO ao gerar link de afiliado. Pulando este produto.")
            continue

        print(f"[BOT] Link afiliado gerado: {link_afiliado}")

        mensagem = montar_mensagem(produto, link_afiliado)

        # 3) VOLTAR PARA O WHATSAPP ANTES DE ENVIAR
        print(f"[BOT] Voltando para o WhatsApp e abrindo conversa '{NOME_CONVERSA}'...")
        abrir_whatsapp(driver)              # navega de volta para https://web.whatsapp.com
        abrir_conversa(driver, NOME_CONVERSA)

        print(f"[BOT] Enviando mensagem para o grupo '{NOME_CONVERSA}'...")
        enviar_mensagem(driver, mensagem)

    print("\n[BOT] Fim do envio de ofertas!")



def main():
    enviar_ofertas(PRODUTOS)


if __name__ == "__main__":
    main()
