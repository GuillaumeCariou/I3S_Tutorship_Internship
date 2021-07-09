import numpy as np


# pourrais être remplacé par un semble int, je pensé rajouté d'autre chose mais ce n'est pas arrivé
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
#resize un flux événementielle
def log_luminance(events, matrix_level_HQ, matrix_level_LQ, divide_matrix_by, sensor_size, ROI_size, treshold=1, interpolation=0):
    events_LQ = []
    if len(events) > 0:
        # les données brutes qui sorte de la caméra événementielle on quand même des coordonnées compris entre 0 et 640, 0 et 480
        # comme j'ai crop au milieu de l'image les coordonnée ne comment donc pas a 0 mais au niveau du crop
        # je dois donc convertir ces coordonnée en coordonnée pour la matrice de taille de crop qui est compris entre 0 et taille de crop
        x_minus = int((sensor_size[0] - ROI_size[0]) / 2)
        y_minus = int((sensor_size[1] - ROI_size[1]) / 2)
        for e in events:
            # donnée les bonne coordonné
            x_matrix_HQ = e[0] - x_minus - 1
            y_matrix_HQ = e[1] - y_minus - 1
            # ajouter ou soustraire le niveau au pixel HQ
            if e[2] == 0:
                matrix_level_HQ[x_matrix_HQ][y_matrix_HQ].level_minus_1()
            else:
                matrix_level_HQ[x_matrix_HQ][y_matrix_HQ].level_plus_1()

            # eo permet de caculer event d'origine, c'est à dire le premier pixel en haut à gauche à partir du quel je commence à compter les niveau
            eo_x = x_matrix_HQ % (divide_matrix_by + interpolation)
            eo_y = y_matrix_HQ % (divide_matrix_by + interpolation)
            origin_x = x_matrix_HQ
            origin_y = y_matrix_HQ
            if eo_x != 0:
                origin_x -= eo_x
            if eo_y != 0:
                origin_y -= eo_y

            # calculer niveau du pixel LQ
            # ici si on à un paramétre d'interpolation de 1 par exemple on compte 1 pixel de plus dans toutes les directions
            # il existe une erreur dans ce code, on compte l'interpolation avant d'ajouter tous les événement dans la zone, on peut donc avoir des niveau faux
            sum_level = 0
            for i in range((divide_matrix_by + interpolation)):
                for j in range((divide_matrix_by + interpolation)):
                    if (origin_x + i) >= len(matrix_level_HQ) or (origin_y + j) >= len(matrix_level_HQ):
                        continue
                    else:
                        sum_level += matrix_level_HQ[origin_x + i][origin_y + j].get_level()
            new_level_LQ = sum_level / ((divide_matrix_by + interpolation) ** 2)  # dois-je rajouter l'interpolation ici ?

            # récupérer level LQ aux bonnes coordonnées
            x_matrix_LQ = int(x_matrix_HQ / divide_matrix_by)  # compris entre x_LQ et x_lq + (divide_matrix_by-1)
            y_matrix_LQ = int(y_matrix_HQ / divide_matrix_by)
            current_level_LQ = matrix_level_LQ[x_matrix_LQ][y_matrix_LQ].get_level()

            # en fonction du nombre de niveau que l'on à passé on emet plus ou moins d'event
            # le treshold de base est à 1 mais peut être modifié, le baissé rend le capteur plus sensemble
            current_level_LQ = current_level_LQ - (current_level_LQ % treshold)
            new_level_LQ = new_level_LQ - (new_level_LQ % treshold)
            difference = abs(new_level_LQ - current_level_LQ)
            nombre_event_a_emetre = int(difference / treshold)

            # le treshold est pris en compte
            if current_level_LQ + treshold < new_level_LQ:
                for i in range(nombre_event_a_emetre):
                    events_LQ.append([x_matrix_LQ, y_matrix_LQ, 1, e[3]])
                matrix_level_LQ[x_matrix_LQ][y_matrix_LQ].set_level(new_level_LQ)
            elif current_level_LQ - treshold > new_level_LQ:
                matrix_level_LQ[x_matrix_LQ][y_matrix_LQ].set_level(new_level_LQ)
                for i in range(nombre_event_a_emetre):
                    events_LQ.append([x_matrix_LQ, y_matrix_LQ, 0, e[3]])
            """
            # le treshold n'est pas pris en compte pour ce code
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


"""
Version sans interpolation au cas ou

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
            for i in range((divide_matrix_by + interpolation)):
                for j in range((divide_matrix_by + interpolation)):
                    sum_level += matrix_level_HQ[origin_x + i][origin_y + j].get_level()
            new_level_LQ = sum_level / (divide_matrix_by ** 2)  # dois-je rajouter l'interpolation ici ?
"""