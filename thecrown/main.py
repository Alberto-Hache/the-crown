# Standard library imports
import sys
import os
import types
import time
import datetime
import numpy as np
from collections import namedtuple

# Local application imports
import board as bd
import gameplay as gp
import crownutils as ut

# Paths:
GAMES_PATH = "/games/"  # Location of saved games.
OUTPUT_PATH = "/output/"  # Results of the game.
# Output files.
GAME_METRICS_FILE = "game_metrics.txt"
GAME_RECORD_FILE = "game_record.txt"

# Local constants.
HUMAN_PLAYER = "Human"
MACHINE_PLAYER = "Computer"

# Player as a named tuple:
Player = namedtuple('Player', 'name, type, side, params')

# Players set.
DEFAULT_WHITE_PLAYER = "crowny-iii"
DEFAULT_BLACK_PLAYER = "crowny-iii"

crown_players = {
    "human": Player(
        "Human", HUMAN_PLAYER, None, None
    ),
    "crowny-i": Player(
        "Crowny-I", MACHINE_PLAYER, None, gp.PLY1_SEARCH_PARAMS
    ),
    "crowny-ii": Player(
        "Crowny-II", MACHINE_PLAYER, None, gp.PLY2_SEARCH_PARAMS
    ),
    "crowny-iii": Player(
        "Crowny-III", MACHINE_PLAYER, None, gp.PLY3_SEARCH_PARAMS
    ),
    "crowny-iv": Player(
        "Crowny-IV", MACHINE_PLAYER, None, gp.PLY4_SEARCH_PARAMS
    ),
    "crowny-v": Player(
        "Crowny-V", MACHINE_PLAYER, None, gp.PLY5_SEARCH_PARAMS
    ),
    "crowny-vi": Player(
        "Crowny-VI", MACHINE_PLAYER, None, gp.PLY6_SEARCH_PARAMS
    ),
    "crowny-vii": Player(
        "Crowny-VII", MACHINE_PLAYER, None, gp.PLY7_SEARCH_PARAMS
    )
}


