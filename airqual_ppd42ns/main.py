"""
Based on example by Seeedstudio
Adapted for Pycom by Rob Braggaar

Shinyei Model PPD42NS Particle Sensor
    min: 1 um diameter particulate matter
    output unit: pcs/L or pcs/0.01cf.

    wires:
    4.75 - 5.25 V INPUT :: Red wire
    GND :: Black wire
    digital input :: Yellow wire

    current draw 90 mA
    typical startup time: 3 min (resistor heats up)
"""
import time
from machine import Pin, Timer


INPUT_PIN = 'P11'
SAMPLETIME_MS = 10000

# setup pin
IN_PIN = Pin(INPUT_PIN, mode=Pin.IN)

chrono = Timer.Chrono()

while True:
    # start of new sampling window
    starttime = time.now()  # current time
    # reflects on which level LPO Time takes up the whole sample time
    ratio = 0
    #  Lo Pulse Occupancy Time(LPO Time) in microseconds
    low_pulse_occ = 0
    # concentration based on LPO time and characteristics graph
    concentration = 0
    while time.now() - starttime <= SAMPLETIME_MS:  # in sampling window
        # check if pin is low, start timing
        if INPUT_PIN.value() = 0:
            chrono.start()
        # get duration of low pulse and reset timer
        else:
            low_pulse_occ += chrono.read_us()
            chrono.reset()
    ratio = low_pulse_occ / (SAMPLETIME_MS * 10.0)  # Integer percentage (0 - 100%)
    concentration = 1.1 * (ratio ** 3) - 3.8 * (ratio ** 2) + 520 * ratio + 0.62
    if concentration != 0.62:
        print("Concentration is {} pcs/0.01cf".format(concentration))
