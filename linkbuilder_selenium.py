import time
from typing import Optional
import re  # ✅ ADICIONE ESTA LINHA

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys  # ✅ novo import

# URL do Link Builder
LINK_BUILDER_URL = "https://www.mercadolivre.com.br/afiliados/linkbuilder#hub"


def _log(msg: str) -> None:
    print(f"[LINK] {msg}")


def conectar_chrome() -> webdriver.Chrome:
    """
    Conecta em um Chrome já aberto com debug na porta 9222.

    Exemplo de comando para abrir o Chrome manualmente:
      chrome.exe --remote-debugging-port=9222 --user-data-dir=\"C:/chrome-debug\"

    (Mantém seu login do Mercado Livre.)
    """
    _log("Conectando ao Chrome na porta 9222...")
    options = webdriver.ChromeOptions()
    options.debugger_address = "127.0.0.1:9222"
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    return driver


def _esperar_elemento(driver, by, selector, timeout=30):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, selector))
    )


def obter_url_canonica_no_navegador(driver, url_produto: str) -> str:
    """
    Abre a URL do produto no próprio Chrome (logado) e devolve a URL final
    (geralmente a versão longa, com o nome do produto), que o Link Builder aceita.
    """
    _log(f"Abrindo produto para obter URL canônica: {url_produto}")
    driver.get(url_produto)

    try:
        # Espera o título do produto aparecer
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1.ui-pdp-title"))
        )
    except TimeoutException:
        _log("[WARN] Não achei o título do produto, usando current_url mesmo assim.")

    url_final = driver.current_url.strip()
    _log(f"URL canônica obtida no navegador: {url_final}")
    return url_final


def _encontrar_textarea_entrada(driver):
    """
    Encontra o textarea (campo de entrada) no Link Builder.
    """
    _log("Aguardando textarea do Link Builder...")
    textarea = _esperar_elemento(
        driver, By.CSS_SELECTOR, "textarea.andes-form-control__field", timeout=60
    )
    return textarea


def _encontrar_botao_gerar(driver, timeout: int = 60):
    """
    Procura o botão 'Gerar' já habilitado e clicável.
    """
    _log("Procurando botão 'Gerar' clicável...")
    botao = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Gerar')]"))
    )
    _log("Botão 'Gerar' localizado e clicável.")
    return botao

def _extrair_primeiro_link_afiliado(texto: str) -> Optional[str]:
    """
    Procura a primeira URL do ML com '/sec/' dentro do texto.
    """
    if not texto:
        return None

    # acha qualquer http(s)://...
    candidatos = re.findall(r"https?://[^\s]+", texto)
    for url in candidatos:
        if "mercadolivre.com" in url and "/sec/" in url:
            return url

    return None

def _esperar_link_gerado(driver, timeout=60) -> Optional[str]:
    """
    Espera o ML gerar o link e varre inputs, textareas e divs,
    extraindo apenas a URL curta (https://mercadolivre.com/sec/...).
    """
    _log("Aguardando link gerado aparecer (varrendo inputs, textareas e innerText)...")

    fim = time.time() + timeout

    while time.time() < fim:
        campos = driver.find_elements(By.CSS_SELECTOR, "input, textarea, div")

        for c in campos:
            textos = [
                (c.get_attribute("value") or "").strip(),
                (c.get_attribute("innerText") or "").strip(),
                (c.text or "").strip(),
            ]

            for t in textos:
                link = _extrair_primeiro_link_afiliado(t)
                if link:
                    _log(f"Link encontrado: {link}")
                    return link

        time.sleep(1)

    _log("[ERRO] Não foi possível encontrar o link depois do timeout. Salvando HTML...")
    try:
        with open("debug_linkbuilder.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
    except Exception as e:
        _log(f"[WARN] Falha ao salvar debug_linkbuilder.html: {e}")

    return None


def gerar_link_afiliado(
    url_produto: str, driver: Optional[webdriver.Chrome] = None
) -> Optional[str]:
    """
    Fluxo:
      1. Abre a página do produto no Chrome e pega a URL canônica.
      2. Abre o Link Builder.
      3. Digita a URL canônica no textarea (como usuário).
      4. Clica em 'Gerar'.
      5. Lê o link curto gerado.
    """
    _log(f"GERANDO LINK PARA PRODUTO: {url_produto}")

    criado_driver = False
    if driver is None:
        driver = conectar_chrome()
        criado_driver = True

    try:
        # 1) Obter URL canônica via navegador (sem usar requests)
        url_canonica = obter_url_canonica_no_navegador(driver, url_produto)

        # 2) Abrir Link Builder
        _log(f"Abrindo Link Builder: {LINK_BUILDER_URL}")
        driver.get(LINK_BUILDER_URL)

        # 3) Digitar a URL no textarea como se fosse um usuário
        textarea = _encontrar_textarea_entrada(driver)
        _log("Inserindo URL do produto no textarea...")
        textarea.clear()
        textarea.send_keys(url_canonica)
        textarea.send_keys(Keys.ENTER)

        # 4) Clicar em "Gerar" quando estiver habilitado
        botao_gerar = _encontrar_botao_gerar(driver)
        _log("Clicando em 'Gerar'...")
        botao_gerar.click()

        # 5) Esperar link curto aparecer
        link = _esperar_link_gerado(driver, timeout=60)
        if not link:
            _log("[ERRO] Timeout esperando link de afiliado aparecer.")
            return None

        _log(f"✅ LINK GERADO: {link}")
        return link

    except Exception as e:
        _log(f"[ERRO] Não foi possível gerar o link: {e}")
        return None

    finally:
        # NÃO fecha o Chrome porque estamos conectando
        # num browser manualmente aberto. Você fecha quando quiser.
        if criado_driver:
            try:
                driver.implicitly_wait(0)
            except Exception:
                pass
