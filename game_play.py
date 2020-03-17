import numpy as np
import copy
import sys
import types
import time
from operator import itemgetter

import board as bd
import utils


########################################################################
# Tree search parameters:

PLY1_SEARCH_PARAMS = {
    "max_depth":                1,
    "max_check_quiesc_depth":   4,
    "randomness":               0
}

PLY2_SEARCH_PARAMS = {
    "max_depth":                2,
    "max_check_quiesc_depth":   6,
    "randomness":               0
}

PLY3_SEARCH_PARAMS = {
    "max_depth":                3,
    "max_check_quiesc_depth":   8,
    "randomness":               0
}

PLY4_SEARCH_PARAMS = {
    "max_depth":                4,
    "max_check_quiesc_depth":   10,
    "randomness":               0
}

PLY5_SEARCH_PARAMS = {
    "max_depth":                5,
    "max_check_quiesc_depth":   11,
    "randomness":               0
}

MINIMAL_SEARCH_PARAMS = PLY1_SEARCH_PARAMS
DEFAULT_SEARCH_PARAMS = PLY4_SEARCH_PARAMS

########################################################################
# Evaluation of static positions.

# Material:
piece_weights = np.array([
    [  # From White's point of view (Prince, Soldier, Knight).
        [100, 1, 10],
        [-100, -1, -10]
    ],
    [  # From Black's point of view (Prince, Soldier, Knight).
        [-100, -1, -10],
        [100, 1, 10]
    ]
])

# Pieces mobility:
# max mobility of a Knight = 23 moves, so 2 Knights max = 46 moves.
# 46 moves * 0.1 = 4.6 ≈ 1/2 Knight
KNIGHT_MOVE_VALUE = 0.1

# Other:
# TODO: fine tune mobility vs shortest wins.
STATIC_DEPTH_PENALTY = 0.05  # Subtract to foster faster wins.
END_DEPTH_PENALTY = 1  # Subtract to foster faster wins.

########################################################################
# Possible end-game results
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

# Table used for game-tracing:
DEFAULT_TRACE_LENGTH = 500  # Max depth supported by the program.
HASH = 0            # Index of hash column.
NODE_COUNT = 1      # Index of node_counter column.
IRREVERSIBLE = 2    # Index of flag for board obtained after irreversible move.
N_TRACE_COLS = 3    # Number of columns required for the above data.


class Gametrace:
    def __init__(self, first_board, max_length=DEFAULT_TRACE_LENGTH):
        """
        Initialize array to trace game played so far and currently searched.
        Game played:
            ply = 0 ... self.current_board_ply
        Game searched:
            ply = self.current_board_ply ... DEFAULT_TRACE_LENGTH
        TODO:
        - Update an 'irreversible' boolean for each ply.
          to cut repetition search above plies labelled as "True".
        - Manage overflow beyond DEFAULT_TRACE_LENGTH.
        - Store moves sequence from start to self.current_board_ply.
        """
        # Initialize the tracing array.
        self.level_trace = np.zeros((max_length, N_TRACE_COLS))
        # Initialize internal variables.
        self.current_board_ply = -1  # So that first board gets 0.
        self.max_depth_searched = 0  # Search not started yet.

        # Register first board of the game (assume no repetition).
        _ = self.register_played_board(
            first_board, irreversible=False
        )

    def register_played_board(
        self, board, irreversible=False
    ):
        """
        Register a board that has just been actually played
        (not just searched).

        Input:
            board:          Board - the position to register.
            irreversible:   Boolean - whether this board was produced by a move
                            changing material of any side.

        Output:
            repeated:       Boolean - whether this position had already
                            happenned in the game traced.
        """
        board_hash = board.hash
        # Update variables after search ended (or at start).
        self.current_board_ply += 1
        self.max_depth_searched = 0  # Reset max depth.
        # Update the tracing array at the ply just played.
        self.level_trace[self.current_board_ply, HASH] = board_hash
        self.level_trace[self.current_board_ply, NODE_COUNT] = 0
        self.level_trace[self.current_board_ply, IRREVERSIBLE] = irreversible
        # Zero out the tracing array from current board onwards.
        self.level_trace[self.current_board_ply + 1:, HASH] = 0
        self.level_trace[self.current_board_ply + 1:, NODE_COUNT] = 0
        self.level_trace[self.current_board_ply + 1:, IRREVERSIBLE] = False

        # Check if the board is repeated in past history.
        return self.board_repeated(board_hash, self.current_board_ply)

    def register_searched_board(
        self, board, depth, irreversible=False
    ):
        """
        Register a board position at its given ply_number that
        is being explored during game search.

        Input:
            board:          Board - the position to register.
            depth:          integer - detph of the node in the game search:
                            0 for root node, 1 for its children, etc.                            
            irreversible:   Boolean - whether this board was produced by a move
                            changing material of any side.

        Output:
            repeated:       Boolean - whether this position had already
                            happenned in the game traced.
        """
        board_hash = board.hash
        ply_number = self.current_board_ply + depth  # idx in gral. game trace.
        # Update the tracing array.
        self.level_trace[ply_number, HASH] = board_hash
        self.level_trace[ply_number, NODE_COUNT] += 1
        self.level_trace[ply_number, IRREVERSIBLE] = irreversible

        # Update internal variables.
        self.max_depth_searched = max(
            self.max_depth_searched,
            depth
        )

        # Check if the board is repeated in past history.
        return self.board_repeated(board_hash, ply_number)

    def board_repeated(self, board_hash, board_ply):
        """
        Given a board position at a certain ply in the game tree,
        check if it has already happened in the game traced.

        Algorithm:
        1. plies flagged as 'irreversible' interrupt search with False.
        2. Plies discarded for hash comparison:
          ply - 1 : opponent's move.
          ply - 2 : can't be the same, as the player changed something.
          ply - 3 : opponent's move.
        3. First ply for hash check: ply - 4 (player's move => same_turn)
        """

        # For plies -3 to 0 relative to board:
        # check only 'irrevesible' flags for a fast False.
        min_idx = max(0, board_ply - 3)
        if np.any(self.level_trace[min_idx:board_ply + 1, IRREVERSIBLE]):
            return False

        # Search trace from the 4 plies above to ply 0.
        same_turn = True  # The board 4 plies above was the player's move.
        min_idx = max(0, board_ply - 4)
        for ply in range(min_idx, -1, -1):
            # If turns match, check hash.
            if same_turn and self.level_trace[ply, HASH] == board_hash:
                return True
            # Else, check if previous boards can be skipped.
            if self.level_trace[ply, IRREVERSIBLE]:
                return False
            same_turn = not same_turn  # Flip turns for next node.
        # No match was found.
        return False


