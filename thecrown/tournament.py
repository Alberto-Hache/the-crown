###############################################################################
# Execution of a full tournament of The Crown.
###############################################################################

# Standard library imports
import csv
import os
import sys
from collections import namedtuple
import shutil

# Local application imports
import gameplay as gp
import main
import board as bd

# Paths:
TOURNAMENT_PATH = "/tournament/"  # Location of all tournament data.
GAMES_RECORD_PATH = f"{TOURNAMENT_PATH}gamesrecords/"  # Loc. of all detailed games.
GAMES_PATH = "/games/"  # Location of saved games.
PLAYERS_PATH = "/players/"  # Information about human / machine players.
OUTPUT_PATH = "/output/"  # Results of the game.
# Output files.
GAME_METRICS_FILE = "game_metrics.txt"
GAME_RECORD_FILE = "game_record.txt"
# Tournament file(s):
TOURNAMENT_SETTING_FILE = "tournament.csv"


def play_tournament(tournament_file_name):
    """
    Play a full tournament based on conf. file passed, e.g. "tournament.csv"
    Leave all the results in the same directory as "tournament_out.csv"

    Arguments:
        tournament_file_name (string):  A .csv file with the settings.
                                        E.g. "tournament.csv"
    Returns:
        None
    """
    # Identify tournament settings.
    tournament = read_tournament_data(tournament_file_name)
    # Initialize file for tournament output.
    dir_path = os.path.dirname(os.path.realpath(__file__))
    tourn_name = tournament_file_name.split(".")[0]
    tourn_output_path = f"{dir_path}{TOURNAMENT_PATH}{tourn_name}_out.csv"
    with open(tourn_output_path, mode="w") as tournament_out_file:
        field_names = [
            "player_1", "rnd_1", "player_2", "rnd_2",
            "board", "n_rounds", "score_1", "score_2"
        ]
        writer = csv.DictWriter(tournament_out_file, fieldnames=field_names)
        writer.writeheader()

    for match in tournament:
        # Play this match.
        player_1_score, player_2_score = play_match(
            match["player_1"], match["rnd_1"],
            match["player_2"], match["rnd_2"],
            match["board"], int(match["n_rounds"]),
            tourn_output_path
        )
        # Update players' scores.
        pass  # Done offline.


def read_tournament_data(tournament_file_name):
    """
    Read the settings defining a tournament into a list of matches.

    Arguments:
        tournament_file_name (string):  A .csv file with the settings.
                                        E.g. "tournament.csv"

    Returns:
        A list containing one row for each match to be played in the
        tournament. Each match is a dictionary with this content:
        "player_1": (str) player to play White on first game.
        "rnd_1":    (float) random factor applied to player 1.
                    None = 0.0
        "player_2": (str) player to play Black on first game.
        "rnd_2":    (float) random factor applied to player 2.
                    None = 0.0
        "board":    (str) initial position of the game to play.
                    None = "initial_position"
        "n_rounds": (int) the number of rounds these players must play.
                    Each round = 2 games, alternating sides.
    """
    # Aux. function to process strings: numbers to float, "" to None.
    def convert_string(value):
        try:
            value = float(value)
        except ValueError:
            if value == "":
                value = None
            else:
                pass
        return value

    # Read tournament data as a list.
    tournament = []

    dir_path = os.path.dirname(os.path.realpath(__file__))
    tournament_file = f"{dir_path}{TOURNAMENT_PATH}{tournament_file_name}"
    with open(tournament_file, 'r') as csv_file:
        try:
            tournament_plan = csv.DictReader(csv_file)
        except Exception as exc:
            print(exc)
            exit(1)

        for match_row in tournament_plan:
            for k, v in match_row.items():
                v = convert_string(v)
                match_row[k] = v
            tournament.append(match_row)

    return tournament


