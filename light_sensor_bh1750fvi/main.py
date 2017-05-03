import time
from machine import I2C
import bh1750fvi

# SDA:P23, SCL:P22
i2c = I2C(0, I2C.MASTER, baudrate=100000, pins=('P23', 'P22'))
addr = i2c.scan()
print(addr)
addr = addr[0]

light_sensor = bh1750fvi.BH1750FVI(i2c, addr)

while True:
    lum = light_sensor.read()
    print(lum)
    time.sleep(1)
