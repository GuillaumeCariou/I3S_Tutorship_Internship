import cv2

vid = cv2.VideoCapture(0)

while True:
    ret, original = vid.read()
    cv2.imshow('Camera View', original)
    # stop the program by pressing q
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

