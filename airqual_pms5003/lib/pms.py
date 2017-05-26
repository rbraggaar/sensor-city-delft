#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2016-2017 Niccolo Rigacci <niccolo@rigacci.org>
#
# Data acquisition program for Plantower PMS5003 particulate
# matter sensor. Developend and tested on the Raspberry Pi.
# https://github.com/RigacciOrg/AirPi/tree/master/lib
#
# Features:
#  * Handle sleep-down and awake of the sensor.
#  * Wait some time before read, allow the sensor to settle.
#  * Multiple read with average calculation.
#  * Verify data checksum.
#  * Handle communication errors.
#  * Single read or endless loop.
#  * Write data to status file (STATUS_FILE).
#
# === Single read ===
# Mode suitable for a cronjob: set AVERAGE_READS_SLEEP
# to -1. The sensor will be awakened before the reading, and
# it will be put at sleep before program exit.
#
# === Endless loop ===
# Set AVERAGE_READS_SLEEP to the acquiring interval (seconds).
# If the interval is greather than three times the sensor's settling
# time, the sensor will be put to sleep before the next read.
#
# PMS5003 specifications:
# http://www.rigacci.org/wiki/lib/exe/fetch.php/doc/appunti/hardware/raspberrypi/plantower-pms5003-manual_v2-3.pdf
#
# Author        Niccolo Rigacci <niccolo@rigacci.org>
# Version       0.1.2  2017-02-20
#
#   Modified by paulv (c) March 2017
#   - changed bash type programming to RPi.GPIO
#   - removed logging
#   - removed software programming for the sensor, sleep function did not work


from __future__ import print_function

try:
    import serial
except ImportError, e:
    print("Python module serial not found, 'sudo apt-get install python-serial'")
    sys.exit(0)

import datetime
import os
import os.path
import sys
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
# GPIO wired to RESET line of PMS5003 (pin 6)
PMS5003_RESET_GPIO = 17
GPIO.setup(PMS5003_RESET_GPIO, GPIO.OUT)
# GPIO wired to SET line of PMS5003 (pin 3)
PMS5003_SLEEP_GPIO = 27
GPIO.setup(PMS5003_SLEEP_GPIO, GPIO.OUT)

# Make several reads, then calculate the average.
AVERAGE_READS = 4  # for testing, was 16
# Seconds to sleep before repeating averaged read. Use -1 to exit.
AVERAGE_READS_SLEEP = -1

# Attempt a sensor reset after some errors.
RESET_ON_FRAME_ERRORS = 2
# Abort the averaged read after too many errors.
MAX_FRAME_ERRORS = 10

# Sensor settling after wakeup requires at least 30 seconds (sensor sepcifications).
WAIT_AFTER_WAKEUP = 35
# Total Response Time is 10 seconds (sensor specifications).
MAX_TOTAL_RESPONSE_TIME = 12


# Normal data frame length.
DATA_FRAME_LENGTH = 28
# Command response frame length.
CMD_FRAME_LENGTH = 4

# Serial read timeout value in seconds.
SERIAL_TIMEOUT = 2.0

# Calculate average on this output data.
AVERAGE_FIELDS = ['data1', 'data2', 'data3', 'data4', 'data5',
                  'data6', 'data7', 'data8', 'data9', 'data10', 'data11', 'data12']

# Status file where to save the last averaged reading.
STATUS_FILE = 'pms5003.txt'


#---------------------------------------------------------------
# Convert a two bytes string into a 16 bit integer.
#---------------------------------------------------------------
def int16bit(b):
    return (ord(b[0]) << 8) + ord(b[1])


#---------------------------------------------------------------
# Return the hex dump of a buffer of bytes.
#---------------------------------------------------------------
def buff2hex(b):
    return " ".join("0x{:02x}".format(ord(c)) for c in b)


#---------------------------------------------------------------
# Make a list of averaged reads: (datetime, float, float, ...)
#---------------------------------------------------------------
def make_average(reads_list):
    average = []
    average.append(datetime.datetime.utcnow())
    for k in AVERAGE_FIELDS:
        average.append(float(sum(r[k] for r in reads_list)) / len(reads_list))
    return average


#---------------------------------------------------------------
# Convert the list created by make_average() to a string.
#---------------------------------------------------------------
def average2str(avg):
    s = avg[0].strftime('%Y-%m-%d %H:%M:%S ')
    for f in avg[1:]:
        s += ' %0.2f' % (f)
    return s


