###############################################################################
# This auxiliary program creates the .csv file on which a tournament
# can be played by 'tournament.py'.
###############################################################################

# Standard library imports
import csv
import os

# Local application imports
pass

# Paths:
TOURNAMENT_PATH = "/tournament/"  # Location of all tournament data.

# Tournament configuration:
tournament_name = "I_Crown_Tournament"

players = (
    ("crowny-i", (0.025, 0.2, 1.6)),
    ("crowny-ii", (0.025, 0.2, 1.6)),
    ("crowny-iii", (0.025, 0.2, 1.6)),
    ("crowny-iv", (0.025, 0.2, 1.6)),
    ("crowny-v", (0.025, 0.2, 1.6)),
    ("crowny-vi", (0.025, 0.2, 1.6)),
)

n_rounds_per_match = 5
pair_equal_depth = False

# Creation of the list of matches.
players_list = [
    [p[0], r]
    for p in players
    for r in p[1]
]

n_players = len(players_list)
pairings = [
    [players_list[i], players_list[j]]
    for i in range(n_players)
    for j in range(i+1, n_players) if
    players_list[i] != players_list[j] and (
        players_list[i][0] != players_list[j][0] or pair_equal_depth
    )
]

# Dump now pairings into .csv file.
dir_path = os.path.dirname(os.path.realpath(__file__))
tourn_file_name = f"{dir_path}{TOURNAMENT_PATH}{tournament_name}.csv"
with open(tourn_file_name, mode="w") as csv_file:
    writer = csv.writer(
        csv_file, delimiter=',', quotechar='"',
        quoting=csv.QUOTE_MINIMAL
    )
    writer.writerow([
        "player_1", "rnd_1", "player_2", "rnd_2", "board", "n_rounds"
    ])
    for p in pairings:
        writer.writerow([
            p[0][0], p[0][1], p[1][0], p[1][1], "", n_rounds_per_match
        ])
