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

    def minimax_depth_4(self):
        test_cases = (
            "01", "02", "03"
        )
        for test_case in test_cases:
            command = "loop_minimax('{}')".format(test_case)
            cProfile.run(command, sort='tottime')
            self.assertTrue(True)  # TODO: Add proper test (duration?)

    def minimax_depth_5(self):
        test_cases = (
            "04",
        )
        for test_case in test_cases:
            command = "loop_minimax('{}')".format(test_case)
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
            board.turn = color
            for _ in range(iterations):
                _, _ = gp.generate_pseudomoves(board)


def loop_minimax(case_idx):

    test_cases = {
        # MAX DEPTH = 4
        "01": (
            (
                "test_minimax_10b.cor",
            ),
            gp.PLY4_SEARCH_PARAMS
        ),
        "02": (
            (
                "test_minimax_01.cor",
                "test_minimax_02.cor",
                "test_minimax_06.cor"
            ),
            gp.PLY4_SEARCH_PARAMS
        ),
        "03": (
            (
                "test_minimax_07.cor",
                "test_minimax_08.cor",
                "test_minimax_09.cor"
            ),
            gp.PLY4_SEARCH_PARAMS
        ),
        # MAX DEPTH = 5
        "04": (
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
        for _ in range(iterations):
            _, _, _, _ = gp.minimax(
                board, 0, -np.Infinity, np.Infinity,
                params=test_params, trace=game_trace
            )


if __name__ == '__main__':
    unittest.main()
