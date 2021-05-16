PORT = 8000

from http.server import BaseHTTPRequestHandler
import socketserver
import json
from readchar import readkey
from sys import argv
from os import environ
import numpy as np
import cv2
from Time import Time

httpd = None
DISPLAY = 'DISPLAY' in environ

"""  
stop sign
"""
def signal(image, path):
    signal_cascade = cv2.CascadeClassifier(path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = signal_cascade.detectMultiScale(gray, 1.2, 5)
    if faces is ():
        return 'bad'
    else:
        for (x,y,w,h) in faces:
            if w > 40:
                cv2.rectangle(image, (x,y),(x+w,y+h),(255,0,0),2)
                return 'good'
            else:
                return 'bad'

def ar_left(image):
    cascade = cv2.CascadeClassifier('114_2.xml')
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = cascade.detectMultiScale(gray, 1.2, 5)
    if faces is ():
        return 'no'
    else:
        for (x,y,w,h) in faces:
            if w > 60:
                cv2.rectangle(image, (x,y),(x+w,y+h),(255,0,0),2)
                return 'left'
            else:
                return 'no'

def ar_stop(image):
    cascade = cv2.CascadeClassifier('2537_2.xml')
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = cascade.detectMultiScale(gray, 1.2, 5)
    if faces is ():
        return 'no'
    else:
        for (x,y,w,h) in faces:
            if w > 50:
                cv2.rectangle(image, (x,y),(x+w,y+h),(255,0,0),2)
                return 'stop'
            else:
                return 'no'



"""  
mask
"""
def select_white(image, white):
    lower = np.uint8([white,white,white])
    upper = np.uint8([255,255,255])
    white_mask = cv2.inRange(image, lower, upper)
    return white_mask


"""  
방향 결정
"""
def first_nonzero(arr, axis, invalid_val=-1):
    arr = np.flipud(arr)   
    mask = arr != 0
    return np.where(mask.any(axis=axis), mask.argmax(axis=axis), invalid_val)

def sum_of_zeromask(arr, height, forward):
    mask = arr == 0
    zeromask = np.where(mask, 1, 0)
    left_sum = np.sum(zeromask[height-forward:height, :160])
    right_sum = np.sum(zeromask[height-forward:height, 160:])


def set_path2(image, upper_limit, fixed_center = 'False'):
    height, width = image.shape
    image = image[height-upper_limit:,:]
    height = upper_limit-1
    width = width-1
    center=int(width/2)
    left=0
    right=width       
    
    if not fixed_center:
        center = int((left+right)/2)        
        if image[height][:center].min(axis=0) == 255:
            left = 0
        else:
            left = image[height][:center].argmin(axis=0)
        
        if image[height][center:].max(axis=0) == 0:
            right = width
        else:    
            right = center+image[height][center:].argmax(axis=0)        
        center = int((left+right)/2)  
    
    image = np.flipud(image) # in python3, np.flip(image, axis=0)
    mask = image!= 0
    integral = np.where(mask.any(axis=0), mask.argmax(axis=0), height) 
    
    left_sum = np.sum(integral[left:center])
    right_sum = np.sum(integral[center:right])
    forward_sum = np.sum(integral[center-10:center+10])   
    
    return forward_sum, left_sum, right_sum

def set_path3(image, forward_cri):
    height, width = image.shape
    height = height-1
    width = width-1
    center=int(width/2)
    left=0
    right=width
    
    center = int((left+right)/2)      

    try:
        if image[height][:center].min(axis=0) == 255:
            left = 0
        else:
            left = image[height][:center].argmin(axis=0)    
        if image[height][center:].max(axis=0) == 0:
            right = width
        else:    
            right = center+image[height][center:].argmax(axis=0)  
        center = int((left+right)/2)
        
        # print(int(first_nonzero(image[:,center],0,height)))

        forward = min(int(height),int(first_nonzero(image[:,center],0,height))-1)
        #print(height, first_nonzero(image[:,center],0,height))
        
        left_line = first_nonzero(image[height-forward:height,center:],1, width-center)
        right_line = first_nonzero(np.fliplr(image[height-forward:height,:center]),1, center)
        
        center_y = (np.ones(forward)*2*center-left_line+right_line)/2-center
        center_x = np.vstack((np.arange(forward), np.zeros(forward)))
        m, c = np.linalg.lstsq(center_x.T, center_y, rcond=-1)[0]

    except:
        m = 0
    
    return m, forward

""" 
통신 
"""
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.end_headers()

        print("Write to stdin")
        # while True:
        data = {"action": self.result[0]}
        print(Time(), 'Sending', data)
        self.wfile.write(
            bytes(json.dumps(data), encoding='utf8'))
        self.wfile.write(b'\n')

        self.finish()
        httpd.shutdown()



    def do_POST(self):
        self.send_response(200)
        # self.send_header("")
        self.end_headers()

        # 이미지 받음
        data = self.rfile.read(int(self.headers['Content-Length']))
        data = np.asarray(bytearray(data), dtype="uint8")
        img = cv2.imdecode(data, cv2.IMREAD_ANYCOLOR)
        masked_img = select_white(img, 120)
        # masked_img = edge_detection(img)
        """  
        순서 : 거리 -> ar marker -> cascade -> 방향결정
        """
        left_res = ar_left(img)
        stop_res = ar_stop(img)
        
        c = signal(img, './cascade.xml')

        forward_sum, left_sum, right_sum = set_path2(masked_img, 120)
        m, forward = set_path3(masked_img, 0.25)

        if forward < 25 or forward_sum < 1300 :
            result = 'back'
        elif abs(m)< 0.15 and forward > 100: # + forward sum 이용하기
            result = 'forward'
        elif forward < 80 and abs(m) < 0.2 and abs(left_sum - right_sum) < 1000 and left_sum < 13000 and right_sum < 13000:
            result = 'uturn'
        elif m > 0 or left_sum > right_sum + 90:
            result = 'left' 
        elif m < 0 or left_sum < right_sum - 90:
            result = 'right'
        
        else:
            result = 'back'

        y1, x1 = masked_img.shape
        x1 = int(x1/2)
        x2 = int(-forward * round(m,4) + x1)
        y2 = y1-forward
        # cv2.line(image,(x1,y1),(x2,y2),(0,0,255),2)  
        cv2.line(masked_img,(x1,y1),(x2,y2),(100),2)

        if DISPLAY:
            cv2.imshow('Masked image', masked_img)
            # cv2.imshow('Raw image', img)
            cv2.waitKey(1)
            pass


        data = {"action": result, "ar_left" : left_res, "ar_stop" : stop_res,"cascade" : c}
        # data = {"action": result[0]}
        print(Time(), 'Sending', data)
        print('forward : {}\nforward_sum : {}\nleft_sum : {}\nright_sum : {}'.format(forward, forward_sum, left_sum, right_sum))
        self.wfile.write(bytes(json.dumps(data), encoding='utf8'))
        self.wfile.write(b'\n')




if __name__ == '__main__':
    with socketserver.TCPServer(("0.0.0.0", PORT),
                                Handler,
                                bind_and_activate=False) as httpd:
        httpd.server = httpd
        httpd.allow_reuse_address = True
        httpd.server_bind()
        httpd.server_activate()
        print("HTTPServer Serving at port", PORT)
        httpd.serve_forever()