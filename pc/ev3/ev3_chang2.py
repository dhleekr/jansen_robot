#!/usr/bin/env python3
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_D, SpeedPercent
from ev3dev2.sensor import INPUT_4
from ev3dev2.sensor.lego import UltrasonicSensor
import socket
import time, os
import subprocess

# HOST = '192.168.0.7' 
HOST = '192.168.137.1'
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
        print(data)
        if data == b'f':
            print('turn1')
            motor_control(40,-40)
            time.sleep(1.6)
            motor_control(0,0)
            time.sleep(.1)
            
        elif data == b'b':
            print('turn2')
            motor_control(40,-40)
            time.sleep(3.3)
            motor_control(0,0)
            time.sleep(.1)
            
        elif data == b'r':
            print('turn3')
            motor_control(40,-40)
            time.sleep(4.9)
            motor_control(0,0)
            time.sleep(.1)
            
        else:
            motor_control(0, 0)
            print(' ')
            
            
    except:
        LMotor.reset()
        RMotor.reset()
        break

client_socket.close()