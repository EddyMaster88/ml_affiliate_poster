import os
import time
import requests
from datetime import datetime, date
import random

# ============================================================
# VARIÁVEIS DE AMBIENTE
# ============================================================

MODO_TESTE_SECO = os.getenv("MODO_TESTE_SECO", "True").lower() == "true"
WHATS_DESTINO = os.getenv("WHATS_DESTINO")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

# Configurações avançadas
# Frequência de checagem do loop (segundos)
LOOP_SLEEP_SECONDS = int(os.getenv("LOOP_SLEEP_SECONDS", "60"))

# Janela de horário ativo (ex.: 8h às 20h)
ACTIVE_HOUR_START = int(os.getenv("ACTIVE_HOUR_START", "8"))
ACTIVE_HOUR_END = int(os.getenv("ACTIVE_HOUR_END", "20"))

# Blast da manhã
MORNING_HOUR = int(os.getenv("MORNING_HOUR", "8"))
MORNING_MIN_QTD = int(os.getenv("MORNING_MIN_QTD", "3"))
MORNING_MAX_QTD = int(os.getenv("MORNING_MAX_QTD", "5"))

# Ofertas por disparo horário
HOURLY_OFFERS_QTD = int(os.getenv("HOURLY_OFFERS_QTD", "3"))

# Lista de categorias (separadas por "|")
CATEGORIES = os.getenv(
    "CATEGORIES",
    "sabonete nivea|shampoo dove|perfume natura|fraldas pampers|luvas nitrílicas|creme nívea"
).split("|")


# ============================================================
# BUSCA DE PRODUTOS NO MERCADO LIVRE
# ============================================================

def buscar_produtos(query, limit=50):
    url = f"https://api.mercadolibre.com/sites/MLB/search?q={query}&limit={limit}"
    print(f"[INFO] Buscando produtos: {query}")

    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            print("[ERRO] Busca retornou:", resp.status_code)
            print("[ERRO] Corpo:", resp.text)
            print("[AVISO] usando produtos mockados")
            return produtos_mockados(query)

        data = resp.json()

    except Exception as e:
        print(f"[ERRO] Exceção em buscar_produtos: {e}")
        print("[AVISO] usando produtos mockados")
        return produtos_mockados(query)

    produtos = []
    for item in data.get("results", []):
        preco = item.get("price", 0)
        preco_original = item.get("original_price") or preco
        if preco_original:
            desconto = round((1 - preco / preco_original) * 100, 2)
        else:
            desconto = 0

        produtos.append({
            "title": item.get("title"),
            "price": preco,
            "price_original": preco_original,
            "desconto_pct": desconto,
            "thumbnail": item.get("thumbnail"),
            "permalink": item.get("permalink"),
        })

    # Ordenar por maior desconto
    produtos = sorted(produtos, key=lambda p: p["desconto_pct"], reverse=True)

    # Top 10 daquela categoria
    return produtos[:10]


# ============================================================
# MOCKS (FALLBACK QUANDO API DO ML FALHA)
# ============================================================

def produtos_mockados(query):
    return [
        {
            "title": f"Oferta destaque ({query})",
            "price": 19.90,
            "price_original": 29.90,
            "desconto_pct": 33,
            "thumbnail": "https://http2.mlstatic.com/D_NQ_NP_2X.webp",
            "permalink": "https://produto.mercadolivre.com.br/MLB-TESTE",
        },
        {
            "title": f"Combo promocional ({query})",
            "price": 39.90,
            "price_original": 59.90,
            "desconto_pct": 33,
            "thumbnail": "https://http2.mlstatic.com/D_NQ_NP_2X.webp",
            "permalink": "https://produto.mercadolivre.com.br/MLB-TESTE2",
        },
    ]


# ============================================================
# LINK DE AFILIADO (PLACEHOLDER)
# ============================================================

def gerar_link_afiliado(link):
    # Aqui você pluga sua lógica real de afiliado depois
    return link + "?aff=TESTE123"


# ============================================================
# ENVIO VIA WHATSAPP CLOUD
# ============================================================

