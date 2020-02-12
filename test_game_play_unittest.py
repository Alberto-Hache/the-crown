import time
import glob
import unittest
import filecmp
import cProfile

import game_play as gp
import board as bd
import utils


class Test_game_play(unittest.TestCase):
    def setUp(self):
        pass

    def test_position_attacked(self):
        file_list = glob.glob(bd.GAMES_PATH + "position*.cor")

        with open("output.txt", "w") as f:
            for full_file_name in file_list:
                # Loop over all board states stored.
                file_name = full_file_name[len(bd.GAMES_PATH):]  # Remove rel. path.
                for position in range(bd.N_POSITIONS):
                    # Loop over each position on that board.
                    board = bd.Board(file_name)  # Actual board to put pieces on.
                    display_board = bd.Board("empty.cor")  # A blank board for tracing.
                    if board.board1d[position] is None:
                        # Test function from that free position.
                        print("\nKnight attacks from position {}"
                              .format(position), file=f)
                        board.include_piece(bd.KNIGHT, board.turn, position)
                        for position_2 in range(bd.N_POSITIONS):
                            if gp.position_attacked(board, position_2, board.turn):
                                display_board.include_piece(
                                    bd.TRACE, board.turn, position_2, tracing=True)
                        board.print_char(out_file=f)
                        print("Positions attacked...", file=f)
                        display_board.print_char(out_file=f)

        self.assertTrue(filecmp.cmp(
            "output.txt",
            "tests/output_position_attacked.txt"))

    def test_generate_pseudomoves(self):
        file_list = glob.glob(bd.GAMES_PATH + "position*.cor")

        with open("output.txt", "w") as f:
            for full_file_name in file_list:
                # Loop over all board states stored.
                file_name = full_file_name[len(bd.GAMES_PATH):]  # Remove rel. path.
                board = bd.Board(file_name)  # Actual board to put pieces on.
                print("Loading game position {} ...".format(file_name), file=f)
                display_board = bd.Board("empty.cor")  # A blank board for tracing.

                for turn in [bd.WHITE, bd.BLACK]:
                    # Try board for both side.                    
                    board.turn = turn
                    display_board.turn = turn
                    print("\nPseudo-moves for position: {}".format(file_name), file=f)
                    board.print_char(out_file=f)
                    # Generate pseudomoves to test.
                    moves, moves_count = gp.generate_pseudomoves(board)
                    for piece_moves in moves:
                        # Loop over each instance of [piece, [move, move...]]
                        p_i, moves_i = piece_moves
                        display_board.include_piece(
                            p_i.type, p_i.color, p_i.coord)
                        for move_position in moves_i:
                            # Loop over each move.
                            display_board.include_piece(
                                bd.TRACE, p_i.color, move_position, tracing=True)
                        print("piece = {} {} at {}: {} moves:".format(
                            bd.color_name[p_i.color], bd.piece_name[p_i.type],
                            p_i.coord, moves_count), file=f)
                        display_board.print_char(out_file=f)
                        display_board.clear_board()

        self.assertTrue(filecmp.cmp(
            "output.txt",
            "tests/output_generate_pseudomoves.txt"))

    def test_make_pseudo_move(self):
        # Definition of test cases to run:
        # - File to load.
        # - moves to try.
        # - expected return from make_pseudo_move().
        test_cases = [
            [
                "test_make_pseudo_move_01.cor",
                ["c8b7", "c8c3", "c8a8", "e3e2"],
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
        with open("output.txt", "w") as f:
            for test_case in test_cases:
                file_name, moves_list = test_case
                board = bd.Board(file_name)
                print("--------------------------------------------------------", file=f)
                print("Loading game position {} ...".format(file_name), file=f)
                board.print_char(out_file=f)
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
                    print("make_pseudo_move({})".format(move_txt), file=f)
                    print("Result: ", file=f)
                    if is_legal:
                        new_board.print_char(out_file=f)
                    else:
                        print("[BOARD NOT PRINTED]: {} is an illegal move.".
                              format(move_txt),
                              file=f)
                    print("is_legal = {}, result = {}, game_end = {}, "
                          "game_status = {}".
                          format(is_legal, result, game_end, game_status),
                          file=f)

        self.assertTrue(filecmp.cmp(
            "output.txt",
            "tests/output_make_pseudo_move.txt"))

    def test_evaluate(self):
        file_list = glob.glob(bd.GAMES_PATH + "position*.cor")

        with open("output.txt", "w") as f:
            for full_file_name in file_list:
                file_name = full_file_name[len(bd.GAMES_PATH):]  # Remove rel. path.
                board = bd.Board(file_name)  # The board to put pieces on.

                print("Evaluation of position {}:".format(file_name), file=f)
                board.print_char(out_file=f)
                eval, game_end, game_status = gp.evaluate(board)
                print("Eval = {}, Finished = {}, Status = {}".format(
                    eval, game_end,  game_status), file=f)

                board.turn = bd.WHITE if board.turn == bd.BLACK else bd.BLACK
                print("{} to move:".format(bd.color_name[board.turn]), file=f)
                eval, game_end, game_status = gp.evaluate(board)
                print("Eval = {}, Finished = {}, Status = {}".format(
                    eval, game_end,  game_status), file=f)
                print("", file=f)

        self.assertTrue(filecmp.cmp(
            "output.txt",
            "tests/output_test_evaluate.txt"))


if __name__ == '__main__':
    unittest.main()