def run_the_crown(arg_list):
    """
    Main function, receiving 'arguments' given to main.py

    Arguments are interpreted like this:
    - 1st string with the name of a player -> White player.
    - 2nd string with the name of a player -> Black player.
    - A string ≠ player name -> a board file to load.
    - integer -> Maximum number of moves to play.

    Default values:
    - White player: DEFAULT_WHITE_PLAYER
    - Black player: DEFAULT_BLACK_PLAYER
    - Board file:   None [initial position]
    - Num. moves:   Infinity
    """
    # Initialize arguments.
    board_file_name = None
    white_player, black_player = None, None
    max_moves = np.Infinity

    # Check args passd
    for arg in arg_list:
        if str.isdigit(arg):
            # Limitation of number of moves to play.
            max_moves = int(arg)
        else:
            # Check if it's the name of a player.
            arg = str.lower(arg)
            player = crown_players.get(arg)  # Check if it's a player.
            if player:
                # It's a known player.
                if white_player is None:
                    white_player = arg
                elif black_player is None:
                    black_player = arg
            else:
                # It must be a board_file_name to load.
                dir_path = os.path.dirname(os.path.realpath(__file__))
                board_file_name = f"{dir_path}{GAMES_PATH}{arg}"

    # Load board position.
    board = bd.Board(board_file_name)
    if not gp.is_legal_loaded_board(board):
        print(f"Error: {board_file_name} is not a legal board for The Crown.")
        sys.exit(1)
    # Assign default players to missing sides.
    if white_player is None:
        white_player = DEFAULT_WHITE_PLAYER
    if black_player is None:
        black_player = DEFAULT_BLACK_PLAYER

    # And now retrieve them from known 'crown_players' dict.
    player_set = [
        crown_players[white_player],
        crown_players[black_player]
    ]

    # Start a match between two players.
    game_result, end_status = play_game(
        board, board_file_name, player_set, max_moves)


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
                ut.algebraic_move_2_coords(move_txt)
            if valid_input:
                # Validate that the move is legal.
                is_legal, explanation = gp.is_legal_move(
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


def display_start(board, player, board_file_name, rec_file):
    # On-SCREEN output:
    game_txt = "Initial position" if board_file_name is None \
        else board_file_name.split("/")[-1]  # Take name of the file only.
    print(
        "Starting The Crown!\n[{}]"
        .format(game_txt)
    )

    # Game-record FILE:
    rec_file.truncate(0)
    print(
        "---< The Crown >---\n({})\n".format(game_txt),
        file=rec_file
    )
    print("White: {}".format(player[0].name), file=rec_file)
    print("Black: {}".format(player[1].name), file=rec_file)
    print("{}\n".format(time.ctime()), file=rec_file)
    board.print_char(out_file=rec_file)
    move_number = 1  # Used to print the game played.
    if board.turn == bd.BLACK:
        print(
            "{}. ...".format(move_number), end="",
            file=rec_file
        )

    # Game-traces FILE:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    metrics_file_path = f"{dir_path}{OUTPUT_PATH}{GAME_METRICS_FILE}"
    with open(metrics_file_path, "w") as metrics_file:
        metrics_file.truncate(0)
        print(
            "MAX_DPTH CHECK_DPTH  RAND "
            "SIDE   MOVE       TIME  EVALUATION   DEPTH       "
            "NODES   TT_SIZE    TT_USE   TT_HITS  TT_COLLS   TT_UPDT"
            "   FULL_SRCH  QUIESC_SRCH  TOP_20_LEVELS",
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
            "{}. {}".format(move_number, ut.move_2_txt(move)),
            end="",
            file=rec_file
        )
    else:
        # Black just played a move.
        print(
            ", {}".format(ut.move_2_txt(move)),
            file=rec_file
        )
        move_number += 1

    # Game-traces FILE:
    pass

    return move_number


def display_end_results(board, result, end_status, rec_file):
    # Result of the game.
    if result == gp.DRAW:
        game_result_txt = gp.TXT_DRAW
    elif result == gp.PLAYER_WINS and board.turn == bd.WHITE:
        game_result_txt = gp.TXT_BLACK_WINS
    else:
        game_result_txt = gp.TXT_WHITE_WINS

    # On-SCREEN output:
    # Final status of the board.
    end_status_txt = "\nEnd of the game: {}".format(
        ut.game_status_txt[end_status])
    print("{}".format(game_result_txt))
    print("{}".format(end_status_txt))

    # Game-record FILE:
    print("\n{}".format(game_result_txt), file=rec_file)
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


def display_move_metrics(
    side, move, result, player_params, time_used, tt_metrics,
    game_trace, metrics_file
):
    """
    Display metrics of a move just produced by the program:

    - SIDE who played (White / Black)
    - MOVE played (algebraic notation).
    - TIME spent for the move (seconds).
    - EVALuation (float).
    - MAX DEPTH reached (integer).
    - TOTAL NODES searched (integer).
    - TT_USAGE
    - TT_SIZE
    - TT_HITS
    - TT_COLLISIONS
    - TT_UPDATES
    - Nodes searched in top 20 levels (list of integers).
    """
    # Variables and player's search parameters:
    player_max_depth = player_params["max_depth"]
    player_max_check_quiesc_depth = player_params["max_check_quiesc_depth"]
    player_randomness = player_params["randomness"]
    player_hash = tt_metrics[0]
    hash_use = tt_metrics[1]

    move_txt = ut.move_2_txt(move)
    nodes_count = game_trace.level_trace[
        game_trace.current_board_ply:, gp.NODE_COUNT_COL
    ].sum()

    # On-SCREEN output:
    print(
        "Move:   {} ({:+.5f})".format(move_txt, result)
    )
    print(
        "Params: full_depth={}, check_depth={}, hash_max={}, rnd={:0.2f}"
        .format(
            player_max_depth,
            player_max_check_quiesc_depth,
            player_hash,
            player_randomness
        )
    )
    print(
        "Search: {:.0f} nodes, "
        "{:.2f} sec, max depth={:d}, "
        "hash use={:d}"
        .format(
            nodes_count,
            time_used,
            game_trace.max_depth_searched,
            hash_use
        )
    )
    # Game-record FILE:
    pass

    # Game-traces FILE:
    # Player's parameters:
    print(
        "{:>8d} {:>10d} {:>5.2f} "
        .format(
            player_max_depth,
            player_max_check_quiesc_depth,
            player_randomness
        ),
        end="",
        file=metrics_file
    )
    # Main search results:
    print(
        "{:<5}  {:<6} {:>8.2f} {:>+11.5f} {:>7d}{:>12.0f} "
        "{:>9} {:>9} {:>9} {:>9} {:>9}"
        .format(
            bd.color_name[side],
            move_txt,
            time_used,
            result,
            game_trace.max_depth_searched,
            nodes_count,
            tt_metrics[0], tt_metrics[1], tt_metrics[2], tt_metrics[3],
            tt_metrics[4]
        ),
        end="",
        file=metrics_file
    )
    ply = game_trace.current_board_ply

    # Full search nodes; quiescence search nodes.
    full_search_nodes = game_trace.level_trace[
        ply:ply + player_max_depth, gp.NODE_COUNT_COL
        ].sum()
    quiescence_search_nodes = game_trace.level_trace[
        ply + player_max_depth:, gp.NODE_COUNT_COL
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
        gp.NODE_COUNT_COL
    ]
    with np.printoptions(formatter={'float': '{:>2.0f}'.format}):
        print("{}".format(nodes_per_level), file=metrics_file)


def play_game(board, board_file_name, player_set, max_moves, timing=None):
    """
    Play a game of The Crown under the conditions given, returning end result.

    Args:
        board (Board):          The board position to play.
        board_file_name (str):  The name of the board to display.
        player_set (list):      A list with two instances of Player:
                                white and black player.
        max_moves (int):        The maximum number of moves to play.
        timing_type (int):      None = no limit;
                                "move" = time limit per move.
                                "game" = total time limit for the game.

    Returns:
        str:    gp.TXT_DRAW, gp.TXT_WHITE_WINS or gp.TXT_BLACK_WINS
        int:    gp.ON_GOING, gp.VICTORY_CROWNING, gp.VICTORY_NO_PIECES_LEFT,
                gp.DRAW_NO_PRINCES_LEFT, gp.DRAW_STALEMATE,
                gp.DRAW_THREE_REPETITIONS, gp.PLAYER_RESIGNS
    """
    # Start the match!
    dir_path = os.path.dirname(os.path.realpath(__file__))

    rec_file_path = f"{dir_path}{OUTPUT_PATH}{GAME_RECORD_FILE}"
    metrics_file_path = f"{dir_path}{OUTPUT_PATH}{GAME_METRICS_FILE}"
    with open(rec_file_path, "a") as rec_file:
        move_number = display_start(
            board, player_set, board_file_name, rec_file
        )
        # Initialize game variables.
        game_end = False
        player_quit = False
        max_moves_played = False
        game_trace = gp.Gametrace(board)
        # Initialize one transposition table and killer moves list per side.
        t_table = [gp.Transposition_table(), gp.Transposition_table()]
        killer_list = [gp.Killer_Moves(), gp.Killer_Moves()]
        # Main game loop.
        while not game_end:
            # Main loop of the full game.
            board.print_char()
            if player_set[board.turn].type == MACHINE_PLAYER:
                # A MACHINE plays this side.
                move, result, game_end, end_status, time_used, tt_metrics =\
                    gp.play(
                        board,
                        params=player_set[board.turn].params,
                        trace=game_trace, t_table=t_table[board.turn],
                        killer_list=killer_list[board.turn]
                    )
                # Print move metrics.
                with open(metrics_file_path, "a") as metrics_file:
                    display_move_metrics(
                        board.turn, move, result,
                        player_set[board.turn].params,
                        time_used, tt_metrics,
                        game_trace, metrics_file
                    )
            else:
                # A HUMAN plays this side.
                move, result = request_human_move(board)
                if result is not None:
                    # Non-void value signals end.
                    player_quit = True
                    game_end = True
            # Update outputs after move.
            if not game_end:
                # Update board with move.
                coord1, coord2 = move
                _, _, _ = board.make_move(coord1, coord2)
                # Update game trace.  TODO: include irreversible arg.
                repetition = game_trace.register_played_board(board)
                # Print move in game log.
                move_number = display_move(board, move, move_number, rec_file)
                if repetition:
                    # Draw; end of game.
                    game_end = True
                    result = gp.DRAW
                    end_status = gp.DRAW_THREE_REPETITIONS
                    display_end_results(
                        board, result, end_status, rec_file
                    )
                else:
                    # Draw separation line.
                    print('.' * 80)
            else:
                # End of the game.
                if player_quit:
                    # Human chose to quit.
                    result = gp.OPPONENT_WINS
                    end_status = gp.PLAYER_RESIGNS
                    display_quit_results(board, rec_file)
                elif max_moves_played:
                    # Max. number of moves requested reached.
                    end_status = gp.ON_GOING
                else:
                    # The game reached an end.
                    display_end_results(board, result, end_status, rec_file)
            # Update moves count.
            max_moves -= 1
            if max_moves == 0:
                game_end = True
                max_moves_played = True

    # Result of the game.
    if result == gp.DRAW:
        game_result = gp.TXT_DRAW
    elif result == gp.PLAYER_WINS and board.turn == bd.WHITE:
        game_result = gp.TXT_BLACK_WINS
    else:
        game_result = gp.TXT_WHITE_WINS

    return game_result, end_status


# Main program.
if __name__ == "__main__":
    # If called directly, run main function with arguments passed.
    run_the_crown(sys.argv[1:])