def play(
    board, params=DEFAULT_SEARCH_PARAMS, trace=None
):
    search_end = False
    alpha, beta = [-float("inf"), float("inf")]
    depth = 0

    time_0 = time.time()
    while not search_end:
        move, result, game_end, game_status = minimax(
            board, depth, alpha, beta, params, trace)
        search_end = True  # No iterated search for now.
    time_1 = time.time()

    return move, result, game_end, game_status, time_1 - time_0


def minimax(
    board, depth, alpha, beta, params=DEFAULT_SEARCH_PARAMS, trace=None
):
    """
    Given a *legal* position in the game-tree, find and evaluate the best move.

    Input:
        board:          Board - the position to play on.
        depth:          int - the depth of the node in the game tree.
        alpha, beta:    float, float - with alpha < beta
                        The window within which result is expected to fall. 
                        'alpha' is the value to maximize and return.
                        Search is prunned when alpha >= beta.
        params:         A dictionary with the search settings to follow:
                        max_depth, quiescence,randomness, (more to come).
        trace:          The structure tracking played / searched boards.

    Output:
        best_move:      A list [coord1, coord2], or None.
        result:         float - evaluation of the node from the moving side's
                        perspective (+ is good).
        game_end:       Boolen - whether the game was ended in this node.
        game_status:    int - situation of the board passed.
                        Conditions detected:
                        ON_GOING / VICTORY_CROWNING / VICTORY_NO_PIECES_LEFT /
                        DRAW_NO_PRINCES_LEFT / DRAW_STALEMATE /
                        DRAW_THREE_REPETITIONS
    """

    # If at max_depth, quiescence search takes care.
    if depth == params["max_depth"]:
        return quiesce(board, depth, alpha, beta, params, trace)

    # 0. Register searched node, checking repetitions.
    if trace is not None:
        repetition = trace.register_searched_board(board, depth)
        if repetition and depth != 0:
            # The position already happenned in the game [excluding root node].
            return None, DRAW, True, DRAW_THREE_REPETITIONS

    # 1. Check for other end conditions:
    #   VICTORY_CROWNING / VICTORY_NO_PIECES_LEFT / DRAW_NO_PRINCES_LEFT
    #   Otherwise, assume ON_GOING
    childs_move, result, game_end, game_status = evaluate_end(board, depth)
    if game_end:
        # End of game: no move is returned.
        return None, result, game_end, game_status  # TODO: Return beta?

    # 2. Generate and explore existing pseudomoves.
    moves, moves_count = generate_pseudomoves(board)
    assert(moves_count > 0),\
        "ERROR: No pseudomoves found despite game is not ended "\
        "and MAX_DEPTH has not been reached."
    best_move = None
    n_legal_moves_tried = 0
    for piece_moves in moves:  # [[piece_1, [13, 53...]], [piece_2, [...]]
        piece, pseudomoves_list = piece_moves  # piece_1, [13, 53...]
        coord1 = piece.coord
        for coord2 in pseudomoves_list:  # 13
            # Try pseudomove 'i' on board;
            # if it leads to a game end, we can use result_i.
            is_legal_i, is_dynamic_i, \
                result_i, game_end_i, game_status_i, \
                captured_piece, leaving_piece = \
                make_pseudomove(
                    board, coord1, coord2, depth, params
                )
            if is_legal_i:
                # Assess the legal move.
                n_legal_moves_tried += 1
                if game_end_i:
                    # The pseudomove led to a final position.
                    # No search required, we know 'result_i'.
                    pass  # TODO: review / kill this code branch?
                else:
                    # We need to recursively search this move deeper.
                    childs_move, result_i, game_end_i, game_status_i = \
                        minimax(
                            board, depth + 1, -beta, -alpha,
                            params, trace
                        )
                    result_i = -float(result_i)  # Switch to player's view.
                # And 'unmake' the move.
                board.unmake_move(
                    coord1, coord2, captured_piece, leaving_piece)
                if result_i >= beta:
                    # Ignore rest of pseudomoves [fail hard beta cutoff].
                    return [coord1, coord2], beta, False, ON_GOING
                if result_i > alpha:
                    # Update move choice with this better one for player.
                    best_move, alpha = [coord1, coord2], result_i
            else:
                # Simply 'unmake' the illegal move.
                board.unmake_move(
                    coord1, coord2, captured_piece, leaving_piece)

    # Check exploration results.
    if n_legal_moves_tried > 0:
        # A legal best move was found: return results.
        return best_move, alpha, False, ON_GOING

    # 3. No legal moves were found: check for player's Prince check.
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
        coord1, coord2 = player_prince.coord, None  # Prince leaving move.
        best_move = [coord1, coord2]
        is_legal_i, is_dynamic_i, \
            result_i, game_end_i, game_status_i, \
            captured_piece, leaving_piece = \
            make_pseudomove(
                board, coord1, coord2, depth, params
            )
        # And the new board must be assessed.
        childs_move, result_i, game_end_i, game_status_i = \
            minimax(
                board, depth + 1, -beta, -alpha,
                params, trace
            )
        alpha = -float(result_i)  # Switch to player's view.
        # And 'unmake' the move.
        board.unmake_move(
            coord1, coord2, captured_piece, leaving_piece)
        return best_move, alpha, False, ON_GOING

    # The player is stalemated.
    return None, DRAW, True, DRAW_STALEMATE


