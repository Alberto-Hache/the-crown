import time
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


if __name__ == '__main__':
    # Main program.
    print("Testing 'The Crown' code:")
    time_0 = time.ctime()  # Start time.
    print("{:<20}{}".format("- Started:", time_0))

    # test_expected_coord1to3()
    # test_calculate_simple_moves()
    # test_calculate_knight_moves()
    test_calculate_kingdoms()

    time_end = time.ctime()  # End time.
    print("{:<20}{}".format("- Ended:", time.ctime()))
