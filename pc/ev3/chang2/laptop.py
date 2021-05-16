import numpy as np
import cv2
import math
import tensorflow as tf
from keras.models import load_model
from tensorflow import keras
from tensorflow.keras import layers
import socket
from _thread import *
import time

# HOST = '192.168.0.7' 
HOST = '192.168.137.1'
PORT = 12345

def process(img_input):

    gray = cv2.cvtColor(img_input, cv2.COLOR_BGR2GRAY)

    gray = cv2.resize(gray, (28, 28), interpolation=cv2.INTER_AREA)


    (thresh, img_binary) = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)


    h,w = img_binary.shape

  
    ratio = 100/h
    new_h = 100
    new_w = w * ratio

    img_empty = np.zeros((110,110), dtype=img_binary.dtype)
    img_binary = cv2.resize(img_binary, (int(new_w), int(new_h)), interpolation=cv2.INTER_AREA)
    img_empty[:img_binary.shape[0], :img_binary.shape[1]] = img_binary

    img_binary = img_empty


    cnts = cv2.findContours(img_binary.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


    # 컨투어의 무게중심 좌표를 구합니다. 
    M = cv2.moments(cnts[0][0])
    center_x = (M["m10"] / M["m00"])
    center_y = (M["m01"] / M["m00"])

    # 무게 중심이 이미지 중심으로 오도록 이동시킵니다. 
    height,width = img_binary.shape[:2]
    shiftx = width/2-center_x
    shifty = height/2-center_y

    Translation_Matrix = np.float32([[1, 0, shiftx],[0, 1, shifty]])
    img_binary = cv2.warpAffine(img_binary, Translation_Matrix, (width,height))


    img_binary = cv2.resize(img_binary, (28, 28), interpolation=cv2.INTER_AREA)
    flatten = img_binary.flatten() / 255.0

    return flatten




def threaded(client_socket, addr):
    print('Connected by :', addr[0], ':', addr[1])
    global Loop_state
    global stop_time
    

    while(True):
        ret, img_color = cap.read()
        if ret == False:
            break
        try:
            img_input = img_color.copy()
            cv2.rectangle(img_color, (250, 150),  (width-250, height-150), (0, 0, 255), 3)
            cv2.imshow('bgr', img_color)

            img_roi = img_input[150:height-150, 250:width-250]

            key = cv2.waitKey(1)

            if key == 27:
                break
            elif key == 32:
                test_num = process(img_roi)
                predictions = model.predict(test_num[np.newaxis,:])

                with tf.compat.v1.Session() as sess:
                    result = tf.argmax(predictions, 1).eval()[0]
                    print(result)

                    if result == 1:
                        action = 'f'
                    elif result == 2:
                        action = 'b'
                    elif result == 3:
                        action = 'r'
                    else:
                        action = ' '

                    print(action)
                    client_socket.sendall(action.encode())

            if key == ord('q'):
                client_socket.close()
                break
            
        except:
            print('except')
            client_socket.close()
            break
    Loop_state=2

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()
print('server start')

model = tf.keras.models.Sequential([
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(512, activation=tf.nn.relu),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(10, activation=tf.nn.softmax)
])

model.load_weights('mnist_checkpoint')

cap = cv2.VideoCapture(0)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

Loop_state=1
time.sleep(.1)
stop_time = 0

print('wait')

client_socket, addr = server_socket.accept()
start_new_thread(threaded, (client_socket, addr))

while True:
    if Loop_state==2:
        break
    pass

server_socket.close()
cap.release()
cv2.destroyAllWindows()