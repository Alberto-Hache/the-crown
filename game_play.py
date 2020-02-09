import numpy as np
import copy

import board as bd

# AI search hyperparameters
MAX_DEPTH = 2

# Possible game results
PLAYER_WINS = 1
OPPONENT_WINS = -1
DRAW = 0

# Types of game node status
ON_GOING = 0
VICTORY_CROWNING = 1
VICTORY_NO_PIECES_LEFT = 2
DRAW_NO_PRINCES_LEFT = 3
DRAW_STALEMATE = 4
DRAW_THREE_REPETITIONS = 5


def play(board):
    search_end = False
    alpha, beta = [-float("inf"), float("inf")]
    depth = 0
    while not search_end:
        move, result, game_end, game_status = mini_max(
            board, depth, alpha, beta)
        search_end = True  # No iterated search for now.
    return move, result, game_end, game_status


def mini_max(board, depth, alpha, beta):
    # best_move = None
    # if depth == MAX_DEPTH  # A leave node
    #   result, game_end, game_status = evaluate(board)
    # else:
    #   moves = calculate pseudo_moves (not checked as legal yet)
    #   n_moves_tried = 0
    #   while len(moves) > 0:
    #       m = pick_move(moves)
    #       new_board, legal = make_move(board, m)
    #       if legal(new_board):
    #           n_moves_tried +=1
    #           childs_move, result, game_end, game_status = mini_max(
    #               new_board, depth + 1, -beta, -alpha)
    #           if result > alpha:
    #               best_move, alpha = childs_move, result
    #               if alpha >= beta:
    #                   return(...)
    #   if n_moves_tried == 0:
    #       check why and set result, game_end, game_status:
    #           Stalemate, check-mate, no-pieces-left
    #   return best_move

    best_move, result, game_end, game_status = None, None, True, ON_GOING

    if depth == MAX_DEPTH:
        # A leave node.
        result, game_end, game_status = evaluate(board)
    else:
        # An intermediate node.
        moves, moves_count = generate_pseudomoves(board)
        if moves_count == 0:
            # Playing side has no pseudomoves: evaluate and return.
            result, game_end, game_status = evaluate(board)
            return None, -result, game_end, game_status  # Flip result's sign.
        else:
            # Detect if position is game end?
            # Explore pseudomoves.
            n_moves_tried = 0

    return best_move, result, game_end, game_status


def position_attacked(board, pos, attacking_side):

    attacked = False
    # Loop over each of the up to 6 directions till attacked == True
    for positions in bd.knight_moves[pos]:  # [1, 2, 3, 4, 5, ...] for pos = 0
        # Get the closest piece in that direction and its distance.
        pieces = board.board1d[positions]  # [None, None, piece_1, None, ...]
        try:
            piece_pos = np.where(pieces)[0][0]  # 2
            closest_piece = pieces[piece_pos]  # piece_1

            if closest_piece.color == attacking_side:
                # Keep checking.
                if closest_piece.type == bd.KNIGHT:  # A Knight.
                    attacked = True
                elif closest_piece.type == bd.SOLDIER:  # A Soldier
                    # Check proximity and position in its kingdom.
                    attacked = (piece_pos == 0) or \
                        (piece_pos == 1 and
                         bd.kingdoms[attacking_side][positions[piece_pos]])
                else:  # If it's a Prince; check if it's adjacent.
                    attacked = (piece_pos == 0)
            if attacked:
                break  # No need to check the other directions.
        except IndexError:
            pass  # No pieces found in that direction; do nothing.
    return attacked


def generate_pseudomoves(board):
    """
    Generate a list of non-legally checked moves for the playing side.
    It returns:
        list of lists: [[piece_1, [13, 53...]], [piece_2, [...]]
        lnteger:        The total number of pseudo_moves. 
    """
    moves = []
    moves_count = 0
    # Iterate over every piece from the moving side.
    for piece in board.pieces[board.turn]:
        # Obtain list with piece moves | lists of moves
        p_moves = bd.piece_moves[piece.type][piece.color][piece.coord]
        if type(p_moves[0]) == list:
            # List of moves lists (K or S in kingdom): [[1, 2...], [13, 15...]]
            new_moves = set()  # A set with the moves to find for this 'piece'.
            for moves_list in p_moves:  # [1, 2, 3, 4,...]
                # Get the closest piece in that direction and its distance.
                pieces = board.board1d[moves_list]  # [None, None, piece_1,...]
                try:
                    piece_pos = np.where(pieces)[0][0]  # 2
                    closest_piece = pieces[piece_pos]  # piece_1

                    if closest_piece.color == piece.color:
                        # Add moves till closest_piece [EXCLUDING it].
                        new_moves = new_moves.union(moves_list[:piece_pos])
                    else:
                        # Add moves till closest_piece [INCLUDING it].
                        new_moves = new_moves.union(moves_list[:piece_pos + 1])
                except IndexError:
                    # No pieces in that direction: add all moves.
                    new_moves = new_moves.union(moves_list)
        else:
            # List of moves (P, or S out of kingdom): [1, 2, 3...]
            new_moves = set(
                [p for p in p_moves if board.board1d[p] is None
                    or board.board1d[p].color != piece.color]
            )

        # Update main list.
        moves.append((piece, list(new_moves)))
        moves_count += len(new_moves)

    return moves, moves_count


