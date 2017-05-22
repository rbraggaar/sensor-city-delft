import time
from machine import Timer
import machine


SAMPLE_WINDOW = 50  # Sample window width in ms (50 ms = 20Hz)
sample = 0

adc = machine.ADC(bits=10)             # create an ADC object
apin = adc.channel(pin='P16')   # create an analog pin on P16


while True:
    chrono = Timer.Chrono()
    chrono.start()
    start_time = chrono.read_ms()

    peak_to_peak = 0  # peak-to-peak level
    signal_max = 0  # max signal
    signal_min = 1024  # min signal

    while (start_time - chrono.read_ms()) < SAMPLE_WINDOW:  # 50 ms
        sample = apin()  # read an analog value

        if sample > signal_max:
            signal_max = sample
        elif sample < signal_min:
            signal_min = sample

    peak_to_peak = signal_max - signal_min
    print(peak_to_peak)
    volts = (peak_to_peak * 3.3) / 1024
    print(volts)
