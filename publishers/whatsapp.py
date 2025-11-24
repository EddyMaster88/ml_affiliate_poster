from typing import Optional
import pywhatkit as kit
import time

def send_whatsapp(number: str, message: str, image_path: Optional[str] = None):
    """Envia via WhatsApp Web:
    - se image_path: envia imagem com legenda
    - caso contrário: envia texto
    """
    if image_path:
        kit.sendwhats_image(receiver=number, img_path=image_path, caption=message, wait_time=12, tab_close=True)
    else:
        kit.sendwhatmsg_instantly(phone_no=number, message=message, wait_time=10, tab_close=True)
    time.sleep(5)
