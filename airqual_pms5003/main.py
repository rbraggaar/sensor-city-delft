"""
Micropython library for PMS5003
by Rob Braggaar
"""
import time
import struct
from machine import UART, Pin


class PMS5003():
    def __init__(self, set='P11', reset='P12'):
        """
            Lopy     :: PMS
            TXD: P9  :: RXD: P4
            RXD: P10 :: TXD: P5
            SET: P11 :: SET: P3
            RESET: P12 :: RESET: P6
        """
        self.STARTUP_TIME = 30  # startup time
        self.port = UART(1, 9600, parity=None, stop=1, pins=('P9', 'P10'))
        self.set_pin = Pin(set, mode=Pin.OUT)
        self.reset_pin = Pin(reset, mode=Pin.OUT)

        self.set_pin.value(0)  # start powered off
        self.reset_pin.value(1)  # pull low and high for reset

    def set_pms(self):
        print("PMS: set")
        self.set_pin.value(1)
        time.sleep(self.STARTUP_TIME)

    def reset_pms(self):
        print("PMS: reset")
        self.reset_pin.value(0)
        time.sleep_ms(50)
        self.reset_pin.value(1)

    def sleep(self):
        print("PMS: sleep")
        self.set_pin.value(0)

    def packet_from_data(self, data):
        numbers = struct.unpack('>16H', data)
        csum = sum(data[:-2])
        if csum != numbers[-1]:
            print("Bad packet data: %s / %s", data, csum)
            return None
        return numbers[2:-2]

    def read_pms(self):
        c = self.port.read(1)
        print(c)
        if c != '\x42':
            self.read_pms()

        c = self.port.read(1)
        print(c)
        if c != '\x4d':
            self.read_pms()

        data = bytearray((0x42, 0x4d))
        print('data:', len(data), '\n', data)

        data += self.port.read(30)
        print('data:', len(data), '\n', data)

        if len(data) != 32:
            self.read_pms()

        measurements = self.packet_from_data(data)
        if measurements == None:
            print("PMS: read failed")
        else:
            return measurements


pms = PMS5003()
pms.set_pms()
print(pms.read_pms())
