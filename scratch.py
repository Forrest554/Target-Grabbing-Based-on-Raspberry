import pigpio
import time
import math
import numpy as np
'''
这个类实现了给定x, y坐标后实现抓取(x, y单位为cm)
'''
class Scratch:
	def __init__(self):
		self.h = 9.5 # 底盘高度
		self.a = 10.5 # 从下往上三个臂长
		self.b = 8.85
		self.c = 17.0
		self.e = 1.0 # 底盘圆心与机械臂距离

		self.pi = pigpio.pi()
		self.pins = [12, 16, 20, 21, 19, 13]
		self.currents = np.uint16(np.ones(6) * 1500)
		self.restore()

	def __getindex(self, pin):
		for i, p in enumerate(self.pins):
			if p == pin:
				return i
		return -1

	def restore(self):
		for pin in self.pins:
			self.pi.set_PWM_range(pin, 20000)
			self.pi.set_PWM_frequency(pin, 50)
			self.pi.set_PWM_dutycycle(pin, 1500)

	def clamp(self, motion = 'clamp'):
		pin = 12
		if motion == 'open':
			for i in range(1500, 500-1, -5):
				self.pi.set_PWM_dutycycle(pin, i)
				time.sleep(0.01)
		elif motion == 'close':
			for i in range(500, 1500+1, 5):
				self.pi.set_PWM_dutycycle(pin, i)
				time.sleep(0.01)
		elif motion == 'clamp':
			self.clamp(motion = 'open')
			self.clamp(motion = 'close')

	def setloc(self, pin, loc, Radian = False):
		index = self.__getindex(pin)
		assert index != -1
		start = self.currents[index]
		if Radian == True:
			loc = loc * 2 / math.pi * 1000 + 1500
		loc = round(loc)
		assert loc <= 2500 and loc >= 500
		self.currents[index] = loc
		loc = loc + 1 if loc > start else loc - 1
		step = 5 if loc > start else -5
		for i in range(start, loc, step):
			self.pi.set_PWM_dutycycle(pin, i)
			time.sleep(0.01)

	def scratch(self, x, y):
		d = (x * x + y * y) ** 0.5 - self.e
		for alpha in range(180, 90, -1):
			alpha = alpha * math.pi / 180
			d1 = d - self.a * math.cos(alpha - math.pi / 2)
			d2 = self.h + self.a * math.sin(alpha - math.pi / 2)
			m = (d1 ** 2 + d2 ** 2) ** 0.5
			if self.b + self.c < m:
				continue
			theta = math.acos((self.b * self.b + self.c * self.c - m * m) / (2 * self.b * self.c))
			if theta < math.pi / 2:
				continue
			beta1 = 1.5 * math.pi - alpha - math.acos(d1 / m)
			beta2 = math.acos((self.b * self.b + m * m - self.c * self.c) / (2 * self.b * m))
			beta = beta1 + beta2
			if beta < math.pi / 2:
				continue
			# 旋转底盘
			dest = math.atan(x / y) * 2 / math.pi * 1000 + 1500
			self.setloc(13, dest)
			if self.currents[2] != 1500:
				self.setloc(16, 1500)
			# 旋转舵机
			self.setloc(19, math.pi - alpha, Radian = True)
			self.setloc(21, -(math.pi - beta), Radian = True)
			self.clamp('open')
			self.setloc(20, -(math.pi - theta), Radian = True)
			self.clamp('close')
			for i in self.pins:
				self.setloc(i, 1500)
			return
		print('cannot access!')
		
if __name__ == '__main__':
	s = Scratch()
	s.scratch(-15,15)