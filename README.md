# Target-Grabbing-Based-on-Raspberry
[演示视频](https://github.com/Forrest554/Target-Grabbing-Based-on-Raspberry/blob/master/image/Demonstration.mp4)
## 任务要求
（1）使用摄像头识别目标物品。
（2） 使用摄像头单目测距测量目标物与舵机之间的距离，误差在厘米级别。
（3）控制机械臂抓取指定的目标物品。
## 任务思路
![blockchain](https://github.com/Forrest554/Target-Grabbing-Based-on-Raspberry/blob/master/image/mind.png?raw=true)
### 总体思路
先利用相似三角形原理来实现摄像头视频像素大小和实际距离大小的转换，通过辅助纸来方便确定摄像头位置，通过9999端口监听，添加互斥锁，因为一次只有一个线程可以操控舵机，利用HSV进行颜色识别，利用分水岭算法进行图像分割，形状识别，还加入了LBP特征的机器学习，调用detectMultiScale函数进行不规则玩偶的识别，识别出图像后返回中心坐标，将坐标进行转换，再借助五边形抓取公式来实现机械臂的弯曲抓取。
### 具体实现
（1）用相似三角形计算物体或者目标到相机的距离，这个方法对摄像机标定的要求比较高，同时要求镜头本身造成的畸变就比较小，但总体来说这种方法的可移植性和实用性都较强。且实验由于摄像头放置得不是很远，所以可以忽略畸变。其主要的思路还是小孔成像的模型。且加入了田字辅助纸方便寻找摄像头的位置。
（2）图像分割算法提取前景，通过preprocessHSV - 通过HSV分割，目前在计算机视觉领域存在着较多类型的颜色空间(color space)。HSL和HSV是两种最常见的圆柱坐标表示的颜色模型,它重新影射了RGB模型,从而能够视觉上比RGB模型更具有视觉直观性。我们采用了HSV颜色模型，分割更精准。
（3）使用膨胀、腐蚀、fillHole孔洞填充、分水岭算法对图像进行处理，获得封闭的边界曲线，在分割的过程中，它会把跟临近像素间的相似性作为重要的参考依据，从而将在空间位置上相近并且灰度值相近（求梯度）的像素点互相连接起来构成一个封闭的轮廓，利用findContours()等函数实现了我们自己的findcircle函数。
（4） 基于LBP特征的机器学习，利用正负样本数据以及使用opencv提供的opencv_createsamples.exe程序生成样本文件，使用opencv_traincascade.exe进行训练，每一级的强训练器达到预设的比例后就跑去训练下一级，等bat跑结束后，我们所需的xml文件就生成了，之后我们就可以拿来测试了。
（5） 自己设计的通式机械臂抓取，通过测量可知a、b、c、h四边，通过摄像头拍摄到的坐标可计算出d，知道五条边的长度，首先开始弯曲alpha角，根据m、b、c可以计算theta的角度，直到大于90°最后计算出beta角度，可见示意图。

![blockchain](https://github.com/Forrest554/Target-Grabbing-Based-on-Raspberry/blob/master/image/arm_demonstration.png?raw=true)
### 其他
利用python的Tkinter接口制作了界面，界面包含一个视频窗口和三个功能按键，本系统可通过两种方式下达指令。既可通过Button按钮改变全局变量data来实现指令的下达，同时还利用了Socket通信，完成局域网内的远程操控，同样可以下达指令，且利用Socket通信可以直接输入自己想要的颜色既可实现识别和抓取。
#### 效果截图
![blockchain](https://github.com/Forrest554/Target-Grabbing-Based-on-Raspberry/blob/master/image/arm_demon.png?raw=true)
##### 设计和研发人员
数字图像处理课程第七小组
