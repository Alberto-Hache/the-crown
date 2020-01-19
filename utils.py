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


def calculate_prince_moves():
    prince_moves = [
        # row 1 (bottom)
        [1],  # 0
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
        [11],
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
        [46]  # 48; this move kept for Soldiers' use.
    ]
    return prince_moves


if __name__ == "__main__":
    print("Testing utils.py")

    expected_coord1to3 = np.array([tuple for _ in range(3 ** 2)])
    values = (
        # 1st row (:, :, 0)
        (0, 0, 0),
        (0, 1, 0),
        (1, 1, 0),
        (1, 2, 0),
        (2, 2, 0),
        # 2nd row (:, :, 1)
        (0, 1, 1),
        (0, 2, 1),
        (1, 2, 1),
        # 3rd row (:, :, 2)
        (0, 2, 2)
    )
    for i in range(expected_coord1to3.shape[0]):
        expected_coord1to3[i] = values[i]

    coord1to3 = calculate_coord1to3(3)
    print("Coords. calculated for a 3-size board:")
    print(coord1to3)
    print("Expected:")
    print(expected_coord1to3)
    np.testing.assert_array_equal(coord1to3, expected_coord1to3,
                                  err_msg='Results differ!')
