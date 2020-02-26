import sys

import board as bd
import game_play as game


class Player:
    def __init__(self, name, player_type, color, params):
        self.name = name
        self.type = player_type
        self.params = params


if __name__ == "__main__":
    # Handle possible arguments passed.
    # Load indicated board position if any.
    file_name = None if (len(sys.argv) == 1) else sys.argv[1]
    board = bd.Board(file_name)

    # Create array with the two players data:
    player = [
        Player(
            "Crowy-I",
            "computer",
            bd.WHITE,
            game.MINIMAL_SEARCH_PARAMS
        ),
        Player(
            "Crowy-II",
            "computer",
            bd.BLACK,
            game.DEFAULT_SEARCH_PARAMS
        )
    ]

    # Start the match!
    with open("game_record.txt", "w") as recorded_game:
        print("Starting The Crown!")
        print(
            "Game started!\n",
            "White: {}\n".format(player[0].name),
            "Black: {}\n".format(player[1].name),
            file=recorded_game
        )
        game_end = False
        move_number = 1
        while not game_end:
            board.print_char()
            move, result, game_end, end_status = game.play(
                board, player[board.turn].params
                )
            coord1, coord2 = move
            if move is not None:
                board.make_move(coord1, coord2)
                if board.turn == bd.BLACK:
                    print(
                        "{}. {}, ".format(move_number, game.move_2_txt(move)),
                        end="",
                        file=recorded_game
                    )
                else:
                    print(
                        "{}".format(game.move_2_txt(move)),
                        file=recorded_game
                    )
            else:
                print("No move found.")
