import sys
import types
import numpy as np

import utils
import textcolors

import game_play as game

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
piece_name = ("Prince", "Soldier", "Knight")
color_name = ("White", "Black")

initial_position = (
    "Pg1", "Kf1", "Kf3", "Se1", "Se3", "Se5",
    "pa1", "ka3", "kb1", "sa5", "sb3", "sc1",
    "w"
)

# UNIQUE CODES for each piece type and color.
piece_code = (
    (1, 2, 3),
    (4, 5, 6)
)

# Load precalculated tables:
coord1to3 = utils.calculate_coord1to3(N_ROWS)  # TODO: move to utils.py
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
        # Generic boaard info.
        self.n_rows = N_ROWS
        self.n_positions = N_ROWS ** 2
        self.crown_position = N_ROWS ** 2 - 1
        self.prince_position = [N_ROWS * 2 - 2, 0]

        # Pieces info.
        self.pieces = [[], []]  # Lists of pieces from 0=WHITE, 1=BLACK.
        self.piece_count = np.zeros((2, 3))  # 2 sides x 3 piece types.
        self.prince = [None, None]  # List with the Prince of each side.

        self.board1d = np.full((self.n_positions), None)
        self.boardcode = np.zeros(self.n_positions + 1)  # Positions + turn.
        # self.boardcode = np.array(blank_code)  # 49 positions + turn.

        # Set position and sides.
        self.load_board(file_name)

    def load_board(self, file_name):
        # TODO: Check file is valid, piece count, side (b/w)...
        if file_name is None:
            lines = initial_position
        else:
            try:
                file_name = GAMES_PATH + file_name
                board_file = open(file_name, 'r')
                lines = board_file.read().splitlines()
                board_file.close()
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
                self.boardcode[self.n_positions] = self.turn
            else:
                try:
                    type, color = char_piece[line[0]]
                    coord = utils.coord_2_algebraic.index(line[1:])
                    self.include_new_piece(type, color, coord)
                except ValueError:
                    print("Error found in file {} ; "
                          "Incorrect <piece><coord>: {}".format(
                            file_name, line))
                    sys.exit(1)

        self.hash = self.calculate_hash()

        if not self.is_legal_board():
            print("Error: {} is not a legal board for 'The Crown'.".format(
                file_name
            ))
            sys.exit(1)

    def is_legal_board(self):
        """
        Check if a board is legal (e.g. after loading it from a .cor file).
        Conditions checked:
        - No Princes can be taken.
        - Number of Princes, Knights, Soldiers per side.
        - No Soldiers in their Prince's starting position.
        """

        # Check basic conditions: Princes <= 1 by side; Prince can't be taken.
        if not game.is_legal(self):
            return False

        # Check now the rest of pieces:
        if (
            self.piece_count[WHITE][KNIGHT] > 2 or
            self.piece_count[WHITE][SOLDIER] > 3 or
            self.piece_count[BLACK][KNIGHT] > 2 or
            self.piece_count[BLACK][SOLDIER] > 3
        ):
            return False

        # Finally, check no Soldier stands on its Princes's starting position.
        p_at_white_promo = self.board1d[self.prince_position[WHITE]]
        if p_at_white_promo is not None:
            if p_at_white_promo.type == SOLDIER and \
               p_at_white_promo.color == WHITE:
                return False

        p_at_black_promo = self.board1d[self.prince_position[BLACK]]
        if p_at_black_promo is not None:
            if p_at_black_promo.type == SOLDIER and \
               p_at_black_promo.color == BLACK:
                return False

        # Otherwise, the board is legal.
        return True

    def include_new_piece(self, type, color, coord, tracing=False):
        """
        Creates a new instance of the piece described and
        puts it in the Board at the given coordinate,
        updating all attributes.
        """
        # Check that it's empty.
        assert self.board1d[coord] is None, \
            "Coord {} ({}) is not empty.".format(
                coord, utils.coord_2_algebraic[coord]
                )
        # Create the piece.
        code_to_use = 0 if tracing else piece_code[color][type]
        piece = types.SimpleNamespace(
            type=type, color=color, coord=coord,
            code=code_to_use, tracing=tracing)
        # Update board references.
        self.pieces[color].append(piece)
        self.board1d[coord] = piece
        self.boardcode[coord] = piece.code
        # Update piece counts (unless just tracing for testing purposes).
        if not piece.tracing:
            self.piece_count[color][type] += 1
        # If it's a Prince, update Princes' list.
        if type == PRINCE:
            self.prince[color] = piece

    def include_existing_piece(self, piece, coord):
        """
        Puts an already existing piece in the Board at the given coordinate,
        updating all attributes.
        """
        # Check that it's empty.
        assert self.board1d[coord] is None, \
            "Coord {} ({}) is not empty.".format(
                coord, utils.coord_2_algebraic[coord]
                )
        # Extract piece's features:
        type = piece.type
        color = piece.color
        # Update piece's coord and board references.
        piece.coord = coord
        self.pieces[color].append(piece)
        self.board1d[coord] = piece
        self.boardcode[coord] = piece.code
        # Update piece counts (unless just tracing for testing purposes).
        if not piece.tracing:
            self.piece_count[color][type] += 1
        # If it's a Prince, update Princes' list.
        if type == PRINCE:
            self.prince[color] = piece

    def remove_piece(self, coord):
        """
        Removes from the board the piece in the coord given,
        updating all attributes.
        """
        # Identify the piece.
        piece = self.board1d[coord]
        # Update board references.
        self.pieces[piece.color].remove(piece)
        self.board1d[coord] = None
        self.boardcode[coord] = 0
        # Update piece counts.
        if not piece.tracing:
            self.piece_count[piece.color][piece.type] -= 1
        # If it's a Prince, update Princes' list.
        if piece.type == PRINCE:
            self.prince[piece.color] = None

    def make_move(self, coord1, coord2):
        """
        Execute all board updates required for a move from coord1 to coord2,
        and report piece changes (captures or leaves).
        NOTE: if coord2 is None, assumption is that a checkmated Prince
              is in coord1, and must now leave.

        Input:
            coord1: int - initial position of the move.
            coord2: int - final position of the move (or None),

        Output:
            captured_piece: Piece - Opponent's piece captured at coord2
                            (or None).
            leaving_piece:  Piece - Playing piece that left the board,
                            (or None):
                            a) Prince checkmated.
                            b) Soldier promoted to Prince.
            old_hash:       int - hash value of the board BEFORE the move.

        """
        # Keep old_hash before changes.
        old_hash = self.hash
        # Obtain moving piece.
        piece1 = self.board1d[coord1]
        # Captured piece and leaving piece to detect:
        captured_piece = None
        leaving_piece = None

        if coord2 is not None:
            # A normal move from coord1 to coord2.
            piece2 = self.board1d[coord2]
            # Piece2 captured?
            if piece2 is not None:
                assert piece2.color != piece1.color, \
                    "Piece {} can't move to coord {} ({}): \
                    already occupied by {}." \
                    .format(
                        piece_char[piece1.type][piece1.color],
                        coord2, utils.coord_2_algebraic[coord2],
                        piece_char[piece2.type][piece2.color]
                    )
                captured_piece = piece2
                self.remove_piece(coord2)
            # Move piece1.
            self.board1d[coord1] = None
            self.boardcode[coord1] = 0

            piece1.coord = coord2
            self.board1d[coord2] = piece1
            self.boardcode[coord2] = piece_code[piece1.color][piece1.type]
            # Manage possible Soldier's promotion.
            if coord2 == self.prince_position[piece1.color] and \
               piece1.type == SOLDIER:
                # A Soldier is promoted to Prince.
                leaving_piece = piece1
                self.remove_piece(coord2)
                self.include_new_piece(PRINCE, self.turn, coord2)
        else:
            # A checkmated Prince in coord1 must leave.
            assert piece1.type == PRINCE, \
                "ERROR: a piece of type {} can't move to 'None'.".\
                format(piece_name[piece1.type])
            leaving_piece = piece1
            self.remove_piece(coord1)

        # Change turns.
        self.flip_turn()
        # self.turn = WHITE if self.turn == BLACK else BLACK
        # self.boardcode[self.n_positions] = self.turn

        # Finally, refresh the board's hash.
        self.hash = self.calculate_hash()

        return captured_piece, leaving_piece, old_hash

    def unmake_move(
        self, coord1, coord2, captured_piece, leaving_piece, old_hash
    ):
        """
        Execute all board updates required to revert a previous move
        from coord1 to coord2, managing changes in pieces.

        Input:
            coord1: int - initial position of the original move.
            coord2: int - final position of the original move (or None),
            captured_piece: Piece - Opponent's piece captured at coord 2,
                            restored now (or None).
            leaving_piece:  Piece - Playing piece that left the board,
                            (or None):
                            a) Prince checkmated, now resurrected.
                            b) Soldier promoted to Prince, now demoted.
            old_hash:       int - hash value of the board BEFORE the move.

        Output:
            (none)

        Move types (examples):          coord2  captured_piece  leaving_piece

        Prince: crowning                a13     -               -
        Normal move                     h3      -               -
        Normal capture                  h3      Knight          -
        Soldier promotion               a1      -               Soldier
        Soldier: capture + promotion    a1      Knight          Soldier
        Prince leaves the board         -       -               Prince
        """

        # Check the piece to return is in coord2, or a mated Prince.
        assert self.board1d[coord2] is not None \
            or leaving_piece.type == PRINCE, \
            "Error: no piece found in {}" \
            .format(utils.coord_2_algebraic[coord2])
        # Check the coord to return is empty.
        assert self.board1d[coord1] is None, \
            "Error: unexpected piece found in {}" \
            .format(utils.coord_2_algebraic[coord1])

        if coord2 is not None:
            # It was a normal move (no checkmate) from coord1 to coord2.

            # Obtain returning piece and put it back.
            if leaving_piece is None:
                # The same piece returns from coord2 to coord1.
                piece1 = self.board1d[coord2]

                self.board1d[coord2] = None
                self.boardcode[coord2] = 0

                piece1.coord = coord1
                self.board1d[coord1] = piece1
                self.boardcode[coord1] = piece_code[piece1.color][piece1.type]
                # Now restablish state at 'coord2'.  # TODO: Take this out of if/else?
                if captured_piece is not None:
                    # It was a move with capture.
                    self.include_existing_piece(captured_piece, coord2)
            else:
                # A Soldier was promoted and must be replaced in coord1.
                self.remove_piece(coord2)
                self.include_existing_piece(leaving_piece, coord1)
                # Now restablish state at 'coord2'.
                if captured_piece is not None:
                    # The move was a capture.
                    self.include_existing_piece(captured_piece, coord2)
        else:
            # A checkmated Prince who was on coord1 must return.
            self.include_existing_piece(leaving_piece, coord1)

        # Change turns.
        self.flip_turn()
        # self.turn = WHITE if self.turn == BLACK else BLACK
        # self.boardcode[self.n_positions] = self.turn

        # Finally, refresh the board's hash.
        # self.hash = self.calculate_hash()
        self.hash = old_hash

    def set_turn(self, color):
        self.turn = color
        self.boardcode[self.n_positions] = self.turn

    def flip_turn(self):
        new_turn = WHITE if self.turn == BLACK else BLACK
        self.turn = new_turn
        self.boardcode[self.n_positions] = self.turn

    def clear_board(self):
        # Not tested. TODO: remove function?

        # Remove all pieces.
        for piece in self.pieces[0] + self.pieces[1]:
            self.remove_piece(piece.coord)
        # Finally, refresh the board's hash.
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        return hash(self.boardcode.tostring())  # v1
        # return hash(str(self.boardcode))  # v2: SLOOOOQW

    def print_char(self, out_file=None, stylized=False):
        current_pos = self.n_positions - 1
        n_pos_in_row = 1
        n_indent = 2*self.n_rows + 2
        # Draw the top.
        line = ".".rjust(n_indent)
        print(line, file=out_file)
        # Draw the rows.
        for row in range(self.n_rows, 0, -1):  # rows from 7 to 1.
            n_indent -= 1
            black_pos = True  # Start in black position.
            line = ("{} /".format(row*2 - 1)).rjust(n_indent)
            print(line, end='', file=out_file)
            # Draw row with pieces.
            for pos in range(current_pos - n_pos_in_row + 1,
                             current_pos + 1, +1):
                piece = self.board1d[pos]
                edge = "\\" if black_pos else "/"
                if piece is None:
                    print(EMPTY + edge, end='', file=out_file)
                else:
                    if piece.tracing:  # A non-playing piece (for tracing).
                        trace_char = "*" if piece.type == TRACE \
                            else hex(piece.type)[2].capitalize()
                        print(trace_char + edge,
                              end='', file=out_file)
                    else:  # A proper piece.
                        if stylized:
                            # Decorate ASCII:
                            if piece.color == WHITE:
                                txt_color, txt_style, bg_color = \
                                    'reset', 'normal', 'reset'
                            else:
                                txt_color, txt_style, bg_color = \
                                    'white', 'bold', 'black'
                            piece_txt = textcolors.colorize_bg(
                                piece_char[piece.type][piece.color],
                                txt_color,
                                fg_intensity='bright',
                                bg_color=bg_color,
                                style=txt_style
                                )
                        else:
                            # Plain ASCII
                            piece_txt = piece_char[piece.type][piece.color]
                        print(piece_txt + edge,
                              end='', file=out_file)
                black_pos = not black_pos
            print(" ", file=out_file)
            # Draw row with horizontal edge.
            n_indent -= 1
            if row == 1:  # Bottom edge.
                print(" ·" + "---·"*(n_pos_in_row//2) + "---·", file=out_file)
                char_ord = ord('a')
                print("  ", end='', file=out_file)
                for i in range(self.n_rows - 1):
                    print("{} / ".format(chr(char_ord + i)),
                          end='', file=out_file)
                print("{}".format(chr(char_ord + i + 1)), file=out_file)
            else:  # Regular edge.
                line = "/".rjust(n_indent) + "---."*(n_pos_in_row//2) + "---\\"
                print(line, file=out_file)
            current_pos -= n_pos_in_row
            n_pos_in_row += 2
        print(color_name[self.turn] + " to move.\n", file=out_file)

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
    else:
        print("First argument must be the .cor file to display.")
