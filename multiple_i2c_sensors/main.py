import time
from machine import I2C
import tsl2561
import bh1750fvi


# pins=(SDA, SCL)
i2c = I2C(0, I2C.MASTER, baudrate=100000, pins=('P23', 'P22'))
i2c2 = I2C(0, I2C.MASTER, baudrate=100000, pins=('P10', 'P11'))
addr = i2c.scan()[0]
addr2 = i2c2.scan()[0]
print("Device addresses: ", addr, addr2)

light_sensor_tsl2561 = tsl2561.TSL2561(i2c, addr)
light_sensor_bh1750fvi = bh1750fvi.BH1750FVI(i2c2, addr2)
light_sensor_tsl2561.integration_time(402)
light_sensor_tsl2561.gain(16)
light_sensor_tsl2561._update_gain_and_time()

while True:
    # print light value every 10 seconds
    light_sensor_tsl2561_val = light_sensor_tsl2561.read()
    light_sensor_bh1750fvi_val = light_sensor_bh1750fvi.read()
    print("light_sensor_tsl2561_val: ", light_sensor_tsl2561_val)
    print("light_sensor_bh1750fvi_val: ", light_sensor_bh1750fvi_val)
    print("\n")
    time.sleep(10)
