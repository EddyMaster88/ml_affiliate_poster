import requests
import json

# ====================================
# CONFIGURAÇÃO - EDITE ESTES CAMPOS
# ====================================

# Token TEMPORÁRIO gerado em:
# Casos de uso -> Conectar no WhatsApp -> Testes de API -> "Gerar token de acesso"
WHATSAPP_TOKEN = "COLE_SEU_TOKEN_AQUI"

# ID do número de telefone (aparece em "Identificação do número de telefone")
PHONE_NUMBER_ID = "868762336321984"

# Número padrão para receber as ofertas (você)
# Formato: DDI + DDD + número, sem + e sem espaços
DESTINO_PADRAO = "5541999124817"


# ====================================
# FUNÇÕES DE ENVIO
# ====================================

def enviar_whatsapp_texto(mensagem: str, numero_destino: str = None):
    """Envia uma mensagem de TEXTO via WhatsApp Cloud API."""
    if numero_destino is None:
        numero_destino = DESTINO_PADRAO

    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": numero_destino,
        "type": "text",
        "text": {"body": mensagem}
    }

    resp = requests.post(url, headers=headers, data=json.dumps(payload))
    print("[WHATSAPP][TEXTO]", resp.status_code, resp.text)
    return resp


def enviar_whatsapp_imagem(img_url: str, legenda: str, numero_destino: str = None):
    """Envia IMAGEM + LEGENDA via WhatsApp Cloud API (imagem por link)."""
    if numero_destino is None:
        numero_destino = DESTINO_PADRAO

    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": numero_destino,
        "type": "image",
        "image": {
            "link": img_url,
            "caption": legenda
        }
    }

    resp = requests.post(url, headers=headers, data=json.dumps(payload))
    print("[WHATSAPP][IMAGEM]", resp.status_code, resp.text)
    return resp


# Teste rápido chamando diretamente este arquivo
if __name__ == "__main__":
    texto = "Teste do módulo whatsapp_cloud_api.py 🚀"
    enviar_whatsapp_texto(texto)
