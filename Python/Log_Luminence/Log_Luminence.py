import numpy as np


class PixelState:

    def __init__(self):
        self.level = 0

    def level_plus_1(self):
        self.level += 1

    def level_minus_1(self):
        self.level -= 1


def log_luminence(i, j, k, l, a, b, n_matrix, matrix, divide_size_by):
    return matrix


LOG_LUMINENCE = log_luminence


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
