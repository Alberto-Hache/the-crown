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
        move, result, game_end, end_status = mini_max(
            board, depth, alpha, beta)
        search_end = True  # No iterated search for now.
    return move, result, game_end, end_status


def mini_max(board, depth, alpha, beta):
    # best_move = None
    # if depth == MAX_DEPTH  # A leave node
    #   result, game_end, end_status = evaluate(board)
    # else:
    #   moves = calculate pseudo_moves (not checked as legal yet)
    #   n_moves_tried = 0
    #   keep_exploring = True
    #   while len(moves) > 0 and keep_exploring:
    #       m = pick_move(moves)
    #       new_board, legal = make_move(board, m)
    #       if legal(new_board):
    #           n_moves_tried +=1
    #           sons_move, result, game_end, end_status = mini_max(
    #               new_board, depth + 1, -beta, -alpha)
    #           if result > alpha:
    #               best_move, alpha = sons_move, result
    #           if alpha >= beta:
    #               keep_exploring = False
    #   if n_moves_tried == 0:
    #       check why and set result, game_end, end_status
    #   return best_move

    best_move, result, game_end, end_status = (None, None), None, True, ON_GOING

    if depth == MAX_DEPTH:
        result, game_end, end_status = evaluate(board)
    else:
        pass

    return best_move, result, game_end, end_status


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


def evaluate(board):
    # Return PLAYER_WINS/OPPONENT_WINS/DRAW, with PLAYER being
    # the side whose turn it is to move.
    # NOTE: multiple return points for efficiency.

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
    if board.pieces[player_side].sum() == 0:
        return OPPONENT_WINS, True, VICTORY_NO_PIECES_LEFT
    elif board.pieces[opponent_side].sum() == 0:
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
