import time
import glob
import unittest
import filecmp
import cProfile

import game_play as gp
import board as bd


class Test_game_play(unittest.TestCase):
    def setUp(self):
        pass

    def test_position_attacked(self):
        file_list = glob.glob(bd.GAMES_PATH + "position*.cor")

        with open("output.txt", "w") as f:
            for full_file_name in file_list:
                file_name = full_file_name[len(bd.GAMES_PATH):]  # Remove rel. path.
                for position in range(bd.N_POSITIONS):
                    board = bd.Board(file_name)  # Actual board to put pieces on.
                    display_board = bd.Board("empty.cor")  # A blank board for tracing.
                    if board.board1d[position] is None:
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


if __name__ == '__main__':
    unittest.main()
