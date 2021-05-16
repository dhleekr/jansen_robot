#!/usr/bin/env python3
from ev3dev2.motor import LargeMotor, OUTPUT_B, OUTPUT_C, SpeedPercent
import time, os

LMotor = LargeMotor(OUTPUT_B) 
RMotor = LargeMotor(OUTPUT_C)

def motor_control(speed_L, speed_R):
    LMotor.on(speed_L)
    RMotor.on(speed_R)
    
os.system('setfont Lat15-TerminusBold14')
print('motor')
time.sleep(3)


motor_control(50,50)
time.sleep(1)

motor_control(-50,-50)
time.sleep(1)

motor_control(-50,50)
time.sleep(1)

motor_control(50,-50)
time.sleep(1)

motor_control(0,0)

