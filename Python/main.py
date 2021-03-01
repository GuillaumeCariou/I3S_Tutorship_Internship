import line
import cv2
import time

hist = line.Historique(hist_size=10)
compteur = 0
ips = 0
after = time.time() + 1
imprimer_taille_image = True

if __name__ == '__main__':
    while True:
        ips, compteur, after = line.caclulate_ips(ips, compteur, after)
        angle, height, width = line.line_detection(hist=hist, ips=ips, display_image=True) # si ips == 0 alors les ips ne sont pas affiché
        if imprimer_taille_image:
            print(str(height) + "*" + str(width))
            imprimer_taille_image = False

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
