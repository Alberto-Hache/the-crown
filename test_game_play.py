import time
import glob
import cProfile

import game_play as gp
import board as bd
import utils

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


def profiler_generate_pseudomoves():
    # Main program.
    print("Testing 'The Crown' code:")
    time_0 = time.ctime()  # Start time.
    print("{:<20}{}".format("- Started:", time_0))

    for _ in range(1000):
        test_generate_pseudomoves(draw=False)  # Avoid some I/O overhead.

    time_end = time.ctime()  # End time.
    print("{:<20}{}".format("- Ended:", time_end))


def test_make_pseudo_move(draw=True):
    # Definition of test cases to run:
    test_cases = [
        [
            "test_make_pseudo_move_01.cor",
            ["c8b7", "c8c3", "c8a8", "e3e2"]
        ],
        [
            "test_make_pseudo_move_02.cor",
            ["b2e1", "a5a4", "a5a6", "b5b4", "b5a6"]
        ],
        [
            "test_make_pseudo_move_03.cor",
            ["a7b5", "c5b6", "f1g1", "c5c4", "f1f2"]
        ],
        [
            "test_make_pseudo_move_04.cor",
            ["b1a1"]
        ],
        [
            "test_make_pseudo_move_05.cor",
            ["a3a1"]
        ],
        [
            "test_make_pseudo_move_06.cor",
            ["a3a1"]
        ],
        [
            "test_make_pseudo_move_07.cor",
            ["a3a1", "a12a13"]
        ]
    ]

    # Go through all test cases, each on one board.
    for test_case in test_cases:
        file_name, moves_list = test_case
        board = bd.Board(file_name)
        if draw:
            print("--------------------------------------------------------")
            print("Loading game position {} ...".format(file_name))
            board.print_char()
        # Go through all moves in the test case.
        for move_txt in moves_list:
            # Parse move.
            coord1_str, coord2_str, is_correct = \
                utils.algebraic_move_2_coords(move_txt)
            assert is_correct, "Error parsing move {}".format(move_txt)
            coord1 = bd.coord_2_algebraic.index(coord1_str)
            coord2 = bd.coord_2_algebraic.index(coord2_str)

            # Make the move and check results.
            new_board, is_legal, result, game_end, game_status = \
                gp.make_pseudo_move(board, coord1, coord2)
            if draw:
                print("make_pseudo_move({})".format(move_txt))
                print("Result: ")
                if is_legal:
                    new_board.print_char()
                else:
                    print("[BOARD NOT PRINTED]: {} is an illegal move.".format(
                        move_txt))
                print("is_legal = {}, result = {}, game_end = {}, "
                      "game_status = {}".format(
                          is_legal, result, game_end, game_status
                      ))


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


if __name__ == '__main__':
    # Main program.
    print("Testing 'The Crown' code:")

    # test_position_attacked()
    # test_evaluate()
    # test_generate_pseudomoves()
    # cProfile.run('profiler_generate_pseudomoves()', sort='tottime')
    test_make_pseudo_move()