def quiesce(
    board, depth, alpha, beta,
    params=DEFAULT_SEARCH_PARAMS, trace=None
):
    """
    Evaluate a *legal* position exploring only DYNAMIC moves (or none).
    This is used instead of minimax() once MAX_DEPTH has been reached.

    Input:
        board:          Board - the position to play on.
        depth:          int - the depth of the node in the game tree.
        alpha, beta:    float, float - with alpha < beta
                        The window within which result is expected to fall. 
                        'alpha' is the value to maximize and return.
                        Search is prunned when alpha >= beta.
        params:         A dictionary with the search settings to follow:
                        max_depth, quiescence,randomness, (more to come).
        trace:          The structure tracking played / searched boards.

    Output:
        best_move:      A list [coord1, coord2], or None.
        result:         float - evaluation of the node from the moving side's
                        perspective (+ is good).
        game_end:       Boolen - whether the game was ended in this node.
        game_status:    int - situation of the board passed.
                        Conditions detected:
                        ON_GOING / VICTORY_CROWNING / VICTORY_NO_PIECES_LEFT /
                        DRAW_NO_PRINCES_LEFT / DRAW_STALEMATE /
                        DRAW_THREE_REPETITIONS
    """

    # 0. Register searched node, checking repetitions.
    if trace is not None:
        repetition = trace.register_searched_board(board, depth)
        if repetition:
            # The position had already happenned in the game.
            return None, DRAW, True, DRAW_THREE_REPETITIONS

    # 1. Check for other end conditions:
    #   VICTORY_CROWNING / VICTORY_NO_PIECES_LEFT / DRAW_NO_PRINCES_LEFT
    #   Otherwise, assume ON_GOING
    childs_move, result, game_end, game_status = evaluate_end(board, depth)
    if game_end:
        # End of game: no move is returned.
        return None, result, game_end, game_status  # TODO: Return beta?

    # 2. Null-move: Perform static evaluation if it is legal.
    player_side = board.turn
    opponent_side = bd.BLACK if player_side == bd.WHITE else bd.WHITE

    board.turn = opponent_side  # Flip turns temporarily.
    player_in_check = not is_legal(board)
    board.turn = player_side  # Restablish original turn.

    if not player_in_check:
        # Null move is possible; evaluate it.
        player_in_check = False
        best_move = None
        result_i = evaluate_static(board, depth)
        # Check result of null_move vs alpha-beta window.
        if result_i >= beta:
            return None, beta, False, ON_GOING  # [fail hard beta cutoff]
        if result_i > alpha:
            # Update move choice with this better one for player.
            alpha = result_i

    # 3. Run a recursive quiescence search.
    # 3.1. Generate and explore dynamic pseudomoves.
    moves, moves_count = generate_pseudomoves(board)
    assert(moves_count > 0),\
        "ERROR: No pseudomoves found despite game is not ended."
    best_move = None
    n_legal_moves_tried = 0
    n_legal_moves_found = 0
    for piece_moves in moves:  # [[piece_1, [13, 53...]], [piece_2, [...]]
        piece, pseudomoves_list = piece_moves  # piece_1, [13, 53...]
        coord1 = piece.coord
        for coord2 in pseudomoves_list:  # 13
            # Try pseudomove 'i' on board;
            # if it leads to a game end, we can use result_i.
            is_legal_i, is_dynamic_i, \
                result_i, game_end_i, game_status_i, \
                captured_piece, leaving_piece = \
                make_pseudomove(
                    board, coord1, coord2, depth, params,
                    check_dynamic=True)
            # Check if it's legal.
            if is_legal_i:
                n_legal_moves_found += 1
                # Check if it's a dynamic move or check evasion.
                if is_dynamic_i or player_in_check:
                    # A move worth searching in quiesce().
                    n_legal_moves_tried += 1
                    if game_end_i:
                        # The pseudomove led to a final position.
                        # No search required, we know 'result_i'.
                        pass  # TODO: review / kill this code branch?
                    else:
                        # We need to recursively search this move deeper:
                        childs_move, result_i, game_end_i, game_status_i = \
                            quiesce(
                                board, depth + 1, -beta, -alpha,
                                params, trace
                            )
                        result_i = -float(result_i)  # Switch to player's view.
                    # And 'unmake' the move.
                    board.unmake_move(
                        coord1, coord2, captured_piece, leaving_piece)
                    if result_i >= beta:
                        # Ignore rest of pseudomoves [fail hard beta cutoff].
                        return [coord1, coord2], beta, False, ON_GOING
                    if result_i > alpha:
                        # Update move choice with this better one for player.
                        best_move, alpha = [coord1, coord2], result_i
                else:
                    # Simply 'unmake' the not-searched move.
                    board.unmake_move(
                        coord1, coord2, captured_piece, leaving_piece)
            else:
                # Simply 'unmake' the illegal move.
                board.unmake_move(
                    coord1, coord2, captured_piece, leaving_piece)

    # 3.2. Check exploration results.
    if n_legal_moves_tried > 0:
        # A legal best move was found: return results.
        return best_move, alpha, False, ON_GOING

    # 3.3. No legal moves were played: check for player's Prince check.
    player_prince = board.prince[player_side]
    if player_in_check:
        # The player is checkmated, its Prince leaves and yields turn.
        coord1, coord2 = player_prince.coord, None  # Prince leaving move.
        best_move = [coord1, coord2]
        is_legal_i, result_i, \
            result_i, game_end_i, game_status_i, \
            captured_piece, leaving_piece = \
            make_pseudomove(
                board, coord1, coord2, depth, params,
                check_dynamic=True
            )
        # And the new board must be searched.
        childs_move, result_i, game_end_i, game_status_i = \
            quiesce(
                board, depth + 1, -beta, -alpha,
                params, trace
            )
        alpha = -float(result_i)  # Switch to player's view.
        # And 'unmake' the move.
        board.unmake_move(
            coord1, coord2, captured_piece, leaving_piece)
        return best_move, alpha, False, ON_GOING

    if n_legal_moves_found == 0:
        # The player is stalemated.
        return None, DRAW, True, DRAW_STALEMATE
    else:
        # The player has only non-dynamic moves.
        return None, alpha, False, ON_GOING


