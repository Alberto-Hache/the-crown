import unittest

import board as bd


class Test_board(unittest.TestCase):
    def setUp(self):
        pass

    def test_hash(self):
        # Pick two random DIFFERENT boards.
        board1 = bd.Board("test_minimax_09.cor")
        board2 = bd.Board("test_quiesce_02.cor")
        # Get and compare their hash values.
        hash1 = board1.hash
        hash2 = board2.hash
        self.assertNotEqual(hash1, hash2)

        # Create a new board from a previous position.
        board3 = bd.Board("test_minimax_09.cor")
        hash3 = board3.hash
        self.assertEqual(hash1, hash3)


if __name__ == '__main__':
    unittest.main()
