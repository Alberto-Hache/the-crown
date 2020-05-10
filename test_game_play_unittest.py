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
        file_list = (
            "position_01.cor",
            "position_02.cor",
            "position_03.cor",
            "position_04.cor",
            "position_05.cor",
            "position_06.cor",
            "position_07.cor",
            "position_08.cor",
            "position_09.cor",
            "position_10.cor",
        )

        with open("output.txt", "w") as f:
            for file_name in file_list:
                # Loop over all board states stored.
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

    def test_pre_evaluate_pseudomoves(self):

        # Test cases.
        test_cases = (
            (
                # Case: No killer moves.
                "test_captures_00.cor",
                [
                    [1,  2],  # s x K
                    [41, 44],  # k x S (not defended)
                    [28, 29],  # s x S (defended)
                    [1,  0],
                    [1, 13],
                    [1, 14],
                    [26, 16],
                    [26, 25],
                    [26, 27],
                    [28, 18],
                    [28, 27],
                    [41, 13],
                    [41, 14],
                    [41, 24],
                    [41, 25],
                    [41, 33],
                    [41, 34],
                    [41, 36],
                    [41, 40],
                    [41, 42],
                    [41, 43],
                    [41, 45],
                    [41, 46],
                    [41, 48],
                    [41, 37]  # K x s (defended)
                ],
                [None, None]
            ),
            (
                # Case: 1 killer move.
                "test_captures_00.cor",
                [
                    [1,  2],  # s x K
                    [41, 44],  # k x S (not defended)
                    [28, 29],  # s x S (defended)
                    [41, 24],  # Killer move
                    [1,  0],
                    [1, 13],
                    [1, 14],
                    [26, 16],
                    [26, 25],
                    [26, 27],
                    [28, 18],
                    [28, 27],
                    [41, 13],
                    [41, 14],
                    [41, 25],
                    [41, 33],
                    [41, 34],
                    [41, 36],
                    [41, 40],
                    [41, 42],
                    [41, 43],
                    [41, 45],
                    [41, 46],
                    [41, 48],
                    [41, 37]  # K x s (defended)
                ],
                [[41, 24], [None, None]]
            ),
            (
                # Case: No moves, no killer moves.
                "test_minimax_02.cor",
                [],
                [None, None]
            ),
            (
                # Case: Endgame.
                "endgame_07.cor",
                [
                    [47, 46],
                    [33, 34],
                    [5, 17],
                    [5, 4],
                    [5, 6],
                    [25, 24],
                    [25, 26],
                    [47, 43]
                ],
                [None, None]
            ),
            (
                # Case: Endgame.
                "endgame_08.cor",
                [
                    [45, 46],
                    [36, 42],
                    [36, 35],
                    [36, 37],
                    [45, 41]
                ],
                [None, None]
            )
        )

        # Loop over all test cases.
        for test in test_cases:
            file_name, expected_moves, killer_moves = test

            # Generate and sort moves.
            board = bd.Board(file_name)
            moves, moves_count = gp.generate_pseudomoves(board)
            moves = gp.pre_evaluate_pseudomoves(
                board, moves, killer_moves
                )

            # Check results.
            self.assertTrue(
                np.array_equal(moves, np.array(expected_moves)),
                "Error found in position {} with killer moves {}".format(
                    file_name, killer_moves)
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
                "f1f2", True, True, None, False, 0, None
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
                "ERROR in position {}, move: {}:\n"
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
                "ERROR in position {}, after 'unmaking' move: {}:\n"
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
                "ERROR in position {}, after 'unmaking' move: {}:\n"
                ".piece_count differs".format(
                    file_name, test_move
                )
            )
            # Check .boardcode
            self.assertTrue(
                (board.boardcode == board_orig.boardcode).all(),
                "ERROR in position {}, after 'unmaking' move: {}:\n"
                ".boardcode differs.".format(
                    file_name, test_move
                )
            )
            # Check .board1d, all coordinates.
            self.assertTrue(
                (board.board1d == board_orig.board1d).all(),
                "ERROR in position {}, after 'unmaking' move: {}:\n"
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

    def test_evaluate_terminal(self):
        test_cases = (
            ("position_01.cor", (None, None, False, 0), (None, None, False, 0)),
            ("position_02.cor", (None, None, False, 0), (None, None, False, 0)),
            ("position_03.cor", (None, None, False, 0), (None, None, False, 0)),
            ("position_04.cor", (None, None, False, 0), (None, None, False, 0)),
            ("position_05.cor", (None, None, False, 0), (None, None, False, 0)),
            ("position_06.cor", (None, 10000.0, True, 1), (None, -10000.0, True, 1)),
            ("position_07.cor", (None, 10000.0, True, 2), (None, -10000.0, True, 2)),
            ("position_08.cor", (None, 0, True, 3), (None, 0, True, 3)),
            ("position_09.cor", (None, None, False, 0), (None, None, False, 0)),
            ("position_10.cor", (None, None, False, 0), (None, None, False, 0)),
            ("position_11.cor", (None, None, False, 0), (None, None, False, 0))
        )

        for test in test_cases:
            file_name, exp_1, exp_2 = test

            # Test 1
            board = bd.Board(file_name)
            # Evaluate from original moving side.
            exp_best_move, exp_eval, exp_game_end, exp_game_status = exp_1
            best_move, eval, game_end, game_status = gp.evaluate_terminal(
                board, depth=0)
            # Check results.
            self.assertEqual(
                (best_move, eval, game_end, game_status),
                (exp_best_move, exp_eval, exp_game_end, exp_game_status),
                "Error in position {}, {} to move: "
                "expected {}, received {}".format(
                    file_name, board.turn,
                    (best_move, eval, game_end, game_status),
                    (exp_best_move, exp_eval, exp_game_end, exp_game_status)
                )
            )

            # Test 2
            board.flip_turn()
            # Evaluate from original moving side.
            exp_best_move, exp_eval, exp_game_end, exp_game_status = exp_2
            best_move, eval, game_end, game_status = gp.evaluate_terminal(
                board, depth=0)
            # Check results.
            self.assertEqual(
                (best_move, eval, game_end, game_status),
                (exp_best_move, exp_eval, exp_game_end, exp_game_status),
                "Error in position {}, {} to move: "
                "expected {}, received {}".format(
                    file_name, board.turn,
                    (best_move, eval, game_end, game_status),
                    (exp_best_move, exp_eval, exp_game_end, exp_game_status)
                )
            )

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
                99.99
            ),
            (
                -9990, 2, 4,
                -9988
            ),
            (
                -100, 2, 4,
                -99.99
            )
        )

        for test in test_cases:
            evaluation, from_depth, to_depth, correct_eval = test
            new_eval = gp.correct_eval_from_to_depth(
                evaluation, from_depth, to_depth
            )
            self.assertEqual(
                new_eval, correct_eval,
                f"Error correcting {evaluation} "
                f"from depth {from_depth} to {to_depth}."
            )

    def test_soldiers_lag(self):
        test_cases = (
            ("test_quiesce_01.cor", 0, 6),
            ("test_quiesce_02.cor", 0, 0),
            ("test_quiesce_03.cor", 0, 4),
            ("test_quiesce_05.cor", 0, 4),
            ("test_quiesce_06.cor", 0, 0),
            ("test_quiesce_07.cor", 0, 0),
            ("test_quiesce_08.cor", 0, 0),
            ("test_minimax_01.cor", 0, 10),
            ("test_minimax_02.cor", 0, 0),
            ("test_minimax_03.cor", 0, 0),
            ("test_minimax_05.cor", 0, 0),
            ("test_minimax_06.cor", 0, 1),
            ("test_minimax_07.cor", 0, 0),
            ("test_minimax_08.cor", 0, 0),
            ("test_minimax_09.cor", 0, 0),
            ("test_minimax_10.cor", 0, 0),
            ("test_minimax_11.cor", 0, 0),
            ("test_minimax_13.cor", 0, 0),
            ("test_make_pseudomove_01.cor", 0, 2),
            ("test_make_pseudomove_04.cor", 4, 0),
            ("test_make_pseudomove_07.cor", 0, 8),
            ("test_make_pseudomove_12.cor", 0, 2),
            ("endgame_00.cor", 0, 0),
            ("endgame_01.cor", 0, 0),
            ("endgame_02.cor", 0, 0)
        )

        for test in test_cases:
            file_name, exp_w, exp_b = test
            board = bd.Board(file_name)
            board.set_turn(bd.WHITE)
            res_w = gp.soldiers_lag(board, bd.WHITE)
            board.set_turn(bd.BLACK)
            res_b = gp.soldiers_lag(board, bd.BLACK)

            self.assertEqual(
                (res_w, res_b), (exp_w, exp_b),
                "Error in position {}".format(
                    file_name
                )
            )

    def test_soldiers_advance_reward(self):
        test_cases = (
            ("test_quiesce_01.cor", 0.1, 0),
            ("test_quiesce_02.cor", 0.1, 0),
            ("test_quiesce_03.cor", 0.1, 0),
            ("test_quiesce_05.cor", 0.1, 0),
            ("test_quiesce_06.cor", 0.1, 0),
            ("test_quiesce_07.cor", 0.1, 0),
            ("test_quiesce_08.cor", 0.1, 0.1),
            ("test_minimax_01.cor", 0.1, 0),
            ("test_minimax_02.cor", 0.1, 0),
            ("test_minimax_03.cor", 0.1, 0),
            ("test_minimax_05.cor", 0, 0),
            ("test_minimax_06.cor", 0.4, 0),
            ("test_minimax_07.cor", 0, 0.4),
            ("test_minimax_08.cor", 0.3, 0),
            ("test_minimax_09.cor", 0, 0.55),
            ("test_minimax_10.cor", 0.1, 0),
            ("test_minimax_11.cor", 0, 0),
            ("test_minimax_13.cor", 0, 0),
            ("test_make_pseudomove_01.cor", 0.2, 0.30000000000000004),
            ("test_make_pseudomove_04.cor", 0.1, 0),
            ("test_make_pseudomove_07.cor", 0.1, 0),
            ("test_make_pseudomove_12.cor", 0.2, 0.1),
            ("endgame_00.cor", 0.30000000000000004, 0.7),
            ("endgame_01.cor", 0.7999999999999999, 0.44999999999999996),
            ("endgame_02.cor", 0, 0)
        )

        for test in test_cases:
            file_name, exp_w, exp_b = test
            board = bd.Board(file_name)
            board.set_turn(bd.WHITE)
            res_w = gp.soldiers_advance_reward(board, bd.WHITE)
            board.set_turn(bd.BLACK)
            res_b = gp.soldiers_advance_reward(board, bd.BLACK)

            self.assertEqual(
                (res_w, res_b), (exp_w, exp_b),
                "Error in position {}".format(
                    file_name
                )
            )

    def test_make_pseudomove(self):
        """
        Check is_dynamic flag for moves in different positions.
        """

        test_cases = (
            (
                "endgame_00.cor",
                [[45, 20]]
            ),
            (
                "endgame_01.cor",
                [[38, 44]]
            ),
            (
                "endgame_02.cor",
                [[39, 38]]
            ),
            (
                "endgame_06.cor",
                [[35, 34], [35, 36], [38, 44]]
            )
        )

        for test in test_cases:
            file_name, exp_moves = test
            board = bd.Board(file_name)
            moves, _ = gp.generate_pseudomoves(board)
            dynamic_moves = []
            non_dynamic_moves = []
            # Try all pseudomoves in the position.
            for move in moves:
                coord1, coord2 = move
                # Make the move and check results.
                is_legal, is_dynamic, result, game_end, game_status, \
                    captured_piece, leaving_piece, old_hash, \
                    opponent_in_check = \
                    gp.make_pseudomove(
                        board, coord1, coord2,
                        depth=0, params=gp.DEFAULT_SEARCH_PARAMS,
                        check_dynamic=True
                    )
                # Keep if it's dynamic.
                if is_legal and is_dynamic:
                    dynamic_moves.append(move)

                # Now 'unmake' the move and check against 'board_orig'.
                board.unmake_move(
                    coord1, coord2, captured_piece, leaving_piece, old_hash)
            # Check found dynamic moves vs expected.
            exp_moves.sort()
            dynamic_moves.sort()
            self.assertEqual(
                exp_moves, dynamic_moves,
                "Error in position {}".format(file_name)
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
        # Test case:
        # - Position to play.
        # - Search parameters.
        # - Move / list of moves, result, end, status.
        test_cases = (
            ("endgame_09.cor", None, 1.43, False, 0),
            ("test_quiesce_01.cor", None, -13.246666666666666, False, 0),
            ("test_quiesce_02.cor", None, 0, True, 4),
            ("test_quiesce_03.cor", None,  -14.146666666666665, False, 0),
            ("test_quiesce_05.cor", [33, None], -115.60333333333332, False, 0),
            ("test_quiesce_06.cor", [35, 34], -13.541666666666666, False, 0),
            ("test_quiesce_07.cor", [33, 34], -9991.0, False, 0),
            ("test_quiesce_08.cor", None, -114.09666666666668, False, 0),
            #  Taken from negamax() unit tests.
            ("test_minimax_01.cor", None, 9996.0, True, 1),
            ("test_minimax_02.cor", None, -9996.0, True, 2),
            ("test_minimax_03.cor", None, 0, True, 4),
            ("test_minimax_04.cor", None, 0, True, 3),
            ("test_minimax_05.cor", None, -9996, True, 2),
            ("test_minimax_06.cor", None, 9995.0, False, 0),
            ("test_minimax_07.cor", [19, 40], 9995.0, False, 0),
            ("test_minimax_08.cor", [[32, 46], [32, 48]], 9994.0, False, 0),
            ("test_minimax_09.cor", [41, 45], 0.908333333333333, False, 0),
            ("test_minimax_10.cor", None, -12.946666666666665, False, 0),
            ("test_minimax_10b.cor", None, 9987.0, False, 0)
        )

        params = TEST_SEARCH_PARAMS_4
        with open("output.txt", "w") as f:
            for test in test_cases:
                file_name, exp_move, exp_result, exp_end, exp_status = test
                board = bd.Board(file_name)  # The board to put pieces on.
                # The game trace, indexing first board appropriately.
                game_trace = gp.Gametrace(board)
                game_trace.current_board_ply = params["max_depth"] - 1
                # Transposition table and killer_list.
                transp_table = gp.Transposition_table() \
                    if params["transposition_table"] else None
                killer_list = gp.Killer_Moves() \
                    if params["killer_moves"] else None

                print("\nAnalysis of position {}:".format(file_name), file=f)
                board.print_char(out_file=f)

                # Call to quiesce() with depth 'max_depth".
                best_move, result, game_end, game_status = gp.quiesce(
                    board, params["max_depth"], -np.Infinity, np.Infinity,
                    params=params, t_table=transp_table, trace=game_trace,
                    killer_list=killer_list
                    )

                # Display results.
                utils.display_results(
                    best_move, result, game_end, game_status, f
                )

                # And check vs. expected.
                # Move:
                if exp_move is not None and type(exp_move[0]) == list:
                    self.assertTrue(
                        best_move in exp_move,
                        "Position: {}; {} not in {}".format(
                            file_name, best_move, exp_move)
                    )
                else:
                    self.assertEqual(
                        best_move, exp_move,
                        "Position: {}; {} != {}".format(
                            file_name, best_move, exp_move)
                    )
                # evaluation:
                self.assertAlmostEqual(
                    (result),
                    (exp_result),
                    places=4,
                    msg="Position: {}; {} != {}".format(
                        file_name, result, exp_result)
                )
                # game_end, game_status:
                self.assertEqual(
                    (game_end, game_status),
                    (exp_end, exp_status),
                    "Position: {}; {} != {}".format(
                        file_name,
                        (game_end, game_status), (exp_end, exp_status))
                )

    def test_negamax(self):
        # Definition of test cases to run:
        # - File to load.
        # - move to try...
        # - expected return from mini_max():
        #   best_move, result, game_end, game_status

        TEST_SEARCH_PARAMS_4 = gp.PLY4_SEARCH_PARAMS
        # Go through all test cases, each on one board.
        # - Position to play
        # - Move/list of moves, result, end, status
        test_cases = (
            ("test_minimax_01.cor", None, 10000, True, 1),
            ("test_minimax_02.cor", None, -10000, True, 2),
            ("test_minimax_03.cor", None, 0, True, 4),
            ("test_minimax_04.cor", None, 0, True, 3),
            ("test_minimax_05.cor", None, -10000, True, 2),
            ("test_minimax_06.cor", [46, 48], 9999.0, False, 0),
            ("test_minimax_07.cor", [19, 40], 9999.0, False, 0),
            ("test_minimax_08.cor", [[32, 46], [32, 48]], 9998.0, False, 0),
            ("test_minimax_09.cor", [41, 45], 1.541666666666667, False, 0),
            ("test_minimax_10.cor", [[33, 25], [26, 27], [26, 16]], -9990, False, 0),
            ("test_minimax_10b.cor", [28, 26], 9994, False, 0)
        )

        params = TEST_SEARCH_PARAMS_4
        with open("output.txt", "w") as f:
            print("")  # To clean up the screen traces.
            for test in test_cases:
                file_name, exp_move, exp_result, exp_end, exp_status = test
                board = bd.Board(file_name)  # The board to put pieces on.
                game_trace = gp.Gametrace(board)  # The game trace.
                transp_table = gp.Transposition_table() \
                    if params["transposition_table"] else None
                killer_list = gp.Killer_Moves() \
                    if params["killer_moves"] else None

                print("Testing position {}: ".format(file_name), end="")
                print("Analysis of position {}: ".format(file_name), file=f)
                board.print_char(out_file=f)

                # Call to negamax.
                t_start = time.time()
                best_move, result, game_end, game_status = gp.negamax(
                    board, 0, -np.Infinity, np.Infinity,
                    params=params, t_table=transp_table, trace=game_trace,
                    killer_list=killer_list)
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
                        "Position: {}. Expected: {}; received: {}".format(
                            file_name, exp_move, best_move)
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

    def test_eval_princes_end(self):
        # Testcases:
        p_vs_p_test_cases = (
            (
                "endgame_02.cor", 4,
                -9988.0, 9989.0
            ),
            (
                "endgame_03.cor", 4,
                -9988.0, -9988.0
            ),
            (
                "endgame_04.cor", 4,
                9987.0, 9989.0
            ),
            (
                "endgame_05.cor", 4,
                9987.0, -9986.0
            )
        )

        # Loop over cases.
        for test_case in p_vs_p_test_cases:
            file_name, test_depth, exp_result_w, exp_result_b = test_case
            board = bd.Board(file_name)

            # Run 2 tests per case.
            board.turn = bd.WHITE
            result_w = gp.eval_princes_end(board, test_depth)
            board.turn = bd.BLACK
            result_b = gp.eval_princes_end(board, test_depth)

            # Check results.
            self.assertEqual(
                (result_w, result_b), (exp_result_w, exp_result_b),
                f"Error in position {file_name}"
            )

    def test_eval_princes_and_soldiers_end(self):
        # Testcases:
        endgame_test_cases = (
            ("test_minimax_09.cor", 9993.0, None),
            ("endgame_01.cor", None, 9989.0),
            ("endgame_06.cor", None, 9989.0),
            ("endgame_07.cor", None, None),
            ("endgame_08.cor", None, None),
            ("endgame_09.cor", None, None),
            ("endgame_10.cor", None, None),
            ("endgame_11.cor", None, None),
            ("endgame_12.cor", None, None),
            ("endgame_13.cor", None, None),
            ("endgame_14.cor", None, None),
            ("endgame_15.cor", None, None),
            ("endgame_16.cor", -9982.0, 9983.0),
            ("endgame_17.cor", None, 9981.0),
            ("endgame_18.cor", None, 9983.0)
        )

        # Loop over test cases.
        for test_case in endgame_test_cases:
            file_name, exp_result_w, exp_result_b = test_case
            board = bd.Board(file_name)
            test_depth = 4  # Arbitrary value for tests.

            # Run tests per case.
            board.turn = bd.WHITE
            result_w = gp.eval_princes_and_soldiers_end(board, test_depth)
            board.turn = bd.BLACK
            result_b = gp.eval_princes_and_soldiers_end(board, test_depth)

            # Check results.
            self.assertEqual(
                (result_w, result_b), (exp_result_w, exp_result_b),
                f"Error in position {file_name}"
            )

    def test_eval_player_without_knights(self):
        """
        Evaluate a given position in which:
        - one player has no Knights
        - the other player some Knight
        """
        # Test cases: position, expected resul (if two values,
        # sides are flipped for a second test on the position).
        test_cases = (
            ("position_11.cor", 9989.0),
            ("test_minimax_08.cor", None),
            ("test_quiesce_01.cor", None),
            ("test_quiesce_02.cor", None, 9985.0),  # Test both sides
            ("test_quiesce_03.cor", None, 9987.0),  # Test both sides
            ("test_quiesce_05.cor", None),
            ("test_quiesce_06.cor", None),
            ("test_quiesce_07.cor", None),
            ("test_quiesce_08.cor", None, 9987.0),  # Test both sides
            ("test_minimax_03.cor", None, 9985.0),  # Test both sides 
            ("test_minimax_06.cor", 9995.0),
            ("test_minimax_07.cor", None),
            ("test_minimax_10.cor", None, 9987.0),
            ("endgame_19.cor", None),
            ("test_make_pseudomove_03.cor", None),
            ("test_make_pseudomove_05.cor", None, None),
            ("test_make_pseudomove_07.cor", None, None),
            ("test_make_pseudomove_11.cor", None, None)
        )
        # Loop over test cases:
        for test in test_cases:
            file_name, exp_results = test[0], test[1:]
            board = bd.Board(file_name)
            player_side = board.turn
            opponent_side = bd.WHITE if player_side == bd.BLACK else bd.BLACK
            test_depth = 4  # Arbitrary value for tests.

            # Obtain and check results.
            res_1 = gp.eval_player_without_knights(board, test_depth)
            self.assertEqual(
                res_1, exp_results[0],
                f"Error in position {file_name} with {board.turn} to move."
            )

            # If it's a two sides test, run second test.
            if len(exp_results) == 2:
                board.turn = opponent_side
                res_2 = gp.eval_player_without_knights(board, test_depth)
                self.assertEqual(
                    res_2, exp_results[1],
                    f"Error in position {file_name} with {board.turn} to move."
                )

    def test_prince_has_moves(self):
        # Test cases: position, expected result.
        test_cases = (
            ("position_11.cor", True, True),
            ("endgame_19.cor", True, None),  # No blank Prince
            ("endgame_20.cor", True, False),
            ("test_quiesce_01.cor", True, False),
            ("test_quiesce_02.cor", True, False),
            ("test_quiesce_03.cor", True, True),
            ("test_quiesce_05.cor", True, False),
            ("test_quiesce_06.cor", True, False),
            ("test_quiesce_07.cor", True, True),
            ("test_quiesce_08.cor", True, None),  # No black Prince
            ("test_minimax_03.cor", True, False),
            ("test_minimax_06.cor", True, True),
            ("test_minimax_07.cor", True, None),  # No blank Prince
            ("test_minimax_08.cor", True, True),
            ("test_minimax_10.cor", True, True),
            ("test_make_pseudomove_03.cor", True, None),  # No blank Prince
            ("test_make_pseudomove_05.cor", True, None),  # No blank Prince
            ("test_make_pseudomove_07.cor", True, True),
            ("test_make_pseudomove_11.cor", True, True)
        )
        # Loop over test cases:
        for test in test_cases:
            file_name, exp_res_w, exp_res_b = test
            board = bd.Board(file_name)
            # White test.
            board.turn = bd.WHITE
            if board.prince[board.turn] is not None:
                # Prince present for player.
                has_moves_w = gp.prince_has_moves(board, board.turn)
                self.assertEqual(
                    has_moves_w, exp_res_w,
                    f"Error in position {file_name} with {board.turn} to move."
                )
            # Black test.
            board.turn = bd.BLACK
            if board.prince[board.turn] is not None:
                # Prince present for player.
                has_moves_b = gp.prince_has_moves(board, board.turn)
                self.assertEqual(
                    has_moves_b, exp_res_b,
                    f"Error in position {file_name} with {board.turn} to move."
                )

    def test_endgame_prediction(self):
        # Testcases:
        endgame_test_cases = (
            ("endgame_01.cor", None, 9989.0),
            ("endgame_02.cor", -9988.0, 9989.0),
            ("endgame_03.cor", -9988.0, -9988.0),
            ("endgame_04.cor", 9987.0, 9989.0),
            ("endgame_05.cor", 9987.0, -9986.0),
            ("endgame_06.cor", None, 9989.0),
            ("endgame_07.cor", None, None),
            ("endgame_08.cor", None, None),
            ("endgame_09.cor", None, None),
            ("endgame_10.cor", None, None),
            ("endgame_11.cor", None, None),
            ("endgame_12.cor", None, None),
            ("endgame_13.cor", None, None),
            ("endgame_14.cor", None, None),
            ("endgame_15.cor", None, None),
            ("endgame_16.cor", -9982.0, 9983.0),
            ("endgame_17.cor", None, 9981.0),
            ("endgame_18.cor", None, 9983.0),
            ("endgame_19.cor", None, None),
            ("endgame_20.cor", 9985.0, None),
            ("position_11.cor", None, 9989.0),
            ("test_quiesce_01.cor", 9987.0, None),
            ("test_quiesce_02.cor", 9985.0, None),
            ("test_quiesce_03.cor", 9987.0, None),
            ("test_quiesce_05.cor", None, None),
            ("test_quiesce_06.cor", None, None),
            ("test_quiesce_07.cor", 9987.0, None),
            ("test_quiesce_08.cor", 9987.0, None),  # No black Prince
            ("test_minimax_03.cor", 9985.0, None),
            ("test_minimax_06.cor", 9995.0, None),
            ("test_minimax_07.cor", None, None),  # No black Prince
            ("test_minimax_08.cor", None, None),
            ("test_minimax_09.cor", 9993.0, None),
            ("test_minimax_10.cor", 9987.0, None),
            ("test_make_pseudomove_03.cor", None, None),  # No black Prince
            ("test_make_pseudomove_05.cor", None, None),  # No black Prince
            ("test_make_pseudomove_07.cor", None, None),
            ("test_make_pseudomove_11.cor", None, None)
        )

        # Loop over test cases.
        for test_case in endgame_test_cases:
            file_name, exp_result_w, exp_result_b = test_case
            board = bd.Board(file_name)
            test_depth = 4  # Arbitrary value for tests.

            # Run tests per case.
            board.set_turn(bd.WHITE)
            result_w = gp.endgame_prediction(board, test_depth)
            board.set_turn(bd.BLACK)
            result_b = gp.endgame_prediction(board, test_depth)

            # Check results.
            self.assertEqual(
                (result_w, result_b), (exp_result_w, exp_result_b),
                f"Error in position {file_name}"
            )


if __name__ == '__main__':
    unittest.main()
