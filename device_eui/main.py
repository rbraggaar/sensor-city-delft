from network import LoRa
import binascii


lora = LoRa(mode=LoRa.LORAWAN)
dev_eui = binascii.hexlify(lora.mac()).upper().decode('utf-8')

print(dev_eui)
