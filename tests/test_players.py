# Standard library imports
import unittest
import glob
import yaml
from os.path import dirname, realpath

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

        for file in file_list:
            with open(file) as player_file:
                try:
                    player = yaml.full_load(player_file)
                except yaml.YAMLError:
                    result_ok = False
                    print(f"Error found in player file {file}.")

        self.assertTrue(result_ok)


if __name__ == '__main__':
    unittest.main()
