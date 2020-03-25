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
    "transposition_table":      True,
    "randomness":               0
}

PLY2_SEARCH_PARAMS = {
    "max_depth":                2,
    "max_check_quiesc_depth":   6,
    "transposition_table":      True,
    "randomness":               0
}

PLY3_SEARCH_PARAMS = {
    "max_depth":                3,
    "max_check_quiesc_depth":   8,
    "transposition_table":      True,
    "randomness":               0
}

PLY4_SEARCH_PARAMS = {
    "max_depth":                4,
    "max_check_quiesc_depth":   10,
    "transposition_table":      True,
    "randomness":               0
}

PLY5_SEARCH_PARAMS = {
    "max_depth":                5,
    "max_check_quiesc_depth":   11,
    "transposition_table":      True,
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
HASH_COL = 0            # Index of hash column.
NODE_COUNT_COL = 1      # Index of node_counter column.
IRREVERSIBLE_COL = 2    # Index of flag for board obtained after irreversible move.
N_TRACE_COLS = 3    # Number of columns required for the above data.

# Hash table used for transpositions.
HASH_SIZE_MIN = 13
HASH_SIZE_1 = 65537
HASH_SIZE_2 = 131071
HASH_SIZE_3 = 262147
HASH_SIZE_4 = 524287
HASH_SIZE_5 = 1048573

DEFAULT_HASH_SIZE = HASH_SIZE_5  # Max. size of the hash table.

TT_HASH_IDX = 0    # The full hash value of the position.
TT_DEPTH_IDX = 1   # The depth at which the position was explored.
TT_VALUE_IDX = 2   # The value found for the position.
TT_FLAG_IDX = 3    # The type of value (EXACT / LOWERBOUND / UPPERBOUND).
TT_MOVE_IDX = 4    # The best move found in the position.

EXACT = 0
LOWER_BOUND = 1
UPPER_BOUND = 2


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
        self.level_trace[self.current_board_ply, HASH_COL] = board_hash
        self.level_trace[self.current_board_ply, NODE_COUNT_COL] = 0
        self.level_trace[self.current_board_ply, IRREVERSIBLE_COL] = irreversible
        # Zero out the tracing array from current board onwards.
        self.level_trace[self.current_board_ply + 1:, HASH_COL] = 0
        self.level_trace[self.current_board_ply + 1:, NODE_COUNT_COL] = 0
        self.level_trace[self.current_board_ply + 1:, IRREVERSIBLE_COL] = False

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
        self.level_trace[ply_number, HASH_COL] = board_hash
        self.level_trace[ply_number, NODE_COUNT_COL] += 1
        self.level_trace[ply_number, IRREVERSIBLE_COL] = irreversible

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
        if np.any(self.level_trace[min_idx:board_ply + 1, IRREVERSIBLE_COL]):
            return False

        # Search trace from the 4 plies above to ply 0.
        same_turn = True  # The board 4 plies above was the player's move.
        min_idx = max(0, board_ply - 4)
        for ply in range(min_idx, -1, -1):
            # If turns match, check hash.
            if same_turn and self.level_trace[ply, HASH_COL] == board_hash:
                return True
            # Else, check if previous boards can be skipped.
            if self.level_trace[ply, IRREVERSIBLE_COL]:
                return False
            same_turn = not same_turn  # Flip turns for next node.
        # No match was found.
        return False


class Transposition_table:
    """
    Implements a hash-table of some limited size storing information about
    board positions, identified by some key.

    Board information is stored as a list:
    - The full hash value of the position (in case it's cut to table's length).
    - The depth at which the position was explored.
    - The value found for the position.
    - The type of value (EXACT / LOWERBOUND / UPPERBOUND).
    - The best move found in the position.

    Assumptions:
        The key provided identifies uniquely a board position.
        Python 3.7: Dictionary order is guaranteed to be insertion order. 
    """
    def __init__(self, size=DEFAULT_HASH_SIZE):
        # Data:
        self.size = size
        self.table = {}
        # Metrics:
        self.hits = 0
        self.collisions = 0
        self.updates = 0

    def insert(self, key, value):
        current_value = self.table.get(key, None)
        if current_value is None:
            # Empty position: use it.
            self.table[key] = value
            # If max. size exceeded, pop oldest entry.
            if len(self.table) > self.size:
                self.table.pop(next(iter(self.table)))
        else:
            # Collision or update: resolve by depth (root node has depth 0).
            self.updates += 1
            if value[TT_DEPTH_IDX] < current_value[TT_DEPTH_IDX]:
                # The new value was more deeply explored: replace.
                self.table[key] = value

    def retrieve(self, key):
        current_value = self.table.get(key, None)
        if current_value is not None and current_value[TT_HASH_IDX] == key:
            # Successful retrieval.
            self.hits += 1
            return current_value
        else:
            # Value not found.
            return None

    def metrics(self):
        return (
            self.size, len(self.table), self.hits, self.collisions,
            self.updates
            )

    def clear(self):
        self.table.clear()
        self.hits = 0
        self.collisions = 0
        self.updates = 0


def update_transp_table(
    t_table, board, depth, value, alpha_orig, beta, move
):
    # Determine flag for the value.
    if value <= alpha_orig:
        flag = UPPER_BOUND
    elif value >= beta:
        flag = LOWER_BOUND
    else:
        flag = EXACT
    # Update transposition table.
    t_table.insert(
        board.hash, (board.hash, depth, value, flag, move)
    )


def play(
    board, params=DEFAULT_SEARCH_PARAMS, trace=None
):
    search_end = False
    alpha, beta = [-float("inf"), float("inf")]
    depth = 0

    while not search_end:
        time_0 = time.time()
        # Initiate move selection.
        t_table = Transposition_table() \
            if params["transposition_table"] else None
        move, result, game_end, game_status = negamax(
            board, depth, alpha, beta, params, t_table, trace)
        t_table_metrics = t_table.metrics()
        t_table.clear()
        # End of move selection.
        time_1 = time.time()
        search_end = True  # No iterative deepening for now.

    return move, result, game_end, game_status, \
        time_1 - time_0, t_table_metrics


def negamax(
    board, depth, alpha, beta, params=DEFAULT_SEARCH_PARAMS,
    t_table=None, trace=None
):
    """
    Given a *legal* position in the game-tree, find and evaluate the best move.
    Algorithm: negamax alpha-beta, fail-hard (value within [alpha, beta]).

    Input:
        board:          Board - the position to play on.
        depth:          int - the depth of the node in the game tree.
        alpha, beta:    float, float - with alpha < beta
                        The window within which result is expected to fall. 
                        'alpha' is the value to maximize and return.
                        Search is prunned when alpha >= beta.
        params:         A dictionary with the search settings to follow:
                        max_depth, quiescence,randomness, (more to come).
        t_table:        The transposition table storing previously explored
                        boards.
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

    # 0. If at max_depth, quiescence search takes care.
    if depth == params["max_depth"]:
        return quiesce(board, depth, alpha, beta, params, t_table, trace)

    # 1. Register searched node, checking repetitions.
    if trace is not None:
        repetition = trace.register_searched_board(board, depth)
        if repetition and depth != 0:
            # The position already happenned in the game [excluding root node].
            return None, DRAW, True, DRAW_THREE_REPETITIONS

    # 2. Check in transposition table.
    alpha_orig = alpha
    value = t_table.retrieve(board.hash)
    hash_move = None
    if value is not None:
        # Position found with enough depth; check value and flags.
        if value[TT_DEPTH_IDX] <= depth:
            if value[TT_FLAG_IDX] == EXACT:
                return value[TT_MOVE_IDX], value[TT_VALUE_IDX], False, ON_GOING
            elif value[TT_FLAG_IDX] == LOWER_BOUND:
                alpha = max(alpha, value[TT_VALUE_IDX])
            elif value[TT_FLAG_IDX] == UPPER_BOUND:
                beta = min(beta, value[TT_VALUE_IDX])
        # Check for alpha-beta cutoff.
        if alpha >= beta:
            return value[TT_MOVE_IDX], value[TT_VALUE_IDX], False, ON_GOING
        # Capture possibly registered move.
        hash_move = value[TT_MOVE_IDX]

    # 3. Check for other end conditions:
    #   VICTORY_CROWNING / VICTORY_NO_PIECES_LEFT / DRAW_NO_PRINCES_LEFT
    childs_move, result, game_end, game_status = evaluate_end(board, depth)
    if game_end:
        # End of game: no move is returned.
        return None, result, game_end, game_status  # TODO: Return beta?

    # 4. Generate and explore existing pseudomoves.
    moves, moves_count = generate_pseudomoves(board)
    assert(moves_count > 0),\
        "ERROR: No pseudomoves found despite game is not ended "\
        "and MAX_DEPTH has not been reached."
    best_move = None
    best_result = -np.Infinity  # Value to store in transposition table.
    n_legal_moves_tried = 0
    for pseudo_move in moves:  # [[24, 14], [24, 13]...]], [2, 3]...]
        coord1, coord2 = pseudo_move  # [24, 14]
        # Try pseudomove 'i' on board;
        # if it leads to a game end, we can use result_i.
        is_legal_i, is_dynamic_i, \
            result_i, game_end_i, game_status_i, \
            captured_piece, leaving_piece = \
            make_pseudomove(
                board, coord1, coord2, depth, params
            )
        # Check if it's legal.
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
                    negamax(
                        board, depth + 1, -beta, -alpha,
                        params, t_table, trace
                    )
                result_i = -float(result_i)  # Switch to player's view.
            if result_i > best_result:
                best_move = [coord1, coord2]
                best_result = result_i
            # And 'unmake' the move.
            board.unmake_move(
                coord1, coord2, captured_piece, leaving_piece)
            if result_i >= beta:
                # Ignore rest of pseudomoves [fail-hard beta cutoff].
                # Update transposition table with best result found.
                update_transp_table(
                    t_table, board, depth, result_i, alpha_orig, beta,
                    [coord1, coord2]
                )
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
        # A legal best move was found.
        # Update transposition table with best result found.
        update_transp_table(
            t_table, board, depth, best_result, alpha_orig, beta,
            best_move
        )
        # Return results [fail-hard alpha cutoff].
        return best_move, alpha, False, ON_GOING

    # 5. No legal moves were found: check for player's Prince check.
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
        # The player is CHECKMATED, its Prince leaves and yields turn.
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
            negamax(
                board, depth + 1, -beta, -alpha,
                params, t_table, trace
            )
        best_result = -float(result_i)  # Switch to player's view.
        # And 'unmake' the move.
        board.unmake_move(
            coord1, coord2, captured_piece, leaving_piece)
        # Update transposition table with best result found.
        update_transp_table(
            t_table, board, depth, best_result, alpha_orig, beta,
            [coord1, coord2]
        )
        # Return results.
        return best_move, best_result, False, ON_GOING

    # 6. The player is STALEMATED.
    return None, DRAW, True, DRAW_STALEMATE


def quiesce(
    board, depth, alpha, beta, params=DEFAULT_SEARCH_PARAMS,
    t_table=None, trace=None
):
    """
    Evaluate a *legal* position exploring only DYNAMIC moves (or none).
    This is used instead of negamax() once MAX_DEPTH has been reached.

    Input:
        board:          Board - the position to play on.
        depth:          int - the depth of the node in the game tree.
        alpha, beta:    float, float - with alpha < beta
                        The window within which result is expected to fall. 
                        'alpha' is the value to maximize and return.
                        Search is prunned when alpha >= beta.
        params:         A dictionary with the search settings to follow:
                        max_depth, quiescence,randomness, (more to come).
        t_table:        The transposition table storing previously explored
                        boards.
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

    # 1. Register searched node, checking repetitions.
    if trace is not None:
        repetition = trace.register_searched_board(board, depth)
        if repetition:
            # The position had already happenned in the game.
            return None, DRAW, True, DRAW_THREE_REPETITIONS

    # 2. Check in transposition table.
    alpha_orig = alpha
    value = t_table.retrieve(board.hash)
    if value is not None:
        # Position found with enough depth; check value and flags.
        if value[TT_DEPTH_IDX] <= depth:
            if value[TT_FLAG_IDX] == EXACT:
                return value[TT_MOVE_IDX], value[TT_VALUE_IDX], False, ON_GOING
            elif value[TT_FLAG_IDX] == LOWER_BOUND:
                alpha = max(alpha, value[TT_VALUE_IDX])
            elif value[TT_FLAG_IDX] == UPPER_BOUND:
                beta = min(beta, value[TT_VALUE_IDX])
        # Check for alpha-beta cutoff.
        if alpha >= beta:
            return value[TT_MOVE_IDX], value[TT_VALUE_IDX], False, ON_GOING

    # 3. Check for other end conditions:
    #   VICTORY_CROWNING / VICTORY_NO_PIECES_LEFT / DRAW_NO_PRINCES_LEFT
    childs_move, result, game_end, game_status = evaluate_end(board, depth)
    if game_end:
        # End of game: no move is returned.
        return None, result, game_end, game_status  # TODO: Return beta?

    # 4.1. Null-move: Perform static evaluation if it is legal.
    player_side = board.turn

    board.flip_turn()  # Flip turns temporarily.
    player_in_check = not is_legal(board)
    board.flip_turn()  # Restablish original turn.

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

    # 4.2. Generate and explore dynamic pseudomoves.
    moves, moves_count = generate_pseudomoves(board)
    assert(moves_count > 0),\
        "ERROR: No pseudomoves found despite game is not ended."
    best_move = None
    best_result = -np.Infinity  # Value to store in transposition table.
    n_legal_moves_tried = 0
    n_legal_moves_found = 0
    for pseudo_move in moves:  # [[24, 14], [24, 13]...]], [2, 3]...]
        coord1, coord2 = pseudo_move  # [24, 14]
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
                            params, t_table, trace
                        )
                    result_i = -float(result_i)  # Switch to player's view.
                if result_i > best_result:
                    best_move = [coord1, coord2]
                    best_result = result_i
                # And 'unmake' the move.
                board.unmake_move(
                    coord1, coord2, captured_piece, leaving_piece)
                if result_i >= beta:
                    # Ignore rest of pseudomoves [fail hard beta cutoff].
                    # Update transposition table with best result found.
                    update_transp_table(
                        t_table, board, depth, result_i, alpha_orig, beta,
                        [coord1, coord2]
                    )
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

    # Check exploration results.
    if n_legal_moves_tried > 0:
        # A legal best move was found.
        # Update transposition table with best result found.
        update_transp_table(
            t_table, board, depth, best_result, alpha_orig, beta,
            best_move
        )
        # Return results [fail-hard alpha cutoff].
        return best_move, alpha, False, ON_GOING

    # 5. No legal moves were played: check for player's Prince check.
    player_prince = board.prince[player_side]
    if player_in_check:
        # The player is CHECKMATED, its Prince leaves and yields turn.
        coord1, coord2 = player_prince.coord, None  # Prince leaving move.
        best_move = [coord1, coord2]
        is_legal_i, is_dynamic_i, \
            result_i, game_end_i, game_status_i, \
            captured_piece, leaving_piece = \
            make_pseudomove(
                board, coord1, coord2, depth, params
            )
        # And the new board must be searched.
        childs_move, result_i, game_end_i, game_status_i = \
            quiesce(
                board, depth + 1, -beta, -alpha,
                params, t_table, trace
            )
        best_result = -float(result_i)  # Switch to player's view.
        # And 'unmake' the move.
        board.unmake_move(
            coord1, coord2, captured_piece, leaving_piece)
        # Update transposition table with best result found.
        update_transp_table(
            t_table, board, depth, best_result, alpha_orig, beta,
            [coord1, coord2]
        )
        # Return results.
        return best_move, best_result, False, ON_GOING

    if n_legal_moves_found == 0:
        # 6. The player is STALEMATED.
        return None, DRAW, True, DRAW_STALEMATE
    else:
        # 4.3 [unexplored by 4.2] The player has only non-dynamic moves.
        update_transp_table(
            t_table, board, depth, alpha, alpha_orig, beta, None
        )
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


