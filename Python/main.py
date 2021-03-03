import line
import cv2
import time
import serial

from gpiozero import LED

angle_hist = line.Historique(hist_size=10)

# Elegoo
speed_min = 100
speed_max = 255

# Camera
vid = cv2.VideoCapture(0)

compteur = 0
ips = 0
after = time.time() + 1

imprimer_taille_image = True

"""
if __name__ == '__main__':
    # Detection de ligne
    while True:
        ret, original = vid.read()
        ips, compteur, after = line.caclulate_ips(ips, compteur, after)
        angle, size, img_line_plus_mean = line.line_detection(hist=angle_hist, ips=ips, display_image=False,
                                                              display_mean=True,
                                                              original_picture=original)  # si ips == 0 alors les ips ne sont pas affiché

        # print image size once
        if imprimer_taille_image:
            print(size)
            imprimer_taille_image = False

        # stop the program by pressing q
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Reaction to angle
        if angle > 0:  # turn left
            print("right")
        elif angle < 0:  # turn right
            print("left")

"""


def send_command(left, right):
    cmd = str(left) + ',' + str(right) + ','
    arduino.write(cmd.encode())
    time.sleep(0.1)  # wait for arduino to answer
    arduino.flushInput()
    arduino.flushOutput()
    """
    while arduino.inWaiting() == 0: pass
    if arduino.inWaiting() > 0:
        answer = arduino.readline()
        print(answer)
        arduino.flushInput()  # remove data after reading
    """


if __name__ == '__main__':
    with serial.Serial("/dev/ttyACM0", 9600, timeout=1) as arduino:
        time.sleep(0.1)  # wait for serial to open

        video = input("Voulez vous la vidéo ? Y or N ")
        if video == "Y":
            video = True
        else:
            video = False

        suivi = input("Voulez vous le suivi de commande ? Y or N ")
        if suivi == "Y":
            suivi = True
        else:
            suivi = False

        if arduino.isOpen():
            print("{} connected!".format(arduino.port))

            # Detection de ligne
            while True:
                ret, original = vid.read()
                ips, compteur, after = line.caclulate_ips(ips, compteur, after)
                angle, size, img_line_plus_mean = line.line_detection(hist=angle_hist, ips=ips, display_image=False,
                                                                      display_mean=video,
                                                                      original_picture=original)  # si ips == 0 alors les ips ne sont pas affiché

                # print image size once
                if imprimer_taille_image:
                    print(size)
                    imprimer_taille_image = False

                # stop the program by pressing q
                if cv2.waitKey(1) & 0xFF == ord('q') & video:
                    break


                # Reaction to angle
                # ENA, ENB
                if 80 > angle >= 0:  # need to turn right
                    send_command(200, 50)
                    commande = "right"
                elif 180 > angle > 100:  # need to turn left
                    commande = "left"
                    send_command(50, 200)
                elif 100 >= angle >= 80:
                    commande = "tout droit"
                    send_command(150, 150)

                if suivi:
                    print("Commande = " + commande + "   Angle = " + str(angle))