# Auxiliary tables for the board.

import numpy as np


def calculate_coord1to3(n_rows):
    coord1to3 = np.array([tuple for _ in range(n_rows ** 2)])
    position = 0
    for y in range(n_rows):
        x2 = y
        for x1 in range(n_rows - y - 1):
            coord1to3[position] = (x1, x2, y)
            position += 1
            coord1to3[position] = (x1, x2 + 1, y)
            position += 1
            x2 += 1
        coord1to3[position] = (n_rows - y - 1, x2, y)
        position += 1
    return coord1to3


def calculate_simple_moves():
    simple_moves = (
        # row 1 (bottom)
        [1,],  # 0
        [13, 0, 2],
        [1, 3],
        [15, 2, 4],
        [3, 5],
        [17, 4, 6],
        [5, 7],
        [19, 6, 8],
        [7, 9],
        [21, 8, 10],
        [9, 11],
        [23, 10, 12],
        [11,],
        # row 2
        [14, 1],  # 13
        [24, 13, 15],  # 14
        [14, 16, 3],  # 15
        [26, 15, 17],  # 16
        [16, 18, 5],  # 17
        [28, 17, 19],  # 18
        [18, 20, 7],  # 19
        [30, 19, 21],  # 20
        [20, 22, 9],  # 21
        [32, 21, 23],  # 22
        [22, 11],  # 23
        # row 3
        [25, 14],  # 24
        [33, 24, 26],  # 25
        [25, 27, 16],  # 26
        [35, 26, 28],  # 27
        [27, 29, 18],  # 28
        [37, 28, 30],  # 29
        [29, 31, 20],  # 30
        [39, 30, 32],  # 31
        [31, 22],  # 32
        # row 4
        [34, 25],  # 33
        [40, 33, 35],  # 34
        [34, 36, 27],  # 35
        [42, 35, 37],  # 36
        [36, 38, 29],  # 37
        [44, 37, 39],  # 38
        [38, 31],  # 39
        # row 3
        [41, 34],  # 40
        [45, 40, 42],  # 41
        [41, 43, 36],  # 42
        [47, 42, 44],  # 43
        [43, 38],  # 44
        # row 2
        [46, 41],  # 45
        [48, 45, 47],  # 46
        [46, 43],  # 47
        # row 1
        [46,]  # 48; for Soldiers' use only.
    )
    return simple_moves


