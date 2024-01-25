import qrcode
import time
from PIL import Image, ImageDraw, ImageFont
#from kod.tests.lib.oled import SSD1331 as SSD1331
import os


def generate_qr_code(data, image_size=60):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
    )
    qr.add_data(data)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color='black', back_color='white')

    qr_img = qr_img.resize((image_size, image_size))

    return qr_img


def qr_oled_display(disp, qr_image: Image):
    # Create blank image for drawing.
    image_outer = Image.new("RGB", (disp.width, disp.height), "WHITE")
    image_outer.paste(qr_image, (0, 0))
    disp.ShowImage(image_outer, 0, 0)


def test():
    print('\nThe OLED screen test.')
    os.system('sudo systemctl stop ip-oled.service')
    time.sleep(1)
    #oledtest()


# if __name__ == "__main__":
    # qr_data = "https://google.com"
    # qr_image = generate_qr_code(qr_data)
    # qr_image.save("qr_test.jpg")
