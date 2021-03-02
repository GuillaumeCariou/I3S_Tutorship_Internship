import line
import cv2
import time
import serial

from gpiozero import LED

hist = line.Historique(hist_size=10)
compteur = 0
ips = 0
after = time.time() + 1
imprimer_taille_image = True

if __name__ == '__main__':
    with serial.Serial("/dev/ttyACM0", 9600, timeout=1) as arduino:
        time.sleep(0.1)  # wait for serial to open
        if arduino.isOpen():
            print("{} connected!".format(arduino.port))


            while True:
                ips, compteur, after = line.caclulate_ips(ips, compteur, after)
                angle, height, width = line.line_detection(hist=hist, ips=ips, display_image=False, display_mean=True) # si ips == 0 alors les ips ne sont pas affiché

                # print image size once
                if imprimer_taille_image:
                    print(str(height) + "*" + str(width))
                    imprimer_taille_image = False

                # stop the program by pressing q
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

                # Reaction to angle
                if angle > 90: # turn left
                    print("left")
                elif angle < 90: # turn right
                    print("rights")