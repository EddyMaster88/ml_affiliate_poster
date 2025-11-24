import requests
import json

TOKEN = "EAAT1dW1k8xABP2o5cBFVaiGzCmNZCVZBjIMnuTzcYkFIOFwmkg6H3tFZCgd8ZCCfQhYZAEAo6A9aJPSvb2rxGQpConFh2Ei5a29ZC6R1i2ZA4UFYGXWy3sqfZCmpNcZCrdGW5IgFO8qBZBSG41xp9bZBZA8ENLmUkDmrpwGbgAoZBLXj1FO0djO9mhnaHzslZBeiv98y2t6epxaPVmcT85m6kLbtM45agZAG9A3YNnaM1MXfKHzZCU46srgxZBka8Vs3CtxQnIE69sVGgMIeaCNq8plsKZBCOXZCF0ohgZDZD"
PHONE_NUMBER_ID = "868762336321984"  # este é o que aparece na sua tela
RECIPIENT = "5541999124817"

url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

body = {
    "messaging_product": "whatsapp",
    "to": RECIPIENT,
    "type": "text",
    "text": {"body": "🔵 Teste enviado com sucesso pela WhatsApp Cloud API!"}
}

response = requests.post(url, headers=headers, data=json.dumps(body))
print("Status:", response.status_code)
print("Resposta:", response.text)
