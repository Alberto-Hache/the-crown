import time
import sys
import glob
import unittest
import filecmp
import numpy as np

import board as bd
import utils


class Test_utils(unittest.TestCase):
    def setUp(self):
        pass

    def test_calculate_coord1to3(self):
        # Generate expected results.
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
        # Now test function vs. expected.
        coord1to3 = utils.calculate_coord1to3(3)
        np.testing.assert_array_equal(
            coord1to3, expected_coord1to3, err_msg='Results differ!')

    def test_calculate_knight_moves(self):
        knight_moves = utils.calculate_knight_moves()
        board = bd.Board()
        with open("output.txt", "w") as f:
            for position in range(bd.N_POSITIONS):
                print("\nKnight moves from position: {}"
                      .format(position), file=f)
                moves = knight_moves[position]
                for direction in moves:
                    board.clear_board()
                    board.include_piece(bd.KNIGHT, bd.WHITE, position)
                    trace = 1
                    for position_2 in direction:
                        board.include_piece(trace, bd.WHITE, position_2,
                                            tracing=True)
                        trace += 1
                    board.print_char(out_file=f)

        self.assertTrue(filecmp.cmp("output.txt", "tests/output.calculate_knight_moves.txt"))




if __name__ == '__main__':
    unittest.main()
