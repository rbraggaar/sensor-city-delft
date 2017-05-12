"""Basic LoRa example based on ABP (authorization by personalization)
Setup your KPN details in config.py
"""
import time
from network import LoRa
import socket
import binascii
import struct
import pycom
import machine
import config


print('Main start')

# LoRa details keys obtained from KPN
dev_addr = struct.unpack(">l", binascii.unhexlify(config.DEV_ADDR))[0]
nwks_key = binascii.unhexlify(config.NWKS_KEY)
apps_key = binascii.unhexlify(config.APPS_KEY)

# Setup LoRa
lora = LoRa(mode=LoRa.LORAWAN, adr=True)

# join a network using ABP
lora.join(activation=LoRa.ABP, auth=(dev_addr, nwks_key, apps_key), timeout=0)
print("LoRa active: ", lora.has_joined())

# create a LoRa socket
lora_sock = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
lora_sock.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)


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
