import sys

import board as bd
import game_play as game

if __name__ == "__main__":
    # Handle possible arguments passed.
    file_name = None if (len(sys.argv) == 1) else sys.argv[1]

    with open("game_record.txt", "w") as recorded_game:
        print("Starting The Crown!")
        print("Game started:", file=recorded_game)
        board = bd.Board(file_name)
        game_end = False
        while not game_end:
            board.print_char()
            move, result, game_end, end_status = game.play(
                board, game.MINIMAL_SEARCH_PARAMS
                )
            coord1, coord2 = move
            if move is not None:
                board.make_move(coord1, coord2)
                print(game.move_2_txt(move), end="", file=recorded_game)
                if board.turn == bd.WHITE:
                    print(", ", end="", file=recorded_game)
                else:
                    print("", file=recorded_game)
            else:
                print("No move found.")
