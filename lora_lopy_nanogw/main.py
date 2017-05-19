"""LoPy LoRaWAN Nano Gateway"""
from nanogateway import NanoGateway
import config


gateway = NanoGateway(id=config.GATEWAY_ID, frequency=config.LORA_FREQUENCY,
                      datarate=config.LORA_DR, ssid=config.WIFI_SSID,
                      password=config.WIFI_PASS, server=config.SERVER,
                      port=config.PORT, ntp=config.NTP,
                      ntp_period=config.NTP_PERIOD_S)

gateway.start()
