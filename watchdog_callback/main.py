import time
from machine import WDT, Pin
import gc


pycom.rgbled(0x001100)


def feeder(arg):
    print("feeding WDT")
    wdt.feed()


wdt_button = Pin('P10', mode=Pin.IN, pull=Pin.PULL_UP)
wdt_button.callback(Pin.IRQ_RISING, feeder)

print(wdt_button())

wdt = WDT(timeout=5000)  # sets the timeout to 5 seconds


while True:
    # do something here, e.g. read a sensor
    gc.collect()  # collect garbage
    time.sleep(5)
