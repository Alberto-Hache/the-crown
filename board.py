import numpy as np
import utils

N_ROWS = 7

WHITE = 0
BLACK = 1
EMPTY = " "
PRINCE = "Prince"
SOLDIER = "Soldier"
KNIGHT = "Knight"

# Load precalculated tables:
coord1to3 = utils.calculate_coord1to3(N_ROWS)
simple_moves = utils.calculate_simple_moves()

piece_char = {
    PRINCE: ("P", "p"),
    SOLDIER: ("S", "s"),
    KNIGHT: ("K", "k")
}
color_name = ["White", "Black"]


class Board:
    def __init__(self):
        self.n_rows = N_ROWS
        self.n_positions = N_ROWS ** 2
        self.crown_position = N_ROWS ** 2 - 1
        self.prince_position = [N_ROWS * 2 - 2, 0]

        self.pieces = [[], []]  # Pieces on the board from each side, 0=WHITE, 1=BLACK.
        self.pieces_removed = [[], []]  # Pieces removed during game.

        self.board1d = np.full((self.n_positions), None)
        self.board3d = np.full((N_ROWS, N_ROWS, N_ROWS), None)

        # Initial position.
        self.include_piece(PRINCE, BLACK, 0)
        self.include_piece(PRINCE, WHITE, N_ROWS * 2 - 2)
        self.turn = WHITE

    def include_piece(self, type, color, coord):
        # Create the piece.
        piece = Piece(type, color, coord)
        # Update board references.
        self.pieces[color].append(piece)
        self.board1d[coord] = piece
        x1, x2, y = coord1to3[coord]
        self.board3d[x1][x2][y] = piece

    def make_move(self, move):
        pass

    def print_char(self, draw_coords=False):
        left_indent = 0 if not draw_coords else 1
        current_pos = self.n_positions - 1
        n_pos_in_row = 1
        n_indent = left_indent + 2*self.n_rows
        print(" "*n_indent + "·")
        for row in range(self.n_rows, 0, -1):  # rows from 7 to 1.
            n_indent -= 1
            black_pos = True  # Start in black position.
            print(" "*n_indent + "/", end='')  # Initial blanks.
            # Draw row with pieces.
            for pos in range(current_pos - n_pos_in_row + 1, current_pos + 1, +1):
                piece = self.board1d[pos]
                edge = "\\" if black_pos else "/"
                if piece is None:
                    print(EMPTY + edge, end='')
                else:
                    print(piece_char[piece.type][piece.color] + edge, end='')
                black_pos = not black_pos
            print(" ")
            # Draw row with horizontal edge.
            n_indent -= 1
            if row == 1:  # Top bottom edge.
                print("·" + "---·"*(n_pos_in_row//2) + "---·")
            else:  # Regular edge.
                print(" "*n_indent + "/" + "---·"*(n_pos_in_row//2) + "---\\")
            current_pos -= n_pos_in_row
            n_pos_in_row += 2
        print(color_name[self.turn] + " to move.")

    def print_1d(self):
        print("[")
        for piece in self.board1d:
            if piece is None:
                print(EMPTY, end='')
            else:
                print(piece_char[piece.type][piece.color], end='')
        print("]")


class Piece:
    def __init__(self, type, color, coords):
        self.type = type
        self.color = color
        self.coords = coords

    def print(self):
        print(self.type)
