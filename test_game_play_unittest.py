import time
import glob
import unittest
import filecmp
import cProfile
import numpy as np

import game_play as gp
import board as bd
import utils


class Test_game_play(unittest.TestCase):
    def setUp(self):
        pass

    def test_minimax(self):
        # Definition of test cases to run:
        # - File to load.
        # - move to try...
        # - expected return from mini_max():
        #   best_move, result, game_end, game_status

        TEST_SEARCH_PARAMS_4 = {
            "max_depth":    4,
            "randomness":   0
        }

        # Go through all test cases, each on one board.
        test_cases = (
            (
                "test_minimax_01.cor",  # Position to play.
                TEST_SEARCH_PARAMS_4,     # Search parameters.
                None, 10000, True, 1    # Move, result, end, status.
            ),
            (
                "test_minimax_02.cor",
                TEST_SEARCH_PARAMS_4,
                None, -10000, True, 2
            ),
            (
                "test_minimax_03.cor",
                TEST_SEARCH_PARAMS_4,
                None, 0, True, 4
            ),
            (
                "test_minimax_04.cor",
                TEST_SEARCH_PARAMS_4,
                None, 0, True, 3
            ),
            (
                "test_minimax_05.cor",
                TEST_SEARCH_PARAMS_4,
                None, -10000, True, 2
            ),
            (
                "test_minimax_06.cor",
                TEST_SEARCH_PARAMS_4,
                [46, 48], 9999.0, False, 0
            ),
            (
                "test_minimax_07.cor",
                TEST_SEARCH_PARAMS_4,
                [19, 40], 9999.0, False, 0
            ),
            (
                "test_minimax_08.cor",
                TEST_SEARCH_PARAMS_4,
                [32, 46], 9998.0, False, 0
            ),
            (
                "test_minimax_09.cor",
                TEST_SEARCH_PARAMS_4,
                [41, 45], 2.0, False, 0
            ),
            (
                "test_minimax_10.cor",
                TEST_SEARCH_PARAMS_4,
                [26, 27], -10.0, False, 0
            )
        )

        with open("output.txt", "w") as f:
            for test in test_cases:
                file_name, params, \
                    exp_move, exp_result, exp_end, exp_status = test
                board = bd.Board(file_name)  # The board to put pieces on.

                print("\nAnalysis of position {}:".format(file_name), file=f)
                board.print_char(out_file=f)

                # Call to mini_max.
                best_move, result, game_end, game_status = gp.minimax(
                    board, 0, -np.Infinity, np.Infinity,
                    params=params)

                # Display results.
                move_txt = "None" if best_move is None else \
                    "{}{}".format(
                        bd.coord_2_algebraic[best_move[0]],
                        bd.coord_2_algebraic[best_move[1]])
                print("Move:       {} ({}) Finished: {}, Status: {}".format(
                    move_txt, result, game_end,
                    gp.game_status_txt[game_status]), file=f)
                print("Raw output: {}, {}, {}, {}".format(
                    best_move, result, game_end, game_status,
                    file=f
                ))
                print("", file=f)

                # And check vs. expected.
                self.assertEqual(
                    (best_move, result, game_end, game_status),
                    (exp_move, exp_result, exp_end, exp_status),
                    "Position: {}".format(file_name)
                )

    def test_quiesce(self):
        # Definition of test cases to run:
        # - File to load.
        # - move to try...
        # - expected return from mini_max():
        #   best_move, result, game_end, game_status

        TEST_SEARCH_PARAMS_4 = {
            "max_depth":            4,
            "max_quiescence_depth": 10,
            "randomness":           0
        }

        # Go through all test cases, each on one board.
        test_cases = (
            (
                "test_minimax_01.cor",  # Position to play.
                TEST_SEARCH_PARAMS_4,   # Search parameters.
                None, 9996, True, 1    # Move, result, end, status.
            ),
            (
                "test_minimax_02.cor",
                TEST_SEARCH_PARAMS_4,
                None, -9996, True, 2
            ),
            (
                "test_minimax_03.cor",
                TEST_SEARCH_PARAMS_4,
                None, 0, True, 4
            ),
            (
                "test_minimax_04.cor",
                TEST_SEARCH_PARAMS_4,
                None, 0, True, 3
            ),
            (
                "test_minimax_05.cor",
                TEST_SEARCH_PARAMS_4,
                None, -9996, True, 2
            ),
            (
                "test_minimax_06.cor",
                TEST_SEARCH_PARAMS_4,
                [46, 48], 9995.0, False, 0
            ),
            (
                "test_minimax_07.cor",
                TEST_SEARCH_PARAMS_4,
                [19, 40], 9995.0, False, 0
            ),
            (
                "test_minimax_08.cor",
                TEST_SEARCH_PARAMS_4,
                [32, 46], 9994.0, False, 0
            ),
            (
                "test_minimax_10.cor",
                TEST_SEARCH_PARAMS_4,
                [26, 27], -10.0, False, 0
            ),
            (
                "test_minimax_09.cor",
                TEST_SEARCH_PARAMS_4,
                [41, 45], 2.0, False, 0
            )
        )

        with open("output.txt", "w") as f:
            for test in test_cases:
                file_name, params, \
                    exp_move, exp_result, exp_end, exp_status = test
                board = bd.Board(file_name)  # The board to put pieces on.

                print("\nAnalysis of position {}:".format(file_name), file=f)
                board.print_char(out_file=f)

                # Call to quiesce() with depth 'max_depth".
                best_move, result, game_end, game_status = gp.quiesce(
                    board, params["max_depth"], -np.Infinity, np.Infinity,
                    params=params)

                # Display results.
                move_txt = "None" if best_move is None else \
                    "{}{}".format(
                        bd.coord_2_algebraic[best_move[0]],
                        bd.coord_2_algebraic[best_move[1]])
                print("Move:       {} ({}) Finished: {}, Status: {}".format(
                    move_txt, result, game_end,
                    gp.game_status_txt[game_status]),
                    file=f)
                print("Raw output: {}, {}, {}, {}".format(
                    best_move, result, game_end, game_status),
                    file=f)
                print("", file=f)

                # And check vs. expected.
                self.assertEqual(
                    (best_move, result, game_end, game_status),
                    (exp_move, exp_result, exp_end, exp_status),
                    "Position: {}".format(file_name)
                )

    def test_position_attacked(self):
        file_list = glob.glob(bd.GAMES_PATH + "position1.cor")
        file_list.sort()

        with open("output.txt", "w") as f:
            for full_file_name in file_list:
                # Loop over all board states stored.
                # Remove rel. path.
                file_name = full_file_name[len(bd.GAMES_PATH):]
                for position in range(bd.N_POSITIONS):
                    # Loop over each position on that board.
                    board = bd.Board(file_name)  # Board to put pieces on.
                    display_board = bd.Board("empty.cor")  # Tracing board.
                    if board.board1d[position] is None:
                        # Test function from that free position.
                        print("\nKnight attacks from position {}"
                              .format(position), file=f)
                        board.include_piece(bd.KNIGHT, board.turn, position)
                        for position_2 in range(bd.N_POSITIONS):
                            if gp.position_attacked(
                                board, position_2, board.turn):
                                display_board.include_piece(
                                    bd.TRACE, board.turn, position_2,
                                    tracing=True)
                        board.print_char(out_file=f)
                        print("Positions attacked...", file=f)
                        display_board.print_char(out_file=f)

        self.assertTrue(filecmp.cmp(
            "output.txt",
            "tests/output_position_attacked.txt"))

    def test_generate_pseudomoves(self):
        file_list = glob.glob(bd.GAMES_PATH + "position*.cor")
        file_list.sort()

        with open("output.txt", "w") as f:
            for full_file_name in file_list:
                # Loop over all board states stored.
                # Remove rel. path.
                file_name = full_file_name[len(bd.GAMES_PATH):]
                board = bd.Board(file_name)  # Actual board to put pieces on.
                print("Loading game position {} ...".format(file_name), file=f)
                display_board = bd.Board("empty.cor")  # Tracing board.

                for turn in [bd.WHITE, bd.BLACK]:
                    # Try board for both side.
                    board.turn = turn
                    display_board.turn = turn
                    print("\nPseudo-moves for position: {}".
                          format(file_name), file=f)
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

    def test_knights_mobility(self):
        # file_list = glob.glob(bd.GAMES_PATH + "position1.cor")
        file_list = [
            "strategy_01.cor",
            "strategy_02.cor"
            ]
        file_list.sort()

        with open("output.txt", "w") as f:
            # Loop over all board states stored.
            for file_name in file_list:
                # Remove rel. path.
                # file_name = full_file_name[len(bd.GAMES_PATH):]
                board = bd.Board(file_name)  # Board to put pieces on.
                print("Testing of position {}:".format(file_name), file=f)
                board.print_char(out_file=f)

                # Test function.
                moves_count_white = gp.knights_mobility(board, bd.WHITE)
                moves_count_black = gp.knights_mobility(board, bd.BLACK)
                print("Knights mobility [WHITE]: {}".\
                      format(moves_count_white), file=f)
                print("Knights mobility [BLACK]: {}".\
                      format(moves_count_black), file=f)

        self.assertTrue(filecmp.cmp(
            "output.txt", "tests/output_knights_mobility.txt"))

    def test_count_knight_pseudomoves(self):
        # file_list = glob.glob(bd.GAMES_PATH + "position1.cor")
        file_list = ["position1.cor", "empty.cor"]
        file_list.sort()

        with open("output.txt", "w") as f:
            # Loop over all board states stored.
            for file_name in file_list:
                # Remove rel. path.
                # file_name = full_file_name[len(bd.GAMES_PATH):]
                board = bd.Board(file_name)  # Board to put pieces on.
                print("Testing of position {}:".format(file_name), file=f)
                board.print_char(out_file=f)

                # Loop over each position on that board.
                for position in range(bd.N_POSITIONS):
                    if board.board1d[position] is None:
                        # Test function from that free position.
                        moves_count = gp.count_knight_pseudomoves(
                            board, position, board.turn)
                        print("Knight mobility from position {}: {}"
                              .format(bd.coord_2_algebraic[position],
                                      moves_count),
                              file=f)

        self.assertTrue(filecmp.cmp(
            "output.txt",
            "tests/output_count_knight_pseudomoves.txt"))

    def test_make_pseudomove(self):
        # Definition of test cases to run:
        # - File to load.
        # - move to try...
        # - expected return from make_pseudomove():
        #   new_board [IGNORED], is_legal, is_dynamic,
        #   result, game_end, game_status
        """
            Types of game node status:
            ON_GOING = 0
            VICTORY_CROWNING = 1
            VICTORY_NO_PIECES_LEFT = 2
            DRAW_NO_PRINCES_LEFT = 3
            DRAW_STALEMATE = 4
            DRAW_THREE_REPETITIONS = 5
        """

        test_cases = [
            # BOARD to test: test_make_pseudomove_01
            [
                "test_make_pseudomove_01.cor",
                "c8b7", True, None, False, 0
            ],
            [
                "test_make_pseudomove_01.cor",
                "c8c3", True, None, False, 0
            ],
            [
                "test_make_pseudomove_01.cor",
                "c8a8", True, None, False, 0
            ],
            [
                "test_make_pseudomove_01.cor",
                "e3e2", False, None, None, None
            ],
            # BOARD to test: test_make_pseudomove_02.cor
            [
                "test_make_pseudomove_02.cor",
                "b2e1", False, None, None, None
            ],
            [
                "test_make_pseudomove_02.cor",
                "a5a4", False, None, None, None
            ],
            [
                "test_make_pseudomove_02.cor",
                "a5a6", False, None, None, None
            ],
            [
                "test_make_pseudomove_02.cor",
                "b5b4", False, None, None, None
            ],
            [
                "test_make_pseudomove_02.cor",
                "b5a6", True, None, False, 0
            ],
            # BOARD to test: test_make_pseudomove_03.cor
            [
                "test_make_pseudomove_03.cor",
                "a7b5", True, 1, True, 2
            ],
            [
                "test_make_pseudomove_03.cor",
                "c5b6", False, None, None, None
            ],
            [
                "test_make_pseudomove_03.cor",
                "f1g1", False, None, None, None
            ],
            [
                "test_make_pseudomove_03.cor",
                "c5c4", True, None, False, 0
            ],
            [
                "test_make_pseudomove_03.cor",
                "f1f2", True, None, False, 0
            ],
            # BOARD to test: test_make_pseudomove_04.cor
            [
                "test_make_pseudomove_04.cor",
                "b1a1", True, None, False, 0
            ],
            # BOARD to test: test_make_pseudomove_05.cor
            [
                "test_make_pseudomove_05.cor",
                "a3a1", True, None, False, 0
            ],
            # BOARD to test: test_make_pseudomove_06.cor
            [
                "test_make_pseudomove_06.cor",
                "a3a1", False, None, None, None
            ],
            # BOARD to test: test_make_pseudomove_07.cor
            [
                "test_make_pseudomove_07.cor",
                "a3a1", False, None, None, None
            ],
            [
                "test_make_pseudomove_07.cor",
                "a12a13", True, 1, True, 1
            ],
            # BOARD to test: test_make_pseudomove_11.cor
            [
                "test_make_pseudomove_11.cor",
                "a12a13", False, None, None, None
            ],
            [
                "test_make_pseudomove_11.cor",
                "a3a1", False, None, None, None
            ],
            [
                "test_make_pseudomove_11.cor",
                "a12b11", True, None, False, 0
            ],
            [
                "test_make_pseudomove_11.cor",
                "b9a10", True, None, False, 0
            ],
            # BOARD to test: test_make_pseudomove_12.cor
            [
                "test_make_pseudomove_12.cor",
                "b2e1", False, None, None, None
            ],
            [
                "test_make_pseudomove_12.cor",
                "a5a4", False, None, None, None
            ],
            [
                "test_make_pseudomove_12.cor",
                "a5a6", False, None, None, None
            ],
            [
                "test_make_pseudomove_12.cor",
                "a5++", True, None, False, 0
            ]
        ]

        # Go through all test cases, each on one board.
        for test_case in test_cases:
            file_name, test_move, res1, res2, res3, res4 = test_case
            board = bd.Board(file_name)
            # Parse move.
            coord1_str, coord2_str, is_correct = \
                utils.algebraic_move_2_coords(test_move)
            assert is_correct, "Error parsing move {}".format(test_move)
            coord1 = bd.coord_2_algebraic.index(coord1_str)
            try:
                coord2 = bd.coord_2_algebraic.index(coord2_str)
            except ValueError:
                coord2 = None

            # Make the move and check results (ignoring 'new_board')
            _, is_legal, result, game_end, game_status = \
                gp.make_pseudomove(board, coord1, coord2, depth=0)

        self.assertTrue(
            (res1, res2, res3, res4) == (
                is_legal, result, game_end, game_status),
            "Expected: {}, {}, {}, {}\n"
            "Received: {}, {}, {}, {}".format(
                res1, res2, res3, res4,
                is_legal, result, game_end, game_status
            ))

    def test_evaluate(self):
        file_list = glob.glob(bd.GAMES_PATH + "position*.cor")
        file_list.sort()

        with open("output.txt", "w") as f:
            for full_file_name in file_list:
                file_name = full_file_name[len(bd.GAMES_PATH):]  # Remove rel. path.
                board = bd.Board(file_name)  # The board to put pieces on.

                print("Evaluation of position {}:".format(file_name), file=f)
                board.print_char(out_file=f)

                # Evaluate from original moving side.
                best_move, eval, game_end, game_status = gp.evaluate_end(
                    board, depth=0, shallow=True)
                move_txt = "None" if best_move is None else \
                    "{} -> {}".format(best_move[0].coord, best_move[1])
                print("Move = {}, Eval = {}, Finished = {}, Status = {}".format(
                    move_txt, eval, game_end,  game_status), file=f)

                # Evaluate from the other side now.
                board.turn = bd.WHITE if board.turn == bd.BLACK else bd.BLACK
                print("\n{} to move:".format(bd.color_name[board.turn]), file=f)

                best_move, eval, game_end, game_status = gp.evaluate_end(
                    board, depth=0, shallow=True)
                move_txt = "None" if best_move is None else \
                    "{} -> {}".format(best_move[0].coord, best_move[1])
                print("Move = {}, Eval = {}, Finished = {}, Status = {}".format(
                    move_txt, eval, game_end,  game_status), file=f)

                print("", file=f)

        self.assertTrue(filecmp.cmp(
            "output.txt",
            "tests/output_test_evaluate.txt"))


if __name__ == '__main__':
    unittest.main()
