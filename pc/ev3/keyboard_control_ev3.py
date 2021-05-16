#!/usr/bin/env python3
from ev3dev2.motor import LargeMotor, OUTPUT_B, OUTPUT_C, SpeedPercent
import socket
import time, os

HOST = '172.30.1.4' # Raspberry pi server IP
PORT = 12345

client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
os.system('setfont Lat15-TerminusBold14')
print('socket connect')

LMotor = LargeMotor(OUTPUT_B) 
RMotor = LargeMotor(OUTPUT_C)

def motor_control(speed_L, speed_R):
    LMotor.on(speed_L)
    RMotor.on(speed_R)
    
time.sleep(1)
while True:
    try:
        data = client_socket.recv(1024)
        
        if data == b'f':
            motor_control(30,30)
            print('forward')

        elif data == b'b':
            motor_control(-20,-20)
            print('back')

        elif data == b'l':
            motor_control(0,25)
            print('left')

        elif data == b'r':
            motor_control(25,0)
            print('right')

        else:
            motor_control(0,0)
            
    except:
        LMotor.reset()
        RMotor.reset()
        break

client_socket.close()