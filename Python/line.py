import time

import cv2
import numpy as np
import copy
import math

################################ Settings ##########################################

# Historique
historique_size = 10

# Canny
sigma = 0.33

# Hough Line
minLineLength = 150
maxLineGap = 50
threshold_hough_line = 100

# Angle
max_diff_in_angle = 30


################################ Settings ##########################################


class Line:
    x1 = 0
    y1 = 0
    x2 = 0
    y2 = 0

    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def changeLineValue(self, x1_value, y1_value, x2_value, y2_value):
        self.x1 = x1_value
        self.y1 = y1_value
        self.x2 = x2_value
        self.y2 = y2_value

    def returnValue(self):
        return self.x1, self.y1, self.x2, self.y2

    def length_of_the_line(self):
        x = self.x2 - self.x1
        y = self.y2 - self.y1
        return math.sqrt((x * x) + (y * y))

    def angle(self):
        deltaY = self.y2 - self.y1
        deltaX = self.x2 - self.x1
        angleInDegrees = math.atan2(deltaY, deltaX) * 180 / np.pi
        return angleInDegrees

    def put_line_forward(self):
        if self.y1 > self.y2:
            buffx = self.x1
            buffy = self.y1
            self.x1 = self.x2
            self.y1 = self.y2
            self.x2 = buffx
            self.y2 = buffy


class Historique:
    hist_size = 10
    hist = []
    hist_compteur = 0

    def __init__(self, hist_size):
        self.hist_size = hist_size
        for i in range(self.hist_size):
            self.hist.append(Line(320, 0, 320, 480))

    def getHistoriqueValue(self):
        x1m, y1m, x2m, y2m = 0, 0, 0, 0
        for line in self.hist:
            x1, y1, x2, y2 = line.returnValue()
            x1m += x1
            y1m += y1
            x2m += x2
            y2m += y2

        x1m = int(x1m / len(self.hist))
        y1m = int(y1m / len(self.hist))
        x2m = int(x2m / len(self.hist))
        y2m = int(y2m / len(self.hist))

        return x1m, y1m, x2m, y2m


def calculate_angle(x1, y1, x2, y2):
    deltaY = y2 - y1
    deltaX = x2 - x1
    angleInDegrees = math.atan2(deltaY, deltaX) * 180 / np.pi
    return angleInDegrees


def is_between_max_diff_in_angle(line, hist):
    x1, y1, x2, y2 = hist.getHistoriqueValue()
    angle_mean = abs(calculate_angle(x1, y1, x2, y2))
    angle_line = abs(line.angle())

    if (angle_mean - max_diff_in_angle) <= angle_line <= (angle_mean + max_diff_in_angle):
        return True
    return False


