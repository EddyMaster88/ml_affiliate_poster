import os
import urllib.parse
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("ML_CLIENT_ID")
CLIENT_SECRET = os.getenv("ML_CLIENT_SECRET")
REDIRECT_URI = os.getenv("ML_REDIRECT_URI")

AUTH_BASE = "https://auth.mercadolivre.com.br/authorization"
TOKEN_URL = "https://api.mercadolibre.com/oauth/token"

def gerar_url_autorizacao():
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
    }
    return f"{AUTH_BASE}?{urllib.parse.urlencode(params)}"

def trocar_code_por_token(code: str):
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    resp = requests.post(TOKEN_URL, data=data)
    print("Status:", resp.status_code)
    print("Resposta JSON:", resp.text)

if __name__ == "__main__":
    print("\nAbra esta URL no navegador, faça login e autorize a aplicação:\n")
    print(gerar_url_autorizacao())
    print("\nDepois copie o parâmetro 'code' da URL exibida após a autorização.\n")

    code = input("Cole aqui o valor de 'code': ").strip()
    trocar_code_por_token(code)
