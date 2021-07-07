import numpy as np


class PixelState:

    def __init__(self):
        self.level = 0

    def get_level(self):
        return self.level

    def set_level(self, level):
        self.level = level

    def level_plus_1(self):
        self.level += 1

    def level_minus_1(self):
        self.level -= 1


def gen_matrix_PixelState(width, height):
    row = []
    for i in range(width):
        columns = []
        for j in range(height):
            columns.append(PixelState())
        row.append(columns)

    return np.array(row)


# event format (x, y, polarity, timestamp)
def log_luminance(events, matrix_level_HQ, matrix_level_LQ, divide_matrix_by, sensor_size, ROI_size, treshold=1):
    events_LQ = []
    if len(events) > 0:
        # lorsque je génére la matrice pixelstate HQ je doit rajouter un valeur corespondant au cordonnées de ce pixel pour le pixel LQ
        x_minus = int((sensor_size[0] - ROI_size[0]) / 2)
        y_minus = int((sensor_size[1] - ROI_size[1]) / 2)
        for e in events:
            # ajouter ou soustraire le niveau au pixel HQ
            x_matrix_HQ = e[0] - x_minus - 1
            y_matrix_HQ = e[1] - y_minus - 1
            if e[2] == 0:
                matrix_level_HQ[x_matrix_HQ][y_matrix_HQ].level_minus_1()
            else:
                matrix_level_HQ[x_matrix_HQ][y_matrix_HQ].level_plus_1()

            # calculer niveau du pixel LQ
            eo_x = x_matrix_HQ % divide_matrix_by
            eo_y = y_matrix_HQ % divide_matrix_by
            origin_x = x_matrix_HQ
            origin_y = y_matrix_HQ
            if eo_x != 0:
                origin_x -= eo_x
            if eo_y != 0:
                origin_y -= eo_y

            sum_level = 0
            for i in range(divide_matrix_by):
                for j in range(divide_matrix_by):
                    sum_level += matrix_level_HQ[origin_x + i][origin_y + j].get_level()
            new_level_LQ = sum_level / (divide_matrix_by ** 2)

            # récupérer level LQ aux bonnes coordonnées
            x_matrix_LQ = int(x_matrix_HQ / divide_matrix_by)  # compris entre x_LQ et x_lq + (divide_matrix_by-1)
            y_matrix_LQ = int(y_matrix_HQ / divide_matrix_by)
            current_level_LQ = matrix_level_LQ[x_matrix_LQ][y_matrix_LQ].get_level()

            # faire fonctionner le treshold
            current_level_LQ = current_level_LQ - (current_level_LQ % treshold)
            new_level_LQ = new_level_LQ - (new_level_LQ % treshold)
            difference = abs(new_level_LQ - current_level_LQ)
            nombre_event_a_emetre = int(difference / treshold)

            if current_level_LQ + treshold < new_level_LQ:
                for i in range(nombre_event_a_emetre):
                    events_LQ.append([x_matrix_LQ, y_matrix_LQ, 1, e[3]])
                matrix_level_LQ[x_matrix_LQ][y_matrix_LQ].set_level(new_level_LQ)
            elif current_level_LQ - treshold > new_level_LQ:
                matrix_level_LQ[x_matrix_LQ][y_matrix_LQ].set_level(new_level_LQ)
                for i in range(nombre_event_a_emetre):
                    events_LQ.append([x_matrix_LQ, y_matrix_LQ, 0, e[3]])
            """
            # ne marche pas pour l'instant avec le threshold
            if int(current_level_LQ) + treshold < int(new_level_LQ):
                events_LQ.append([x_matrix_LQ, y_matrix_LQ, 1, e[3]])
                matrix_level_LQ[x_matrix_LQ][y_matrix_LQ].set_level(new_level_LQ)
            elif int(current_level_LQ) - treshold > int(new_level_LQ):
                events_LQ.append([x_matrix_LQ, y_matrix_LQ, 0, e[3]])
                matrix_level_LQ[x_matrix_LQ][y_matrix_LQ].set_level(new_level_LQ)
            """

    return events_LQ
    # return un tableau d'event emit avec x_matrix_HQ et y_matrix_HQ compris entre 0 et la taille de matrix level LQ selon largeur ou hauteur
    # je pourrais à partir de ça créer une image à afficher
