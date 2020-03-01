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
                    board, [coord1, coord2])
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


def display_end_results(board, result, end_status, rec_file):
    # Result of the match.
    if result == game.DRAW:
        match_result_txt = "1/2 - 1/2"
    elif result == game.PLAYER_WINS and board.turn == bd.WHITE:
        match_result_txt = "1 - 0"
    else:
        match_result_txt = "0 - 1"

    # Final status of the board.
    end_status_txt = "\nEnd of the game: {}".format(
        utils.game_status_txt[end_status])

    # Display texts.
    print("{}".format(match_result_txt))
    print("\n{}".format(match_result_txt), file=rec_file)
    print("{}".format(end_status_txt))
    print("{}".format(end_status_txt), file=rec_file)


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
    with open("game_record.txt", "w") as rec_file:
        print("Starting The Crown!")
        print(
            "Game started!\n\n",
            "White: {}\n".format(player[0].name),
            "Black: {}\n".format(player[1].name),
            "{}\n".format(time.ctime()),
            file=rec_file
        )
        game_end = False
        player_quit = False
        move_number = 1
        white_move_printed = False  # In case Black starts.
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
                if result is not None:
                    # Non-void value signals end.
                    player_quit = True
                    game_end = True

            if not game_end:
                # Update board with move.
                coord1, coord2 = move
                board.make_move(coord1, coord2)
                # Register move in game log.
                if board.turn == bd.BLACK:
                    # White just played a move.
                    white_move_printed = True
                    print(
                        "{}. {}, ".format(move_number, utils.move_2_txt(move)),
                        end="", file=rec_file
                    )
                else:
                    # Black just played a move.
                    if not white_move_printed:
                        print(
                            "{}. ..., ".format(move_number),
                            end="", file=rec_file
                        )
                    print(
                        "{}".format(utils.move_2_txt(move)),
                        file=rec_file
                    )
                    move_number += 1
            else:
                # End of the game.
                if player_quit:
                    print("\nBye!")  # The player left the game.
                else:
                    display_end_results(board, result, end_status, rec_file)
