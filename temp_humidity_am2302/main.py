import time
from machine import Pin
from dth import DTH

# data pin connected to P11
# 1 for AM2302
th = DTH(Pin('P3', mode=Pin.OPEN_DRAIN), 1)
time.sleep(2)

while True:
    result = th.read()
    print(result, type(result))
    print(result.is_valid())
    # if result.is_valid():
    print('Temperature: {:3.2f}'.format(result.temperature / 1.0))
    print('Humidity: {:3.2f}'.format(result.humidity / 1.0))
    time.sleep(2)
