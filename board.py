import numpy as np
import utils
import types

N_ROWS = 7
N_POSITIONS = N_ROWS ** 2

WHITE = 0
BLACK = 1
EMPTY = " "
PRINCE = 0
SOLDIER = 1
KNIGHT = 2

# Load precalculated tables:
coord1to3 = utils.calculate_coord1to3(N_ROWS)
simple_moves = utils.calculate_simple_moves()
knight_moves = utils.calculate_knight_moves()
kingdoms = utils.calculate_kingdoms(N_POSITIONS)

piece_char = {
    PRINCE: ("P", "p"),
    SOLDIER: ("S", "s"),
    KNIGHT: ("K", "k")
}
piece_name = ("Prince", "Knight", "Soldier")
color_name = ("White", "Black")


class Board:
    def __init__(self):
        self.n_rows = N_ROWS
        self.n_positions = N_ROWS ** 2
        self.crown_position = N_ROWS ** 2 - 1
        self.prince_position = [N_ROWS * 2 - 2, 0]

        self.pieces = [[], []]  # Pieces on the board from 0=WHITE, 1=BLACK.
        self.piece_count = np.zeros((2, 3))  # 2 sides x 3 piece types.

        self.board1d = np.full((self.n_positions), None)
        self.board3d = np.full((N_ROWS, N_ROWS, N_ROWS), None)

        # Initial position.
        self.include_piece(PRINCE, BLACK, 0)
        self.include_piece(PRINCE, WHITE, N_ROWS * 2 - 2)
        self.turn = WHITE
        self.computer_side = WHITE

    def include_piece(self, type, color, coord):
        # Create the piece.
        piece=types.SimpleNamespace(type = type, color = color, coord = coord)
        # Update board references.
        self.pieces[color].append(piece)
        self.board1d[coord] = piece
        x1, x2, y = coord1to3[coord]
        self.board3d[x1][x2][y] = piece
        # Update piece counts.
        self.piece_count[color][type] += 1

    def remove_piece(self, coord):
        # Identify the piece.
        piece = self.board1d[coord]
        # Update board references.
        self.pieces[piece.color].remove(piece)
        self.board1d[coord] = None
        x1, x2, y = coord1to3[coord]
        self.board3d[x1][x2][y] = None
        # Update piece counts.
        self.piece_count[piece.color][piece.type] -= 1

    def make_move(self, move):
        coord1, coord2 = move
        # Identify the piece(s).
        piece1 = self.board1d[coord1]
        piece2 = self.board1d[coord2]
        # Piece2 captured?
        if piece2 is not None:
            self.remove_piece(coord2)
        # Move piece1
        self.board1d[coord1] = None
        x1, x2, y = coord1to3[coord1]
        self.board3d[x1][x2][y] = None
        self.board1d[coord2] = piece1
        x1, x2, y = coord1to3[coord2]
        self.board3d[x1][x2][y] = piece1

    def clear_board(self):
        for piece in self.pieces[0] + self.pieces[1]:
            self.remove_piece(piece.coord)

    def print_char(self):
        current_pos = self.n_positions - 1
        n_pos_in_row = 1
        n_indent = 2*self.n_rows + 2
        # Draw the top.
        line = ".".rjust(n_indent)
        print(line)
        # Draw the rows.
        for row in range(self.n_rows, 0, -1):  # rows from 7 to 1.
            n_indent -= 1
            black_pos = True  # Start in black position.
            line = ("{} /".format(row*2 - 1)).rjust(n_indent)
            print(line, end='')
            # Draw row with pieces.
            for pos in range(current_pos - n_pos_in_row + 1,
                             current_pos + 1, +1):
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
            if row == 1:  # Bottom edge.
                print(" ·" + "---·"*(n_pos_in_row//2) + "---·")
                char_ord = ord('a')
                print("  ", end='')
                for i in range(self.n_rows):
                    print("{} / ".format(chr(char_ord + i)), end = '')
                print("")
            else:  # Regular edge.
                line = "/".rjust(n_indent) + "---."*(n_pos_in_row//2) + "---\\"
                print(line)
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
