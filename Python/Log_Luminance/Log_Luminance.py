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


def print_matrix(matrix, name):
    sourcefile = open(name, "w")
    for i in range(len(matrix)):
        string = ""
        for j in range(len(matrix[i])):
            string += str("{}".format(matrix[i][j]))
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


def create_image_from_pixel_state(matrix):
    minimun = min_pixelState_matrix(matrix)
    maximun = max_pixelState_matrix(matrix)
    nb = abs(minimun) + abs(maximun)
    par = nb / 255
    blank_image = np.zeros((len(matrix), len(matrix[0]), 3), np.uint8)
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            if matrix[i][j].get_level() == 0:
                level = 0
            else:
                level = matrix[i][j].get_level() // par
            if level <= 255:
                blank_image[i][j][0] = 0
                blank_image[i][j][1] = 0
                blank_image[i][j][2] = level
            elif 255 < level <= 255*2:
                blank_image[i][j][0] = 0
                blank_image[i][j][1] = level
                blank_image[i][j][2] = 255
            elif 255*2 < level <= 255*3:
                blank_image[i][j][0] = level
                blank_image[i][j][1] = 255
                blank_image[i][j][2] = 255
            else:
                blank_image[i][j][0] = 255
                blank_image[i][j][1] = 255
                blank_image[i][j][2] = 255

    return blank_image


# on part du principe que l'on récupére des batch
def create_image_from_log_luminance(events, size):
    blank_image = np.zeros((size[0], size[1], 3), np.uint8)
    for e in events:
        # print("x = {} y = {}".format(e[0], e[1]))
        if e[2] == 1:
            blank_image[e[0]][e[1]][0] = 255
            blank_image[e[0]][e[1]][1] = 255
            blank_image[e[0]][e[1]][2] = 255
        else:
            blank_image[e[0]][e[1]][0] = 0
            blank_image[e[0]][e[1]][1] = 255
            blank_image[e[0]][e[1]][2] = 0
    # print_matrix(blank_image, "log.txt")
    return blank_image


# event format (x, y, polarity, timestamp)
def log_luminance(events, matrix_level_HQ, matrix_level_LQ, divide_matrix_by, sensor_size, ROI_size, treshold=1):
    events_LQ = []
    if len(events) > 0:
        # lorsque je génére la matrice pixelstate HQ je doit rajouter un valeur corespondant au cordonnées de ce pixel pour le pixel LQ
        x_minus = int((sensor_size[0] / divide_matrix_by) - (ROI_size[0] / divide_matrix_by))
        y_minus = int((sensor_size[1] / divide_matrix_by) - (ROI_size[1] / divide_matrix_by))
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
            level_LQ = matrix_level_LQ[x_matrix_LQ][y_matrix_LQ].get_level()

            # ne marche pas pour l'instant avec le threshold
            if int(level_LQ) + treshold < int(new_level_LQ):
                events_LQ.append([x_matrix_LQ, y_matrix_LQ, 1, e[3]])
                # print("event = {}".format((x_matrix_LQ, y_matrix_LQ, 1, e[3])))
                matrix_level_LQ[x_matrix_LQ][y_matrix_LQ].set_level(new_level_LQ)
            elif int(level_LQ) - treshold > int(new_level_LQ):
                events_LQ.append([x_matrix_LQ, y_matrix_LQ, 0, e[3]])
                # print("event = {}".format((x_matrix_LQ, y_matrix_LQ, 1, e[3])))
                matrix_level_LQ[x_matrix_LQ][y_matrix_LQ].set_level(new_level_LQ)


    return events_LQ
    # return un tableau d'event emit avec x_matrix_HQ et y_matrix_HQ compris entre 0 et la taille de matrix level LQ selon largeur ou hauteur
    # je pourrais à partir de ça créer une image à afficher


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
