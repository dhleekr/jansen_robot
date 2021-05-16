PORT = 8000

from http.client import HTTPConnection
import json
import numpy as np
import time
import RPi.GPIO as GPIO
from Time import Time
from sys import argv


r_motor_back = 24
r_motor_forward = 22
l_motor_forward = 16
l_motor_back = 18


GPIO.setmode(GPIO.BOARD)
GPIO.setup(r_motor_forward, GPIO.OUT)
GPIO.setup(r_motor_back, GPIO.OUT)
GPIO.setup(l_motor_forward, GPIO.OUT)
GPIO.setup(l_motor_back, GPIO.OUT)


GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(r_motor_forward, GPIO.OUT)
GPIO.setup(r_motor_back, GPIO.OUT)
GPIO.setup(l_motor_forward, GPIO.OUT)
GPIO.setup(l_motor_back, GPIO.OUT)


rf_pwm = GPIO.PWM(r_motor_forward, 1000)
rb_pwm = GPIO.PWM(r_motor_back, 1000)
lf_pwm = GPIO.PWM(l_motor_forward, 1000)
lb_pwm = GPIO.PWM(l_motor_back, 1000)


rf_pwm.start(0)
rb_pwm.start(0)
lf_pwm.start(0)
lb_pwm.start(0)


def forward():
    rf_pwm.ChangeDutyCycle(100)
    rb_pwm.ChangeDutyCycle(0)
    lf_pwm.ChangeDutyCycle(100)
    lb_pwm.ChangeDutyCycle(0)

def back():
    rf_pwm.ChangeDutyCycle(0)
    rb_pwm.ChangeDutyCycle(100)
    lf_pwm.ChangeDutyCycle(0)
    lb_pwm.ChangeDutyCycle(100)

def right():
    rf_pwm.ChangeDutyCycle(0)
    rb_pwm.ChangeDutyCycle(100)
    lf_pwm.ChangeDutyCycle(100)
    lb_pwm.ChangeDutyCycle(0)

def left():
    rf_pwm.ChangeDutyCycle(100)
    rb_pwm.ChangeDutyCycle(0)
    lf_pwm.ChangeDutyCycle(0)
    lb_pwm.ChangeDutyCycle(100)

def rf():
    rf_pwm.ChangeDutyCycle(80)
    rb_pwm.ChangeDutyCycle(0)
    lf_pwm.ChangeDutyCycle(100)
    lb_pwm.ChangeDutyCycle(0)

def lf():
    rf_pwm.ChangeDutyCycle(100)
    rb_pwm.ChangeDutyCycle(0)
    lf_pwm.ChangeDutyCycle(80)
    lb_pwm.ChangeDutyCycle(0)

def stop():
    rf_pwm.ChangeDutyCycle(0)
    rb_pwm.ChangeDutyCycle(0)
    lf_pwm.ChangeDutyCycle(0)
    lb_pwm.ChangeDutyCycle(0)


print(argv)


def main():
    while True:
        conn = HTTPConnection("MSI:8000")

        try:
            conn.request("GET", "/")
        except ConnectionRefusedError as error:
            print(error)
            time.sleep(1)
            continue

        print('Connected')
        res = conn.getresponse()
        while True:
            chunk = res.readline()
            if (chunk == b'\n'): continue
            if (not chunk): break

            chunk = chunk[:-1].decode()
            data = json.loads(chunk)
            print(Time(), data)
            action = data['action']
            print('action', action)
            try:
                if action == 'w':
                    print('forward')
                    forward()
                elif action == 'a':
                    print('left')
                    left()
                    time.sleep(0.4)
                    back()
                    time.sleep(0.1)
                    forward()
                elif action == 'd':
                    print('right')
                    right()
                    time.sleep(0.4)
                    back()
                    time.sleep(0.1)
                    forward()
                elif action == 's':
                    print('back')
                    back()
                elif action =='q':
                    print('left forward')
                    lf()
                    time.sleep(0.0005)
                elif action =='e':
                    print('right forward')
                    rf()
                    time.sleep(0.0005)
                elif action == ' ':
                    print('stop')
                    stop()
                    time.sleep(0.001)
                elif action == 'p':
                    print('cleanup')
                    GPIO.cleanup()

            except KeyError as error:
                print(error)


main()
