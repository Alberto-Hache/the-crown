# AI hyperparameters
MAX_DEPTH = 2


def play(board):
    search_end = False
    depth = 1
    while not search_end:
        move, game_end, result = mini_max(board, max_depth)
        search_end = True
    return move, game_end, result


def mini_max(board, max_depth):
    move, game_end, result = None, True, None
    pass
    return move, game_end, result


def evaluate(board):
    pass
