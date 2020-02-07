import time
import sys
import glob
import cProfile
import numpy as np

import board as bd
import game_play as gp
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


def test_position_attacked():
    file_list = glob.glob(bd.GAMES_PATH + "position*.cor")

    for full_file_name in file_list:
        file_name = full_file_name[len(bd.GAMES_PATH):]  # Remove rel. path.
        for position in range(bd.N_POSITIONS):
            board = bd.Board(file_name)  # Actual board to put pieces on.
            display_board = bd.Board("empty.cor")  # A blank board for tracing.
            if board.board1d[position] is None:
                print("\nKnight attacks from position {}".format(position))
                board.include_piece(bd.KNIGHT, board.turn, position)
                for position_2 in range(bd.N_POSITIONS):
                    if gp.position_attacked(board, position_2, board.turn):
                        display_board.include_piece(
                            bd.TRACE, board.turn, position_2, tracing=True)
                board.print_char()
                print("Positions attacked...")
                display_board.print_char()


def test_evaluate():
    file_list = glob.glob(bd.GAMES_PATH + "position*.cor")

    for full_file_name in file_list:
        file_name = full_file_name[len(bd.GAMES_PATH):]  # Remove rel. path.
        board = bd.Board(file_name)  # The board to put pieces on.

        print("Evaluation of position {}:".format(file_name))
        board.print_char()
        eval, game_end, game_status = gp.evaluate(board)
        print("Eval = {}, Finished = {}, Status = {}".format(
            eval, game_end,  game_status))

        board.turn = bd.WHITE if board.turn == bd.BLACK else bd.BLACK
        print("{} to move:".format(bd.color_name[board.turn]))
        eval, game_end, game_status = gp.evaluate(board)
        print("Eval = {}, Finished = {}, Status = {}".format(
            eval, game_end,  game_status))
        print("")


def test_generate_pseudomoves(draw=True):
    file_list = glob.glob(bd.GAMES_PATH + "position*.cor")

    for full_file_name in file_list:
        file_name = full_file_name[len(bd.GAMES_PATH):]  # Remove rel. path.
        board = bd.Board(file_name)  # Actual board to put pieces on.
        if draw:
            print("Loading game position {} ...".format(file_name))
        display_board = bd.Board("empty.cor")  # A blank board for tracing.

        for turn in [bd.WHITE, bd.BLACK]:
            board.turn = turn
            display_board.turn = turn
            if draw:
                print("\nPseudo-moves for position: {}".format(file_name))
                board.print_char()

            moves, moves_count = gp.generate_pseudomoves(board)
            for piece_moves in moves:
                p_i, moves_i = piece_moves
                display_board.include_piece(
                    p_i.type, p_i.color, p_i.coord)
                for move_position in moves_i:
                    display_board.include_piece(
                        bd.TRACE, p_i.color, move_position, tracing=True)
                if draw:
                    print("piece = {} {} at {}: {} moves:".format(
                        bd.color_name[p_i.color], bd.piece_name[p_i.type],
                        p_i.coord, moves_count))
                    display_board.print_char()
                display_board.clear_board()


def profiler():
    # Main program.
    print("Testing 'The Crown' code:")
    time_0 = time.ctime()  # Start time.
    print("{:<20}{}".format("- Started:", time_0))

    for _ in range(2000):
        test_generate_pseudomoves(draw=False)  # Avoid some I/O overhead.

    time_end = time.ctime()  # End time.
    print("{:<20}{}".format("- Ended:", time_end))


if __name__ == '__main__':
    # Main program.
    print("Testing 'The Crown' code:")

    # test_expected_coord1to3()
    # test_calculate_simple_moves()
    # test_calculate_knight_moves()
    # test_calculate_kingdoms()
    # test_position_attacked()
    # test_calculate_soldier_moves()
    # test_evaluate()
    # test_generate_pseudomoves()
    cProfile.run('profiler()', sort='tottime')
