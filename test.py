import numpy as np

import board as bd
import game_play as gp
import utils


if __name__ == "__main__":
    # Test cases.
    board = bd.Board("test_captures_00.cor")
    expected_moves = [
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

    # Generate and sort moves.
    moves, moves_count = gp.generate_pseudomoves(board)
    moves = gp.pre_evaluate_pseudomoves_WIP(board, moves)

    # Check results.
    assert((moves == expected_moves).all)

