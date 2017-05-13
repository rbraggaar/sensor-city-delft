import HMC5883L
import gc
import time


compass = HMC5883L.HMC5883L()

while True:
    compass.readAxes()
    compass.heading()
    print(compass)
    time.sleep_ms(1000)
    gc.collect()