def evaluate_static(board, depth):
    """
    Evaluate a static position from playing side's perspective.

    Input:
        board:      Board - The game position to evaluate.
        depth:      int - Depth of node in the search tree.

    Output:
        result:     float - A heuristic evaluation taking into account
                    material and positional features.
    """

    player_side = board.turn
    opponent_side = bd.WHITE if player_side == bd.BLACK else bd.BLACK

    material = np.multiply(board.piece_count, piece_weights[player_side]).sum()
    positional = (
        knights_mobility(board, player_side) -
        knights_mobility(board, opponent_side)
    ) * KNIGHT_MOVE_VALUE
    other = - depth*STATIC_DEPTH_PENALTY

    return material + positional + other


def evaluate_end(board, depth):
    """
    Detect and evaluate clear end positions from playing side's perspective.

    Input:
        board:      Board - The game position to evaluate.
        depth:      int - Depth of node in the search tree.

    Output:
        best_move:  A list [coord1, coord2], or None, with child's best move
                    in case a quiecence searh is run.
        result:     int - OPPONENT_WINS / DRAW / PLAYER_WINS,
                    with PLAYER being the side whose turn it is to move.
                    End positions are estimated as (PLAYER_WINS - depth)
                    or (OPPONENT_WINS + depth) to prefer shorter wins.
        game_end:   Boolean - Whether the game has finished.
        game_status:int
                    Conditions checked:
                    ON_GOING / VICTORY_CROWNING / VICTORY_NO_PIECES_LEFT
                    DRAW_NO_PRINCES_LEFT

                    Conditions not checked:
                    DRAW_STALEMATE
                    [Detected by calling method once moves are generated.]
                    DRAW_THREE_REPETITIONS
                    [Done before by calling method]
    """

    player_side = board.turn
    opponent_side = bd.BLACK if player_side == bd.WHITE else bd.WHITE

    # 1. Prince on the crown_position?
    piece = board.board1d[board.crown_position]
    if piece is not None:
        if piece.type == bd.PRINCE:
            result = PLAYER_WINS - depth*END_DEPTH_PENALTY \
                if piece.color == player_side \
                else OPPONENT_WINS + depth*END_DEPTH_PENALTY
            return None, result, True, VICTORY_CROWNING

    # 2. Side without pieces left?
    if board.piece_count[player_side].sum() == 0:
        return None, OPPONENT_WINS + depth*END_DEPTH_PENALTY, \
               True, VICTORY_NO_PIECES_LEFT
    elif board.piece_count[opponent_side].sum() == 0:
        return None, PLAYER_WINS - depth*END_DEPTH_PENALTY, \
               True, VICTORY_NO_PIECES_LEFT

    # 3. No Princes left?
    if board.piece_count[player_side][bd.PRINCE] == 0 and \
            board.piece_count[opponent_side][bd.PRINCE] == 0:
        return None, DRAW, True, DRAW_NO_PRINCES_LEFT

    # 4. Stalemate.
    # [Detected by calling method once moves are generated.]

    # 5. Three repetitions.
    # [Done before by calling method.]

    # 6. Otherwise, it's not decided yet.
    return None, None, False, ON_GOING


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


