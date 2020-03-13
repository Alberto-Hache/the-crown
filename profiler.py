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

    def minimax(self):
        cProfile.run('loop_minimax()', sort='tottime')
        self.assertTrue(True)  # TODO: Add proper test (duration?)


def loop_generate_pseudomoves():
    iterations = 1000
    time_0 = time.ctime()  # Start time.
    print("{:<20}{}".format("- Started:", time_0))

    board = bd.Board("test_make_pseudomove_01.cor")
    for _ in range(iterations):
        _, _ = gp.generate_pseudomoves(board)

    time_end = time.ctime()  # End time.
    print("{:<20}{}".format("- Ended:", time_end))


def loop_minimax():

    test_cases = (
        "test_minimax_11.cor",
    )
    test_params = gp.PLY5_SEARCH_PARAMS

    """
        "test_minimax_10b.cor",
        PLY4_SEARCH_PARAMS

        "test_minimax_01.cor",
        "test_minimax_02.cor",
        "test_minimax_06.cor"
        PLY4_SEARCH_PARAMS

        "test_minimax_07.cor",
        "test_minimax_08.cor",
        "test_minimax_09.cor"
        PLY4_SEARCH_PARAMS

        "test_minimax_11.cor",
        PLY5_SEARCH_PARAMS
    """

    iterations = 1

    for test in test_cases:
        board = bd.Board(test)
        for _ in range(iterations):
            _, _, _, _ = gp.minimax(
                board, 0, -np.Infinity, np.Infinity,
                params=test_params
            )


if __name__ == '__main__':
    unittest.main()
