# Auxiliary tables for the board.

import re  # Regular expressions.

import numpy as np


# Precalculated table(s):

coord_2_algebraic = (
    "a1", "a2", "b1", "b2", "c1", "c2", "d1", "d2", "e1", "e2", "f1", "f2",
    "g1",
    "a3", "a4", "b3", "b4", "c3", "c4", "d3", "d4", "e3", "e4", "f3",
    "a5", "a6", "b5", "b6", "c5", "c6", "d5", "d6", "e5",
    "a7", "a8", "b7", "b8", "c7", "c8", "d7",
    "a9", "a10", "b9", "b10", "c9",
    "a11", "a12", "b11",
    "a13"
)

game_status_txt = (
    "Game on-going",
    "Victory (Prince crowned)",
    "Victory (no pieces left)",
    "Draw (no Princes left)",
    "Draw, (stalemate)",
    "Draw, (repetitions)"
)

# Functions:


def move_2_txt(move):
    """
    Transform a move [coord1, coord2] into a string: "f1c6", "a1++", "None".
    """
    if move is None:
        move_txt = "None"
    else:
        txt1 = coord_2_algebraic[move[0]]
        txt2 = "++" if move[1] is None else coord_2_algebraic[move[1]]
        move_txt = txt1 + txt2

    return move_txt


def display_results(move, eval, game_end, game_status, f=None):
    move_txt = move_2_txt(move)
    print("Move:       {} ({}) Finished: {}, Status: {}".format(
        move_txt, eval, game_end,
        game_status_txt[game_status]), file=f)
    print("Raw output: {}, {}, {}, {}".format(
        move, eval, game_end, game_status), file=f)
    print("", file=f)


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


def algebraic_move_2_coords(move_txt):
    """
    Transform a move expressed in algebraic notation into
    a pair of coordinates ([1, 2], [12, None]).

    Input:
        move_txt:       string - e.g. "a1a2", "a12a13", "g1++".

    Output:
        coord1, coord2: int, int - the coordinates of the move.
        is_correct:     Boolean - Detects:
                        a) wrong algebraic formats
                        b) unexisting coordinates
    """

    # First, get rid of possible capital letters.
    move_txt = str.lower(move_txt)

    # Define regular expression for moves in algebraic coords.
    # Patterns expected: "a1a2", "a12a13", etc.
    # Also "a1++" to denote checkmate for a Prince in "a1".
    r = re.compile("(([a-g]{1})([0-9]+))(([a-g]{1})([0-9]+)|(\+{2}$))")

    bits = r.match(move_txt)  # Try to match the move.

    # Check if the move received fits in.
    if bits is not None:
        # It worked: associate the right groups: "a1", "a2"
        is_correct = True
        coord1_txt = bits.group(1)
        coord2_txt = bits.group(4)
    else:
        # Wrong format.
        is_correct = False
        coord1_txt, coord2_txt = "", ""

    # Try on coord1_txt.
    try:
        coord1 = coord_2_algebraic.index(coord1_txt)
    except ValueError:
        # If not found, the coordinate is wrong.
        is_correct = False
        coord1 = None

    # Try on coord2_txt.
    if coord2_txt == "++":
        # coord2 can be "++", which correspondes to a 'None'.
        coord2 = None
    else:
        try:
            coord2 = coord_2_algebraic.index(coord2_txt)
        except ValueError:
            # If not found, the coordinate is wrong.
            is_correct = False
            coord2 = None

    return coord1, coord2, is_correct


def calculate_simple_moves():
    simple_moves = (
        # row 1 (bottom)
        [1, ],  # 0
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
        [11, ],
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
        [46, ]  # 48; for Soldiers' use only.
    )
    return simple_moves