def enviar_whats(destino, texto):
    if not destino:
        print("[ERRO] WHATS_DESTINO não configurado!")
        return

    print("\n====== PRÉ-VISUALIZAÇÃO DA MENSAGEM ======")
    print(f"Destino: {destino}")
    print(texto)
    print("==========================================\n")

    if MODO_TESTE_SECO:
        print("[MODO_TESTE_SECO] Mensagem NÃO enviada (modo teste ligado).")
        return

    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
        print("[ERRO] WHATSAPP_TOKEN ou WHATSAPP_PHONE_NUMBER_ID não configurados!")
        return

    url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": destino,
        "type": "text",
        "text": {"body": texto}
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        print("Status Whats:", resp.status_code)
        print("Resposta:", resp.text)
    except Exception as e:
        print(f"[ERRO] Falha ao enviar mensagem no WhatsApp: {e}")


# ============================================================
# FORMATAÇÃO DE MENSAGEM
# ============================================================

def montar_mensagem(titulo, produtos):
    texto = f"🔥 *{titulo}*\n\n"
    for p in produtos:
        texto += (
            f"🛒 *{p['title']}*\n"
            f"💰 De R$ {p['price_original']:.2f} por R$ {p['price']:.2f}\n"
            f"📉 Desconto: {p['desconto_pct']}%\n"
            f"🔗 {gerar_link_afiliado(p['permalink'])}\n\n"
        )
    return texto.strip()


# ============================================================
# ROTINAS DE ENVIO (MANHÃ + HORÁRIA)
# ============================================================

def enviar_burst_manha():
    print("[INFO] Envio do Boletim da Manhã")

    categoria_topo = CATEGORIES[0].strip()
    print(f"[INFO] Categoria do boletim da manhã: {categoria_topo}")

    produtos = buscar_produtos(categoria_topo)
    if not produtos:
        print("[AVISO] Nenhum produto retornado no boletim da manhã.")
        return

    qtd = random.randint(MORNING_MIN_QTD, MORNING_MAX_QTD)
    selecionados = produtos[:qtd]

    msg = montar_mensagem("Boletim de Ofertas da Manhã 🔥", selecionados)
    enviar_whats(WHATS_DESTINO, msg)


def enviar_oferta_horaria(hora_atual):
    # Escolhe categoria baseada na hora (pra variar automaticamente)
    idx = hora_atual % len(CATEGORIES)
    categoria = CATEGORIES[idx].strip()

    print(f"[INFO] Envio horário usando categoria: {categoria}")

    produtos = buscar_produtos(categoria)
    if not produtos:
        print("[AVISO] Nenhum produto retornado para envio horário.")
        return

    selecionados = produtos[:HOURLY_OFFERS_QTD]
    msg = montar_mensagem(f"Ofertas da hora – {categoria}", selecionados)
    enviar_whats(WHATS_DESTINO, msg)


# ============================================================
# LOOP PRINCIPAL COM AGENDAMENTO
# ============================================================

def main():
    print("==========================================")
    print("[INFO] Iniciando bot ml_affiliate_poster")
    print(f"[INFO] MODO_TESTE_SECO = {MODO_TESTE_SECO}")
    print(f"[INFO] LOOP_SLEEP_SECONDS = {LOOP_SLEEP_SECONDS}")
    print(f"[INFO] Janela ativa: {ACTIVE_HOUR_START}h às {ACTIVE_HOUR_END}h")
    print(f"[INFO] MORNING_HOUR = {MORNING_HOUR}")
    print(f"[INFO] Categorias: {CATEGORIES}")
    print("==========================================")

    ultima_data_burst = None
    ultima_hora_enviada = None

    while True:
        agora = datetime.now()
        hoje = agora.date()
        hora = agora.hour

        # 1) Blast da manhã (uma vez por dia)
        if hora == MORNING_HOUR and ultima_data_burst != hoje:
            try:
                enviar_burst_manha()
                ultima_data_burst = hoje
            except Exception as e:
                print(f"[ERRO] Exceção no burst da manhã: {e}")

        # 2) Envio de hora em hora dentro da janela ativa
        if ACTIVE_HOUR_START <= hora <= ACTIVE_HOUR_END:
            if ultima_hora_enviada != hora:
                try:
                    enviar_oferta_horaria(hora)
                    ultima_hora_enviada = hora
                except Exception as e:
                    print(f"[ERRO] Exceção nas ofertas horárias: {e}")

        time.sleep(LOOP_SLEEP_SECONDS)


if __name__ == "__main__":
    main()
