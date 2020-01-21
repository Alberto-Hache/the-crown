import board as bd

# AI hyperparameters
MAX_DEPTH = 2

WHITE_WINS = 1
BLACK_WINS = -1
DRAW = 0


def play(board):
    search_end = False
    depth = 1
    while not search_end:
        move, game_end, result = mini_max(board, depth)
        search_end = True
    return move, game_end, result


def mini_max(board, depth):
    move, game_end, result = None, True, None
    pass
    return move, game_end, result


def evaluate(board):
    # Return WHITE_WINS/BLACK_WINS/DRAW from white's perspective.

    # 1. Prince on the crown_position?
    piece = board.board1d[crown_position]
    if piece is not None:
        if piece.type == PRINCE:
            result = WHITE_WINS if piece.color == bd.WHITE \
                else BLACK_WINS
            game_end = True

    # 2. Side without pieces left?
    if board.pieces[bd.WHITE].sum() == 0:
        result, game_end = BLACK_WINS, True
    elif board.pieces[bd.BLACK].sum() == 0:
        result, game_end = WHITE_WINS, True

    # 3. No Princes left?
    if not game_end:
        if board.piece_count[bd.WHITE][bd.PRINCE] == 0 and \
                board.piece_count[bd.BLACK][bd.PRINCE] == 0:
            result = DRAW
            game_end = True

    # 4. Stalemate?
    pass  # Note: Would require calculating moves everytime.

    # 5. Three repetitions?
    pass  # Note: will require a record of all past positions.

    # 6. Otherwise, it's not decided yet ≈ DRAW
    result = DRAW
    game_end = False

    return game_end, result
