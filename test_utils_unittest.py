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

    def test_algebraic_move_2_coords(self):
        # Define tests and expected results.
        correct_test_cases = [  # Input string; Output: coord1, coord2
            ["a1a12", 0, 46],
            ["b1b2", 2, 3],
            ["a12a13", 46, 48],
            ["b9b10", 42, 43],
            ["G1f1", 12, 10],
            ["a1++", 0, None],
            ["b11++", 47, None]
        ]
        incorrect_test_cases = [
            "ab12", "ab1a2", "c1", "d1", "c1 d1", "b12++", "++", "a1+", \
            "a1+++", "a1a34"
        ]

        # Run test cases for correct moves.
        for case in correct_test_cases:
            coord1, coord2, is_correct = utils.algebraic_move_2_coords(case[0])
            self.assertEqual(case[1], coord1,
                             "Error found while testing correct move: {}"
                             .format(case[0]))
            self.assertEqual(case[2], coord2,
                             "Error found while testing correct move: {}"
                             .format(case[0]))
            self.assertTrue(is_correct,
                            "Error found while testing correct move: {}"
                            .format(case[0]))

        # Run test cases for INCORRECT moves.
        for case in incorrect_test_cases:
            _, _, is_correct = utils.algebraic_move_2_coords(case)
            self.assertFalse(is_correct,
                             "Error found while testing incorrect move: {}"
                             .format(case))

    def test_calculate_simple_moves(self):
        simple_moves = utils.simple_moves
        board = bd.Board()
        with open("output.txt", "w") as f:
            for position in range(bd.N_POSITIONS):
                print("\nPrince moves from position: {}"
                      .format(position), file=f)
                moves = simple_moves[position]
                board.clear_board()
                board.include_new_piece(bd.PRINCE, bd.WHITE, position)
                trace = 1
                for position_2 in moves:
                    board.include_new_piece(
                        trace, bd.WHITE, position_2, tracing=True)
                    trace += 1
                board.print_char(out_file=f)

        self.assertTrue(filecmp.cmp(
            "output.txt",
            "tests/output_calculate_simple_moves.txt"))

    def test_calculate_soldier_moves(self):
        soldier_moves = utils.soldier_moves
        board = bd.Board()
        with open("output.txt", "w") as f:
            for side in [bd.WHITE, bd.BLACK]:
                for position in range(bd.N_POSITIONS):
                    moves = soldier_moves[side][position]
                    board.clear_board()
                    board.include_new_piece(bd.SOLDIER, side, position)
                    if moves == []:
                        # Soldier on Prince's throne.
                        n_moves = 0
                    else:
                        if type(moves[0]) == int:
                            # Simple list out of kingdom.
                            for position_2 in moves:
                                board.include_new_piece(
                                    bd.TRACE, side, position_2, tracing=True)
                            n_moves = len(moves)
                        else:
                            # List of lists within the kingdom.
                            moves_set = set()
                            for moves_list in moves:
                                moves_set = moves_set.union(moves_list)
                            for position_2 in moves_set:
                                board.include_new_piece(
                                    bd.TRACE, side, position_2, tracing=True)
                            n_moves = len(moves_set)
                    print("{} Soldier: {} moves from position {}"
                          .format(bd.color_name[side], n_moves, position),
                          file=f)
                    board.print_char(out_file=f)

        self.assertTrue(filecmp.cmp(
            "output.txt",
            "tests/output_calculate_soldier_moves.txt"))

    def test_calculate_knight_moves(self):
        knight_moves = utils.knight_moves
        board = bd.Board()
        with open("output.txt", "w") as f:
            for position in range(bd.N_POSITIONS):
                print("\nKnight moves from position: {}"
                      .format(position), file=f)
                moves = knight_moves[position]
                for direction in moves:
                    board.clear_board()
                    board.include_new_piece(bd.KNIGHT, bd.WHITE, position)
                    trace = 1
                    for position_2 in direction:
                        board.include_new_piece(trace, bd.WHITE, position_2,
                            tracing=True)
                        trace += 1
                    board.print_char(out_file=f)

        self.assertTrue(filecmp.cmp(
            "output.txt",
            "tests/output_calculate_knight_moves.txt"))

    def test_calculate_kingdoms(self):
        kingdoms = utils.calculate_kingdoms(bd.N_POSITIONS)
        board = bd.Board()
        board.clear_board()
        with open("output.txt", "w") as f:
            positions = np.argwhere(kingdoms[0]).flatten()
            for position in positions:
                board.include_new_piece(
                    bd.WHITE, bd.WHITE, position, tracing=True)
            positions = np.argwhere(kingdoms[1]).flatten()
            for position in positions:
                board.include_new_piece(
                    bd.BLACK, bd.BLACK, position, tracing=True)
            board.print_char(out_file=f)

        self.assertTrue(filecmp.cmp(
            "output.txt",
            "tests/output_calculate_kingdoms.txt"))


if __name__ == '__main__':
    unittest.main()