def position_attacked_new_UNFINISHED(board, pos, attacking_side):

    position_lists = bd.knight_moves[pos]
    board_slices = itemgetter(*position_lists)(board.board1d)
    # TODO: Pending next steps...


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


def knights_mobility(board, color):
    """
    Count non-legally checked moves for ALL Knights of a given color.

    Input:
        board:      Board - The game position to generate moves on.
        color:      int - the side of the piece

    Output:
        moves_count:integer - the total number of pseudomoves.
    """
    # Obtain list of Knights for player with the 'color'.
    knight_list = [p for p in board.pieces[color] if p.type == bd.KNIGHT]
    moves_count = 0

    # Loop over all Knights.
    for knight in knight_list:
        # Obtain list with lists of moves.
        p_moves = bd.piece_moves[bd.KNIGHT][color][knight.coord]
        # List of moves lists: [[1, 2...], [13, 15...]]
        moves = set()  # A set with the moves to find for this 'piece'.
        for moves_list in p_moves:  # [1, 2, 3, 4,...]
            # Get the closest piece in that direction and its distance.
            pieces = board.board1d[moves_list]  # [None, None, piece_1,...]
            try:
                piece_pos = np.where(pieces)[0][0]  # 2
                closest_piece = pieces[piece_pos]  # piece_1
                if closest_piece.color == color:
                    # Add moves till closest_piece [EXCLUDING it].
                    moves = moves.union(moves_list[:piece_pos])
                else:
                    # Add moves till closest_piece [INCLUDING it].
                    moves = moves.union(moves_list[:piece_pos + 1])
            except IndexError:
                # No pieces in that direction: add all moves.
                moves = moves.union(moves_list)
        moves_count += len(moves)

    return moves_count


