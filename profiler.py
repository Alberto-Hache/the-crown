import time
import cProfile

import game_play as gp
import board as bd
import utils


def profiler_generate_pseudomoves():
    iterations = 1000
    time_0 = time.ctime()  # Start time.
    print("{:<20}{}".format("- Started:", time_0))

    board = bd.Board("test_make_pseudo_move_01.cor")
    for _ in range(iterations):
        _, _ = gp.generate_pseudomoves(board)

    time_end = time.ctime()  # End time.
    print("{:<20}{}".format("- Ended:", time_end))


if __name__ == '__main__':
    cProfile.run('profiler_generate_pseudomoves()', sort='tottime')