def calculate_knight_moves():
    knight_moves = (
        # row 1 [bottom]
        # From 0:
        [
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            [1, 13, 14, 24, 25, 33, 34, 40, 41, 45, 46, 48]
        ],
        # From 1:
        [
            [0,],
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            [13, 14, 24, 25, 33, 34, 40, 41, 45, 46, 48]
        ],
        # From 2:
        [
            [1, 0],
            [3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            [1, 13],
            [3, 15, 16, 26, 27, 35, 36, 42, 43, 47]
        ],
        # From 3:
        [
            [2, 1, 0],
            [4, 5, 6, 7, 8, 9, 10, 11, 12],
            [15, 14, 24],
            [15, 16, 26, 27, 35, 36, 42, 43, 47]
        ],
        # From 4:
        [
            [3, 2, 1, 0],
            [5, 6, 7, 8, 9, 10, 11, 12],
            [3, 15, 14, 24],
            [5, 17, 18, 28, 29, 37, 38, 44]
        ],
        # From 5:
        [
            [4, 3, 2, 1, 0],
            [6, 7, 8, 9, 10, 11, 12],
            [17, 16, 26, 25, 33],
            [17, 18, 28, 29, 37, 38, 44]
        ],
        # From 6:
        [
            [5, 4, 3, 2, 1, 0],
            [7, 8, 9, 10, 11, 12],
            [5, 17, 16, 26, 25, 33],
            [7, 19, 20, 30, 31, 39]
        ],
        # From 7:
        [
            [6, 5, 4, 3, 2, 1, 0],
            [8, 9, 10, 11, 12],
            [19, 18, 28, 27, 35, 34, 40],
            [19, 20, 30, 31, 39]
        ],
        # From 8:
        [
            [7, 6, 5, 4, 3, 2, 1, 0],
            [9, 10, 11, 12],
            [7, 19, 18, 28, 27, 35, 34, 40],
            [9, 21, 22, 32]
        ],
        # From 9:
        [
            [8, 7, 6, 5, 4, 3, 2, 1, 0],
            [10, 11, 12],
            [21, 20, 30, 29, 37, 36, 42, 41, 45],
            [21, 22, 32]
        ],
        # From 10:
        [
            [9, 8, 7, 6, 5, 4, 3, 2, 1, 0],
            [11, 12],
            [9, 21, 20, 30, 29, 37, 36, 42, 41, 45],
            [11, 23]
        ],
        # From 11:
        [
            [10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0],
            [12,],
            [23, 22, 32, 31, 39, 38, 44, 43, 47, 46, 48]
        ],
        # From 12:
        [
            [11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0],
            [11, 23, 22, 32, 31, 39, 38, 44, 43, 47, 46, 48]
        ],
        # row 2 [bottom]
        # From 13:
        [
            [14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
            [1, 0],
            [14, 24, 25, 33, 34, 40, 41, 45, 46, 48],
            [1, 2]
        ],
        # From 14:
        [
            [15, 16, 17, 18, 19, 20, 21, 22, 23],
            [13, 1, 0],
            [24, 25, 33, 34, 40, 41, 45, 46, 48],
            [15, 3, 4]
        ],
        # From 15:
        [
            [14, 13],
            [16, 17, 18, 19, 20, 21, 22, 23],
            [3, 2],
            [16, 26, 27, 35, 36, 42, 43, 47],
            [3, 4],
            [14, 24]
        ],
        # From 16:
        [
            [15, 14, 13],
            [17, 18, 19, 20, 21, 22, 23],
            [15, 3, 2],
            [26, 27, 35, 36, 42, 43, 47],
            [17, 5, 6],
            [26, 25, 33]
        ],
        # From 17:
        [
            [16, 15, 14, 13],
            [18, 19, 20, 21, 22, 23],
            [5, 4],
            [18, 28, 29, 37, 38, 44],
            [5, 6],
            [16, 26, 25, 33]
        ],
        # From 18:
        [
            [17, 16, 15, 14, 13],
            [19, 20, 21, 22, 23],
            [17, 5, 4],
            [28, 29, 37, 38, 44],
            [19, 7, 8],
            [28, 27, 35, 34, 40]
        ],
        # From 19:
        [
            [18, 17, 16, 15, 14, 13],
            [20, 21, 22, 23],
            [7, 6],
            [20, 30, 31, 39],
            [7, 8],
            [18, 28, 27, 35, 34, 40]
        ],
        # From 20:
        [
            [19, 18, 17, 16, 15, 14, 13],
            [21, 22, 23],
            [19, 7, 6],
            [30, 31, 39],
            [21, 9, 10],
            [30, 29, 37, 36, 42, 41, 45]
        ],
        # From 21:
        [
            [20, 19, 18, 17, 16, 15, 14, 13],
            [22, 23],
            [9, 8],
            [22, 32],
            [9, 10],
            [20, 30, 29, 37, 36, 42, 41, 45]
        ],
        # From 22:
        [
            [21, 20, 19, 18, 17, 16, 15, 14, 13],
            [21, 9, 8],
            [23, 11, 12],
            [32, 31, 39, 38, 44, 43, 47, 46, 48]
        ],
        # From 23:
        [
            [22, 21, 20, 19, 18, 17, 16, 15, 14, 13],
            [11, 10],
            [11, 12],
            [22, 32, 31, 39, 38, 44, 43, 47, 46, 48]
        ],
        # From 24:
        [
            [25, 26, 27, 28, 29, 30, 31, 32],
            [14, 13, 1, 0],
            [25, 33, 34, 40, 41, 45, 46, 48],
            [14, 15, 3, 4]
        ],
        # From 25:
        [
            [26, 27, 28, 29, 30, 31, 32],
            [24, 14, 13, 1, 0],
            [33, 34, 40, 41, 45, 46, 48],
            [26, 16, 17, 5, 6]
        ],
        # From 26:
        [
            [25, 24],
            [27, 28, 29, 30, 31, 32],
            [16, 15, 3, 2],
            [27, 35, 36, 42, 43, 47],
            [16, 17, 5, 6],
            [25, 33]
        ],
        # From 27:
        [
            [26, 25, 24],
            [28, 29, 30, 31, 32],
            [26, 16, 15, 3, 2],
            [35, 36, 42, 43, 47],
            [28, 18, 19, 7, 8],
            [35, 34, 40]
        ],
        # From 28:
        [
            [27, 26, 25, 24],
            [29, 30, 31, 32],
            [18, 17, 5, 4],
            [29, 37, 38, 44],
            [18, 19, 7, 8],
            [27, 35, 34, 40]
        ],
        # From 29:
        [
            [28, 27, 26, 25, 24],
            [30, 31, 32],
            [28, 18, 17, 5, 4],
            [37, 38, 44],
            [30, 20, 21, 9, 10],
            [37, 36, 42, 41, 45]
        ],
        # From 30:
        [
            [29, 28, 27, 26, 25, 24],
            [31, 32],
            [20, 19, 7, 6],
            [31, 39],
            [20, 21, 9, 10],
            [29, 37, 36, 42, 41, 45]
        ],
        # From 31:
        [
            [30, 29, 28, 27, 26, 25, 24],
            [30, 20, 19, 7, 6],
            [32, 22, 23, 11, 12],
            [39, 38, 44, 43, 47, 46, 48]
        ],
        # From 32:
        [
            [31, 30, 29, 28, 27, 26, 25, 24],
            [22, 21, 9, 8],
            [22, 23, 11, 12],
            [31, 39, 38, 44, 43, 47, 46, 48]
        ],
        # From 33:
        [
            [34, 35, 36, 37, 38, 39],
            [25, 24, 14, 13, 1, 0],
            [34, 40, 41, 45, 46, 48],
            [25, 26, 16, 17, 5, 6]
        ],
        # From 34:
        [
            [35, 36, 37, 38, 39],
            [33, 25, 24, 14, 13, 1, 0],
            [40, 41, 45, 46, 48],
            [35, 27, 28, 18, 19, 7, 8]
        ],
        # From 35:
        [
            [34, 33],
            [36, 37, 38, 39],
            [27, 26, 16, 15, 3, 2],
            [36, 42, 43, 47],
            [27, 28, 18, 19, 7, 8],
            [34, 40]
        ],
        # From 36:
        [
            [35, 34, 33],
            [37, 38, 39],
            [35, 27, 26, 16, 15, 3, 2],
            [42, 43, 47],
            [37, 29, 30, 20, 21, 9, 10],
            [42, 41, 45]
        ],
        # From 37:
        [
            [36, 35, 34, 33],
            [38, 39],
            [29, 28, 18, 17, 5, 4],
            [38, 44],
            [29, 30, 20, 21, 9, 10],
            [36, 42, 41, 45]
        ],
        # From 38:
        [
            [37, 36, 35, 34, 33],
            [37, 29, 28, 18, 17, 5, 4],
            [39, 31, 32, 22, 23, 11, 12],
            [44, 43, 47, 46, 48]
        ],
        # From 39:
        [
            [38, 37, 36, 35, 34, 33],
            [31, 30, 20, 19, 7, 6],
            [31, 32, 22, 23, 11, 12],
            [38, 44, 43, 47, 46, 48]
        ],
        # From 40:
        [
            [41, 42, 43, 44],
            [34, 33, 25, 24, 14, 13, 1, 0],
            [41, 45, 46, 48],
            [34, 35, 27, 28, 18, 19, 7, 8]
        ],
        # From 41:
        [
            [42, 43, 44],
            [40, 34, 33, 25, 24, 14, 13, 1, 0],
            [45, 46, 48],
            [42, 36, 37, 29, 30, 20, 21, 9, 10]
        ],
        # From 42:
        [
            [41, 40],
            [43, 44],
            [36, 35, 27, 26, 16, 15, 3, 2],
            [43, 47],
            [36, 37, 29, 30, 20, 21, 9, 10],
            [41, 45]
        ],
        # From 43:
        [
            [42, 41, 40],
            [42, 36, 35, 27, 26, 16, 15, 3, 2],
            [44, 38, 39, 31, 32, 22, 23, 11, 12],
            [47, 46, 48]
        ],
        # From 44:
        [
            [43, 42, 41, 40],
            [38, 37, 29, 28, 18, 17, 5, 4],
            [38, 39, 31, 32, 22, 23, 11, 12],
            [43, 47, 46, 48]
        ],
        # From 45:
        [
            [46, 47],
            [41, 40, 34, 33, 25, 24, 14, 13, 1, 0],
            [46, 48],
            [41, 42, 36, 37, 29, 30, 20, 21, 9, 10]
        ],
        # From 46:
        [
            [45, 41, 40, 34, 33, 25, 24, 14, 13, 1, 0],
            [47, 43, 44, 38, 39, 31, 32, 22, 23, 11, 12],
            [48,]
        ],
        # From 47:
        [
            [46, 45],
            [43, 42, 36, 35, 27, 26, 16, 15, 3, 2],
            [43, 44, 38, 39, 31, 32, 22, 23, 11, 12],
            [46, 48]
        ],
        # From 48:
        [
            [46, 45, 41, 40, 34, 33, 25, 24, 14, 13, 1, 0],
            [46, 47, 43, 44, 38, 39, 31, 32, 22, 23, 11, 12]
        ]
    )
    return knight_moves

def calculate_kingdoms(n):
    kingdoms = np.zeros((2, n), dtype=bool)
    white_k = [8, 9, 10, 11, 12, 21, 22, 23, 32]
    black_k = [0, 1, 2, 3, 4, 13, 14, 15, 24]
    kingdoms[0][white_k] = True
    kingdoms[1][black_k] = True
    return kingdoms
