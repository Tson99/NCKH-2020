import cv2
import time
import os
import numpy as np
import serial, time

ser = serial.Serial('com10', 9600, timeout=1)
time.sleep(1)
ith = 0

coordX, coordY = 0, 0
centroidX, centroidY = 640, 360              #Dua vao thong so cua camera
coordX_trashcan, coordY_trashcan = 0, 100 

CONFIDENCE_THRESHOLD = 0.1
NMS_THRESHOLD = 0.4
COLORS = [(0, 255, 255), (255, 255, 0), (0, 255, 0), (255, 0, 0)]
class_names = []
with open(r"yolov4-custom.txt", "r") as f:
    class_names = [cname.strip() for cname in f.readlines()]

vc = cv2.VideoCapture(0)
net = cv2.dnn.readNet(r"yolov4-custom_best.weights", r"yolov4-custom.cfg")
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
vc.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
vc.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
model = cv2.dnn_DetectionModel(net)
model.setInputParams(size=(608, 608), scale=1/255) #(320, 320), (416, 416), (608, 608)

def TakePicture():
	Point = []
	(_, frame) = vc.read()
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
	cv2.imwrite(r'Image\TEST{}.jpg'.format(ith),frame)
	return Point

def DistanceToCentroid(Point):
	Distance = [(P[0] - centroidX, P[1] - centroidY) for P in Point]
	return Distance

def DistanceToStep(Distance):
	alphaX, betaX = 20, 0
	alphaY, betaY = 20, -7900 #-13589
	Step = []
	for D in Distance:
		stepX = int(alphaX * D[0]) + betaX
		stepY = int(alphaY * D[1]) + betaY
		Step.append((stepX, stepY))
	return Step


def StepToCoordWeed(Step):
	CoordWeed = [(coordX + S[0], coordY + S[1]) for S in Step]
	return CoordWeed

def Transmit(X, Y):
	temp = "${};{};0#".format(X, Y)
	ser.write(temp.encode())


for cameraX, cameraY in [(25000,15800)]: #(25000,0),(25000,7900),(25000,15800),(25000,21900)]
	ith += 1
	Transmit(cameraX, cameraY)
	coordX, coordY = cameraX, cameraY # update new coord
	print("Goc chup thu {}".format(ith))
	print("Toa do chup anh (X, Y) = ({},{})".format(coordX, coordY))
	time.sleep(8)
	Point = TakePicture()
	Distance = DistanceToCentroid(Point)

	Step = DistanceToStep(Distance)
	CoordWeed = StepToCoordWeed(Step)
	
	for CW in CoordWeed:
		Transmit(CW[0], CW[1])
		coordX, coordY = CW[0], CW[1] # update new coord
		print("Toa do co (X, Y) = ({},{})".format(coordX, coordY))
		time.sleep(8)
		#Bo co vao thung rac
		Transmit(coordX_trashcan, coordY)
		coordX, coordY = coordX_trashcan, coordY
		print("Toa do thung rac (X, Y) = ({},{})".format(coordX, coordY))
		time.sleep(8)
	#flag = None
	#Neu nhan dc ky tu gui tu Arduino thi lam vong for tiep theo
	#x = ser.readline()
	#print(x)

Transmit(0, 0)
coordX, coordY = 0, 0
	