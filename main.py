import cv2
import time
import os
import numpy as np
import serial, time

ser = serial.Serial('com10', 9600, timeout=1)
time.sleep(1)

coordX, coordY = 0, 0
centroidX, centroidY = 640, 360
coordX_trashcan, coordY_trashcan = 0, 0 

CONFIDENCE_THRESHOLD = 0.2
NMS_THRESHOLD = 0.4
COLORS = [(0, 255, 255), (255, 255, 0), (0, 255, 0), (255, 0, 0)]
class_names = []
with open(r"yolov4-custom.txt", "r") as f:
    class_names = [cname.strip() for cname in f.readlines()]

vc = cv2.VideoCapture("MyVideo.mp4")
net = cv2.dnn.readNet(r"yolov4-custom_best.weights", r"yolov4-custom.cfg")
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
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
	cv2.imwrite('TEST.jpg',frame)
	return Point

def DistanceToCentroid(Point):
	Distance = [(P[0] - centroidX, P[1] - centroidY) for P in Point]
	return Distance

def DistanceToStep(Distance):
	alphaX, betaX = 10, 0
	alphaY, betaY = 10, 0
	Step = []
	for D in Distance:
		stepX = alphaX * D[0] + betaX
		stepY = alphaY * D[1] + betaY
		Step.append((stepX, stepY))
	return Step


def StepToCoordWeed(Step):
	CoordWeed = [(coordX + S[0], coordY + S[1]) for S in Step]
	return CoordWeed

def Transmit(X, Y):
	temp = "${};{};0#".format(X, Y)
	ser.write(temp.encode())



for cameraX, cameraY in [(0,0)]:
	Transmit(cameraX - coordX, cameraY - coordY)
	coordX, coordY = cameraX, cameraY # update new coord
	print(coordX, coordY)
	Point = TakePicture()
	Distance = DistanceToCentroid(Point)
	Step = DistanceToStep(Distance)
	CoordWeed = StepToCoordWeed(Step)
	#Step = [(5000,0), (-5000,0)]
	for CW in CoordWeed:
		Transmit(CW[0] - coordX, CW[1] - coordY)
		coordX, coordY = CW[0], CW[1] # update new coord
		print(coordX, coordY)

		#Bo co vao thung rac
		Transmit(coordX_trashcan - coordX, coordY_trashcan - coordY)
		coordX, coordY = coordX_trashcan, coordY_trashcan
		print(coordX, coordY)
	
	x = ser.readline()
	print(x)