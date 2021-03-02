import cv2

vid = cv2.VideoCapture(0)

while True:
    ret, original = vid.read()
    cv2.imshow('Camera View', original)

