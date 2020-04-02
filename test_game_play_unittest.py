import time
import datetime
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

    def test_negamax(self):
        # Definition of test cases to run:
        # - File to load.
        # - move to try...
        # - expected return from mini_max():
        #   best_move, result, game_end, game_status

        TEST_SEARCH_PARAMS_4 = gp.PLY4_SEARCH_PARAMS
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
                [[32, 46], [32, 48]], 9998.0, False, 0
            ),
            (
                "test_minimax_09.cor",
                TEST_SEARCH_PARAMS_4,
                [41, 45], 1.8, False, 0
            ),
            (
                "test_minimax_10.cor",
                TEST_SEARCH_PARAMS_4,
                [33, 25], -9991, False, 0
            ),
            (
                "test_minimax_10b.cor",
                TEST_SEARCH_PARAMS_4,
                [28, 26], 9994, False, 0
            )
        )

        with open("output.txt", "w") as f:
            print("")  # To clean up the screen traces.
            for test in test_cases:
                file_name, params, \
                    exp_move, exp_result, exp_end, exp_status = test
                board = bd.Board(file_name)  # The board to put pieces on.
                game_trace = gp.Gametrace(board)  # The game trace.
                transp_table = gp.Transposition_table() \
                    if params["transposition_table"] else None

                print("Testing position {}: ".format(file_name), end="")
                print("Analysis of position {}: ".format(file_name), file=f)
                board.print_char(out_file=f)

                # Call to negamax.
                t_start = time.time()
                best_move, result, game_end, game_status = gp.negamax(
                    board, 0, -np.Infinity, np.Infinity,
                    params=params, t_table=transp_table, trace=game_trace)
                t_end = time.time()
                print("{}".format(
                    datetime.timedelta(seconds=t_end - t_start))
                )

                # Display results.
                utils.display_results(
                    best_move, result, game_end, game_status, f
                )

                # And check vs. expected.
                if exp_move is not None and type(exp_move[0]) == list:
                    self.assertTrue(
                        best_move in exp_move,
                        "Position: {}".format(file_name)
                    )
                else:
                    self.assertEqual(
                        best_move, exp_move,
                        "Position: {}".format(file_name)
                    )
                self.assertEqual(
                    (result, game_end, game_status),
                    (exp_result, exp_end, exp_status),
                    "Position: {}".format(file_name)
                )

    def test_quiesce(self):
        # Definition of test cases to run:
        # - File to load.
        # - move to try...
        # - expected return from mini_max():
        #   best_move, result, game_end, game_status

        TEST_SEARCH_PARAMS_4 = gp.PLY4_SEARCH_PARAMS

        # Go through all test cases, each on one board.
        # WARNING: float values from 'result' are very sensitive to
        # depth search parameters in TEST_SEARCH_PARAMS_4.
        test_cases = (
            (
                "test_quiesce_01.cor",  # Position to play.
                TEST_SEARCH_PARAMS_4,   # Search parameters.
                None, -11.5, False, 0    # Move, result, end, status.
            ),
            (
                "test_quiesce_02.cor",
                TEST_SEARCH_PARAMS_4,
                None, 0, True, 4
            ),
            (
                "test_quiesce_03.cor",
                TEST_SEARCH_PARAMS_4,
                None, -12.8, False, 0
            ),
            (
                "test_quiesce_05.cor",
                TEST_SEARCH_PARAMS_4,
                [33, None], -112.85, False, 0
            ),
            (
                "test_quiesce_06.cor",
                TEST_SEARCH_PARAMS_4,
                [35, 34], -11.55, False, 0
            ),
            (
                "test_quiesce_07.cor",
                TEST_SEARCH_PARAMS_4,
                [33, 34], -9991.0, False, 0
            ),
            (
                "test_quiesce_08.cor",
                TEST_SEARCH_PARAMS_4,
                None, -112.1, False, 0
            ),
            #  Taken from negamax() unit tests.
            (
                "test_minimax_01.cor",  # Position to play.
                TEST_SEARCH_PARAMS_4,   # Search parameters.
                None, 9996.0, True, 1    # Move, result, end, status.
            ),
            (
                "test_minimax_02.cor",
                TEST_SEARCH_PARAMS_4,
                None, -9996.0, True, 2
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
                [[32, 46], [32, 48]], 9994.0, False, 0
            ),
            (
                "test_minimax_09.cor",
                TEST_SEARCH_PARAMS_4,
                None, 1.8, False, 0
            ),
            (
                "test_minimax_10.cor",
                TEST_SEARCH_PARAMS_4,
                None, -11.5, False, 0
            ),
            (
                "test_minimax_10b.cor",
                TEST_SEARCH_PARAMS_4,
                [28, 26], 9990.0, False, 0
            )
        )

        with open("output.txt", "w") as f:
            for test in test_cases:
                file_name, params, \
                    exp_move, exp_result, exp_end, exp_status = test
                board = bd.Board(file_name)  # The board to put pieces on.
                # game_trace = gp.Gametrace(board)  # The game trace.
                transp_table = gp.Transposition_table() \
                    if params["transposition_table"] else None

                print("\nAnalysis of position {}:".format(file_name), file=f)
                board.print_char(out_file=f)

                # Call to quiesce() with depth 'max_depth".
                best_move, result, game_end, game_status = gp.quiesce(
                    board, params["max_depth"], -np.Infinity, np.Infinity,
                    params=params, t_table=transp_table)

                # Display results.
                utils.display_results(
                    best_move, result, game_end, game_status, f
                )

                # And check vs. expected.
                if exp_move is not None and type(exp_move[0]) == list:
                    self.assertTrue(
                        best_move in exp_move,
                        "Position: {}".format(file_name)
                    )
                else:
                    self.assertEqual(
                        best_move, exp_move,
                        "Position: {}".format(file_name)
                    )
                self.assertEqual(
                    (game_end, game_status),
                    (exp_end, exp_status),
                    "Position: {}".format(file_name)
                )
                self.assertAlmostEqual(
                    (result),
                    (exp_result),
                    places=4,
                    msg="Position: {}".format(file_name)
                )

    def test_position_attacked(self):
        file_list = glob.glob(bd.GAMES_PATH + "position_01.cor")
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
                        board.include_new_piece(
                            bd.KNIGHT, board.turn, position
                        )
                        for position_2 in range(bd.N_POSITIONS):
                            if gp.position_attacked(
                               board, position_2, board.turn
                               ):
                                display_board.include_new_piece(
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
                    # Try board for both sides.
                    board.set_turn(turn)
                    display_board.set_turn(turn)
                    print("\nPseudo-moves for position: {}".
                          format(file_name), file=f)
                    board.print_char(out_file=f)
                    # Generate pseudomoves to test.
                    moves, moves_count = gp.generate_pseudomoves(board)
                    moves_count_check = 0
                    # Loop over all pieces in the board.
                    for p_i in board.pieces[turn]:
                        coord1 = p_i.coord
                        display_board.include_new_piece(
                            p_i.type, p_i.color, p_i.coord)
                        # Spot the piece's moves in moves generated.
                        for move_pair in moves:
                            if move_pair[0] == coord1:
                                moves_count_check += 1
                                display_board.include_new_piece(
                                    bd.TRACE, p_i.color, move_pair[1],
                                    tracing=True
                                )
                        # Display moves of the piece.
                        print("piece = {} {} at {}: {} moves:".format(
                            bd.color_name[p_i.color], bd.piece_name[p_i.type],
                            p_i.coord, moves_count), file=f)
                        display_board.print_char(out_file=f)
                        display_board.clear_board()

                    # Check total move counts for that side.
                    self.assertEqual(
                        moves_count,
                        moves_count_check,
                        "Error found in moves from {}.".format(
                            bd.color_name[turn]
                            )
                    )

        self.assertTrue(filecmp.cmp(
            "output.txt",
            "tests/output_generate_pseudomoves.txt"))

    def test_evaluate_pseudomoves(self):

        # Test cases.
        test_cases = (
            (
                "test_captures_00.cor",
                [
                    [1, 2],
                    [41, 44],
                    [28, 29],
                    [41, 48],
                    [41, 46],
                    [41, 45],
                    [41, 43],
                    [41, 42],
                    [41, 40],
                    [41, 36],
                    [41, 34],
                    [41, 33],
                    [41, 25],
                    [41, 24],
                    [41, 14],
                    [41, 13],
                    [28, 27],
                    [28, 18],
                    [26, 27],
                    [26, 25],
                    [26, 16],
                    [1, 14],
                    [1, 13],
                    [1, 0],
                    [41, 37]
                ]
            ),
            (
                "test_minimax_02.cor",
                []
            )
        )

        # Loop over all test cases.
        for test in test_cases:
            file_name, expected_moves = test

            # Generate and sort moves.
            board = bd.Board(file_name)
            moves, moves_count = gp.generate_pseudomoves(board)
            moves = gp.pre_evaluate_pseudomoves(board, moves)

            # Check results.
            self.assertTrue(
                np.array_equal(moves, np.array(expected_moves)),
                "Error found in position {}".format(file_name)
            )

    def test_knights_mobility(self):
        # file_list = glob.glob(bd.GAMES_PATH + "position1.cor")
        file_list = [
            "strategy_01.cor",
            "strategy_02.cor",
            "game_record_23F2020.cor",
            "game_record_23F2020b.cor"
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
                print("Knights mobility [WHITE]: {}".
                      format(moves_count_white), file=f)
                print("Knights mobility [BLACK]: {}".
                      format(moves_count_black), file=f)

        self.assertTrue(filecmp.cmp(
            "output.txt", "tests/output_knights_mobility.txt"))

    def test_count_knight_pseudomoves(self):
        # file_list = glob.glob(bd.GAMES_PATH + "position_01.cor")
        file_list = ["position_01.cor", "empty.cor"]
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
                              .format(utils.coord_2_algebraic[position],
                                      moves_count),
                              file=f)

        self.assertTrue(filecmp.cmp(
            "output.txt",
            "tests/output_count_knight_pseudomoves.txt"))

    def test_make_unmake_pseudomove(self):
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
            # Test:
            # move_to_make,
            # is_legal, is_dynamic, result, game_end, game_status
            [
                "test_make_pseudomove_01.cor",
                "c8b7", True, False, None, False, 0, False
            ],
            [
                "test_make_pseudomove_01.cor",
                "c8c3", True, True, None, False, 0, None
            ],
            [
                "test_make_pseudomove_01.cor",
                "c8a8", True, True, None, False, 0, True
            ],
            [
                "test_make_pseudomove_01.cor",
                "e3e2", False, None, None, None, None, None
            ],
            # BOARD to test: test_make_pseudomove_02.cor
            [
                "test_make_pseudomove_02.cor",
                "b2e1", False, None, None, None, None, None
            ],
            [
                "test_make_pseudomove_02.cor",
                "a5a4", False, None, None, None, None, None
            ],
            [
                "test_make_pseudomove_02.cor",
                "a5a6", False, None, None, None, None, None
            ],
            [
                "test_make_pseudomove_02.cor",
                "b5b4", False, None, None, None, None, None
            ],
            [
                "test_make_pseudomove_02.cor",
                "b5a6", True, False, None, False, 0, False
            ],
            # BOARD to test: test_make_pseudomove_03.cor
            [
                "test_make_pseudomove_03.cor",
                "a7b5", True, True, 9999.0, True, 2, None
            ],
            [
                "test_make_pseudomove_03.cor",
                "c5b6", False, None, None, None, None, None
            ],
            [
                "test_make_pseudomove_03.cor",
                "f1g1", False, None, None, None, None, None
            ],
            [
                "test_make_pseudomove_03.cor",
                "c5c4", True, False, None, False, 0, None
            ],
            [
                "test_make_pseudomove_03.cor",
                "f1f2", True, False, None, False, 0, None
            ],
            # BOARD to test: test_make_pseudomove_04.cor
            [
                "test_make_pseudomove_04.cor",
                "b1a1", True, True, None, False, 0, None
            ],
            # BOARD to test: test_make_pseudomove_05.cor
            [
                "test_make_pseudomove_05.cor",
                "a3a1", True, True, None, False, 0, None
            ],
            # BOARD to test: test_make_pseudomove_06.cor
            [
                "test_make_pseudomove_06.cor",
                "a3a1", False, None, None, None, None, None
            ],
            # BOARD to test: test_make_pseudomove_07.cor
            [
                "test_make_pseudomove_07.cor",
                "a3a1", False, None, None, None, None, None
            ],
            [
                "test_make_pseudomove_07.cor",
                "a12a13", True, True, 9999.0, True, 1, None
            ],
            # BOARD to test: test_make_pseudomove_11.cor
            [
                "test_make_pseudomove_11.cor",
                "a12a13", False, None, None, None, None, None
            ],
            [
                "test_make_pseudomove_11.cor",
                "a3a1", False, None, None, None, None, None
            ],
            [
                "test_make_pseudomove_11.cor",
                "a12b11", True, False, None, False, 0, False
            ],
            [
                "test_make_pseudomove_11.cor",
                "b9a10", True, False, None, False, 0, False
            ],
            # BOARD to test: test_make_pseudomove_12.cor
            [
                "test_make_pseudomove_12.cor",
                "b2e1", False, None, None, None, None, None
            ],
            [
                "test_make_pseudomove_12.cor",
                "a5a4", False, None, None, None, None, None
            ],
            [
                "test_make_pseudomove_12.cor",
                "a5a6", False, None, None, None, None, None
            ],
            [
                "test_make_pseudomove_12.cor",
                "a5++", True, True, None, False, 0, None
            ]
        ]

        # Go through all test cases, each on one board.
        for test_case in test_cases:
            file_name, test_move, res1, res2, res3, res4, res5, res6 = \
                test_case
            board = bd.Board(file_name)
            board_orig = bd.Board(file_name)  # Reference for unmake tests.
            # Parse move.
            coord1, coord2, is_correct = \
                utils.algebraic_move_2_coords(test_move)
            assert is_correct, "Error parsing move {}".format(test_move)

            # Make the move and check results.
            is_legal, is_dynamic, result, game_end, game_status, \
                captured_piece, leaving_piece, old_hash, opponent_in_check = \
                gp.make_pseudomove(
                    board, coord1, coord2,
                    depth=0, params=gp.DEFAULT_SEARCH_PARAMS,
                    check_dynamic=True
                )

            self.assertTrue(
                (res1, res2, res3, res4, res5, res6) == (
                    is_legal, is_dynamic, result, game_end, 
                    game_status, opponent_in_check),
                "ERROR in position {}, move: {}:"
                "Expected: {}, {}, {}, {}, {}, {}\n"
                "Received: {}, {}, {}, {}, {}, {}".format(
                    file_name, test_move,
                    res1, res2, res3, res4, res5, res6,
                    is_legal, is_dynamic, result, game_end, game_status,
                    opponent_in_check
                ))

            # Now 'unmake' the move and check against 'board_orig'.
            board.unmake_move(
                coord1, coord2, captured_piece, leaving_piece, old_hash)
            # Check .turn, .hash
            self.assertEqual(
                (board.turn, board.hash),
                (board_orig.turn, board_orig.hash),
                "ERROR in position {}, after 'unmaking' move: {}: "
                "Expected: {}, {}\n"
                "Received: {}, {}".format(
                    file_name, test_move,
                    board.turn, board.hash,
                    board_orig.turn, board_orig.hash
                )
            )
            # Check .piece_count
            self.assertTrue(
                (board.piece_count == board_orig.piece_count).all(),
                "ERROR in position {}, after 'unmaking' move: {}: "
                ".piece_count differs".format(
                    file_name, test_move
                )
            )
            # Check .boardcode
            self.assertTrue(
                (board.boardcode == board_orig.boardcode).all(),
                "ERROR in position {}, after 'unmaking' move: {}: "
                ".boardcode differs.".format(
                    file_name, test_move
                )
            )
            # Check .board1d, all coordinates.
            self.assertTrue(
                (board.board1d == board_orig.board1d).all(),
                "ERROR in position {}, after 'unmaking' move: {}: "
                ".board1d differs.".format(
                    file_name, test_move
                )
            )
            # Check .prince for both colors.
            if board.prince[bd.WHITE] is None:
                white_prince_data_0 = (None, None, None, None, None)
            else:
                white_prince_data_0 = (
                    board.prince[bd.WHITE].type,
                    board.prince[bd.WHITE].color,
                    board.prince[bd.WHITE].coord,
                    board.prince[bd.WHITE].code,
                    board.prince[bd.WHITE].tracing,
                )
            if board_orig.prince[bd.WHITE] is None:
                white_prince_data_1 = (None, None, None, None, None)
            else:
                white_prince_data_1 = (
                    board_orig.prince[bd.WHITE].type,
                    board_orig.prince[bd.WHITE].color,
                    board_orig.prince[bd.WHITE].coord,
                    board_orig.prince[bd.WHITE].code,
                    board_orig.prince[bd.WHITE].tracing,
                )
            if board.prince[bd.BLACK] is None:
                black_prince_data_0 = (None, None, None, None, None)
            else:
                black_prince_data_0 = (
                    board.prince[bd.BLACK].type,
                    board.prince[bd.BLACK].color,
                    board.prince[bd.BLACK].coord,
                    board.prince[bd.BLACK].code,
                    board.prince[bd.BLACK].tracing,
                )
            if board_orig.prince[bd.BLACK] is None:
                black_prince_data_1 = (None, None, None, None, None)
            else:
                black_prince_data_1 = (
                    board_orig.prince[bd.BLACK].type,
                    board_orig.prince[bd.BLACK].color,
                    board_orig.prince[bd.BLACK].coord,
                    board_orig.prince[bd.BLACK].code,
                    board_orig.prince[bd.BLACK].tracing,
                )
            self.assertEqual(
                (white_prince_data_0, black_prince_data_0),
                (white_prince_data_1, black_prince_data_1),
                "ERROR in position {}, after 'unmaking' move {}: "
                ".prince differs".format(
                    file_name, test_move
                )
            )
            # Check .pieces

    def test_evaluate(self):
        file_list = glob.glob(bd.GAMES_PATH + "position*.cor")
        file_list.sort()

        with open("output.txt", "w") as f:
            for full_file_name in file_list:
                # Remove rel. path.
                file_name = full_file_name[len(bd.GAMES_PATH):]
                board = bd.Board(file_name)  # The board to put pieces on.

                print("Evaluation of position {}:".format(file_name), file=f)
                board.print_char(out_file=f)

                # Evaluate from original moving side.
                best_move, eval, game_end, game_status = gp.evaluate_end(
                    board, depth=0)
                # Display results.
                utils.display_results(
                    best_move, eval, game_end, game_status, f
                )

                # Evaluate from the other side now.
                board.flip_turn()
                print(
                    "\n{} to move:".format(bd.color_name[board.turn]), file=f
                )

                best_move, eval, game_end, game_status = gp.evaluate_end(
                    board, depth=0)

                # Display results.
                utils.display_results(
                    best_move, eval, game_end, game_status, f)

        self.assertTrue(filecmp.cmp(
            "output.txt",
            "tests/output_test_evaluate.txt"))

    def test_correct_eval_from_to_depth(self):
        # Test cases are:
        # ( evaluation, from_depth, to_depth,
        #  expected_result )
        test_cases = (
            (
                9990, 2, 4,
                9988
            ),
            (
                100, 2, 4,
                99.9
            ),
            (
                -9990, 2, 4,
                -9988
            ),
            (
                -100, 2, 4,
                -99.9
            )
        )

        for test in test_cases:
            evaluation, from_depth, to_depth, correct_eval = test
            new_eval = gp.correct_eval_from_to_depth(
                evaluation, from_depth, to_depth
            )
            self.assertEqual(
                new_eval, correct_eval
            )


if __name__ == '__main__':
    unittest.main()
