import time
import numpy as np
import unittest
import cProfile

import game_play as gp
import board as bd
import utils


class Profiler(unittest.TestCase):
    def setUp(self):
        pass

    def generate_pseudomoves(self):
        cProfile.run('loop_generate_pseudomoves()', sort='tottime')
        self.assertTrue(True)  # TODO: Add proper test (duration?)

    def negamax_depth_4(self):
        test_cases = (
            "4.01", "4.02", "4.03", "4.04"
        )
        for test_case in test_cases:
            print("\nProfiler.negamax_depth_4: Test case {}".format(test_case))
            command = "loop_negamax('{}')".format(test_case)
            cProfile.run(command, sort='tottime')
            self.assertTrue(True)  # TODO: Add proper test (duration?)

    def negamax_depth_5(self):
        test_cases = (
            "5.01",
        )
        for test_case in test_cases:
            print("\nProfiler.negamax_depth_5: Test case {}".format(test_case))
            command = "loop_negamax('{}')".format(test_case)
            cProfile.run(command, sort='tottime')
            self.assertTrue(True)  # TODO: Add proper test (duration?)

    def position_attacked(self):
        cProfile.run('loop_position_attacked()', sort='tottime')
        self.assertTrue(True)  # TODO: Add proper test (duration?)


def loop_position_attacked():

    test_cases = (
        "test_minimax_01.cor",
        "test_minimax_02.cor",
        "test_minimax_03.cor",
        "test_minimax_04.cor",
        "test_minimax_05.cor",
        "test_minimax_06.cor",
        "test_minimax_07.cor",
        "test_minimax_08.cor",
        "test_minimax_09.cor",
        "test_minimax_10.cor",
        "test_minimax_10b.cor",
        "test_minimax_11.cor",
    )
    iterations = 100

    for test_board in test_cases:
        board = bd.Board(test_board)
        for coord in range(board.n_positions):
            for color in [bd.WHITE, bd.BLACK]:
                for _ in range(iterations):
                    _ = gp.position_attacked(
                        board, coord, color
                    )


def loop_generate_pseudomoves():

    test_cases = (
        "test_minimax_01.cor",
        "test_minimax_02.cor",
        "test_minimax_03.cor",
        "test_minimax_04.cor",
        "test_minimax_05.cor",
        "test_minimax_06.cor",
        "test_minimax_07.cor",
        "test_minimax_08.cor",
        "test_minimax_09.cor",
        "test_minimax_10.cor",
        "test_minimax_10b.cor",
        "test_minimax_11.cor",
    )
    iterations = 10000

    for test_board in test_cases:
        board = bd.Board(test_board)
        for color in [bd.WHITE, bd.BLACK]:
            board.set_turn(color)
            for _ in range(iterations):
                _, _ = gp.generate_pseudomoves(board)


def loop_negamax(case_idx):

    test_cases = {
        # MAX DEPTH = 4
        "4.01": (
            (
                "test_minimax_10b.cor",
            ),
            gp.PLY4_SEARCH_PARAMS
        ),
        "4.02": (
            (
                "test_minimax_01.cor",
                "test_minimax_02.cor",
                "test_minimax_06.cor"
            ),
            gp.PLY4_SEARCH_PARAMS
        ),
        "4.03": (
            (
                "test_minimax_07.cor",
                "test_minimax_08.cor",
                "test_minimax_09.cor"
            ),
            gp.PLY4_SEARCH_PARAMS
        ),
        "4.04": (
            (
                "test_minimax_11.cor",
            ),
            gp.PLY4_SEARCH_PARAMS
        ),
        # MAX DEPTH = 5
        "5.01": (
            (
              "test_minimax_11.cor",
            ),
            gp.PLY5_SEARCH_PARAMS
        )
    }

    test_boards, test_params = test_cases[case_idx]
    iterations = 1

    for board_name in test_boards:
        board = bd.Board(board_name)  # The board to play on.
        game_trace = gp.Gametrace(board)  # Tracking repetitions.
        transp_table = gp.Transposition_table() \
            if test_params["transposition_table"] else None
        for _ in range(iterations):
            _, _, _, _ = gp.negamax(
                board, 0, -np.Infinity, np.Infinity,
                params=test_params, t_table=transp_table, trace=game_trace
            )


if __name__ == '__main__':
    unittest.main()
