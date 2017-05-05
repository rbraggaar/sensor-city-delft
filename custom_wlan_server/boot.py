import os
import time
import machine
import network
import pycom
import config

uart = machine.UART(0, 115200)
os.dupterm(uart)

pycom.heartbeat(False)


def setup_ap(ssid=config.SSID, channel=1):
    """
    This functions configures the Pycom device as AP

    Parameters:
    ssid: defaults to SSID set in config.py
    """
    wlan = network.WLAN(
        mode=network.WLAN.AP,
        ssid=ssid,
        auth=(network.WLAN.WPA2, config.WLAN_PASSWORD),
        channel=channel,
        antenna=network.WLAN.INT_ANT)


def connect_wlan(ip='192.168.1.60'):
    """
    Use this function when you want to hook up the Lopy to an existing Wi-Fi
    network. Change parameters in the config tuple according to your needs.

    Parameters:
    ip-adres: the ip adres of the Pycom device
    """
    # configure as a station/client
    wlan = network.WLAN(mode=network.WLAN.STA)
    # configure station settings: ip, subnet_mask, gateway, DNS_server
    wlan.ifconfig(
        config=(ip, '255.255.255.0', '192.168.1.1', '8.8.8.8'))
    wlan.connect(ssid=config.SSID, auth=(network.WLAN.WPA2, config.WPASSWORD))

    while not wlan.isconnected():
        time.sleep(.1)

    # prints out local IP
    print(wlan.ifconfig())


# These changes affect the telnet and ftp credentials/security
# Parameters can be added in the config file to obscure them from the main code
server = network.Server(login=(
    config.USERNAME, config.PASSWORD), timeout=60)

# start main script
machine.main('main.py')
