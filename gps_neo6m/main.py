import time
import gps
import machine
from gps import GPS_UART_start
from gps import NmeaParser
from machine import RTC

# connect to GPS device
com = GPS_UART_start()
now = RTC()
now.init((2017, 5, 12, 12, 30, 0, 0, 0))
print(now)

while True:
    # print str(place.longitude * 100000),  str(place.latitude * 100000)
    time.sleep(5)
    if (com.any()):
        data = com.readline()
        #print (data)

        if (data[0:6] == b'$GPGGA'):
            place = NmeaParser()
            place.update(data)
            print ("place", place.longitude,  ":",  place.latitude,  ":", place.fix_time)

            # f_log = open('Lora_log','a')  # careful that log file fills up the memory
            # f_log.write(data + ' ' + str(lora.rssi()) + '\n\n')
            # f_log.close()
            # wait a random amount of time
            time.sleep(10 + (machine.rng() & 0x3f) / 10)
