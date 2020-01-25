import board as bd

# AI search hyperparameters
MAX_DEPTH = 2

# Possible game results
WHITE_WINS = 1
BLACK_WINS = -1
DRAW = 0

# Types of game end status
ON_GOING = 0
VICTORY_CROWNING = 1
VICTORY_NO_PIECES_LEFT = 2
DRAW_NO_PRINCES_LEFT = 3
DRAW_STALEMATE = 4
DRAW_THREE_REPETITIONS = 5


def play(board):
    search_end = False
    alpha_beta_window = [-float("inf"), float("inf")]
    while not search_end:
        move, result, game_end, end_status = mini_max(
            board, depth=0, side=board.turn, alpha_beta_window)
        search_end = True  # No iterated search for now.
    return move, result, game_end, end_status


def mini_max(board, depth, side, alpha_beta_window):
    move, result, game_end, end_status = (None, None), None, True, ON_GOING
    # If depth >= MAX_DEPTH.
        # A leave node: Evaluate board.
    # else, Keep exploring:
        # Calculate pseudo_moves (not checked as legal).
        # while len(moves) > 0:
            # m = pick_move()
            # new_board, legal = make_move(board, m)
            # if legal:
                # 

    
    return move, result, game_end, end_status


def evaluate(board):
    # Return WHITE_WINS/BLACK_WINS/DRAW from white's perspective.

    # 1. Prince on the crown_position?
    piece = board.board1d[board.crown_position]
    if piece is not None:
        if piece.type == bd.PRINCE:
            result = WHITE_WINS if piece.color == bd.WHITE \
                else BLACK_WINS
            game_end, end_status = True, VICTORY_CROWNING

    # 2. Side without pieces left?
    if board.pieces[bd.WHITE].sum() == 0:
        result, game_end = BLACK_WINS, True
    elif board.pieces[bd.BLACK].sum() == 0:
        result, game_end, end_status = WHITE_WINS, True, VICTORY_NO_PIECES_LEFT

    # 3. No Princes left?
    if not game_end:
        if board.piece_count[bd.WHITE][bd.PRINCE] == 0 and \
                board.piece_count[bd.BLACK][bd.PRINCE] == 0:
            result, game_end, end_status = DRAW, True, DRAW_NO_PRINCES_LEFT

    # 4. Stalemate?
    pass  # Note: Would require calculating moves everytime.
    # DRAW_STALEMATE

    # 5. Three repetitions?
    pass  # Note: will require a record of all past positions.
    # DRAW_THREE_REPETITIONS

    # 6. Otherwise, it's not decided yet ≈ DRAW
    result, game_end, end_status = DRAW, False, ON_GOING

    return result, game_end, end_status
