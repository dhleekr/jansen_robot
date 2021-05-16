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
from ar_markers import detect_markers

httpd = None
DISPLAY = False#'DISPLAY' in environ

def cascade(img):
    cascade_stop = cv2.CascadeClassifier('./cascade.xml')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = cascade_stop.detectMultiScale(gray, 1.2, 5)
    if faces is ():
        return 'bad'
    else:
        return 'good'

def select_white(image, white):
    lower = np.uint8([white,white,white])
    upper = np.uint8([255,255,255])
    white_mask = cv2.inRange(image, lower, upper)
    return white_mask

def first_nonzero(arr, axis, invalid_val=-1):
    arr = np.flipud(arr)   
    mask = arr != 0
    return np.where(mask.any(axis=axis), mask.argmax(axis=axis), invalid_val)

def path_decision(image, forward_cri):
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

        if forward < 20:
            result = 'back'

        elif forward < 50 and abs(m) < 0.25:
            result = 'uturn'

        elif abs(m) < forward_cri:
            result = 'forward'

        elif m > 0:
            result = 'left'

        else:
            result = 'right'

    except:
        result = 'back'
        m = 0
    
    return result, round(m,4), forward



class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        print("Write to stdin")
        while True:
            key = readkey()
            if key == '\x03':
                break

            data = {"action": key}
            print(Time(), 'Sending', data)
            self.wfile.write(bytes(json.dumps(data), encoding='utf8'))
            self.wfile.write(b'\n')

        self.finish()
        httpd.shutdown()
    
    def do_POST(self):
        self.send_response(200)
        self.send_header('X-Server2Client', '123')
        self.end_headers()

        data = self.rfile.read(int(self.headers['Content-Length']))
        data_numpy = np.asarray(bytearray(data), dtype="uint8")
        img = cv2.imdecode(data_numpy, cv2.IMREAD_ANYCOLOR)
        markers = detect_markers(img)
        mark_result = ' '
        if markers:
            for marker in markers:
                print("detected", marker.id)
                marker.highlite_marker(img)
                if marker.id == 114:
                    mark_result = 'left'
                if marker.id == 922:
                    mark_result = 'right'
                if marker.id == 2537:
                    mark_result = 'stop'
        
        cas_result = cascade(img)

        masked_img = select_white(img, 120)

        k = path_decision(masked_img, 0.25)
        y1, x1 = masked_img.shape
        x1 = int(x1/2)
        x2 = int(-k[2] * k[1] + x1)
        y2 = y1-k[2]
        # cv2.line(image,(x1,y1),(x2,y2),(0,0,255),2)  
        cv2.line(masked_img,(x1,y1),(x2,y2),(100),2)
        
        with open('rawvideo.jpg', 'wb') as File:
            File.write(data)

        with open('mask.jpg', 'wb') as File:
            result, masked_data = cv2.imencode('.jpg', masked_img, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
            File.write(masked_data)
            print('m : {}'.format(k[1]))
            print('forward : {}'.format(k[2]))

        send = {"action": k[0], "markers" : mark_result, "cascade" : cas_result}        
        self.wfile.write(
            bytes(json.dumps(send), encoding='utf8'))
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