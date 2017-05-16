"""Basic LoRa example based on OTAA (Over The Air Authentication)
Setup your TTN details in config.py
"""
import time
from network import LoRa
import socket
import binascii
import config
import pycom


print('Main start')

# Setup LoRa
lora = LoRa(mode=LoRa.LORAWAN, adr=True)

app_eui = binascii.unhexlify(config.APP_EUI)
app_key = binascii.unhexlify(config.APP_KEY)

lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)

# wait until the module has joined the network
print('Joining LoRa...')

pycom.rgbled(0xFF)

while not lora.has_joined():
    time.sleep(2.5)

pycom.rgbled(0)

print("LoRa joined")

print("LoRa active: ", lora.has_joined())
# create a LoRa socket
lora_sock = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
lora_sock.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)

lora_sock.setblocking(False)


def ack():
    for i in range(3):
        pycom.rgbled(0x00ff00)
        time.sleep_ms(100)
        pycom.rgbled(0)
        time.sleep_ms(100)


def lora_tx(payload):
    lora_sock.setblocking(True)
    print('Sending uplink message')
    pycom.rgbled(0xff0000)
    lora_sock.send(payload)
    print('LoRa uplink complete')
    ack()
    lora_sock.setblocking(False)
    data = lora_sock.recv(64)
    print(data)


# call this function to send 'hi' as raw byte data (hex format)
def send_hi_bytes():
    lora_tx(bytes([0x68, 0x69]))


# call this function to send 'hi' as string through the socket
def send_hi_string():
    lora_tx('hi')


lora_sock.send(bytes([1, 2, 3]))
