"""LoPy LoRaWAN Nano Gateway configuration details"""

GATEWAY_ID = "70B3D54995506D3E"  # '11aa334455bb7788'

# SERVER = "ttn-router-eu"  # 'router.eu.thethings.network'
SERVER = 'router.eu.thethings.network'
PORT = 1700

NTP = "pool.ntp.org"
NTP_PERIOD_S = 3600

WIFI_SSID = "DigiDelfland.nl"  # 'my-wifi'
WIFI_PASS = "A8GZBNC*DE"  # 'my-wifi-password'

LORA_FREQUENCY = 868100000
LORA_DR = "SF7BW125"   # DR_5
