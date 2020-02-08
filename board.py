import sys
import numpy as np

import utils
import types

# Saved games location
GAMES_PATH = "./games/"

# Game dimensions
N_ROWS = 7
N_POSITIONS = N_ROWS ** 2

# Game constants
WHITE = 0
BLACK = 1
EMPTY = " "
PRINCE = 0
SOLDIER = 1
KNIGHT = 2
TRACE = -1  # A fictitious piece for debugging purpose.

piece_char = {
    PRINCE: ("P", "p"),
    SOLDIER: ("S", "s"),
    KNIGHT: ("K", "k")
}
char_piece = {
    "P": (PRINCE, WHITE),
    "K": (KNIGHT, WHITE),
    "S": (SOLDIER, WHITE),
    "p": (PRINCE, BLACK),
    "k": (KNIGHT, BLACK),
    "s": (SOLDIER, BLACK)
}
piece_name = ("Prince", "Knight", "Soldier")
color_name = ("White", "Black")

initial_position = (
    "Pg1", "Kf1", "Kf3", "Se1", "Se3", "Se5",
    "pa1", "ka3", "kb1", "sa5", "sb3", "sc1",
    "w"
)

# Load precalculated tables:
coord1to3 = utils.calculate_coord1to3(N_ROWS)
coord_2_algebraic = utils.calculate_coord_2_algebraic()
kingdoms = utils.calculate_kingdoms(N_POSITIONS)

simple_moves = utils.calculate_simple_moves()  # For the Prince of any side.
soldier_moves = utils.calculate_soldier_moves()  # 2 lists, one for each side.
knight_moves = utils.calculate_knight_moves()  # For the Knight of any side.

# Generate moves table for the 2 x 3 side-type combinations.
piece_moves = (
    # 0: PRINCE; both sides have the same moves.
    (simple_moves, simple_moves),
    # 1: SOLDIER; each side has DIFFERENT moves (kingdom, throne...).
    (soldier_moves[0], soldier_moves[1]),
    # 2: KNIGHT; both sides have the same moves.
    (knight_moves, knight_moves)
)


class Board:
    def __init__(self, file_name=None):
        self.n_rows = N_ROWS
        self.n_positions = N_ROWS ** 2
        self.crown_position = N_ROWS ** 2 - 1
        self.prince_position = [N_ROWS * 2 - 2, 0]

        self.pieces = [[], []]  # Pieces on the board from 0=WHITE, 1=BLACK.
        self.piece_count = np.zeros((2, 3))  # 2 sides x 3 piece types.
        self.prince = [None, None]

        self.board1d = np.full((self.n_positions), None)
        self.board3d = np.full((N_ROWS, N_ROWS, N_ROWS), None)

        # Set position and sides.
        self.load_board(file_name)
        self.computer_side = self.turn

    def load_board(self, file_name):
        if file_name is None:
            lines = initial_position
        else:
            try:
                file_name = GAMES_PATH + file_name
                # print("Loading game position {} ...".format(file_name))
                board_file = open(file_name, 'r')
                lines = board_file.read().splitlines()
            except OSError:
                print("Error accessing file {}".format(file_name))
                sys.exit(1)

        end_line = False
        for line in lines:
            if end_line:
                print("Error found in file {} ; "
                      "lines found after end line (w|b): {}".format(
                        file_name, line))
                sys.exit(1)
            if line in ["w", "W", "b", "B"]:
                end_line = True
                self.turn = WHITE if (line in ["w", "W"]) else BLACK
            else:
                try:
                    type, color = char_piece[line[0]]
                    coord = coord_2_algebraic.index(line[1:])
                    self.include_piece(type, color, coord)
                except ValueError:
                    print("Error found in file {} ; "
                          "Incorrect <piece><coord>: {}".format(
                            file_name, line))
                    sys.exit(1)

    def include_piece(self, type, color, coord, tracing=False):
        # Check that it's empty.
        assert self.board1d[coord] is None, \
            "Coord {} ({}) is not empty.".format(
                coord, coord_2_algebraic[coord])

        # Create the piece.
        piece = types.SimpleNamespace(
            type=type, color=color, coord=coord, tracing=tracing)
        # Update board references.
        self.pieces[color].append(piece)
        self.board1d[coord] = piece
        x1, x2, y = coord1to3[coord]
        self.board3d[x1][x2][y] = piece
        # Update piece counts (unless just tracing for testing purposes).
        # TODO: Check if the number of legal pieces is exceeded [1P, 2K, 3S]
        if not piece.tracing:
            self.piece_count[color][type] += 1
        # If it's a Prince, update Princes' list.
        if type == PRINCE:
            self.prince[color] = piece

    def remove_piece(self, coord):
        # Identify the piece.
        piece = self.board1d[coord]
        # Update board references.
        self.pieces[piece.color].remove(piece)
        self.board1d[coord] = None
        x1, x2, y = coord1to3[coord]
        self.board3d[x1][x2][y] = None
        # Update piece counts.
        if not piece.tracing:
            self.piece_count[piece.color][piece.type] -= 1
        # If it's a Prince, update Princes' list.
        if piece.type == PRINCE:
            self.prince[piece.color] = None

    def make_move(self, piece1, coord2):
        # Obtain full info: piece1@coord1 -> [piece2 @]coord2
        coord1 = piece1.coord
        piece2 = self.board1d[coord2]
        # Piece2 captured?
        if piece2 is not None:
            assert piece2.color != piece1.color, \
                "Piece {} can't move to coord {} ({}): \
                already occupied by {}." \
                .format(
                    piece_char[piece1.type][piece1.color],
                    coord2, coord_2_algebraic[coord2],
                    piece_char[piece2.type][piece2.color]
                )
            self.remove_piece(coord2)
        # Move piece1
        self.board1d[coord1] = None
        x1, x2, y = coord1to3[coord1]
        self.board3d[x1][x2][y] = None
        self.board1d[coord2] = piece1
        x1, x2, y = coord1to3[coord2]
        self.board3d[x1][x2][y] = piece1
        # Change turn
        self.turn = WHITE if self.turn == BLACK else BLACK

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
                    if piece.tracing:  # A non-playing piece (for tracing).
                        trace_char = "*" if piece.type == TRACE \
                            else hex(piece.type)[2].capitalize()
                        print(trace_char + edge,
                              end='')
                    else:  # A proper piece.
                        print(piece_char[piece.type][piece.color] + edge,
                              end='')
                black_pos = not black_pos
            print(" ")
            # Draw row with horizontal edge.
            n_indent -= 1
            if row == 1:  # Bottom edge.
                print(" ·" + "---·"*(n_pos_in_row//2) + "---·")
                char_ord = ord('a')
                print("  ", end='')
                for i in range(self.n_rows - 1):
                    print("{} / ".format(chr(char_ord + i)), end='')
                print("{}".format(chr(char_ord + i + 1)))
            else:  # Regular edge.
                line = "/".rjust(n_indent) + "---."*(n_pos_in_row//2) + "---\\"
                print(line)
            current_pos -= n_pos_in_row
            n_pos_in_row += 2
        print(color_name[self.turn] + " to move.\n")

    def print_1d(self):
        print("[")
        for piece in self.board1d:
            if piece is None:
                print(EMPTY, end='')
            else:
                print(piece_char[piece.type][piece.color], end='')
        print("]")


if __name__ == '__main__':
    # Main program.
    if len(sys.argv) > 0:
        board = Board(sys.argv[1])
        board.print_char()
