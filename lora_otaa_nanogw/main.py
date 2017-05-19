"""Basic LoRa example based on OTAA (Over The Air Authentication)
Setup your TTN details in config.py

Special LoPy-node script compatible with the LoPy Nano Gateway
"""

from network import LoRa
import socket
import binascii
import struct
import time
import config


print('Main start')

# Setup LoRa
lora = LoRa(mode=LoRa.LORAWAN)

dev_eui = binascii.unhexlify(config.DEV_EUI)
app_eui = binascii.unhexlify(config.APP_EUI)
app_key = binascii.unhexlify(config.APP_KEY)

# set the 3 default channels to the same frequency
# (must be before sending the OTAA join request)
lora.add_channel(0, frequency=868100000, dr_min=0, dr_max=5)
lora.add_channel(1, frequency=868100000, dr_min=0, dr_max=5)
lora.add_channel(2, frequency=868100000, dr_min=0, dr_max=5)

# join a LoRa network using OTAA
lora.join(activation=LoRa.OTAA, auth=(dev_eui, app_eui, app_key), timeout=0)

# wait until the module has joined the network
print('Joining LoRa...')
pycom.rgbled(0x0A0000)

while not lora.has_joined():
    time.sleep(2.5)

pycom.rgbled(0)
print("LoRa joined")
print("LoRa active: ", lora.has_joined())

# remove all the non-default channels
for i in range(3, 16):
    lora.remove_channel(i)

# create a LoRa socket
lora_sock = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
lora_sock.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)

# make the socket blocking
lora_sock.setblocking(False)

time.sleep(5.0)


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
    time.sleep(4)
    rx = lora_sock.recv(256)
    if rx:
        print(rx)


# call this function to send 'hi' as raw byte data (hex format)
def send_hi_bytes():
    lora_tx(bytes([0x68, 0x69]))


# call this function to send 'hi' as string through the socket
def send_hi_string():
    lora_tx('hi')


send_hi_bytes()
