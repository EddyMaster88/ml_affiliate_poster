# -*- coding: utf-8 -*-
import time
from typing import Optional, List

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


WPP_URL = "https://web.whatsapp.com/"


def _log(msg: str) -> None:
    print(f"[WPP] {msg}")


def _remove_non_bmp(text: str) -> str:
    """
    Remove caracteres fora do BMP (ex: alguns emojis) para evitar:
    'ChromeDriver only supports characters in the BMP'.
    """
    if not isinstance(text, str):
        text = str(text)
    return "".join(ch for ch in text if ord(ch) <= 0xFFFF)


def _esperar_elemento(
    driver,
    by: By,
    selector: str,
    timeout: int = 30,
    cond=EC.visibility_of_element_located,
):
    return WebDriverWait(driver, timeout).until(
        cond((by, selector))
    )


def _tentar_seletores(
    driver,
    seletores: List[str],
    timeout_total: int = 30,
    cond=EC.visibility_of_element_located,
) -> Optional[object]:
    inicio = time.time()
    ultima_exc = None

    for sel in seletores:
        restante = timeout_total - (time.time() - inicio)
        if restante <= 0:
            break

        try:
            _log(f"Tentando seletor: {sel}")
            elem = WebDriverWait(driver, restante).until(
                cond((By.CSS_SELECTOR, sel))
            )
            _log(f"Elemento encontrado com seletor: {sel}")
            return elem
        except Exception as e:
            ultima_exc = e
            _log(f"[WARN] Falha com seletor {sel}: {type(e).__name__}")

    if ultima_exc:
        _log("[ERRO] Não foi possível localizar o elemento com os seletores testados.")
        _log(str(ultima_exc))
    return None


# ======================================================================
#   ABRIR WHATSAPP
# ======================================================================

def abrir_whatsapp(driver) -> None:
    _log(f"Abrindo WhatsApp Web: {WPP_URL}")
    driver.get(WPP_URL)

    try:
        _tentar_seletores(
            driver,
            seletores=[
                "canvas[aria-label='Scan me!']",
                "div[role='textbox'][contenteditable='true']",
                "header",
            ],
            timeout_total=60,
        )
        _log("WhatsApp Web carregado.")
    except Exception:
        _log("[ERRO] Timeout ao carregar o WhatsApp Web.")
        raise


# ======================================================================
#   BUSCAR E ABRIR CONVERSA
# ======================================================================

def _obter_campo_busca(driver):
    seletores_busca = [
        "div[contenteditable='true'][role='textbox']",
        "div[contenteditable='true'][data-tab='3']",
        "div[contenteditable='true'][data-tab]",
        "div[contenteditable='true']",
    ]
    return _tentar_seletores(driver, seletores_busca, timeout_total=30)


def abrir_conversa(driver, nome_conversa: str) -> None:
    """
    Usa a barra de busca para localizar e abrir a conversa.
    Busca por PARTE do título (contains) para não depender de emoji.
    """
    _log(f"Abrindo conversa com: '{nome_conversa}'")

    campo_busca = _obter_campo_busca(driver)
    if not campo_busca:
        raise TimeoutException("Não foi possível encontrar o campo de busca.")

    texto_busca = _remove_non_bmp(nome_conversa)
    campo_busca.click()
    campo_busca.clear()
    campo_busca.send_keys(texto_busca)
    time.sleep(1.8)

    # Procurar por span cujo title contém esse texto
    xpaths = [
        f"//span[contains(@title, \"{texto_busca}\")]",
        f"//div[@role='gridcell']//span[contains(@title, \"{texto_busca}\")]",
        f"//span[@dir='auto' and contains(., \"{texto_busca}\")]",
    ]

    conversa_elem = None
    ultima_exc = None
    for xp in xpaths:
        try:
            _log(f"Tentando localizar conversa com XPath: {xp}")
            conversa_elem = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, xp))
            )
            break
        except Exception as e:
            ultima_exc = e
            _log(f"[WARN] Conversa não encontrada com XPath: {xp}")

    if not conversa_elem:
        _log(f"[ERRO] Não achei a conversa contendo: '{texto_busca}'")
        if ultima_exc:
            _log(str(ultima_exc))
        raise TimeoutException(f"Conversa contendo '{texto_busca}' não encontrada.")

    conversa_elem.click()
    _log(f"Conversa contendo '{texto_busca}' aberta.")
    time.sleep(1.5)


# ======================================================================
#   ENVIAR MENSAGEM
# ======================================================================

def _obter_campo_mensagem(driver):
    seletores_mensagem = [
        "footer div[contenteditable='true'][data-tab='10']",
        "footer div[contenteditable='true']",
        "div[contenteditable='true'][data-tab='10']",
        "div[contenteditable='true'][data-tab='6']",
        "div[contenteditable='true']",
    ]
    return _tentar_seletores(
        driver,
        seletores=seletores_mensagem,
        timeout_total=30,
        cond=EC.visibility_of_element_located,
    )


def _obter_botao_enviar(driver):
    seletores_botao = [
        "button[aria-label='Enviar']",
        "span[data-icon='send']",
        "span[data-icon='send-outline']",
        "div[role='button'][aria-label*='Enviar']",
        "button[aria-label*='send']",
    ]
    return _tentar_seletores(
        driver,
        seletores=seletores_botao,
        timeout_total=10,
        cond=EC.element_to_be_clickable,
    )

def _encontrar_campo_mensagem(driver, timeout: int = 30):
    """
    Tenta encontrar o campo de mensagem do WhatsApp Web usando vários seletores.
    """
    seletores = [
        "div[contenteditable='true'][role='textbox']",                 # mais moderno
        "footer div[contenteditable='true'][contenteditable='true']",  # fallback genérico
        "footer div[contenteditable='true'][data-tab='10']",           # seletor antigo
    ]

    for sel in seletores:
        try:
            print(f"[WPP] Tentando seletor de mensagem: {sel}")
            campo = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, sel))
            )
            print(f"[WPP] Campo de mensagem encontrado com seletor: {sel}")
            return campo
        except TimeoutException:
            print(f"[WPP] [WARN] Falha com seletor {sel}: TimeoutException")

    raise TimeoutException("Campo de mensagem não encontrado.")


def enviar_mensagem(driver, mensagem: str):
    """
    Envia uma mensagem na conversa já aberta.
    """
    from time import sleep

    campo = _encontrar_campo_mensagem(driver)

    # clica para focar
    campo.click()
    sleep(0.5)

    # digita a mensagem
    campo.send_keys(mensagem)
    sleep(0.5)

    # ENTER para enviar
    campo.send_keys(Keys.ENTER)
    print("[WPP] Mensagem enviada.")