def calculate_soldier_moves():
    # An array of shape (2, 49, <movs>) with legal moves for a Soldier
    # of each side, from each position, where <movs> is:
    # a) a list for positions out of the kingdom.
    # b) a list of lists for positions in the kingdom.
    soldier_moves = (
        # A WHITE Soldier:
        [
            # row 1 (bottom)
            [1, ],  # 0
            [13, 0, 2],  # 1
            [1, 3],  # 2
            [15, 2, 4],  # 3
            [3, 5],  # 4
            [17, 4, 6],  # 5
            [5, 7],  # 6
            [19, 6, 8],  # 7
            [[7, 6], [7, 19], [9, 21], [9, 10]],  # 8: Moves in kingdom.
            [[8, 7], [21, 20], [21, 22], [10, 11]],  # 9: Moves in kingdom.
            [[9, 8], [9, 21], [11, 23], [11, 12]],  # 10: Moves in kingdom.
            [[10, 9], [23, 22], [12]],  # 11: Moves in kingdom.
            [],  # 12: A white Soldier can't ever be here.
            # row 2
            [14, 1],  # 13
            [24, 13, 15],  # 14
            [14, 16, 3],  # 15
            [26, 15, 17],  # 16
            [16, 18, 5],  # 17
            [28, 17, 19],  # 18
            [18, 20, 7],  # 19
            [30, 19, 21],  # 20
            [[20, 19], [20, 30], [22, 32],  # 21: Moves in kingdom.
             [22, 23], [9, 8], [9, 10]],
            [[21, 20], [21, 9], [32, 31], [23, 11]],  # 22: Moves in kingdom.
            [[22, 21], [22, 32], [11, 10], [11, 12]],  # 23: Moves in kingdom.
            # row 3
            [25, 14],  # 24
            [33, 24, 26],  # 25
            [25, 27, 16],  # 26
            [35, 26, 28],  # 27
            [27, 29, 18],  # 28
            [37, 28, 30],  # 29
            [29, 31, 20],  # 30
            [39, 30, 32],  # 31
            [[31, 30], [31, 39], [22, 21], [22, 23]],  # 32: Moves in kingdom.
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
            [46, ]  # 48; for Soldiers' use only.
        ],
        # A BLACK Soldier:
        [
            # row 1 (bottom)
            [],  # 0: A black Soldier can't ever be here.
            [[0], [13, 14], [2, 3]],  # 1: Moves in kingdom.
            [[1, 0], [1, 13], [3, 15], [3, 4]],  # 2: Moves in kingdom.
            [[15, 14], [15, 16], [2, 1], [4, 5]],  # 3: Moves in kingdom.
            [[3, 2], [3, 15], [5, 17], [5, 6]],  # 4: Moves in kingdom.
            [17, 4, 6],  # 5
            [5, 7],  # 6
            [19, 6, 8],  # 7
            [7, 9],  # 8
            [21, 8, 10],  # 9
            [9, 11],  # 10
            [23, 10, 12],  # 11
            [11, ],  # 12
            # row 2
            [[14, 24], [14, 15], [1, 2], [1, 0]],  # 13: Moves in kingdom.
            [[24, 25], [13, 1], [15, 16], [15, 3]],  # 14: Moves in kingdom.
            [[14, 13], [14, 24], [16, 17], [16, 26],  # 15: Moves in kingdom.
             [3, 2], [3, 4]],
            [26, 15, 17],  # 16
            [16, 18, 5],  # 17
            [28, 17, 19],  # 18
            [18, 20, 7],  # 19
            [30, 19, 21],  # 20
            [20, 22, 9],  # 21
            [32, 21, 23],  # 22
            [22, 11],  # 23
            # row 3
            [[25, 33], [25, 26], [14, 13], [14, 15]],  # 24: Moves in kingdom.
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
            [46, ]  # 48; for Soldiers' use only.
        ]
    )
    return soldier_moves


