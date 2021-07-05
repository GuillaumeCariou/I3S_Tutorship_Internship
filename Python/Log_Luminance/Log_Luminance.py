import numpy as np


class PixelState:

    def __init__(self):
        self.level = 0

    def get_level(self):
        return self.level

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


def log_luminance(events, matrix_level_HQ, matrix_level_LQ, divide_matrix_by):
    if len(events) > 0:
        print("ahah")

    #return un tableau d'event emit avec x et y compris entre 0 et la taille de matrix level LQ selon largeur ou hauteur
    #je pourrais à partir de ça créer une image à afficher


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