#---------------------------------------------------------------
# Send a SLEEP signal to sensor.
#---------------------------------------------------------------
def send_sensor_2_sleep():
    print("Putting sensor to sleep")
    GPIO.output(PMS5003_SLEEP_GPIO, GPIO.LOW)
    return


#---------------------------------------------------------------
# Send a WAKEUP signal to sensor.
#---------------------------------------------------------------
def wakeup_sensor():
    print("Wake the sensor up")
    GPIO.output(PMS5003_SLEEP_GPIO, GPIO.HIGH)
    print("Waiting %d seconds for the sensor to get fresh samplings" % (WAIT_AFTER_WAKEUP,))
    time.sleep(WAIT_AFTER_WAKEUP)
    return


#---------------------------------------------------------------
# Send a RESET signal to sensor.
#---------------------------------------------------------------
def sensor_reset():
    print("Sending reset signal to sensor")
    GPIO.output(PMS5003_RESET_GPIO, GPIO.LOW)
    time.sleep(0.5)
    GPIO.output(PMS5003_RESET_GPIO, GPIO.HIGH)
    time.sleep(1.0)
    return


#---------------------------------------------------------------
# Save averaged data.
#---------------------------------------------------------------
def save_data(text):
    tmpf = open(STATUS_FILE + '.tmp', 'w')
    tmpf.write(text + '\n')
    tmpf.flush()
    os.fsync(tmpf.fileno())
    tmpf.close()
    os.rename(STATUS_FILE + '.tmp', STATUS_FILE)
    return


#---------------------------------------------------------------
# Read a data frame from the serial port.
#  the first 4 bytes are:
#  0x42, 0x4d, and two bytes as the frame lenght.
# Return None on errors.
#---------------------------------------------------------------
def read_pm_frame(_port):

    frame = b''
    start = datetime.datetime.utcnow()

    while True:
        b0 = _port.read()
        if b0 != '':
            if b0 != b'\x42':
                # skip the legitimate starting byte, print the rest
                print('Got char 0x%x from serial read()' % (ord(b0),))
        else:
            print('Timeout on serial read()')

        if b0 == b'\x42':  # found the start of a frame
            b1 = _port.read()
            if b1 == b'\x4d':  # if second byte is OK, process the frame
                # determine the length of the frame
                b2 = _port.read()
                b3 = _port.read()
                frame_len = ord(b2) * 256 + ord(b3)
                if frame_len == DATA_FRAME_LENGTH:
                    # Normal data frame.
                    frame += b0 + b1 + b2 + b3
                    frame += _port.read(frame_len)
                    if (len(frame) - 4) != frame_len:
                        print("error: Short read, expected %d bytes, got %d" %
                              (frame_len, len(frame) - 4))
                        return None
                    # Verify checksum (last two bytes).
                    expected = int16bit(frame[-2:])
                    checksum = 0
                    for i in range(0, len(frame) - 2):
                        checksum += ord(frame[i])
                    if checksum != expected:
                        print("error: Checksum mismatch: %d, expected %d" % (checksum, expected))
                        return None
                    print("Received data frame = %s" % (buff2hex(frame),))
                    return frame

                elif frame_len == CMD_FRAME_LENGTH:  # no longer used
                    # Command response frame.
                    frame += b0 + b1 + b2 + b3
                    frame += _port.read(frame_len)
                    print("Received command response frame = %s" % (buff2hex(frame),))
                    return frame

                else:
                    # Unexpected frame.
                    print("error: Unexpected frame length = %d" % (frame_len))
                    time.sleep(MAX_TOTAL_RESPONSE_TIME)
                    _port.flushInput()
                    return None

        if (datetime.datetime.utcnow() - start).seconds >= MAX_TOTAL_RESPONSE_TIME:
            print("error: Timeout waiting data-frame signature")
            return None


