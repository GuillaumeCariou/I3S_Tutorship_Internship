import line
import cv2
import time
import serial

from gpiozero import LED

# Camera
vid = cv2.VideoCapture(0)

# Elegoo
power_forward = 100
power_sideway_minimal = 130
power_sideway_maximal = 200

compteur = 0
ips = 0
after = time.time() + 1

imprimer_taille_image = True

left_begin = 0
left_end = 85
right_begin = 95
right_end = 180

compteur_did_not_find_lines = 0


def power_engine_from_angle(begin, end, angle):
    diff = end - begin
    diff_angle_percentage = angle / diff
    power = power_sideway_minimal + ((power_sideway_maximal - power_sideway_minimal) * diff_angle_percentage)

    if power > 255:
        power = 255
    return power


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

        hist_size = input("Quelle taille d'historique voulez vous ?  > 0")
        angle_hist = line.Historique(hist_size=int(hist_size))

        if arduino.isOpen():
            print("{} connected!".format(arduino.port))

            # Detection de ligne
            while True:
                ret, original = vid.read()
                ips, compteur, after = line.caclulate_ips(ips, compteur, after)

                # si ips == 0 alors les ips ne sont pas affiché
                angle, size, img_line_plus_mean, did_not_find_lines = line.line_detection(hist=angle_hist, ips=ips,
                                                                                          display_image=False,
                                                                                          display_mean=video,
                                                                                          original_picture=original)

                # print image size once
                if imprimer_taille_image:
                    print(size)
                    imprimer_taille_image = False

                # stop the program by pressing q
                if cv2.waitKey(1) & 0xFF == ord('q') & video:
                    break

                if did_not_find_lines:
                    compteur_did_not_find_lines += 1

                # Reaction to angle
                # Les moteur sont inversé
                # ENA, ENB
                if did_not_find_lines and compteur_did_not_find_lines > 10:
                    commande = "Backward"
                    send_command(10, 10)  # ceci est un code
                    power = power_forward
                    compteur_did_not_find_lines = 0
                elif left_end > angle >= left_begin:
                    commande = "left"
                    power = power_engine_from_angle(left_begin, left_end, angle)
                    send_command(power, 0)  # Le robot tourna a droite peu efficace
                elif right_end >= angle > right_begin:
                    commande = "right"
                    power = power_engine_from_angle(right_begin, right_end, angle)
                    send_command(0, power)  # Le robot toune a gauche tres efficace
                elif right_begin >= angle >= left_end:
                    commande = "Forward"
                    send_command(power_forward, power_forward)
                    power = power_forward

                if suivi:
                    print("Commande = " + commande + "   Angle = " + str(angle) + "   Power_engine = " + str(power))
