import numpy as np


def print_matrix_PixelState(m):
    for i in range(len(m)):
        print('[', end='')
        for j in range(len(m[0])):
            print("[{}]".format(m[i][j].get_level()), end='')
        print(']', end='\n')


def print_matrix_in_file(matrix, name):
    sourcefile = open(name, "w")
    for i in range(len(matrix)):
        string = ""
        for j in range(len(matrix[i])):
            string += str("{} ".format(matrix[i][j]))
        print(string, file=sourcefile)


def print_matrix_Pixel_State_in_file(matrix, name):
    sourcefile = open(name, "w")
    for i in range(len(matrix)):
        string = ""
        for j in range(len(matrix[i])):
            string += str("[{}]".format(matrix[i][j].get_level()))
        print(string, file=sourcefile)


def min_pixelState_matrix(matrix):
    minimum = matrix[0][0].get_level()
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            if matrix[i][j].get_level() < minimum:
                minimum = matrix[i][j].get_level()
    return minimum


def max_pixelState_matrix(matrix):
    maximum = matrix[0][0].get_level()
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            if matrix[i][j].get_level() > maximum:
                maximum = matrix[i][j].get_level()
    return maximum


def create_image_rgb_from_pixel_state(matrix):
    minimun = min_pixelState_matrix(matrix)
    maximun = max_pixelState_matrix(matrix)
    nb = abs(minimun) + abs(maximun)
    par = nb / 255
    blank_image = np.zeros((len(matrix), len(matrix[0]), 3), np.uint8)
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            if matrix[j][i].get_level() == 0:
                level = 0
            else:
                level = matrix[j][i].get_level() // par
            if level <= 255:
                blank_image[j][i][0] = np.uint8(0)
                blank_image[j][i][1] = np.uint8(0)
                blank_image[j][i][2] = level
            elif 255 < level <= 255*2:
                blank_image[j][i][0] = np.uint8(0)
                blank_image[j][i][1] = level
                blank_image[j][i][2] = np.uint8(255)
            elif 255*2 < level <= 255*3:
                blank_image[j][i][0] = level
                blank_image[j][i][1] = np.uint8(255)
                blank_image[j][i][2] = np.uint8(255)
            else:
                blank_image[j][i][0] = np.uint8(255)
                blank_image[j][i][1] = np.uint8(255)
                blank_image[j][i][2] = np.uint8(255)

    return np.array(blank_image, dtype=np.uint8)


# on part du principe que l'on récupére des batch
def create_image_rgb_from_log_luminance(events, width, height):
    blank_image = np.zeros((height, width, 3), np.uint8)
    #blank_image[:] = (0, 0, 0)
    for e in events:
        if e[2] == 1:
            blank_image[e[1]][e[0]] = (255, 255, 255)
        else:
            blank_image[e[1]][e[0]] = (0, 255, 0)
    # print_matrix(blank_image, "log.txt")
    return blank_image