#---------------------------------------------------------------
# Return the data frame in a verbose format.
#---------------------------------------------------------------
def data_frame_verbose(f):
    return (' PM1.0 (CF=1) μg/m³: {};\n'
            ' PM2.5 (CF=1) μg/m³: {};\n'
            ' PM10  (CF=1) μg/m³: {};\n'
            ' PM1.0 (STD)  μg/m³: {};\n'
            ' PM2.5 (STD)  μg/m³: {};\n'
            ' PM10  (STD)  μg/m³: {};\n'
            ' Particles >  0.3 μm count: {};\n'
            ' Particles >  0.5 μm count: {};\n'
            ' Particles >  1.0 μm count: {};\n'
            ' Particles >  2.5 μm count: {};\n'
            ' Particles >  5.0 μm count: {};\n'
            ' Particles > 10.0 μm count: {};\n'
            ' Reserved: {};\n'
            ' Checksum: {};'.format(
                f['data1'],  f['data2'],  f['data3'],
                f['data4'],  f['data5'],  f['data6'],
                f['data7'],  f['data8'],  f['data9'],
                f['data10'], f['data11'], f['data12'],
                f['reserved'], f['checksum']))


#---------------------------------------------------------------
# Main program.
#---------------------------------------------------------------
def main():

    port = serial.Serial('/dev/ttyAMA0', baudrate=9600, timeout=SERIAL_TIMEOUT)

    wakeup_sensor()

    reads_list = []
    error_count = 0
    error_total = 0

    while True:
        try:
            rcv = read_pm_frame(port)

            # Manage data-frame errors.
            if rcv == None:
                error_count += 1
                error_total += 1
                if error_count >= RESET_ON_FRAME_ERRORS:
                    print("Repeated read errors, attempting sensor reset")
                    sensor_reset()
                    error_count = 0
                    continue
                if error_total >= MAX_FRAME_ERRORS:
                    if (AVERAGE_READS_SLEEP >= 0):
                        print("error: Too many read errors, sleeping a while")
                        time.sleep(AVERAGE_READS_SLEEP)
                        error_total = 0
                        continue
                    else:
                        print("error: Too many read errors, exiting")
                        break  # and terminate this script

            # Skip non-output data-frames.
            if (rcv == None) or ((len(rcv) - 4) != DATA_FRAME_LENGTH):
                continue

            # Got a valid data-frame, assign variables.
            res = {'timestamp': datetime.datetime.utcnow(),
                   'data1':     int16bit(rcv[4:]),
                   'data2':     int16bit(rcv[6:]),
                   'data3':     int16bit(rcv[8:]),
                   'data4':     int16bit(rcv[10:]),
                   'data5':     int16bit(rcv[12:]),
                   'data6':     int16bit(rcv[14:]),
                   'data7':     int16bit(rcv[16:]),
                   'data8':     int16bit(rcv[18:]),
                   'data9':     int16bit(rcv[20:]),
                   'data10':    int16bit(rcv[22:]),
                   'data11':    int16bit(rcv[24:]),
                   'data12':    int16bit(rcv[26:]),
                   'reserved':  buff2hex(rcv[28:]),
                   'checksum':  int16bit(rcv[30:])
                   }
            print("Got valid data frame:\n" + data_frame_verbose(res))

            reads_list.append(res)

            if len(reads_list) >= AVERAGE_READS:
                # Calculate the average of the measured data.
                print("Got %d valid readings, calculating average" % (len(reads_list)))
                average = make_average(reads_list)
                average_str = average2str(average)
                print("Average data: %s" % (average_str,))
                save_data(average_str)
                del reads_list[:]

                if AVERAGE_READS_SLEEP < 0:
                    break

                if AVERAGE_READS_SLEEP > (WAIT_AFTER_WAKEUP * 3):
                    # If sleep time is long enough, enter sensor sleep state.
                    send_sensor_2_sleep()
                    print("Waiting %d seconds before new read" % (AVERAGE_READS_SLEEP,))
                    time.sleep(AVERAGE_READS_SLEEP)
                    wakeup_sensor()
                else:
                    # Keep sensor awake and wait for next reads.
                    print("Waiting %d seconds before new read" % (AVERAGE_READS_SLEEP,))
                    time.sleep(AVERAGE_READS_SLEEP)
                    port.flushOutput()
                    port.flushInput()

        except KeyboardInterrupt:
            break

    try:
        print("Exiting main loop")
        send_sensor_2_sleep()
        port.close()

    except KeyboardInterrupt:
        print("\nCtrl-C  {0}".format(e))
    except Exception as e:
        print("Exception {0}".format(e))
    finally:
        print("GPIO Cleanup")
        GPIO.cleanup(PMS5003_RESET_GPIO)
        sys.exit(0)


if __name__ == '__main__':
    main()
