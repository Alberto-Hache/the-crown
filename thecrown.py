import sys
import types

import board as bd
import game_play as game


# Local constants.
HUMAN_PLAYER = "Human"
MACHINE_PLAYER = "Computer"


class Player:
    def __init__(self, name, player_type, color, params):
        self.name = name
        self.type = player_type
        self.color = color
        self.params = params


if __name__ == "__main__":
    # Handle possible arguments passed.
    # Load indicated board position if any.
    file_name = None if (len(sys.argv) == 1) else sys.argv[1]
    board = bd.Board(file_name)

    # Create array with the two players data:
    player = [
        types.SimpleNamespace(
            name="Crowny-I",
            type=MACHINE_PLAYER,
            color=bd.WHITE,
            params=game.MINIMAL_SEARCH_PARAMS
        ),
        types.SimpleNamespace(
            name="Crowny-I",
            type=MACHINE_PLAYER,
            color=bd.BLACK,
            params=game.MINIMAL_SEARCH_PARAMS
        )
    ]
    """
    # Create the piece.
    piece = types.SimpleNamespace(
        type=type, color=color, coord=coord, tracing=tracing)


    player = [
        Player(
            "Crowny-I",
            MACHINE_PLAYER,
            bd.WHITE,
            game.MINIMAL_SEARCH_PARAMS
        ),
        Player(
            "Crowny-I",
            MACHINE_PLAYER,
            bd.BLACK,
            game.MINIMAL_SEARCH_PARAMS
        )
    ]
    """

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
            if player[board.turn].type == MACHINE_PLAYER:
                # The machine plays this color.
                move, result, game_end, end_status = game.play(
                    board, player[board.turn].params
                    )
                coord1, coord2 = move
            else:
                # The human plays this color. TODO: read keyboard input.
                exit(1)
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
