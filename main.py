from scratch import Scratch
from findCircle import FindCircle
import cv2
import time
import threading
import math
import HSVCOLOR
import socket

def convert(px, py, ratio):
	'''
	这个函数将图像坐标转换成真实坐标
	Parameter:
	  px, py - 图像的x, y轴坐标
	  ratio - 真实长度与像素长度的比
	Returns:
	  px, py - 以机械臂底盘为圆心的x, y坐标
	'''
	px -= img_width / 2
	py -= img_height / 2
	px = px * ratio
	py = py * ratio
	# 下面需要根据照相机方向调整
	px = camera_x + px
	py = camera_y + py
	return (px, py)

# 计算相对误差
def error(x, px):
	return math.fabs((x - px) / px)

# 添加互斥锁，因为一次只有一个线程可以操控舵机
def implement(px, py):
	mutex.acquire()
	scratch.scratch(px, py)
	mutex.release()

# socket 服务端监听
def listen():
	global data
	while True:
		data = sk.recv(1024)

# 需要测量的参数
img_width = 640  # 每一帧的像素宽度
img_height = 480 # 每一帧的像素高度
real_width = 31   # 真实宽度(单位cm)
camera_x = 0     # 照相机相对于机械臂底盘圆心的x坐标
camera_y = 18.7	 # 照相机相对于机械臂底盘圆心的y坐标

# 容差参数，主要用于让被抓物体固定不动后再去抓
ERROR = 0.005
MAX = 8

# 初始化
data = '' 
lastdata = ''
ip_port = ('10.0.0.1', 9999) # 监听9999端口
sk = socket.socket(socket.AF_INET,socket.SOCK_DGRAM,0) # UDP协议
sk.bind(ip_port)
st = threading.Thread(target = listen, args = ())
st.start()

count = MAX
mutex = threading.Lock()
scratch = Scratch()
capture = cv2.VideoCapture(0)
ratio = real_width / img_width
cascade = cv2.CascadeClassifier('/Users/guliqi/Desktop/Classifier/xml/cascade.xml')

while True:
	ret, frame = capture.read()

	if data != '':
		if data.upper() == b'COALA': # 抓考拉
			gray = frame.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			kolas = cascade.detectMultiScale(gray, 2.4, 7)
			objects = []
			for (x, y, w, h) in kolas:
				frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
				objects.append((x + w / 2, y + h / 2))
		else if data.upper() == b'CLEAR': # 清空
			data = ''
		else: # 根据颜色抓球
			if lastdata != data:
				sdata = str(data, encoding = 'utf8').upper()
				colors = sdata.split('&')
				HSVlist = []
				for color in colors:
					if color in HSVCOLOR.ColorDic:
						HSVlist.append(HSVCOLOR.ColorDic[color])
			lastdata = data
			fc = FindCircle(frame, frame = True)
			fc.preprocessHSV(HSVlist)
			fc.setborder()
			objects = fc.findcircle()

	cv2.imshow('frame', frame)
	cv2.waitKey(30)
	if len(objects) != 0:
		if count == MAX:
			px = objects[0][0]
			py = objects[0][1]
			count -= 1
		else:
			if error(objects[0][0], px) >= ERROR\
			  or error(objects[0][1], py) >= ERROR:
				count = MAX
			else:
				px = objects[0][0]
				py = objects[0][1]
				count -= 1
	else:
		count = MAX
	if count == 0:
		count = MAX
		data = ''
		(px, py) = convert(px, py, ratio)
		t = threading.Thread(target = implement, args = (px, py))
		t.start()
		cv2.waitKey(0) # 保持图像，按键后继续