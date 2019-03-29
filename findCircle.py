import cv2
import numpy as np
import math
import time
import HSVCOLOR
'''
这个类用于找到图像中的圆形，需要调参
找圆算法:
	(1) 图像分割算法提取前景:
		preprocessRGB - 通过RGB或灰度值分割，不推荐使用
		preprocessBG  - 通过拍摄背景与前景色分割，当背景固定时可以使用
		preprocessHSV - 通过HSV分割，推荐使用
	(2) 边缘检测算法获得闭合边缘:
		setborder     - 通过分水岭算法漫延出闭合边界
	(3) 圆形检测算法标出圆形:
		findcircle    - 遍历上面提取到的闭合边界，提取质心，计算边界上的所有点到质心到距离，
						计算距离的变异系数，若变异系数较小则表示边界上所有点到质心到距离相
						差很小，可以得出这是一个圆
'''
class FindCircle:
	def __init__(self, path, frame = False):
		'''
		当传入参数为视频帧时，path = 帧图像，frame = True
		当传入为照片时，path = 照片路径，frame = False
		'''
		if frame == True:
			self.img = path
		else:
			self.img = cv2.imread(path)
			while self.img.shape[0] > 600 and self.img.shape[1] > 600:
				self.img = cv2.pyrDown(self.img)
			while self.img.shape[0] < 300 and self.img.shape[1] < 300:
				self.img = cv2.pyrUp(self.img)
		
	def preprocessRGB(self, x = 5, y = 5 , z = 3, INV = False, thresh = 0):
		'''
		x, y, z    高斯滤波参数
		INV = True 时得到的二值化图像会黑白颠倒
		thresh = 0 时默认使用自适应阈值，否则为传入的阈值
		'''
		gray = cv2.cvtColor(self.img, cv2.COLOR_RGB2GRAY)
		# blue = self.img[:,:,0]
		# green = self.img[:,:,1]
		# red = self.img[:,:,2]
		# RedPlusGreen = np.uint8(red / 2 + green / 2)
		self.gaussian = cv2.GaussianBlur(gray, (x, y), z)
		if INV == False:
			if thresh == 0:
				ret, self.thresh = cv2.threshold(self.gaussian, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
			else:
				ret, self.thresh = cv2.threshold(self.gaussian, thresh, 255, cv2.THRESH_BINARY)
		else:
			if thresh == 0:
				ret, self.thresh = cv2.threshold(self.gaussian, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
			else:
				ret, self.thresh = cv2.threshold(self.gaussian, thresh, 255, cv2.THRESH_BINARY_INV)

	def preprocessBG(self, background, error):
		'''
		background 传入背景灰度图
		error      容差范围
		'''
		gray = cv2.cvtColor(self.img, cv2.COLOR_RGB2GRAY)
		dvalue = np.int8(background) - np.int8(gray)
		self.thresh = np.zeros((self.img.shape[0], self.img.shape[1]), np.uint8)
		self.thresh[np.logical_or(dvalue > error, dvalue < -error)] = 255

	def preprocessHSV(self, HSVColors):
		'''
		HSVColors 必须为HSVCOLOR.py中的颜色list
		'''
		assert HSVColors is not None and len(HSVColors) != 0
		HSV = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)
		masks = []
		for color in HSVColors:
			for i in color:
				low = np.array(i[:3])
				high = np.array(i[3:6])
				masks.append(cv2.inRange(HSV, low, high))
		self.thresh = np.uint8(np.sum(masks, axis = 0))

	def __fillHole(self, dilated):
		'''
		填充孔洞算法
		引自 https://bbs.csdn.net/topics/391542633?page=1
		'''
		temp = np.zeros((dilated.shape[0] + 2, dilated.shape[1] + 2), np.uint8)
		temp[1:-1, 1:-1] = dilated
		cv2.floodFill(temp, None, (0, 0), (255))
		temp = temp[1:-1, 1:-1]
		return dilated + ~temp

	def setborder(self, dilate_iter = 4, erode_iter = 4):
		'''
		dilate_iter 膨胀算法迭代次数
		erode_iter  腐蚀算法迭代次数
		'''
		kernel = np.ones((3,3),np.uint8)
		opening = cv2.morphologyEx(self.thresh, cv2.MORPH_OPEN, kernel, iterations = 2)
		sure_bg = cv2.dilate(opening, kernel, iterations = dilate_iter)
		sure_bg = self.__fillHole(sure_bg)
		# dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 3) # 此处导致sublime崩溃，原因未知
		# ret, sure_fg = cv2.threshold(dist_transform, 0.1 * dist_transform.max(), 255, cv2.THRESH_BINARY)
		# sure_fg = np.uint8(sure_fg)
		closing = cv2.morphologyEx(self.thresh, cv2.MORPH_CLOSE, kernel, iterations = 2)
		sure_fg = cv2.erode(closing, kernel, iterations = erode_iter)
		unknown = cv2.subtract(sure_bg, sure_fg)
		# cv2.imshow('bg', sure_bg)
		# cv2.imshow('fg', sure_fg)
		# cv2.imshow('unknown', unknown)
		ret, markers = cv2.connectedComponents(sure_fg)
		markers = markers + 1
		markers[unknown == 255] = 0
		markers = cv2.watershed(self.img, markers)
		self.border = np.zeros((self.img.shape[0], self.img.shape[1],1), np.uint8)
		self.border[markers == -1] = [255]
		self.border[0] = 0
		self.border[-1] = 0
		self.border[:,0] = 0
		self.border[:,-1] = 0

	def findcircle(self, minsides = 20, minArea = 50, reduce = 0, maxCv = 0.08):
		'''
		minsides 边缘的最小边数
		minArea  边缘的最小面积
		reduce   0-0.5内，去除最大距离和最小距离的比例(0表示不去除)
		maxCv    判断是圆最大可接受的变异系数
		'''
		(_, cnts, _) = cv2.findContours(self.border, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
		lastx, lasty, lastmean = 0, 0, 0
		circles = []
		for i, cnt in enumerate(cnts):
			if len(cnt) >= minsides:
				M = cv2.moments(cnt)
				if M['m00'] <= minArea:
					continue
				mx = int(M['m10'] / M['m00'])
				my = int(M['m01'] / M['m00'])
				cv2.circle(self.border, (mx, my), 1, (255), 2)
				list = []
				for coordinate in cnt:
					cx = coordinate[0][0]
					cy = coordinate[0][1]
					list.append(((mx - cx) * (mx - cx) + (my - cy) * (my - cy)) ** 0.5)
				
				list.sort(reverse = True)
				Reduce = round(len(list) * reduce)
				list = list[Reduce : len(list) - Reduce]
				mean = np.mean(list)
		
				rate = 0.05
				# 判断边缘重复
				if i > 1:
					if math.fabs((lastx - mx) / mx) < rate and \
					    math.fabs((lasty - my) / my) < rate and \
					     math.fabs((lastmean - mean) / mean) < rate:
						continue
				lastx = mx
				lasty = my
				lastmean = mean
				# 计算变异系数
				Cv = np.std(list) / mean
				if Cv > maxCv:
					continue

				cv2.circle(self.img, (mx, my), int(mean), (255,0,0), 1)
				circles.append((mx, my, int(mean)))
				# cv2.drawContours(self.img, cnts, j, (0,255,0), 1)
				x,y,w,h = cv2.boundingRect(cnts[i])
				self.img = cv2.rectangle(self.img, (x, y),(x + w, y + h),(0, 255, 0), 2)
		return circles
 
	def show(self):
		cv2.imshow('thresh', self.thresh)
		# cv2.imshow('border', self.border)
		# cv2.imshow('img', self.img)
		# cv2.waitKey(0)

if __name__ == '__main__':
	fc = FindCircle('/Users/guliqi/Downloads/image/light.jpg')
	fc.preprocessHSV([HSVCOLOR.RED])
	fc.setborder()
	circles = fc.findcircle()
	fc.show()