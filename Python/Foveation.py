import sys
import metavision_designer_engine as mvd_engine
import numpy as np
from metavision_designer_engine import Controller, KeyboardEvent
import metavision_designer_cv as mvd_cv
import metavision_designer_core as mvd_core
import metavision_hal as mv_hal
import cv2
from Python.EventProcessor import EventProcessor


def for_int(i, j, k, l, a, b, n_matrix, matrix, divide_size_by):
    if n_matrix[i][j] is None:
        n_matrix[i][j] = 0
    n_matrix[i][j] += matrix[a][b]
    return n_matrix[i][j]


def for_tab(i, j, k, l, a, b, n_matrix, matrix, divide_size_by):
    if n_matrix[i][j] is None:
        n_matrix[i][j] = []
    n_matrix[i][j].append(matrix[a][b])
    return n_matrix[i][j]


# met les événement si il y en a sinon None
def for_event(i, j, k, l, a, b, n_matrix, matrix, divide_size_by):
    # event format (x, y, polarity, timestamp)
    event = matrix[a][b]
    if event is not None:
        if n_matrix[i][j] is None:
            n_matrix[i][j] = (0, 0, 0, 0)
        for n in range(len(event)):
            """"
            print("\ni={} j={} n={}".format(i, j, n))
            print("i={} j={} n={}".format(len(n_matrix), len(n_matrix[i]), len(event)))
            print(event[n])
            print("0={} 1={} 2={} 3={}".format(event[n][0], event[n][1], event[n][2], event[n][3]))
            print(n_matrix[i][j])
            """
            # convertie en pourcentage ((100 / (divide_size_by * divide_size_by)) / 100)
            polarity = n_matrix[i][j][2] + event[n][2] * ((100 / (divide_size_by * divide_size_by)) / 100)
            # print(((100 / (divide_size_by * divide_size_by)) / 100))
            ts = n_matrix[i][j][3] + event[n][3]
            n_matrix[i][j] = (i, j, polarity, ts)
            # print("i={} j={} polarity={} ts={}".format(i, j, polarity, ts))
        if k == divide_size_by - 1 and l == divide_size_by - 1 and len(event) > 0:
            polarity = n_matrix[i][j][2] / (divide_size_by ** 2)
            ts = int(n_matrix[i][j][3] / (divide_size_by ** 2))
            n_matrix[i][j] = (n_matrix[i][j][0], n_matrix[i][j][1], polarity, ts)
            # print("i={} j={} polarity={} ts={}\n".format(n_matrix[i][j][0], n_matrix[i][j][1], polarity, ts))
    return n_matrix[i][j]


FOR_INT = for_int
FOR_TAB = for_tab
FOR_EVENT = for_event


def high_to_low_resolution(matrix, divide_size_by, fonction):
    # done un matrice rempli de None
    n_matrix = np.empty((int(len(matrix) / divide_size_by), int(len(matrix[0]) / divide_size_by)), dtype=np.ndarray)
    for i in range(len(n_matrix)):
        for j in range(len(n_matrix[0])):

            for k in range(divide_size_by):
                for l in range(divide_size_by):
                    a = (divide_size_by * i) + k
                    b = (divide_size_by * j) + l
                    # print('i={}   j={}   k={}   l={}   a={}   b={}'.format(i, j, k, l, a, b))
                    n_matrix[i][j] = fonction(i, j, k, l, a, b, n_matrix, matrix, divide_size_by)
    return n_matrix


def convert_event_matrix_to_int_matrix(matrix):
    matrix_int = np.zeros((len(matrix), len(matrix[0])))
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if matrix[i][j] is None:
                matrix_int[i][j] = 0
            else:
                matrix_int[i][j] = len(matrix[i][j])
    return matrix_int


def convert_bool_matrix_to_int_matrix(matrix):
    matrix_int = np.zeros((len(matrix), len(matrix[0])))
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if matrix[i][j]:
                matrix_int[i][j] = 1
    return matrix_int


# outdated
def scan_for_event_density(matrix_event, threshold=1):
    matrix_bool = np.zeros((len(matrix_event), len(matrix_event[0])), dtype=bool)
    for i in range(len(matrix_event)):
        for j in range(len(matrix_event[i])):
            if matrix_event[i][j] >= threshold:
                matrix_bool[i][j] = True
    return matrix_bool
