import time
from PIL import Image, ImageDraw, ImageFont
import qrcode
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
from mfrc522 import MFRC522
from kod.tests.lib.oled import SSD1331 as SSD1331
from qr_codes import generate_qr_code, oledtest

# Konfiguracja GPIO
# TODO


MQTT_BROKER = "iot-proj.swisz.cz"
MQTT_PORT = 1883

client = mqtt.Client()
client.username_pw_set("iot", "G516cD8#rSb£")
client.connect(MQTT_BROKER, MQTT_PORT, 60)

def process_message(mosq, obj, msg):
    response = msg.payload.decode('utf-8')
    if response == 'Card not assigned to user':
        print('kod kuer')

client.on_message = process_message
client.subscribe('check/user/resp')

# MQTT_PORT = 3000
# MQTT_PORT = 3001
# MQTT_PORT = 5432
# MQTT_PORT = 3567


disp = SSD1331.SSD1331()
disp.Init()
disp.clear()

MIFAREReader = MFRC522()

QR_URL = "qr_test.jpg"

# Card data handling
def handle_card_inserted(card_id):
    print('aaaaa')
    user_exists = check_user_in_database(card_id)

    if user_exists:
        direct_user_to_station()
    else:
        #QR generation and sending to server
        qr_code_path = generate_qr_code(card_id)
        # send_qr_code_to_server(qr_code_path)


        # wait_for_card_reinsert()


#TODO
def check_user_in_database(card_id):

    global client
    client.publish('check/user', card_id)
    return False




# def send_card_id_to_server(card_id):
#     client = mqtt.Client()
#     client.connect(MQTT_BROKER, MQTT_PORT, 60)
#     client.publish(MQTT_TOPIC, card_id)
#     client.disconnect()

#TODO
def direct_user_to_station():
    return False


# def send_qr_code_to_server(qr_code_path):
#     with open(qr_code_path, "rb") as file:
#         qr_code_data = file.read()

#     client.publish(MQTT_TOPIC, qr_code_data)
#     client.disconnect()




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
                handle_card_inserted(card_id)
        time.sleep(0.1)



except KeyboardInterrupt:
    client.disconnect()
    GPIO.cleanup()
