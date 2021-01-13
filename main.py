import cv2
import time
import os
import numpy as np
import serial, time
from calibration import CameraCalib
import json

PathJson = '/home/tson99/Documents/NCKH-2020/camera.json'
mtx = []
dist = []
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(1)
ith = 0

coordX, coordY = 0, 0
centroidX, centroidY = 640, 360              #Dua vao thong so cua camera
coordX_trashcan, coordY_trashcan = 0, 100 

CONFIDENCE_THRESHOLD = 0.01
NMS_THRESHOLD = 0.4 #0.4
COLORS = [(0, 255, 255), (255, 255, 0), (0, 255, 0), (255, 0, 0)]
class_names = []
with open(r"/home/tson99/Documents/NCKH-2020/yolov4_origin.txt", "r") as f:
    class_names = [cname.strip() for cname in f.readlines()]

vc = cv2.VideoCapture(0)
vc.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
vc.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
net = cv2.dnn.readNet(r"/home/tson99/Documents/NCKH-2020/yolov4-custom_best.weights", r"/home/tson99/Documents/NCKH-2020/yolov4-custom.cfg")
#net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
#net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
model = cv2.dnn_DetectionModel(net)
model.setInputParams(size=(608, 608), scale=1/255) #(320, 320), (416, 416), (608, 608)

def TakePicture():
	Point = []
	(_, frame) = vc.read()
	#cam = CameraCalib(mtx, dist)
	#frame = cam.CalibrationImg(orig)
	classes, scores, boxes = model.detect(frame, CONFIDENCE_THRESHOLD, NMS_THRESHOLD)
	for (classid, score, box) in zip(classes, scores, boxes):
		color = COLORS[int(classid) % len(COLORS)]
		label = "%s : %f" % (class_names[classid[0]], score)
		X, Y = int(box[0] + (box[2] / 2)), int(box[1] + (box[3] / 2))
		if class_names[classid[0]].startswith('co'):
			Point.append((X,Y)) 
			cv2.circle(frame, (X,Y), radius=2, color=(0, 0, 255), thickness=5)
		cv2.rectangle(frame, box, color, 2)
		cv2.putText(frame, label, (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
	cv2.imwrite(r'Image/TEST{}.jpg'.format(ith),frame)
	return Point

def DistanceToCentroid(Point):
	Distance = [(P[0] - centroidX, P[1] - centroidY) for P in Point]
	return Distance

def DistanceToStep(Distance):
	alphaX, betaX = 23.2, 0
	alphaY, betaY = 13.5, -7950
	Step = []
	for D in Distance:
		stepX = int(alphaX * D[0]) + betaX
		stepY = int(alphaY * D[1]) + betaY
		Step.append((stepX, stepY))
	return Step


def StepToCoordWeed(Step):
	CoordWeed = [(coordX + S[0], coordY + S[1]) for S in Step]
	return CoordWeed

def Transmit(X, Y, Z):
	temp = "${};{};{}#".format(X, Y, Z)
	ser.write(temp.encode())

def DecodeJson(Path):
	f = open(Path, "r")
	data = json.loads(f.read())
	for i in data['K']:
		mtx.append(i)
	for i in data['D']:
		dist.append(i)
	f.close()

#DecodeJson(PathJson)
#mtx = np.asarray(mtx)
#dist = np.asarray(dist)


for cameraX, cameraY in [(25000,10000)]: #(25000,0),(25000,7900),(25000,15800),(25000,21900)]
	ith += 1
	Transmit(cameraX, cameraY, 0)
	coordX, coordY = cameraX, cameraY # update new coord
	print("Goc chup thu {}".format(ith))
	print("Toa do chup anh (X, Y) = ({},{})".format(coordX, coordY))
	time.sleep(8)
	Point = TakePicture()


	Point = [(206,551),(1077,696)]
	

	Distance = DistanceToCentroid(Point) #So diem pixel tu co toi tam
	Step = DistanceToStep(Distance)
	CoordWeed = StepToCoordWeed(Step)
	for CW in CoordWeed:
		coordX, coordY = CW[0], CW[1]  #update new coord
		Transmit(coordX, coordY, 0)
		print("Toa do co (X, Y) = ({},{})".format(coordX, coordY))
		time.sleep(8)

		
		#Bo co vao thung rac
		Transmit(coordX, coordY, 1)
		time.sleep(8)
		Transmit(coordX, coordY, -1)
		time.sleep(8)
		
		coordX, coordY = coordX_trashcan, coordY  #update new coord
		Transmit(coordX, coordY, 0)
		print("Toa do thung rac (X, Y) = ({},{})".format(coordX, coordY))
		time.sleep(8)
		Transmit(coordX, coordY, 1)
		time.sleep(8)
		Transmit(coordX, coordY, -1)
		time.sleep(8)
		
	#flag = None
	#Neu nhan dc ky tu gui tu Arduino thi lam vong for tiep theo
	#x = ser.readline()
	#print(x)

Transmit(0, 0, 0)
coordX, coordY = 0, 0