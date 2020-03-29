import numpy as np

import board as bd
import game_play as gp
import utils


if __name__ == "__main__":
    board = bd.Board("test_captures_00.cor")

    moves, moves_count = gp.generate_pseudomoves(board)
    moves = gp.pre_evaluate_pseudomoves(board, moves)

    pass
