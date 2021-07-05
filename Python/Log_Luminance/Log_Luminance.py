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


def print_matrix_PixelState(m):
    for i in range(len(m)):
        print('[', end='')
        for j in range(len(m[0])):
            print("[{}]".format(m[i][j].get_level()), end='')
        print(']', end='\n')


# event format (x, y, polarity, timestamp)
def log_luminance(events, matrix_level_HQ, matrix_level_LQ, divide_matrix_by, sensor_size, ROI_size, treshold=1):
    events_LQ = []
    if len(events) > 0:
        # trouver comment calculer le pixel correct le truc en dessous c'est FAUX
        # ok j'ai modifié des truc et ça marcche
        x_minus = int((sensor_size[0] - ROI_size[0]) / 2)
        y_minus = int((sensor_size[1] - ROI_size[1]) / 2)
        for e in events:
            # ajouter ou soustraire le niveau au pixel HQ
            x = e[0] - x_minus - 1
            y = e[1] - y_minus - 1
            if e[2] == 0:
                matrix_level_HQ[x][y].level_minus_1()
            else:
                matrix_level_HQ[x][y].level_plus_1()

            # calculer niveau du pixel LQ
            x_matrix_HQ = x
            y_matrix_HQ = y
            eo_x = x_matrix_HQ % 2
            eo_y = y_matrix_HQ % 2
            if eo_x != 0:
                x_matrix_HQ -= eo_x
            if eo_y != 0:
                y_matrix_HQ -= eo_y

            sum_level = 0
            for i in range(divide_matrix_by):
                for j in range(divide_matrix_by):
                    sum_level += matrix_level_HQ[x_matrix_HQ + i][y_matrix_HQ + j].get_level()
            new_level_LQ = sum_level / (divide_matrix_by ** 2)

            #récupérer level LQ aux bonnes coordonnées
            x_matrix_LQ = int(x / divide_matrix_by)  # compris entre x_LQ et x_lq + (divide_matrix_by-1)
            y_matrix_LQ = int(y / divide_matrix_by)
            level_LQ = matrix_level_LQ[x_matrix_LQ][y_matrix_LQ].get_level()
            if level_LQ + treshold < new_level_LQ:
                print("emit event 1")
            elif level_LQ - treshold > new_level_LQ:
                print("emit event 0")
            matrix_level_LQ[x_matrix_LQ][y_matrix_LQ].set_level(new_level_LQ)

            #print_matrix_PixelState(matrix_level_LQ)
    # return un tableau d'event emit avec x et y compris entre 0 et la taille de matrix level LQ selon largeur ou hauteur
    # je pourrais à partir de ça créer une image à afficher


if __name__ == '__main__':
    matrix = gen_matrix_PixelState(10, 10)
    print(matrix)
    print(matrix[0][0].get_level())
    print_matrix_PixelState(matrix)

"""
def log_luminance(i, j, k, l, a, b, n_matrix, matrix, divide_size_by):

    return n_matrix


LOG_LUMINANCE = log_luminance


def high_to_low_resolution(matrix, divide_size_by, fonction):
    # donne une matrice rempli de None
    n_matrix = np.empty((int(len(matrix) / divide_size_by), int(len(matrix[0]) / divide_size_by)), dtype=np.ndarray)
    for i in range(len(n_matrix)):
        for j in range(len(n_matrix[0])):

            for k in range(divide_size_by):
                for l in range(divide_size_by):
                    a = (divide_size_by * i) + k
                    b = (divide_size_by * j) + l
                    n_matrix[i][j] = fonction(i, j, k, l, a, b, n_matrix, matrix, divide_size_by)
    return n_matrix
"""
