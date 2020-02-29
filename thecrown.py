import sys
import types
import time

import board as bd
import game_play as game
import utils

# Local constants.
HUMAN_PLAYER = "Human"
MACHINE_PLAYER = "Computer"


def request_human_move(board):
    """
    Request and validate a move from the keyboard in algebraic notation.

    Input:
        board:          Board - the position to play on.

    Output:
        move:           A list [coord1, coord2], or None.
        result:         None or a string to signal end.
                        - None: the move was valid.
                        - "Quit": human player asked to quit.

    """
    move = None
    result = None

    valid_input = False
    while not valid_input:
        move_txt = input(
            "Type move for {} (Q to quit):\n".
            format(bd.color_name[board.turn])
        )
        if str.upper(move_txt) == "Q":
            valid_input = True
            result = "Quit"
        else:
            # Check the input is formally valid.
            coord1, coord2, valid_input = \
                utils.algebraic_move_2_coords(move_txt)
            if valid_input:
                # Validate that the move is legal.
                is_legal, explanation = game.is_legal_move(
                    board, (coord1, coord2))
                if is_legal:
                    move = [coord1, coord2]
                else:
                    valid_input = False
                    print(explanation)
            else:
                # Wrong format or unexisting coordinates.
                valid_input = False
                print("Invalid move: {}".format(move_txt))
    return move, result


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
            name="Alberto H",
            type=HUMAN_PLAYER,
            color=bd.BLACK,
            params=None
        )
    ]

    # Start the match!
    with open("game_record.txt", "w") as recorded_game:
        print("Starting The Crown!")
        print(
            "Game started!\n\n",
            "White: {}\n".format(player[0].name),
            "Black: {}\n".format(player[1].name),
            "{}\n".format(time.ctime()),
            file=recorded_game
        )
        game_end = False
        move_number = 1
        while not game_end:
            # Main loop of the full game.
            board.print_char()
            if player[board.turn].type == MACHINE_PLAYER:
                # The machine plays this color.
                move, result, game_end, end_status = game.play(
                    board, player[board.turn].params)
            else:
                # The human plays this color.
                move, result = request_human_move(board)
                game_end = (result is not None)  # Non-void value signals end.

            if not game_end:
                # Update board with move.
                coord1, coord2 = move
                board.make_move(coord1, coord2)
                if board.turn == bd.BLACK:
                    print(
                        "{}. {}, ".format(move_number, utils.move_2_txt(move)),
                        end="", file=recorded_game
                    )
                else:
                    print(
                        "{}".format(utils.move_2_txt(move)),
                        file=recorded_game
                    )
                    move_number += 1
            else:
                # Quit game.
                print("Bye!")

