BLACK = [[0, 0, 0, 180, 255, 35]]
GRAY = [[0, 0, 35, 180, 43, 220]]
WHITE = [[0, 0, 221, 180, 30, 255]]
RED = [[0, 43, 35, 10, 255, 255], [156, 43, 35, 180, 255, 255]]
ORANGE = [[11, 43, 35, 25, 255, 255]]
YELLOW = [[26, 43, 35, 34, 255, 255]]
GREEN = [[35, 43, 35, 77, 255, 255]]
CYAN = [[78, 43, 35, 99, 255, 255]]
BLUE = [[100, 43, 35, 124, 255, 255]]
PURPLE = [[125, 43, 35, 155, 255, 255]]

ColorDic = {}

strs = ['BLACK', 'GRAY', 'WHITE', 'RED', 'ORANGE', 'YELLOW',\
	'GREEN', 'CYAN', 'BLUE', 'PURPLE']
for s in strs:
	ColorDic.update({s : eval(s)})