from whatsapp import abrir_whatsapp, abrir_conversa, enviar_mensagem
from linkbuilder_selenium import conectar_chrome

NOME_CONVERSA = "Ofertas Mercado Livre"

def main():
    driver = conectar_chrome()
    abrir_whatsapp(driver)
    abrir_conversa(driver, NOME_CONVERSA)

    enviar_mensagem(driver, "Mensagem de teste enviada pelo bot.")
    print("Fim do teste!")

if __name__ == "__main__":
    main()
