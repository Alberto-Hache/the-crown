import numpy as np
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
    #   keep_exploring = True
    #   while len(moves) > 0 and keep_exploring:
    #       m = pick_move(moves)
    #       new_board, legal = make_move(board, m)
    #       if legal(new_board):
    #           n_moves_tried +=1
    #           sons_move, result, game_end, game_status = mini_max(
    #               new_board, depth + 1, -beta, -alpha)
    #           if result > alpha:
    #               best_move, alpha = sons_move, result
    #           if alpha >= beta:
    #               keep_exploring = False
    #   if n_moves_tried == 0:
    #       check why and set result, game_end, game_status
    #   return best_move

    best_move, result, game_end, game_status = None, None, True, ON_GOING

    if depth == MAX_DEPTH:
        result, game_end, game_status = evaluate(board)
    else:
        pass

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
    Generate a list of possible moves for the playing side.

    """
    # Initiate 'moves', a list of piece/moves: [[p1, [13, 53...]], [p2, [...]]
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


def evaluate(board):
    """Evaluate a position from the playing side's perspective.

    Input:
        Board :     The game position to evaluate.

    Output:
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
    pass  # Note: will require a record of all past positions.
    # DRAW_THREE_REPETITIONS

    # 6. Otherwise, it's not decided yet ≈ DRAW
    return DRAW, False, ON_GOING
