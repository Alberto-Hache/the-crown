import sys
import types
import time
import datetime
import numpy as np

import board as bd
import game_play as game
import utils

# Local constants.
HUMAN_PLAYER = "Human"
MACHINE_PLAYER = "Computer"

# Output files.
GAME_METRICS_FILE = "output_game_metrics.txt"
GAME_RECORD_FILE = "output_game_record.txt"


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


def display_start(board, player, rec_file):
    # On-SCREEN output:
    print("Starting The Crown!")

    # Game-record FILE:
    print(
        "Game started!\n\n",
        "White: {}\n".format(player[0].name),
        "Black: {}\n".format(player[1].name),
        "{}\n".format(time.ctime()),
        file=rec_file
    )
    move_number = 1  # Used to print the game played.
    if board.turn == bd.BLACK:
        print(
            "{}. ...".format(move_number), end="",
            file=rec_file
        )

    # Game-traces FILE:
    with open(GAME_METRICS_FILE, "w") as metrics_file:
        print(
            "SIDE   MOVE       TIME  EVALUATION MAX_DEPTH       "
            "NODES    FULL_SRCH  QUIESC_SRCH  TOP_20_LEVELS",
            file=metrics_file
        )

    return move_number


def display_move(board, move, move_number, rec_file):
    # On-SCREEN output:
    pass

    # Game-record FILE:
    if board.turn == bd.BLACK:
        # White just played a move.
        print(
            "{}. {}".format(move_number, utils.move_2_txt(move)),
            end="",
            file=rec_file
        )
    else:
        # Black just played a move.
        print(
            ", {}".format(utils.move_2_txt(move)),
            file=rec_file
        )
        move_number += 1

    # Game-traces FILE:
    pass

    return move_number


def display_end_results(board, result, end_status, rec_file):
    # Result of the match.
    if result == game.DRAW:
        match_result_txt = "1/2 - 1/2"
    elif result == game.PLAYER_WINS and board.turn == bd.WHITE:
        match_result_txt = "1 - 0"
    else:
        match_result_txt = "0 - 1"

    # On-SCREEN output:
    # Final status of the board.
    end_status_txt = "\nEnd of the game: {}".format(
        utils.game_status_txt[end_status])
    print("{}".format(match_result_txt))
    print("{}".format(end_status_txt))

    # Game-record FILE:
    print("\n{}".format(match_result_txt), file=rec_file)
    print("{}".format(end_status_txt), file=rec_file)

    # Game-traces FILE:
    pass


def display_quit_results(board, rec_file):
    # On-SCREEN output:
    print("\nBye!")  # The player left the game.

    # Game-record FILE:
    print(
        "\n\n{} quit the game.".format(bd.color_name[board.turn]),
        file=rec_file
    )

    # Game-traces FILE:
    pass


def track_move_metrics(
    side, move, result, max_depth, time_used, game_trace, metrics_file
):
    """
    Track metrics of a move just produced by the program:

    - SIDE who played (White / Black)
    - MOVE played (algebraic notation).
    - TIME spent for the move (seconds).
    - EVALuation (float).
    - MAX DEPTH reached (integer).
    - TOTAL NODES searched (integer).
    - Nodes searched in top 20 levels (list of integers).
    """
    # First columns.
    print(
        "{:<5}  {:<6} {:>8.2f} {:>+11.5f} {:>9d}{:>12.0f} "
        .format(
            bd.color_name[side],
            utils.move_2_txt(move),
            # str(datetime.timedelta(seconds=time_used)),
            time_used,
            result,
            game_trace.max_depth_searched,
            game_trace.level_trace[:, game.NODE_COUNT].sum()
        ),
        end="",
        file=metrics_file
    )
    ply = game_trace.current_board_ply

    # Full search nodes; quiescence search nodes.
    full_search_nodes = game_trace.level_trace[
        ply:ply + max_depth, game.NODE_COUNT
        ].sum()
    quiescence_search_nodes = game_trace.level_trace[
        ply + max_depth:, game.NODE_COUNT
        ].sum()
    print(
        "{:>12.0f} {:>12.0f}  ".format(
            full_search_nodes, quiescence_search_nodes
        ),
        end="",
        file=metrics_file
    )

    # Top 20 levels.
    nodes_per_level = game_trace.level_trace[
        ply:ply+20,
        game.NODE_COUNT
    ]
    with np.printoptions(formatter={'float': '{:>2.0f}'.format}):
        print("{}".format(nodes_per_level), file=metrics_file)


if __name__ == "__main__":
    # Handle possible arguments passed.
    # Load indicated board position if any.
    file_name = None if (len(sys.argv) == 1) else sys.argv[1]
    board = bd.Board(file_name)

    # Create array with the two players' configuration:
    player = [
        types.SimpleNamespace(
            name="Crowny-II",
            type=MACHINE_PLAYER,
            color=bd.WHITE,
            params=game.PLY1_SEARCH_PARAMS
        ),
        types.SimpleNamespace(
            name="Crowny-II",
            type=MACHINE_PLAYER,
            color=bd.BLACK,
            params=game.PLY1_SEARCH_PARAMS
        )
    ]

    # Start the match!
    with open(GAME_RECORD_FILE, "w") as rec_file:
        move_number = display_start(board, player, rec_file)
        # Initialize game variables.
        game_end = False
        player_quit = False
        white_move_printed = False  # In case Black starts.
        game_trace = game.Gametrace(board)
        # Main game loop.
        while not game_end:
            # Main loop of the full game.
            board.print_char()
            if player[board.turn].type == MACHINE_PLAYER:
                # The machine plays this color.
                move, result, game_end, end_status, time_used = game.play(
                    board, params=player[board.turn].params, trace=game_trace)
                # Print move metrics.
                with open(GAME_METRICS_FILE, "a") as metrics_file:
                    track_move_metrics(
                        board.turn, move, result,
                        player[board.turn].params["max_depth"],
                        time_used, game_trace, metrics_file
                        )
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
                # Update game trace.  TODO: include irreversible arg.
                repetition = game_trace.register_played_board(board)
                # Print move in game log.
                move_number = display_move(board, move, move_number, rec_file)
                if repetition:
                    # Draw; end of game.
                    game_end = True
                    display_end_results(
                        board, game.DRAW, game.DRAW_THREE_REPETITIONS, rec_file
                    )
            else:
                # End of the game.
                if player_quit:
                    display_quit_results(board, rec_file)
                else:
                    display_end_results(board, result, end_status, rec_file)
