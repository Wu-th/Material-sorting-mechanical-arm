'''
    2021-04-14
    树莓派摄像头通过opencv进行颜色识别并发送给arduino
    摄像头：排线摄像头
    通信方式后：usb数据线
    接收：arduno
    by: wu@@@
'''
'''
    2021-04-26
    树莓派摄像头通过opencv进行轮廓识别并发送给arduino
    摄像头：排线摄像头
    通信方式后：usb数据线
    接收：arduno
    在上一版颜色识别的基础上改进的
    上一版编辑日期：2021-04-14
    by: wu@@@
'''
import numpy as np
import cv2
import serial

green_lower = np.array([35,43,46])
green_upper = np.array([77,255,255])  #绿色
# blue_lower = np.array([100,43,46])
# blue_upper = np.array([124,255,255])  #蓝色
red_lower = np.array([156,43,46])
red_upper = np.array([180,255,255])  #红色
# yellow_lower = np.array([26,43,46])
# yellow_upper = np.array([34,255,255])  #黄色

Port = "COM5"  # 串口
baudRate = 9600  # 波特率

ser = serial.Serial(Port, baudRate, timeout=1)
camera = 1                              #摄像头序号

def yanse():                           #颜色识别
        cap = cv2.VideoCapture(camera+cv2.CAP_DSHOW)    
        cap.set(3, 320)
        cap.set(4, 240)
        ret,frame = cap.read()
        frame = cv2.GaussianBlur(frame, (5, 5), 0)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        edged = cv2.inRange(hsv, (0, 0, 0), (180, 255, 255))
        edged = cv2.dilate(edged, None, iterations=2)       #膨胀操作
        edged = cv2.erode(edged, None, iterations=2)
        
        mask1 = cv2.inRange(hsv, green_lower, green_upper)
        #mask2 = cv2.inRange(hsv, blue_lower, blue_upper)
        mask3 = cv2.inRange(hsv, red_lower, red_upper)
        #mask4 = cv2.inRange(hsv, yellow_lower, yellow_upper)
        mask = {"green": mask1,"red": mask3, }   #"blue": mask2, "yellow": mask4
        for key, value in mask.items():
            target = cv2.bitwise_and(edged, edged, mask=value)
            cnts = cv2.findContours(target, cv2.RETR_EXTERNAL,
                                        cv2.CHAIN_APPROX_SIMPLE)[-2]
            for c in cnts:
                # if the contour is not sufficiently large, ignore it
                if cv2.contourArea(c) <100:
                    continue
                else:
                    # y = i
                    print(key)
                    return(key)
        # cv2.imshow('frame', frame)
        # cv2.imshow('mask', value)
        # cv2.imshow('res', target)
        #if cv2.waitKey(5) & 0xFF == 27:
        #    break
        cap.release()
        cv2.destroyAllWindows() 
def yanse1():
    c = yanse()
    if(c == 'red'):
        send = 'r'  # 发送给arduino的数据
        ser.write(send.encode())    
    if(c == 'green'):
        send = 'g'  # 发送给arduino的数据
        ser.write(send.encode())         
    # if(c == 'yellow'):
    #     send = 'y'  # 发送给arduino的数据
    #     ser.write(send.encode())  
def LKSB():                            #轮廓识别
    cap = cv2.VideoCapture(camera+cv2.CAP_DSHOW)
    
    while True:
        _,frame = cap.read()
        # if frame.isEmpty():
        #     break
        # cv2.imshow('frame', frame)
        gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        #图像模糊
        bl=cv2.blur(gray, (7,7))
        #canny边缘检测
        thresh=cv2.Canny(bl,0,30,3)
        #cv2.imshow("Pick Picture:",frame)
        # 寻找轮廓
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        #面积数组
        area = []    
        # 找到最大的轮廓
        for k in range(len(contours)):
            area.append(cv2.contourArea(contours[k]))
        max_idx = np.argmax(np.array(area))   
        # 画出轮廓，-1,表示所有轮廓，颜色为(0, 255, 0)，即Green，粗细为1
        cv2.drawContours(frame, contours, max_idx, (0, 255, 0), 2)   
        # 弹出显示视频
        # cv2.imshow('Capture', frame)
        #输出最大面积值
        # print(max(area))  
        if(max(area) > 100):
            print(max(area))
            return('w')
        #按esc退出 
        # a=cv2.waitKey(30)
        # if a == 27:#exit
        #     break 

    # 完成所有操作后，释放捕获器    
    cap.release()
    cv2.destroyAllWindows()
    # del cv2
    # del np
def lunkuo1():
    c = LKSB()
    if(c == 'w'): 
        send = 'w'  # 发送给arduino的数据
        ser.write(send.encode())  
while True:
    # send = 'r'  # 发送给arduino的数据
    #ser.write("hello")
    str = ser.read().decode()  # 获取arduino发送的数据
    if(str != ""):
        # print(str)
        if(str == 'Y'): # 发送一次便退出
            yanse1()
            #break
        if(str == 'L'): # 发送一次便退出
            lunkuo1()
            #break 
    # #按esc退出 
    # a=cv2.waitKey(30)
    # if a == 27:#exit
    #     break     
ser.close()                    
          