def count_knight_pseudomoves(board, position, color):
    """
    Count non-legally checked moves for a Knight of a given color
    from a position.

    Input:
        board:      Board - The game position to generate moves on.
        position:   int - The 1D coordinate.
        color:      int - the side of the piece

    Output:
        moves_count:integer - the total number of pseudomoves.
    """
    # Obtain list with lists of moves
    p_moves = bd.piece_moves[bd.KNIGHT][color][position]
    # List of moves lists: [[1, 2...], [13, 15...]]
    moves = set()  # A set with the moves to find for this 'piece'.
    for moves_list in p_moves:  # [1, 2, 3, 4,...]
        # Get the closest piece in that direction and its distance.
        pieces = board.board1d[moves_list]  # [None, None, piece_1,...]
        try:
            piece_pos = np.where(pieces)[0][0]  # 2
            closest_piece = pieces[piece_pos]  # piece_1
            if closest_piece.color == color:
                # Add moves till closest_piece [EXCLUDING it].
                moves = moves.union(moves_list[:piece_pos])
            else:
                # Add moves till closest_piece [INCLUDING it].
                moves = moves.union(moves_list[:piece_pos + 1])
        except IndexError:
            # No pieces in that direction: add all moves.
            moves = moves.union(moves_list)

    return len(moves)


def make_pseudomove_OLD(board, coord1, coord2, depth, params, check_dynamic=False):
    """
    Given a *legal* position, try to make a pseudomove.
    Detect if the move would be ilegal first.
    If it's legal, detect some end of game conditions:
    - Prince crowning
    - Opponent is left with no pieces
    If required, detect if it's a dynamic move.

    Input:
        board:          Board - the position to make the move on.
        coord1:         int - initial position of pseudomove.
        coord2:         int - final position of pseudomove,
                        or None for a checkmated Prince leaving.
        depth:          int - node depth before the pseudomove.
        params:         A dictionary with the search settings to follow.
        check_dynamic:  Boolean - whether dynamism of move must be
                        assessed.

    Output:
        new_board:  Board - a new instance on which pseudomove was made.
        is_legal:   Boolean - whether it was a legal move.
        is_dynamic: Boolean - whether it was a dynamic move.
                    Conditions checked:
                    - Piece captures
                    - Checkmated Prince leaves
                    - Prince Crowning
                    - Soldier promotions
                    - Check evasion (no null move)
                    - Checks [downto 'max_check_quiesc_depth']

                    Conditions not checked:  TODO: check in some cases.
                    - Prince moves upwards (in absence of enemy Knights)?
                    - Soldier moves to throne (in absence of Prince)?

        result:     float - an early evaluation of winner moves,
                    from the moving side's perspective (+ is good)
                    estimated as (PLAYER_WINS - depth),
                    ONLY in these conditions:
                    VICTORY_CROWNING / VICTORY_NO_PIECES_LEFT
        game_end:   Boolean - whether the pseudomove ends the game.
        game_status:int
                    Conditions checked:
                    ON_GOING / VICTORY_CROWNING / VICTORY_NO_PIECES_LEFT

                    Conditions not checked:
                    DRAW_NO_PRINCES_LEFT / DRAW_STALEMATE /
                    DRAW_THREE_REPETITIONS
    """

    if check_dynamic:
        # Initialize vars. for later dynamism check before board changes.
        moving_side = board.turn
        opponent_side = bd.WHITE if moving_side == bd.BLACK else bd.BLACK
        player_prince = board.prince[moving_side]
        if player_prince is not None:
            player_in_check = position_attacked(
                board, player_prince.coord, opponent_side
            )
        else:
            player_in_check = False

    # Register type of moving piece before changes.
    piece_type = board.board1d[coord1].type
    # Create new board on which to try the move, getting pieces removed.
    new_board = copy.deepcopy(board)
    captured_piece, leaving_piece = \
        new_board.make_move(coord1, coord2)  # Turns have switched here!
    depth += 1  # Updated after making the move.

    # Check if the move produced an illegal position.
    if not is_legal(new_board):
        return new_board, False, None, None, None, None

    # Check if a Prince is crowning.
    if (coord2 == new_board.crown_position) and \
       (piece_type == bd.PRINCE):
        # A Prince was legally moved onto the crown!
        return new_board, True, True, PLAYER_WINS - depth*END_DEPTH_PENALTY,\
            True, VICTORY_CROWNING

    # Check if it was the capture of the last piece.
    if new_board.piece_count[new_board.turn].sum() == 0:
        return new_board, True, True, PLAYER_WINS - depth*END_DEPTH_PENALTY,\
            True, VICTORY_NO_PIECES_LEFT

    # Optionally, check dynamic conditions of the move.
    is_dynamic = False
    if check_dynamic:
        # Checked: Piece captures, mated Prince leaves, Soldier promotion,
        # Check, Check evasion.
        # NOT checked:  Prince -> up, Soldier -> throne
        if captured_piece is not None or leaving_piece is not None:
            # Piece captured / mated Prince leaving / Soldier promotion.
            is_dynamic = True
        else:
            # Check on 'new_board' if it produced a check to the opponent.
            opponent_prince = new_board.prince[new_board.turn]
            if opponent_prince is not None and \
               not depth > params["max_check_quiesc_depth"]:
                is_dynamic = position_attacked(
                    new_board, opponent_prince.coord, moving_side
                )
            if not is_dynamic and player_in_check:
                # Check if the move produced a check evasion.
                is_dynamic = not position_attacked(
                    new_board, player_prince.coord, moving_side
                )

    # Report as a legal move, the dynamism of the move and other conditions.
    return new_board, True, is_dynamic, None, False, ON_GOING


