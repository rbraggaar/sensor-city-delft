"""
TXD: P3 = G11
RXD: P4 = G24
"""
import time
import gps
import machine
from gps import GPS_UART_start
from gps import NmeaParser
from machine import RTC

print('start main')
time.sleep(5)

# connect to GPS device
gps = GPS_UART_start()

while True:
    time.sleep(5)
    if (gps.any()):
        data = gps.readline()

        if (data[0:6] == b'$GPGGA'):
            place = NmeaParser()
            place.update(data)
            if place.latitude != 0 or place.longitude != 0:
                print (str(place.latitude) + ', ' + str(place.longitude))
