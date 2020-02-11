import time
import sys
import glob
import numpy as np

import board as bd
import utils


def test_expected_coord1to3():
    # Test expected_coord1to3
    print("Testing expected_coord1to3()")
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

    coord1to3 = utils.calculate_coord1to3(3)
    print("Coords. calculated for a 3-size board:")
    print(coord1to3)
    print("Expected:")
    print(expected_coord1to3)
    np.testing.assert_array_equal(coord1to3, expected_coord1to3,
                                  err_msg='Results differ!')


def test_calculate_knight_moves():
    knight_moves = utils.calculate_knight_moves()
    board = bd.Board()
    for position in range(bd.N_POSITIONS):
        print("\nKnight moves from position: {}".format(position))
        moves = knight_moves[position]
        for direction in moves:
            board.clear_board()
            board.include_piece(bd.KNIGHT, bd.WHITE, position)
            trace = 1
            for position_2 in direction:
                board.include_piece(trace, bd.WHITE, position_2, tracing=True)
                trace += 1
            board.print_char()


def test_calculate_simple_moves():
    simple_moves = utils.calculate_simple_moves()
    board = bd.Board()
    for position in range(bd.N_POSITIONS):
        print("\nPrince moves from position: {}".format(position))
        moves = simple_moves[position]
        board.clear_board()
        board.include_piece(bd.PRINCE, bd.WHITE, position)
        trace = 1
        for position_2 in moves:
            board.include_piece(trace, bd.WHITE, position_2, tracing=True)
            trace += 1
        board.print_char()


def test_calculate_soldier_moves():
    soldier_moves = utils.calculate_soldier_moves()
    board = bd.Board()
    for side in [bd.WHITE, bd.BLACK]:
        for position in range(bd.N_POSITIONS):
            moves = soldier_moves[side][position]
            board.clear_board()
            board.include_piece(bd.SOLDIER, side, position)
            if moves == []:  # Soldier on Prince's throne.
                n_moves = 0
            else:
                if type(moves[0]) == int:  # Simple list out of kingdom.
                    for position_2 in moves:
                        board.include_piece(
                            bd.TRACE, side, position_2, tracing=True)
                    n_moves = len(moves)
                else:  # List of lists within the kingdom.
                    moves_set = set()
                    for moves_list in moves:
                        moves_set = moves_set.union(moves_list)
                    for position_2 in moves_set:
                        board.include_piece(
                            bd.TRACE, side, position_2, tracing=True)
                    n_moves = len(moves_set)
            print("{} Soldier: {} moves from position {}".format(
                bd.color_name[side], n_moves, position))
            board.print_char()


def test_calculate_kingdoms():
    kingdoms = utils.calculate_kingdoms(bd.N_POSITIONS)
    board = bd.Board()
    board.clear_board()
    positions = np.argwhere(kingdoms[0]).flatten()
    for position in positions:
        board.include_piece(bd.WHITE, bd.WHITE, position, tracing=True)
    positions = np.argwhere(kingdoms[1]).flatten()
    for position in positions:
        board.include_piece(bd.BLACK, bd.BLACK, position, tracing=True)
    board.print_char()


def test_algebraic_move_2_coords():
    correct_test_cases = [
        "a1a12", "b1b2", "a12a13", "b9b10", "G1f1"
    ]
    incorrect_test_cases = [
        "ab12", "ab1a2", "c1", "d1", "c1 d1"
    ]

    for case in correct_test_cases:
        coord1, coord2, is_correct = utils.algebraic_move_2_coords(case)
        assert is_correct, "Error found while testing move: {}".format(case)
        print("Test passed: correct move {} : from {} to {}".format(
            case, coord1, coord2
        ))

    for case in incorrect_test_cases:
        coord1, coord2, is_correct = utils.algebraic_move_2_coords(case)
        assert not is_correct, \
            "Error found while testing move: {}".format(case)
        print("Test passed: incorrect move {}".format(case))


if __name__ == '__main__':
    # Main program.
    print("Testing 'The Crown' code:")

    # test_expected_coord1to3()
    test_calculate_knight_moves()
    # test_calculate_simple_moves()
    # test_calculate_soldier_moves()
    # test_calculate_kingdoms()
    # test_algebraic_move_2_coords()
