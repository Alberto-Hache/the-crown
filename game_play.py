import numpy as np
import copy

import board as bd

# AI search hyperparameters
MAX_DEPTH = 4

# Possible game results
PLAYER_WINS = float(10000)  # Winning score; to be reduced by node depth.
OPPONENT_WINS = -PLAYER_WINS  # Losing score; to be increased by node depth.
DRAW = 0

# Types of game node status
ON_GOING = 0
VICTORY_CROWNING = 1
VICTORY_NO_PIECES_LEFT = 2
DRAW_NO_PRINCES_LEFT = 3
DRAW_STALEMATE = 4
DRAW_THREE_REPETITIONS = 5

game_status_txt = (
    "Game on-going",
    "Victory (Prince crowned)",
    "Victory (no pieces left)",
    "Draw (no Princes left)",
    "Draw, (stalemate)",
    "Draw, (three repetitions)"
)


def play(board):
    search_end = False
    alpha, beta = [-float("inf"), float("inf")]
    depth = 0
    while not search_end:
        move, result, game_end, game_status = minimax(
            board, depth, alpha, beta)
        search_end = True  # No iterated search for now.
    return move, result, game_end, game_status


def minimax(board, depth, alpha, beta):
    """
    Given a *legal* position in the game-tree, find and evaluate the best move.

    Input:
        board:          Board - the position to play on.
        depth:          int - the depth of the node in the game tree.
        alpha, beta:    float, float - with alpha < beta
                        The window within which result is expected to fall. 
                        'alpha' is the value to maximize and return.
                        Search can be prunned when alpha >= beta.

    Output:
        best_move:      A list [coord1, coord2], or None.
        result:         float - evaluation of the node from the moving side's
                        perspective (+ is good).
        game_end:       Boolen - whether the game was ended in this node.
        game_status:    int
                        Conditions detected:
                        ON_GOING / VICTORY_CROWNING / VICTORY_NO_PIECES_LEFT /
                        DRAW_NO_PRINCES_LEFT / DRAW_STALEMATE

                        Conditions not checked:
                        DRAW_THREE_REPETITIONS
    """

    # Firstly, check for some end conditions:
    #   VICTORY_CROWNING / VICTORY_NO_PIECES_LEFT / DRAW_NO_PRINCES_LEFT
    #   Otherwise, assume ON_GOING
    childs_move, result, game_end, game_status = evaluate(
        board, depth, shallow=True)

    if game_end or depth == MAX_DEPTH:
        # End of game: no move is returned.
        return None, result, game_end, game_status

    else:
        # Generate existing pseudomoves.
        moves, moves_count = generate_pseudomoves(board)
        assert(moves_count > 0),\
            "ERROR: No pseudomoves found despite game is not ended "\
            "and MAX_DEPTH has not been reached."
        # Explore pseudomoves.
        best_move = None
        n_legal_moves_tried = 0
        for piece_moves in moves:  # [[piece_1, [13, 53...]], [piece_2, [...]]
            piece, pseudomoves_list = piece_moves  # piece_1, [13, 53...]
            coord1 = piece.coord
            for coord2 in pseudomoves_list:  # 13
                # Try pseudomove 'i' on board;
                # if it leads to a game end, we can use result_i.
                new_board_i, is_legal_i, result_i, game_end_i, game_status_i =\
                    make_pseudomove(board, coord1, coord2, depth)
                if is_legal_i:
                    # Manage the legal move.
                    n_legal_moves_tried += 1
                    if game_end_i:
                        # The pseudomove led to a final position.
                        # No search required, we know 'result_i'.
                        pass  # TODO: review / kill this code branch?
                    else:
                        # We need to recursively search this move deeper.
                        childs_move, result_i, game_end_i, game_status_i = \
                            minimax(new_board_i, depth + 1, -beta, -alpha)
                        result_i = -float(result_i)  # Switch to player's view.
                    if result_i > alpha:
                        # Update move choice with this better one for player.
                        best_move, alpha = [coord1, coord2], result_i
                    if alpha >= beta:
                        # Interrupt search of rest of pseudomoves.
                        return best_move, alpha, False, ON_GOING

        # Check exploration results.
        if n_legal_moves_tried > 0:
            # A legal best move was found: return results.
            return best_move, alpha, False, ON_GOING
        else:
            # No legal moves were found: check for Prince in check.
            player_side = board.turn
            opponent_side = bd.BLACK if player_side == bd.WHITE else bd.WHITE
            player_prince = board.prince[player_side]
            assert (player_prince is not None),\
                "ERROR: no legal moves found for {} side, which has {} "\
                "pieces but no Prince.".format(
                    bd.color_name[player_side],
                    np.sum(board.piece_count[player_side])
                )
            if position_attacked(board, player_prince.coord, opponent_side):
                # The player is checkmated, its Prince leaves and yields turn.
                best_move = [player_prince.coord, None]
                new_board_i, is_legal_i, result_i, game_end_i, game_status_i =\
                    make_pseudomove(board, player_prince.coord, None, depth)
                # And the new board must be assessed.
                childs_move, result_i, game_end_i, game_status_i = \
                    minimax(new_board_i, depth + 1, -beta, -alpha)
                alpha = -float(result_i)  # Switch to player's view.
                return best_move, alpha, False, ON_GOING
            else:
                # The player is stalemated.
                return None, DRAW, True, DRAW_STALEMATE


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

    Input:
        board:      Board - The game position to generate moves on.

    Output:
        moves:      list of lists - [[piece_1, [13, 53...]], [piece_2, [...]]
        moves_count:integer - the total number of pseudomoves.
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


def make_pseudomove(board, coord1, coord2, depth):
    """
    Given a *legal* position, try to make a pseudomove.
    Detect if the move would be ilegal first.
    If it's legal, detect some end of game conditions:
    - Prince crowning
    - Opponent is left with no pieces

    Input:
        board:      Board - the position to make the move on.
        coord1:     int - initial position of pseudomove.
        coord2:     int - final position of pseudomove,
                    or None for a checkmated Prince leaving.
        depth:      int - node depth before the pseudomove.

    Output:
        new_board:  Board - a new instance on which pseudomove was made.
        is_legal:   Boolean - whether it was a legal move.
        result:     float - an early evaluation of winner moves,
                    from the moving side's perspective (+ is good)
                    estimated as (PLAYER_WINS - depth).
        game_end:   Boolean - whether the pseudomove ends the game.
        game_status:int
                    Conditions checked:
                    ON_GOING / VICTORY_CROWNING / VICTORY_NO_PIECES_LEFT

                    Conditions not checked:
                    DRAW_NO_PRINCES_LEFT / DRAW_STALEMATE /
                    DRAW_THREE_REPETITIONS
    """

    # Register type of moving piece before changes.
    piece_type = board.board1d[coord1].type
    # Create new board on which to try the move.
    new_board = copy.deepcopy(board)
    new_board.make_move(coord1, coord2)  # Turns have switched here!
    depth += 1  # Updated after making the move.

    # Check if it's NOT a legal position.
    if not is_legal(new_board):
        return new_board, False, None, None, None

    # Check if a Prince's crowning.
    if (coord2 == new_board.crown_position) and \
       (piece_type == bd.PRINCE):
        # A Prince was legally moved onto the crown!
        return new_board, True, PLAYER_WINS - depth,\
            True, VICTORY_CROWNING

    # Check if it was the capture of the last piece.
    if new_board.piece_count[new_board.turn].sum() == 0:
        return new_board, True, PLAYER_WINS - depth,\
            True, VICTORY_NO_PIECES_LEFT

    # Otherwise, it was a normal move.
    return new_board, True, None, False, ON_GOING


def evaluate(board, depth, shallow=True):
    """
    Evaluate a position from the playing side's perspective.

    Input:
        board:      Board - The game position to evaluate.
        depth:      int - Depth of node in the search tree.
        shallow:    boolean - Whether quiescence search is needed.

    Output:
        best_move:  A list [coord1, coord2], or None, with child's best move
                    in case a quiecence searh is run.
        result:     float - in the range (OPPONENT_WINS...DRAW...PLAYER_WINS).
                    with PLAYER being the side whose turn it is to move.
                    End positions are estimated as (PLAYER_WINS - depth)
                    or (OPPONENT_WINS + depth) to prefer shorter wins.
        game_end:   Boolean - Whether the game has finished.
        game_status:int
                    Conditions checked:
                    ON_GOING / VICTORY_CROWNING / VICTORY_NO_PIECES_LEFT
                    DRAW_NO_PRINCES_LEFT

                    Conditions not checked:
                    DRAW_STALEMATE /
                    DRAW_THREE_REPETITIONS

    NOTE: multiple return points for efficiency.
    """

    player_side = board.turn
    opponent_side = bd.BLACK if player_side == bd.WHITE else bd.WHITE

    # 1. Prince on the crown_position?
    piece = board.board1d[board.crown_position]
    if piece is not None:
        if piece.type == bd.PRINCE:
            result = PLAYER_WINS - depth if piece.color == player_side \
                else OPPONENT_WINS + depth
            return None, result, True, VICTORY_CROWNING

    # 2. Side without pieces left?
    if board.piece_count[player_side].sum() == 0:
        return None, OPPONENT_WINS + depth, True, VICTORY_NO_PIECES_LEFT
    elif board.piece_count[opponent_side].sum() == 0:
        return None, PLAYER_WINS - depth, True, VICTORY_NO_PIECES_LEFT

    # 3. No Princes left?
    if board.piece_count[player_side][bd.PRINCE] == 0 and \
            board.piece_count[opponent_side][bd.PRINCE] == 0:
        return None, DRAW, True, DRAW_NO_PRINCES_LEFT

    # 4. Stalemate?
    pass  # Note: Would require calculating legal moves everytime.
    # DRAW_STALEMATE

    # 5. Three repetitions?
    pass  # Note: Would require a record of all past positions.
    # DRAW_THREE_REPETITIONS

    # 6. Otherwise, it's not decided yet.
    # Check if a shallow evaluation is enough.
    if shallow:
        # Assume result ≈ DRAW
        return None, DRAW, False, ON_GOING
    else:
        # A quiescence search is needed to try to improve static eval.
        current_result = DRAW  # Node evaluation without quiescence.
        # TODO: include a proper quiescence search below.
        childs_move, quiescence_result = None, -np.Infinity  # Placeholder.
        if quiescence_result > current_result:
            return childs_move, quiescence_result, False, ON_GOING
        else:
            return None, current_result, False, ON_GOING


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
    if board.piece_count[bd.WHITE][bd.PRINCE] > 1 or \
       board.piece_count[bd.BLACK][bd.PRINCE] > 1:
        return False

    # Check now if the moving side could take other side's Prince
    other_prince = board.prince[no_turn]
    if other_prince is not None:
        # Non-playing side has a Prince.
        if position_attacked(board, other_prince.coord, turn):
            # It's in check! -> Ilegal.
            return False

    return True
