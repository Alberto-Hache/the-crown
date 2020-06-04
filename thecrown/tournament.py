###############################################################################
# Execution of a full tournament of The Crown.
###############################################################################

# Standard library imports
import csv
import os
import sys
from collections import namedtuple

# Local application imports
import gameplay as gp
import main
import board as bd

# Paths:
TOURNAMENT_PATH = "/tournament/"  # Location of all tournament data.
GAMES_PATH = "/games/"  # Location of saved games.
PLAYERS_PATH = "/players/"  # Information about human / machine players.
# Files:
TOURNAMENT_SETTING_FILE = "tournament.csv"


def play_tournament(tournament_file_name):
    """
    """
    tournament = read_tournament_data(tournament_file_name)
    for match in tournament:
        # Check if this match has been fully played.
        if match["score_1"] + match["score_2"] == 2 * match["n_rounds"]:
            # Scores add up to total: skip this match.
            pass
        else:
            # Play this match.
            player_1_score, player_2_score = \
                play_match(
                    match["player_1"], match["rnd_1"],
                    match["player_2"], match["rnd_2"],
                    match["board"], match["n_rounds"]
                )
            # Update players' scores.
            match["score_1"] += player_1_score
            match["score_2"] += player_2_score


def read_tournament_data(tournament_file_name):
    """
    Read the settings defining a tournament into a list of matches.

    Arguments:
        None

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
        "score_1":  (float) score obtained by player 1 (so far).
                    None = 0.0
        "score_2":  (float) score obtained by player 2 (so far).
                    None = 0.0
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
        except yaml.YAMLError as exc:
            print(exc)

        for match_row in tournament_plan:
            for k, v in match_row.items():
                v = convert_string(v)
                match_row[k] = v
            tournament.append(match_row)

    return tournament


def play_match(player_1, rnd_1, player_2, rnd_2, board, n_rounds):
    """

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

    # Load board position.
    if board is None:
        board_file_name = None
    else:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        board_file_name = f"{dir_path}{GAMES_PATH}{board}"
    board = bd.Board(board_file_name)

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
    for round in range(n_rounds):
        # Each round normally two turns (except full simmetry).
        for turn in range(n_turns):  # 1 or 2.
            # Play a game of the round between the two players.
            game_result, end_status = main.play_game(
                board, board_file_name, player_set)
            # Check results and update scorings.
            assert(end_status != gp.ON_GOING), \
                "Error: game between {} and {} ended as 'ON_GOING'.".format(
                    player_1_dict["name"], player_2_dict["name"]
                )
            if game_result == gp.TXT_WHITE_WINS:
                player_scores[0] += 1
            elif game_result == gp.TXT_BLACK_WINS:
                player_scores[1] += 1
            else:
                player_scores[0] += 0.5
                player_scores[1] += 0.5
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
