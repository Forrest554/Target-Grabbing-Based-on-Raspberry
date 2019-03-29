import cv2
import numpy as np
import time
from findCircle import FindCircle
import HSVCOLOR

'''
这个文件就是简单打开摄像头，可以测量一些参数
'''

capture = cv2.VideoCapture(0)

# time.sleep(2)
# _grays = []
# for i in range(3):
# 	_ret, _frame = capture.read()
# 	_frame = cv2.pyrDown(_frame)
# 	_grays.append(cv2.cvtColor(_frame, cv2.COLOR_RGB2GRAY))
# _gray = _grays[0]/3 + _grays[1]/3 + _grays[2]/3
# _gray = np.uint8(_gray)

while True:
	ret, frame = capture.read()
	frame = cv2.pyrDown(frame)

	fc = FindCircle(frame, frame = True)
	fc.preprocessHSV([HSVCOLOR.BLUE])
	fc.setborder()
	fc.show()
	circles = fc.findcircle()
	cv2.imshow('frame', frame)
	cv2.waitKey(30)



