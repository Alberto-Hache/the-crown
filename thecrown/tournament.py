###############################################################################
# Execution of a full tournament of The Crown.
###############################################################################

# Standard library imports
from collections import namedtuple

# Local application imports
from thecrown.main import run_the_crown

# Paths:
TOURNAMENT_PATH = "/tournament/"  # Location of all tournament data.
GAMES_PATH = "/games/"  # Location of saved games.
PLAYERS_PATH = "/players/"  # Information about human / machine players.
# Files:
TOURNAMENT_SETTING_FILE = "tournament.csv"


# Tournament settings.
Match = namedtuple('match', 'w_player w_rnd b_player b_rnd board n_rounds')


def read_tournament_data():
    """
    """



tournament = (
    Match("crowny-i", None, "crowny-i", None, None, 1),
    Match("crowny-ii", None, "crowny-ii", None, None, 1)
)


def run_tournament():


def run_match(w_player, b_player)