def make_pseudo_move(board, coord1, coord2):
    """
    Given a *legal* position, try to make a pseudomove.
    Detect if the move would be ilegal first.
    If it's legal, detect some end of game conditions:
    - Prince crowning
    - Opponent is left with no pieces

    Input
        board: Board, coord1: int, coord2: int
    Output
        new_board: Board, is_legal: Boolean, result: int, game_end: Boolean,
        game_status: int*
        * Checked:   ON_GOING / VICTORY_CROWNING / VICTORY_NO_PIECES_LEFT
        * Unchecked: DRAW_NO_PRINCES_LEFT / DRAW_STALEMATE /
                     DRAW_THREE_REPETITIONS
    """

    # Create new board on which to try the move.
    new_board = copy.deepcopy(board)
    new_board.make_move(coord1, coord2)  # Turns have switched now!

    piece_moved = new_board.board1d[coord2]  # The piece just moved.
    side_moved = board.turn  # The side who made the move.

    # Check if it's NOT a legal position.
    if not is_legal(new_board):
        return new_board, False, None, None, None

    # Check if a Prince's crowning.
    if (coord2 == new_board.crown_position) and \
       (piece_moved.type == bd.PRINCE):
        # A Prince was legally moved onto the crown!
        return new_board, True, PLAYER_WINS, True, VICTORY_CROWNING

    # Check if it was the capture of the last piece.
    if new_board.piece_count[new_board.turn].sum == 0:
        return new_board, True, PLAYER_WINS, True, VICTORY_NO_PIECES_LEFT

    # Otherwise, it was a normal move.
    return new_board, True, None, False, ON_GOING


def evaluate(board):
    """Evaluate a position from the playing side's perspective.

    Input:
        Board :     The game position to evaluate.

    Output:         result, game_end, game_status
        int :       PLAYER_WINS/OPPONENT_WINS/DRAW, with PLAYER being
                    the side whose turn it is to move.
        Boolean:    Whether the game has finished.
        int:        ON_GOING / VICTORY_CROWNING / VICTORY_NO_PIECES_LEFT
                    DRAW_NO_PRINCES_LEFT / DRAW_STALEMATE /
                    DRAW_THREE_REPETITIONS

    NOTE: multiple return points for efficiency.
    """

    player_side = board.turn
    opponent_side = bd.BLACK if player_side == bd.WHITE else bd.WHITE

    # 1. Prince on the crown_position?
    piece = board.board1d[board.crown_position]
    if piece is not None:
        if piece.type == bd.PRINCE:
            result = PLAYER_WINS if piece.color == player_side \
                else OPPONENT_WINS
            return result, True, VICTORY_CROWNING

    # 2. Side without pieces left?
    if board.piece_count[player_side].sum() == 0:
        return OPPONENT_WINS, True, VICTORY_NO_PIECES_LEFT
    elif board.piece_count[opponent_side].sum() == 0:
        return PLAYER_WINS, True, VICTORY_NO_PIECES_LEFT

    # 3. No Princes left?
    if board.piece_count[player_side][bd.PRINCE] == 0 and \
            board.piece_count[opponent_side][bd.PRINCE] == 0:
        return DRAW, True, DRAW_NO_PRINCES_LEFT

    # 4. Stalemate?
    pass  # Note: Would require calculating legal moves everytime.
    # DRAW_STALEMATE

    # 5. Three repetitions?
    pass  # Note: Would require a record of all past positions.
    # DRAW_THREE_REPETITIONS

    # 6. Otherwise, it's not decided yet ≈ DRAW
    return DRAW, False, ON_GOING


def is_legal(board):
    """
    Detect if a given position is legal.
    Ilegal cases checked:
    a) More than one Prince on either side.
    b) The moving side could take other side's Prince.
    NO CHECK MADE ON: number of pieces on board (must check at load time).
    """
    turn = board.turn
    no_turn = bd.WHITE if turn == bd.BLACK else bd.BLACK

    # Check first if the number of Princes is legal.
    if board.piece_count[bd.PRINCE][bd.WHITE] > 1 or \
       board.piece_count[bd.PRINCE][bd.BLACK] > 1:
        return False

    # Check now if the moving side could take other side's Prince
    other_prince = board.prince[no_turn]
    if other_prince is not None:
        # Non-playing side has a Prince.
        if position_attacked(board, other_prince.coord, turn):
            # It's in check! -> Ilegal.
            return False

    return True
