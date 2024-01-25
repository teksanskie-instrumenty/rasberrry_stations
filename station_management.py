import json
import time
from PIL import Image, ImageDraw, ImageFont
import qrcode
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
from mfrc522 import MFRC522
from kod.tests.lib.oled import SSD1331 as SSD1331
from qr_codes import generate_qr_code, qr_oled_display

# Konfiguracja GPIO
# TODO

disp = SSD1331.SSD1331()
disp.Init()
disp.clear()

MQTT_BROKER = "iot-proj.swisz.cz"
MQTT_PORT = 1883

client = mqtt.Client()
client.username_pw_set("iot", "G516cD8#rSb£")
client.connect(MQTT_BROKER, MQTT_PORT, 60)

def process_message(mosq, obj, msg):
    print(msg.topic)
    response = msg.payload.decode('utf-8')
    if msg.topic == 'check/user/resp':
        if response == 'Card not assigned to user':
            qr_data = f"iot-proj.swisz.cz/register/{card_id}"
            qr_code_image = generate_qr_code(qr_data)

            qr_oled_display(disp, qr_code_image)
            # qr_code_image.save("qr_test.jpg")
            # print('gugu gaga')
        else:
            obj = json.loads(response)
            client.publish('get/task', card_id)

    elif msg.topic == 'get/task/resp':
        data = json.loads(msg.payload)
        exercises = data['dailyPlanExercises']

        for exercise in exercises:
            if exercise["is_finished"] == False:
                station = exercise['exercise']['station']

                print(station['name'])
                print(station['color'])

                display_machine_info(station['name'], station['color'])
                return
        #TODO if there are no excercises available
        print("No excercises available!")
        display_machine_info(None, None)

        # print(data)


client.on_message = process_message
client.subscribe('check/user/resp')
client.subscribe('get/task/resp')


disp = SSD1331.SSD1331()
disp.Init()
disp.clear()

MIFAREReader = MFRC522()

def display_machine_info(station_name, station_color):
    image_outer = Image.new("RGB", (disp.width, disp.height), "WHITE")
    draw = ImageDraw.Draw(image_outer)

    text = 'There are no exercises, go home' if station_name is None else f'Go to machine: {station_name}'

    color_rgb = tuple(int(station_color[i:i + 2], 16) for i in (0, 2, 4))

    circle_radius = min((disp.width, disp.height)) // 4
    circle_bbox = (
        (disp.width, disp.height)[0] - circle_radius,
        (disp.width, disp.height)[1] - circle_radius,
        (disp.width, disp.height)[0],
        (disp.width, disp.height)[1]
    )

    draw.ellipse(circle_bbox, fill=color_rgb)

    #basic values
    font = None
    font_size = 20

    text_color = "black"

    text_position = (10, 10)

    draw.text(text_position, text, font=font, fill=text_color)

    disp.ShowImage(image_outer, 0, 0)



#Translating the card ID
def read_card_id(uid):
    num = 0
    for i in range(0, len(uid)):
        num += uid[i] << (i * 8)

    return num


# main loop
try:
    client.loop_start()
    while True:
        #catching card input and input validation
        (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
        if status == MIFAREReader.MI_OK:
            (status, uid) = MIFAREReader.MFRC522_Anticoll()

            if status == MIFAREReader.MI_OK:
                card_id = read_card_id(uid)
                client.publish('check/user', card_id)
        time.sleep(0.1)



except KeyboardInterrupt:
    client.disconnect()
    GPIO.cleanup()