def make_pseudomove(board, coord1, coord2, depth, params, check_dynamic=False):
    """
    Given a *legal* position, try to make a pseudomove.
    Detect if the move would be ilegal first.
    If it's legal, detect some end of game conditions:
    - Prince crowning
    - Opponent is left with no pieces
    If required, detect if it's a dynamic move.

    Input:
        board:          Board - the position to make the move on.
        coord1:         int - initial position of pseudomove.
        coord2:         int - final position of pseudomove,
                        or None for a checkmated Prince leaving.
        depth:          int - node depth before the pseudomove.
        params:         A dictionary with the search settings to follow.
        check_dynamic:  Boolean - whether dynamism of move must be
                        assessed.

    Output:
        is_legal:   Boolean - whether it was a legal move.
        is_dynamic: Boolean - whether it was a dynamic move.
                    Conditions checked:
                    - Piece captures
                    - Checkmated Prince leaves
                    - Prince Crowning
                    - Soldier promotions
                    - Check evasion (no null move)
                    - Checks [downto 'max_check_quiesc_depth']

                    Conditions not checked:  TODO: check in some cases.
                    - Prince moves upwards (in absence of enemy Knights)?
                    - Soldier moves to throne (in absence of Prince)?

        result:     float - an early evaluation of winner moves,
                    from the moving side's perspective (+ is good)
                    estimated as (PLAYER_WINS - depth),
                    ONLY in these conditions:
                    VICTORY_CROWNING / VICTORY_NO_PIECES_LEFT
        game_end:   Boolean - whether the pseudomove ends the game.
        game_status:int
                    Conditions checked:
                    ON_GOING / VICTORY_CROWNING / VICTORY_NO_PIECES_LEFT

                    Conditions not checked:
                    DRAW_NO_PRINCES_LEFT / DRAW_STALEMATE /
                    DRAW_THREE_REPETITIONS

        captured_piece: Piece - Opponent's piece captured at coord2
                        (or None).
        leaving_piece:  Piece - Playing piece that left the board,
                        (or None):
                        a) Prince checkmated.
                        b) Soldier promoted to Prince.
    """

    if check_dynamic:
        # Initialize vars. for later dynamism check before board changes.
        moving_side = board.turn
        opponent_side = bd.WHITE if moving_side == bd.BLACK else bd.BLACK
        player_prince = board.prince[moving_side]
        if player_prince is not None:
            player_in_check = position_attacked(
                board, player_prince.coord, opponent_side
            )
        else:
            player_in_check = False

    # Register type of moving piece before changes.
    piece_type = board.board1d[coord1].type

    # And now, make the move.
    captured_piece, leaving_piece = board.make_move(coord1, coord2)
    depth += 1

    # Check if the move produced an illegal position.
    if not is_legal(board):
        return False, None, None, None, None, captured_piece, leaving_piece

    # Check if a Prince is crowning.
    if (coord2 == board.crown_position) and \
       (piece_type == bd.PRINCE):
        # A Prince was legally moved onto the crown!
        return True, True, PLAYER_WINS - depth*END_DEPTH_PENALTY,\
            True, VICTORY_CROWNING, captured_piece, leaving_piece

    # Check if it was the capture of the last piece.
    if board.piece_count[board.turn].sum() == 0:
        return True, True, PLAYER_WINS - depth*END_DEPTH_PENALTY,\
            True, VICTORY_NO_PIECES_LEFT, captured_piece, leaving_piece

    # Optionally, check dynamic conditions of the move.
    is_dynamic = False
    if check_dynamic:
        # Checked: Piece captures, mated Prince leaves, Soldier promotion,
        # check, check evasion.
        # NOT checked:  Prince -> up, Soldier -> throne
        if captured_piece is not None or leaving_piece is not None:
            # Piece captured / mated Prince leaving / Soldier promotion.
            is_dynamic = True
        else:
            # Check on 'board' if it produced a check to the opponent.
            opponent_prince = board.prince[board.turn]
            if opponent_prince is not None and \
               not depth > params["max_check_quiesc_depth"]:
                is_dynamic = position_attacked(
                    board, opponent_prince.coord, moving_side
                )
            if not is_dynamic and player_in_check:
                # Check if the move produced a check evasion.
                is_dynamic = not position_attacked(
                    board, player_prince.coord, moving_side
                )

    # Report as a legal move, the dynamism of the move and other conditions.
    return True, is_dynamic, None, False, ON_GOING, \
        captured_piece, leaving_piece