def calculate_knight_moves():
    # An array of shape (49, n_d, n_m) with legal moves for a Knight
    # from each position, in n_d different directions.
    knight_moves = (
        # row 1 [bottom]
        # From 0:
        [
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            [1, 13, 14, 24, 25, 33, 34, 40, 41, 45, 46, 48]
        ],
        # From 1:
        [
            [0, ],
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
            [12, ],
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
            [48, ]
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


def calculate_and_save_distance_from_to(n_rows=49):
    """
    Calculate the distance matrix for each i, j coordinates
    and save it as a file.
    """
    simple_moves = calculate_simple_moves()

    # Initialize square matrix of 49x49.
    distance = [[-1 for i in range(n_rows)] for j in range(n_rows)]

    # Initialize 0 distances for n_rows coordinates.
    for i in range(n_rows):
        distance[i][i] = 0

    # Loop till no blanks.
    n_blanks = n_rows*n_rows - n_rows  # Total coords - diagonal.

    while n_blanks > 0:
        for coord_from in range(n_rows):
            for coord_to in range(n_rows):
                if distance[coord_from][coord_to] != -1:
                    # Distance from i to j is known.
                    one_step_coords = simple_moves[coord_to]
                    for new_coord in one_step_coords:
                        if distance[coord_from][new_coord] == -1:
                            # Distance from i to k is unknown:
                            distance[coord_from][new_coord] = \
                                distance[coord_from][coord_to] + 1
                            n_blanks -= 1

    with open("distance_from_to.txt", "w") as d_file:
        for i in range(n_rows):
            print(distance[i], file=d_file)


def calculate_distance_from_to():
    """
    This returns the result produced by calculate_and_save_distance_from_to()
    as a bidimensional list of dimension 49 x 49.
    E.g. distance_from_to[12][48] = 12, the distance from white Prince's starting
    position and the crown.
    """
    distance_from_to = (
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 4, 5, 6, 7, 8, 9, 10, 11, 12, 6, 7, 8, 9, 10, 11, 12, 8, 9, 10, 11, 12, 10, 11, 12, 12],
        [1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 3, 4, 5, 6, 7, 8, 9, 10, 11, 5, 6, 7, 8, 9, 10, 11, 7, 8, 9, 10, 11, 9, 10, 11, 11],
        [2, 1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 2, 3, 2, 3, 4, 5, 6, 7, 8, 9, 10, 4, 5, 4, 5, 6, 7, 8, 9, 10, 6, 7, 6, 7, 8, 9, 10, 8, 9, 8, 9, 10, 10, 11, 10, 12],
        [3, 2, 1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 3, 2, 1, 2, 3, 4, 5, 6, 7, 8, 9, 3, 4, 3, 4, 5, 6, 7, 8, 9, 5, 6, 5, 6, 7, 8, 9, 7, 8, 7, 8, 9, 9, 10, 9, 11],
        [4, 3, 2, 1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 4, 3, 2, 3, 2, 3, 4, 5, 6, 7, 8, 4, 5, 4, 5, 4, 5, 6, 7, 8, 6, 7, 6, 7, 6, 7, 8, 8, 9, 8, 9, 8, 10, 11, 10, 12],
        [5, 4, 3, 2, 1, 0, 1, 2, 3, 4, 5, 6, 7, 5, 4, 3, 2, 1, 2, 3, 4, 5, 6, 7, 5, 4, 3, 4, 3, 4, 5, 6, 7, 5, 6, 5, 6, 5, 6, 7, 7, 8, 7, 8, 7, 9, 10, 9, 11],
        [6, 5, 4, 3, 2, 1, 0, 1, 2, 3, 4, 5, 6, 6, 5, 4, 3, 2, 3, 2, 3, 4, 5, 6, 6, 5, 4, 5, 4, 5, 4, 5, 6, 6, 7, 6, 7, 6, 7, 6, 8, 9, 8, 9, 8, 10, 11, 10, 12],
        [7, 6, 5, 4, 3, 2, 1, 0, 1, 2, 3, 4, 5, 7, 6, 5, 4, 3, 2, 1, 2, 3, 4, 5, 7, 6, 5, 4, 3, 4, 3, 4, 5, 7, 6, 5, 6, 5, 6, 5, 7, 8, 7, 8, 7, 9, 10, 9, 11],
        [8, 7, 6, 5, 4, 3, 2, 1, 0, 1, 2, 3, 4, 8, 7, 6, 5, 4, 3, 2, 3, 2, 3, 4, 8, 7, 6, 5, 4, 5, 4, 5, 4, 8, 7, 6, 7, 6, 7, 6, 8, 9, 8, 9, 8, 10, 11, 10, 12],
        [9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 1, 2, 3, 9, 8, 7, 6, 5, 4, 3, 2, 1, 2, 3, 9, 8, 7, 6, 5, 4, 3, 4, 3, 9, 8, 7, 6, 5, 6, 5, 9, 8, 7, 8, 7, 9, 10, 9, 11],
        [10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 1, 2, 10, 9, 8, 7, 6, 5, 4, 3, 2, 3, 2, 10, 9, 8, 7, 6, 5, 4, 5, 4, 10, 9, 8, 7, 6, 7, 6, 10, 9, 8, 9, 8, 10, 11, 10, 12],
        [11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 1, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 11, 10, 9, 8, 7, 6, 5, 4, 3, 11, 10, 9, 8, 7, 6, 5, 11, 10, 9, 8, 7, 11, 10, 9, 11],
        [12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 12, 11, 10, 9, 8, 7, 6, 5, 4, 12, 11, 10, 9, 8, 7, 6, 12, 11, 10, 9, 8, 12, 11, 10, 12],
        [2, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 2, 3, 4, 5, 6, 7, 8, 9, 10, 4, 5, 6, 7, 8, 9, 10, 6, 7, 8, 9, 10, 8, 9, 10, 10],
        [3, 2, 3, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 2, 3, 4, 5, 6, 7, 8, 9, 3, 4, 5, 6, 7, 8, 9, 5, 6, 7, 8, 9, 7, 8, 9, 9],
        [4, 3, 2, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 2, 1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 2, 3, 2, 3, 4, 5, 6, 7, 8, 4, 5, 4, 5, 6, 7, 8, 6, 7, 6, 7, 8, 8, 9, 8, 10],
        [5, 4, 3, 2, 3, 2, 3, 4, 5, 6, 7, 8, 9, 3, 2, 1, 0, 1, 2, 3, 4, 5, 6, 7, 3, 2, 1, 2, 3, 4, 5, 6, 7, 3, 4, 3, 4, 5, 6, 7, 5, 6, 5, 6, 7, 7, 8, 7, 9],
        [6, 5, 4, 3, 2, 1, 2, 3, 4, 5, 6, 7, 8, 4, 3, 2, 1, 0, 1, 2, 3, 4, 5, 6, 4, 3, 2, 3, 2, 3, 4, 5, 6, 4, 5, 4, 5, 4, 5, 6, 6, 7, 6, 7, 6, 8, 9, 8, 10],
        [7, 6, 5, 4, 3, 2, 3, 2, 3, 4, 5, 6, 7, 5, 4, 3, 2, 1, 0, 1, 2, 3, 4, 5, 5, 4, 3, 2, 1, 2, 3, 4, 5, 5, 4, 3, 4, 3, 4, 5, 5, 6, 5, 6, 5, 7, 8, 7, 9],
        [8, 7, 6, 5, 4, 3, 2, 1, 2, 3, 4, 5, 6, 6, 5, 4, 3, 2, 1, 0, 1, 2, 3, 4, 6, 5, 4, 3, 2, 3, 2, 3, 4, 6, 5, 4, 5, 4, 5, 4, 6, 7, 6, 7, 6, 8, 9, 8, 10],
        [9, 8, 7, 6, 5, 4, 3, 2, 3, 2, 3, 4, 5, 7, 6, 5, 4, 3, 2, 1, 0, 1, 2, 3, 7, 6, 5, 4, 3, 2, 1, 2, 3, 7, 6, 5, 4, 3, 4, 3, 7, 6, 5, 6, 5, 7, 8, 7, 9],
        [10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 2, 3, 4, 8, 7, 6, 5, 4, 3, 2, 1, 0, 1, 2, 8, 7, 6, 5, 4, 3, 2, 3, 2, 8, 7, 6, 5, 4, 5, 4, 8, 7, 6, 7, 6, 8, 9, 8, 10],
        [11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 3, 2, 3, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 1, 9, 8, 7, 6, 5, 4, 3, 2, 1, 9, 8, 7, 6, 5, 4, 3, 9, 8, 7, 6, 5, 9, 8, 7, 9],
        [12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 2, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 10, 9, 8, 7, 6, 5, 4, 3, 2, 10, 9, 8, 7, 6, 5, 4, 10, 9, 8, 7, 6, 10, 9, 8, 10],
        [4, 3, 4, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 2, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0, 1, 2, 3, 4, 5, 6, 7, 8, 2, 3, 4, 5, 6, 7, 8, 4, 5, 6, 7, 8, 6, 7, 8, 8],
        [5, 4, 5, 4, 5, 4, 5, 6, 7, 8, 9, 10, 11, 3, 2, 3, 2, 3, 4, 5, 6, 7, 8, 9, 1, 0, 1, 2, 3, 4, 5, 6, 7, 1, 2, 3, 4, 5, 6, 7, 3, 4, 5, 6, 7, 5, 6, 7, 7],
        [6, 5, 4, 3, 4, 3, 4, 5, 6, 7, 8, 9, 10, 4, 3, 2, 1, 2, 3, 4, 5, 6, 7, 8, 2, 1, 0, 1, 2, 3, 4, 5, 6, 2, 3, 2, 3, 4, 5, 6, 4, 5, 4, 5, 6, 6, 7, 6, 8],
        [7, 6, 5, 4, 5, 4, 5, 4, 5, 6, 7, 8, 9, 5, 4, 3, 2, 3, 2, 3, 4, 5, 6, 7, 3, 2, 1, 0, 1, 2, 3, 4, 5, 3, 2, 1, 2, 3, 4, 5, 3, 4, 3, 4, 5, 5, 6, 5, 7],
        [8, 7, 6, 5, 4, 3, 4, 3, 4, 5, 6, 7, 8, 6, 5, 4, 3, 2, 1, 2, 3, 4, 5, 6, 4, 3, 2, 1, 0, 1, 2, 3, 4, 4, 3, 2, 3, 2, 3, 4, 4, 5, 4, 5, 4, 6, 7, 6, 8],
        [9, 8, 7, 6, 5, 4, 5, 4, 5, 4, 5, 6, 7, 7, 6, 5, 4, 3, 2, 3, 2, 3, 4, 5, 5, 4, 3, 2, 1, 0, 1, 2, 3, 5, 4, 3, 2, 1, 2, 3, 5, 4, 3, 4, 3, 5, 6, 5, 7],
        [10, 9, 8, 7, 6, 5, 4, 3, 4, 3, 4, 5, 6, 8, 7, 6, 5, 4, 3, 2, 1, 2, 3, 4, 6, 5, 4, 3, 2, 1, 0, 1, 2, 6, 5, 4, 3, 2, 3, 2, 6, 5, 4, 5, 4, 6, 7, 6, 8],
        [11, 10, 9, 8, 7, 6, 5, 4, 5, 4, 5, 4, 5, 9, 8, 7, 6, 5, 4, 3, 2, 3, 2, 3, 7, 6, 5, 4, 3, 2, 1, 0, 1, 7, 6, 5, 4, 3, 2, 1, 7, 6, 5, 4, 3, 7, 6, 5, 7],
        [12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 4, 3, 4, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 2, 8, 7, 6, 5, 4, 3, 2, 1, 0, 8, 7, 6, 5, 4, 3, 2, 8, 7, 6, 5, 4, 8, 7, 6, 8],
        [6, 5, 6, 5, 6, 5, 6, 7, 8, 9, 10, 11, 12, 4, 3, 4, 3, 4, 5, 6, 7, 8, 9, 10, 2, 1, 2, 3, 4, 5, 6, 7, 8, 0, 1, 2, 3, 4, 5, 6, 2, 3, 4, 5, 6, 4, 5, 6, 6],
        [7, 6, 7, 6, 7, 6, 7, 6, 7, 8, 9, 10, 11, 5, 4, 5, 4, 5, 4, 5, 6, 7, 8, 9, 3, 2, 3, 2, 3, 4, 5, 6, 7, 1, 0, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 3, 4, 5, 5],
        [8, 7, 6, 5, 6, 5, 6, 5, 6, 7, 8, 9, 10, 6, 5, 4, 3, 4, 3, 4, 5, 6, 7, 8, 4, 3, 2, 1, 2, 3, 4, 5, 6, 2, 1, 0, 1, 2, 3, 4, 2, 3, 2, 3, 4, 4, 5, 4, 6],
        [9, 8, 7, 6, 7, 6, 7, 6, 7, 6, 7, 8, 9, 7, 6, 5, 4, 5, 4, 5, 4, 5, 6, 7, 5, 4, 3, 2, 3, 2, 3, 4, 5, 3, 2, 1, 0, 1, 2, 3, 3, 2, 1, 2, 3, 3, 4, 3, 5],
        [10, 9, 8, 7, 6, 5, 6, 5, 6, 5, 6, 7, 8, 8, 7, 6, 5, 4, 3, 4, 3, 4, 5, 6, 6, 5, 4, 3, 2, 1, 2, 3, 4, 4, 3, 2, 1, 0, 1, 2, 4, 3, 2, 3, 2, 4, 5, 4, 6],
        [11, 10, 9, 8, 7, 6, 7, 6, 7, 6, 7, 6, 7, 9, 8, 7, 6, 5, 4, 5, 4, 5, 4, 5, 7, 6, 5, 4, 3, 2, 3, 2, 3, 5, 4, 3, 2, 1, 0, 1, 5, 4, 3, 2, 1, 5, 4, 3, 5],
        [12, 11, 10, 9, 8, 7, 6, 5, 6, 5, 6, 5, 6, 10, 9, 8, 7, 6, 5, 4, 3, 4, 3, 4, 8, 7, 6, 5, 4, 3, 2, 1, 2, 6, 5, 4, 3, 2, 1, 0, 6, 5, 4, 3, 2, 6, 5, 4, 6],
        [8, 7, 8, 7, 8, 7, 8, 7, 8, 9, 10, 11, 12, 6, 5, 6, 5, 6, 5, 6, 7, 8, 9, 10, 4, 3, 4, 3, 4, 5, 6, 7, 8, 2, 1, 2, 3, 4, 5, 6, 0, 1, 2, 3, 4, 2, 3, 4, 4],
        [9, 8, 9, 8, 9, 8, 9, 8, 9, 8, 9, 10, 11, 7, 6, 7, 6, 7, 6, 7, 6, 7, 8, 9, 5, 4, 5, 4, 5, 4, 5, 6, 7, 3, 2, 3, 2, 3, 4, 5, 1, 0, 1, 2, 3, 1, 2, 3, 3],
        [10, 9, 8, 7, 8, 7, 8, 7, 8, 7, 8, 9, 10, 8, 7, 6, 5, 6, 5, 6, 5, 6, 7, 8, 6, 5, 4, 3, 4, 3, 4, 5, 6, 4, 3, 2, 1, 2, 3, 4, 2, 1, 0, 1, 2, 2, 3, 2, 4],
        [11, 10, 9, 8, 9, 8, 9, 8, 9, 8, 9, 8, 9, 9, 8, 7, 6, 7, 6, 7, 6, 7, 6, 7, 7, 6, 5, 4, 5, 4, 5, 4, 5, 5, 4, 3, 2, 3, 2, 3, 3, 2, 1, 0, 1, 3, 2, 1, 3],
        [12, 11, 10, 9, 8, 7, 8, 7, 8, 7, 8, 7, 8, 10, 9, 8, 7, 6, 5, 6, 5, 6, 5, 6, 8, 7, 6, 5, 4, 3, 4, 3, 4, 6, 5, 4, 3, 2, 1, 2, 4, 3, 2, 1, 0, 4, 3, 2, 4],
        [10, 9, 10, 9, 10, 9, 10, 9, 10, 9, 10, 11, 12, 8, 7, 8, 7, 8, 7, 8, 7, 8, 9, 10, 6, 5, 6, 5, 6, 5, 6, 7, 8, 4, 3, 4, 3, 4, 5, 6, 2, 1, 2, 3, 4, 0, 1, 2, 2],
        [11, 10, 11, 10, 11, 10, 11, 10, 11, 10, 11, 10, 11, 9, 8, 9, 8, 9, 8, 9, 8, 9, 8, 9, 7, 6, 7, 6, 7, 6, 7, 6, 7, 5, 4, 5, 4, 5, 4, 5, 3, 2, 3, 2, 3, 1, 0, 1, 1],
        [12, 11, 10, 9, 10, 9, 10, 9, 10, 9, 10, 9, 10, 10, 9, 8, 7, 8, 7, 8, 7, 8, 7, 8, 8, 7, 6, 5, 6, 5, 6, 5, 6, 6, 5, 4, 3, 4, 3, 4, 4, 3, 2, 1, 2, 2, 1, 0, 2],
        [12, 11, 12, 11, 12, 11, 12, 11, 12, 11, 12, 11, 12, 10, 9, 10, 9, 10, 9, 10, 9, 10, 9, 10, 8, 7, 8, 7, 8, 7, 8, 7, 8, 6, 5, 6, 5, 6, 5, 6, 4, 3, 4, 3, 4, 2, 1, 2, 0]
    )
    return distance_from_to