def line_detection(hist, ips, display_image, display_mean, original_picture):
    height, width, channels = original_picture.shape
    size = (width, height)
    # Gaussian Blur
    dst = cv2.GaussianBlur(original_picture, (5, 5), cv2.BORDER_DEFAULT)

    # Gray Scal
    gray = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)

    # Canny
    v = np.median(gray)
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    """
    upper, thresh_im = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    lower = 0.5 * upper
    """
    edge = cv2.Canny(gray, lower, upper, apertureSize=3)

    # Sobel
    grad_x = cv2.Sobel(edge, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(edge, cv2.CV_64F, 0, 1, ksize=3)

    abs_grad_x = cv2.convertScaleAbs(grad_x)
    abs_grad_y = cv2.convertScaleAbs(grad_y)

    grad = cv2.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0)

    # HoughLines
    img_line = copy.copy(original_picture)

    x1m, y1m, x2m, y2m = 0, 0, 0, 0
    lines = cv2.HoughLinesP(grad, 1, np.pi / 180, threshold=threshold_hough_line, minLineLength=minLineLength,
                            maxLineGap=maxLineGap)

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            x1m += x1
            y1m += y1
            x2m += x2
            y2m += y2
            cv2.line(img_line, (x1, y1), (x2, y2), (0, 255, 0), 1)

        x1m = int(x1m / len(lines))
        y1m = int(y1m / len(lines))
        x2m = int(x2m / len(lines))
        y2m = int(y2m / len(lines))
        line_mean = Line(x1m, y1m, x2m, y2m)

        # line_mean.put_line_forward()  # put line in the right way

        # Update Historique
        if (line_mean.length_of_the_line() >= minLineLength / 2):  # if (line_mean.length_of_the_line() >= minLineLength / 2):  #

            hist.hist[hist.hist_compteur].changeLineValue(x1m, y1m, x2m, y2m)
            hist.hist_compteur += 1
            if hist.hist_compteur >= hist.hist_size:
                hist.hist_compteur = 0

        x1m, y1m, x2m, y2m = hist.getHistoriqueValue()

    # Make mean line
    img_line_plus_mean = copy.copy(img_line)
    cv2.line(img_line_plus_mean, (x1m, y1m), (x2m, y2m), (0, 0, 255), 3)

    # Calcule d'angle par rapport a l'axe x
    angle = calculate_angle(x1m, y1m, x2m, y2m)

    # Show Images
    if display_image:
        cv2.imshow('line', original_picture)
        cv2.imshow('line_gray', gray)
        cv2.imshow('line_edge', edge)
        cv2.imshow('Sobel Image', grad)
        cv2.imshow('Line process', img_line)

    if display_mean:
        # Angle
        cv2.putText(img_line_plus_mean, "Degres : " + str(round(angle, 2)), (30, 30), cv2.QT_FONT_NORMAL, 1,
                    (0, 0, 255))
        # Display IPS
        if not ips == 0:
            cv2.putText(img_line_plus_mean, "IPS : " + str(round(ips, 2)), (30, 60), cv2.QT_FONT_NORMAL, 1, (0, 0, 255))
        cv2.imshow('Line process Plus Mean', img_line_plus_mean)

    return round(angle, 2), size, img_line_plus_mean


def caclulate_ips(ips, compteur, after):
    current = time.time()
    if current >= after:
        after = time.time() + 1
        ips = compteur
        compteur = 0
    else:
        compteur += 1

    return ips, compteur, after


def convert_input_into_video_with_line_detection(input_file_name, output_file_name):
    hist = Historique(hist_size=historique_size)

    vid = cv2.VideoCapture(input_file_name)
    size = (0, 0)
    img_array = []
    frame_count = vid.get(cv2.CAP_PROP_FRAME_COUNT)

    current_frame = 0
    current_percentage = 0.0
    avant = time.time()
    print("==================Find line in image==================")
    while vid.isOpened():
        ret, frame = vid.read()

        current_frame += 1
        if int((current_frame / frame_count) * 100) == current_percentage + 1.0:
            prediction = time.time() - avant
            avant = time.time()
            current_percentage += 1.0
            to_print = str(int(current_percentage))
            print("[" + " " * (3 - len(to_print)) + to_print + "%]   Predictions : " + str(round(prediction, 2)) + "s")

        if frame is not None:
            angle, size, img_line_plus_mean = line_detection(hist, 0, False, True, frame)
            img_array.append(img_line_plus_mean)
        else:
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    fps = vid.get(cv2.CAP_PROP_FPS)
    out = cv2.VideoWriter(output_file_name + '.avi', cv2.VideoWriter_fourcc(*'XVID'), fps, size)

    current_percentage = 0.0
    avant = time.time()
    print("==================Write Image to Disk==================")
    for i in range(len(img_array)):

        if int((i / frame_count) * 100) == current_percentage + 1.0:
            prediction = time.time() - avant
            avant = time.time()
            current_percentage += 1.0
            to_print = str(int(current_percentage))
            print("[" + " " * (3 - len(to_print)) + to_print + "%]   Predictions : " + str(round(prediction, 2)) + "s")

        out.write(img_array[i])
        cv2.imshow('frame', img_array[i])
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    out.release()


if __name__ == '__main__':
    convert_input_into_video_with_line_detection('video_cable.avi', 'output')
"""
if __name__ == '__main__':
    hist = Historique(hist_size=historique_size)
    after = time.time() + 1
    ips = 0
    compteur = 0
    while True:
        # Calcule IPS
        current = time.time()
        if current >= after:
            after = time.time() + 1
            ips = compteur
            compteur = 0
        else:
            compteur += 1

        line_detection(hist, ips)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
"""