def play_match(
    player_1, rnd_1, player_2, rnd_2, board_name, n_rounds, tourn_output_path
):
    """
    Play a match according to arguments passed.

    Arguments:
        player_1 (str): Name of the first player, e.g. "crowny-iv".
        rnd_1 (float):  Random factor applied to player 1.
                        None = 0.0
        player_2 (str): Name of the second player, e.g. "crowny-iii".
        rnd_2 (float):  Random factor applied to player 2.
                        None = 0.0
        board_name (str):
                        Initial position of the game to play.
                        None = "initial_position.cor"
        n_rounds (int): Number of rounds these players must play;
                        (if both are deterministic, n_rounds is made 1).
                        Each round = 2 games, alternating sides;
                        (if it's the same player and it's deterministic,
                        only 1 game is played).
        tourn_output_path (str):   
                        Full route to text file to update match results.

    Returns:
        float:          Score obtained by player_1
        float:          Score obtained by player_2

    """
    # Retrieve players' data from their .yaml files.
    player_1_dict = main.read_player_data(player_1)
    player_2_dict = main.read_player_data(player_2)

    # Update players' parameters as needed, overriding original values.
    if rnd_1 is not None:
        player_1_dict["randomness"] = rnd_1
    if rnd_2 is not None:
        player_2_dict["randomness"] = rnd_2
    # Determine the games to actually play.
    is_deterministic = \
        player_1_dict["randomness"] == 0 and \
        player_2_dict["randomness"] == 0

    # Identify board position.
    dir_path = os.path.dirname(os.path.realpath(__file__))
    if board_name is None:
        board_file_name = None
    else:
        board_file_name = f"{dir_path}{GAMES_PATH}{board_name}"

    # Number of rounds:
    if is_deterministic:
        # Force one round if players have no randomness.
        n_rounds = 1
    # No need to change sides if 100% symmetric.
    n_turns = 1 if is_deterministic and player_1 == player_2 \
        else 2

    # Initialize players' list and scores (a dict. by name).
    player_set = [player_1_dict, player_2_dict]
    player_scores = [0.0, 0.0]

    # Play now all required rounds.
    game_type = "Match"
    for round in range(n_rounds):
        # Each round normally two turns (except full simmetry).
        for turn in range(n_turns):  # 1 or 2.
            # Play a game of the round between the two players.
            board = bd.Board(board_file_name)
            if not gp.is_legal_loaded_board(board):
                print(
                    f"Error: {board_file_name} is not a legal board for The Crown."
                )
                sys.exit(1)
            game_result, end_status, rec_file_path, metrics_file_path = \
                main.play_game(
                    board, board_file_name, player_set,
                    game_type=game_type, round=round + 1
                )
            # Check results and update scorings.
            assert(end_status != gp.ON_GOING), \
                "Error: game between {} and {} ended as 'ON_GOING'.".format(
                    player_1_dict["name"], player_2_dict["name"]
                )
            if game_result == gp.TXT_WHITE_WINS:
                score_w = 1
                score_b = 0
                player_scores[0] += 1
            elif game_result == gp.TXT_BLACK_WINS:
                score_w = 0
                score_b = 1
                player_scores[1] += 1
            else:
                score_w = 0.5
                score_b = 0.5
                player_scores[0] += 0.5
                player_scores[1] += 0.5

            # Update Tournament's tracking file
            with open(tourn_output_path, mode="a") as tourn_out_file:
                game_writer = csv.writer(
                    tourn_out_file, delimiter=',', quotechar='"',
                    quoting=csv.QUOTE_MINIMAL
                )
                game_writer.writerow([
                    player_set[0]["file_name"], player_set[0]["randomness"],
                    player_set[1]["file_name"], player_set[1]["randomness"],
                    board_name, n_rounds,
                    score_w, score_b
                ])

            # Move game record file the tournament's directory .
            # rec_file_path is now '.../thecrown/output/<game-data>.txt
            rec_file_name = rec_file_path.split("/")[-1]  # <game-data>.txt
            new_file_path = "{}{}{}".format(
                dir_path, GAMES_RECORD_PATH, rec_file_name
            )
            shutil.move(rec_file_path, new_file_path)

            # Change turns if needed.
            if n_turns > 1:
                aux1, aux2 = player_set
                player_set = [aux2, aux1]
                aux1, aux2 = player_scores
                player_scores = [aux2, aux1]

    # Match ended.
    return player_scores[0], player_scores[1]


# Main program.
if __name__ == "__main__":
    # If called directly, call run_tournament() with the argument
    # passed (if any).
    tournament_file_name = \
            TOURNAMENT_SETTING_FILE if len(sys.argv) == 1 \
            else sys.argv[1]
    play_tournament(tournament_file_name)