def generate_pseudomoves_OLD(board):
    """
    Generate a list of non-legally checked moves for the playing side.

    Input:
        board:      Board - The game position to generate moves on.

    Output:
        moves:      list of lists - [[24, [14, 13...]], [44, [...]]
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
        moves.append((piece.coord, list(new_moves)))
        moves_count += len(new_moves)

    return moves, moves_count


def generate_pseudomoves(board):
    """
    Generate a list of (non-legally checked) moves for
    the playing side.

    Input:
        board:      Board - The game position to generate moves on.

    Output:
        moves:      list of pairs of ['from', 'to'] int values,
                    each being the two integer coordinates of a move.
                    E. g. [[24, 14], [24, 13]...]], [2, 3]...]
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
                        # Add moves till closest_piece [EXcluding it].
                        new_moves = new_moves.union(moves_list[:piece_pos])
                    else:
                        # Add moves till closest_piece [INcluding it].
                        new_moves = new_moves.union(moves_list[:piece_pos + 1])
                except IndexError:
                    # No pieces in that direction: add all moves.
                    new_moves = new_moves.union(moves_list)
            new_moves = list(new_moves)
        else:
            # List of moves (P, or S out of kingdom): [1, 2, 3...]
            new_moves = [p for p in p_moves if board.board1d[p] is None
                         or board.board1d[p].color != piece.color]

        # Update main list.
        piece_moves_list = [[piece.coord, x] for x in new_moves]
        moves += piece_moves_list
        moves_count += len(piece_moves_list)

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

    # Identify moving_piece.
    moving_piece = board.board1d[coord1]  # The moving piece.
    if moving_piece is None:
        return False, "Error: No piece found at {}.".format(
            utils.coord_2_algebraic[coord1])

    # Obtain pseudomoves for moving side, a list of lists:
    # [[24, 14], [24, 13]...]], [2, 3]...]
    pseudo_moves, _ = generate_pseudomoves(board)

    # Check for move in pseudo_moves.
    if move in pseudo_moves:
        # The move is at least a pseudo-move.
        # Check if the pm is legal by trying it [use default parameters].
        pseudo_move_legal, _, _, _, _, \
            captured_piece, leaving_piece = make_pseudomove(
                board, coord1, coord2,
                depth=0, params=MINIMAL_SEARCH_PARAMS, check_dynamic=False
            )
        # And now, 'unmake' the move:
        board.unmake_move(coord1, coord2, captured_piece, leaving_piece)
        # Check results:
        if pseudo_move_legal:
            return True, ""
        else:
            return False, "Error: {}{} is an illegal move.".format(
                utils.coord_2_algebraic[coord1],
                utils.coord_2_algebraic[coord2]
            )
    else:
        # Move not found in pseudo-moves list.
        # Check if it's a leaving check-mated Prince.
        opponent_side = bd.WHITE if board.turn == bd.BLACK else bd.BLACK
        if moving_piece.type == bd.PRINCE and \
                moving_piece.color == board.turn and \
                coord2 is None and \
                position_attacked(board, coord1, opponent_side):
            # It's a Prince in check leaving the Board. Really mated?
            # Loop over all player's moves to confirm it's a mate
            for move_coords in pseudo_moves:
                pseudo_move_legal, _, _, _, _, \
                    captured_piece, leaving_piece = make_pseudomove(
                        board, move_coords[0], move_coords[1],
                        depth=0, params=MINIMAL_SEARCH_PARAMS, check_dynamic=False
                    )
                # And now, 'unmake' the move:
                board.unmake_move(
                    coord1, coord2, captured_piece, leaving_piece)
                if pseudo_move_legal:
                    # The player has some legal moves.
                    return False, "Error: Prince at {} " \
                        "is not checkmated.".format(
                            utils.coord_2_algebraic[coord1]
                        )
            # No legal pseudomove found: legal leave.
            return True, ""
        else:
            # Not a pseudomove or a leaving mated Prince.
            return False, "Error: {}{} is an illegal move.".format(
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
        best_move, result, game_end, game_status, \
            time_used, t_table_metrics = play(
                board, params=parameters, trace=game_trace
                )

        # Display results.
        utils.display_results(
            best_move, result, game_end, game_status
        )
