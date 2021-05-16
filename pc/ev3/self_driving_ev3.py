#!/usr/bin/env python3
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_D, SpeedPercent
from ev3dev2.sensor import INPUT_4
from ev3dev2.sensor.lego import UltrasonicSensor
import socket
import time, os
import subprocess

HOST = '192.168.137.33' # Raspberry pi server IP
# HOST = '192.168.0.7' 

PORT = 12345

client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
os.system('setfont Lat15-TerminusBold14')
print('socket connect')

us = UltrasonicSensor(INPUT_4)
LMotor = LargeMotor(OUTPUT_A) 
RMotor = LargeMotor(OUTPUT_D)

def motor_control(speed_L, speed_R):
    LMotor.on(speed_L)
    RMotor.on(speed_R)
    
while True:
    try:
        data = client_socket.recv(1024)
        dist = us.distance_centimeters_continuous
        if dist <= 15:
            print('obstacle')
            while True:
                motor_control(0,0)
                dist = us.distance_centimeters_continuous
                if dist > 15:
                    motor_control(10,10)
                    break
            continue
        
        if data == b'f':
            motor_control(40,40)
            print('forward')

        elif data == b'f_l':
            motor_control(30,40)
            print('forward_L')

        elif data == b'f_r':
            motor_control(40,30)
            print('forward_R')

        elif data == b'b':
            motor_control(-20,-20)
            print('back')

        elif data == b'l':
            motor_control(-12,12)
            print('left')

        elif data == b'r':
            motor_control(12,-12)
            print('right')

        elif data == b'u':
            motor_control(40,-40)
            time.sleep(0.9)
            print('utrun')

        elif data == b'cascade_stop':
            print('cascade')
            motor_control(0,0)
            time.sleep(5)

        elif data == b'l_marker':
            print('l_marker')
            motor_control(-15,15)
            time.sleep(0.4)

        elif data == b'r_marker':
            print('r_marker')
            motor_control(15,-15)
            time.sleep(0.77)

        elif data == b's_marker':
            print('s_marker')
            motor_control(0,0)
            time.sleep(5)
            motor_control(30,30)
            time.sleep(1)
            

        else:
            motor_control(0,0)
            print('1')
            
    except:
        LMotor.reset()
        RMotor.reset()
        break

client_socket.close()