def is_legal(board):
    """
    Detect if a given position is legal.
    Ilegal cases checked:
    a) More than one Prince on either side.
    b) The moving side could take other side's Prince.
    NO CHECK ON: number of other pieces on board (must check at load time).
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
            # It's in check! -> Illegal.
            return False

    return True


def is_legal_move(board, move):
    """
    Detect if a move for a given (legal) position is legal.
    Cases checked:
    - The move is at least a pseudo_move.
    - The move is legal.

    Input:
        board:      Board - the position on which to move.
        move:       int, int/None - the coordinates of the move.

    Output:
        result:     Boolean - whether it's a legal move.
        explanation:string - the error cause, or "".
    """
    coord1, coord2 = move  # The coordinates of the move.
    moving_piece = board.board1d[coord1]  # The moving piece.

    # Identify moving_piece.
    if moving_piece is None:
        return False, "Error: No piece found at {}.".format(
            utils.coord_2_algebraic[coord1])

    # First, obtain pseudomoves for moving side, a list of lists:
    # [[piece_1, [13, 53...]], [piece_2, [...]]
    pseudo_moves, _ = generate_pseudomoves(board)
    # Loop over all pseudomoves found to:
    # 1. try to spot the one given.
    # 2. know if the player has any legal move.
    n_legal_pseudo_moves = 0
    for pm_list in pseudo_moves:  # [piece_1, [13, 53...]]
        pm_coord1 = pm_list[0].coord
        # Loop over all moves of the pm_list.
        for pm_coord2 in pm_list[1]:  # [13, 53...]
            # Check if the pm is legal by trying it [use default parameters].
            pseudo_move_legal, _, _, _, _, \
                captured_piece, leaving_piece = make_pseudomove(
                    board, pm_coord1, pm_coord2,
                    depth=0, params=MINIMAL_SEARCH_PARAMS, check_dynamic=False
                )
            # And now, 'unmake' the move:
            board.unmake_move(coord1, coord2, captured_piece, leaving_piece)
            # Check results:
            if pseudo_move_legal:
                # The player has some legal moves.
                n_legal_pseudo_moves += 1
            if pm_list[0] == moving_piece and pm_coord2 == coord2:
                # The move was found, return its legal value.
                if pseudo_move_legal:
                    return True, ""
                else:
                    return False, "Error: {}{} is an illegal move.".format(
                        utils.coord_2_algebraic[coord1],
                        utils.coord_2_algebraic[coord2]
                    )

    # Move not found in the pseudo_moves list; is it a mated Prince leave?
    if (moving_piece.type == bd.PRINCE and
            moving_piece.color == board.turn and
            coord2 is None and
            n_legal_pseudo_moves == 0):
        # It's a legal Prince leave.
        return True, ""
    else:
        # It's an incorrect move.
        return False, \
            "Error: wrong move from {} to {}.".format(
                utils.coord_2_algebraic[coord1],
                utils.coord_2_algebraic[coord2]
            )


if __name__ == '__main__':
    # Main program.
    if len(sys.argv) > 0:
        file_name = sys.argv[1]
        board = bd.Board(file_name)
        game_trace = Gametrace(board)
        parameters = PLY3_SEARCH_PARAMS

        print("\nPlaying position: {}".format(file_name))
        board.print_char()

        # Call  play().
        best_move, result, game_end, game_status, time_used = play(
            board, params=parameters, trace=game_trace)

        # Display results.
        utils.display_results(
            best_move, result, game_end, game_status
        )
