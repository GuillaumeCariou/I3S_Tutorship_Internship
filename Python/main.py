import line
import cv2
import time
import serial

from gpiozero import LED

hist = line.Historique(hist_size=10)
# Camera
vid = cv2.VideoCapture(0)

compteur = 0
ips = 0
after = time.time() + 1

imprimer_taille_image = True

if __name__ == '__main__':
    with serial.Serial("/dev/ttyACM0", 9600, timeout=1) as arduino:
        time.sleep(0.1)  # wait for serial to open
        if arduino.isOpen():
            print("{} connected!".format(arduino.port))

            # ToDo Faire l'envois par serial de left or right

            # Detection de ligne
            while True:
                ret, original = vid.read()
                ips, compteur, after = line.caclulate_ips(ips, compteur, after)
                angle, size, img_line_plus_mean = line.line_detection(hist=hist, ips=ips, display_image=False,
                                                                      display_mean=True,
                                                                      original_picture=original)  # si ips == 0 alors les ips ne sont pas affiché

                # print image size once
                if imprimer_taille_image:
                    print(size)
                    imprimer_taille_image = False

                # stop the program by pressing q
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                sum = 0
                # Reaction to angle
                if angle > 90:  # turn left
                    sum += 1
                    # print("left")
                elif angle < 90:  # turn right
                    sum += 1
                    # print("rights")
