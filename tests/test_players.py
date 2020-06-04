# Standard library imports
import unittest
import glob
import yaml
from os.path import dirname, realpath
import collections

# Local application imports
pass

# Location of saved games.
dir_path = dirname(dirname(realpath(__file__)))
PLAYERS_PATH = dir_path + "/thecrown/players/"


class Test_players(unittest.TestCase):
    def setUp(self):
        pass

    def test_players_consistency(self):
        file_list = glob.glob(f"{PLAYERS_PATH}*.yaml")
        result_ok = True
        player_names = []

        # Check for players .yaml files' integrity.
        for file in file_list:
            with open(file) as player_file:
                try:
                    player = yaml.full_load(player_file)
                    player_names.append(player["name"])
                except yaml.YAMLError:
                    result_ok = False
                    print(f"Error found in player file {file}.")

        self.assertTrue(result_ok)

        # Check for repeated player names.
        repeated_names = [
            name for name, count in collections.Counter(player_names).items()
            if count > 1
        ]
        self.assertTrue(
            len(repeated_names) == 0,
            f"Error: repeated player 'name' found ({repeated_names})"
            )


if __name__ == '__main__':
    unittest.main()
