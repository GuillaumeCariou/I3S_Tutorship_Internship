import sys
import metavision_designer_engine as mvd_engine
import numpy as np
from metavision_designer_engine import Controller, KeyboardEvent
import metavision_designer_cv as mvd_cv
import metavision_designer_core as mvd_core
import metavision_hal as mv_hal
import cv2
from Python.EventProcessor import EventProcessor


def convert_bool_to_int(matrix):
    matrix_int = np.zeros((len(matrix), len(matrix[0])))
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if matrix[i][j]:
                matrix_int[i][j] = 1
    return matrix_int


def scan_for_event(matrix_event, matrix_bool, seuil):
    for i in range(len(matrix_event)):
        for j in range(len(matrix_event[i])):
            if matrix_event[i][j] >= seuil:
                matrix_bool[i][j] = True
    return matrix_bool
