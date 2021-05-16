#!/usr/bin/env python3
from ev3dev2.sensor import INPUT_4
from ev3dev2.sensor.lego import UltrasonicSensor
import  os

us = UltrasonicSensor(INPUT_4)
os.system('setfont Lat15-TerminusBold14')
print('sonic sensor')
    
while True:
    dist = us.distance_centimeters_continuous
    if dist <= 10:
        print('obstacle')
        while True:
            dist = us.distance_centimeters_continuous
            if dist > 10:
                print('no obstacle')
                break