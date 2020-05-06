import numpy as np
import copy
import sys
import types
import time
from operator import itemgetter
from itertools import dropwhile

import board as bd
import utils


########################################################################
# Tree search parameters:

PLY1_SEARCH_PARAMS = {
    "max_depth":                1,
    "max_check_quiesc_depth":   4,
    "transposition_table":      True,
    "iterative_deepening":      False,  # Needless here.
    "killer_moves":             False,  # Needless here.
    "randomness":               0
}

PLY2_SEARCH_PARAMS = {
    "max_depth":                2,
    "max_check_quiesc_depth":   6,
    "transposition_table":      True,
    "iterative_deepening":      True,
    "killer_moves":             True,
    "randomness":               0
}

PLY3_SEARCH_PARAMS = {
    "max_depth":                3,
    "max_check_quiesc_depth":   8,
    "transposition_table":      True,
    "iterative_deepening":      True,
    "killer_moves":             True,
    "randomness":               0
}

PLY4_SEARCH_PARAMS = {
    "max_depth":                4,
    "max_check_quiesc_depth":   14,  # 10 moves below max depth (prev. 10).
    "transposition_table":      True,
    "iterative_deepening":      True,
    "killer_moves":             True,
    "randomness":               0
}

PLY5_SEARCH_PARAMS = {
    "max_depth":                5,
    "max_check_quiesc_depth":   15,  # 10 moves below max depth.
    "transposition_table":      True,
    "iterative_deepening":      True,
    "killer_moves":             True,
    "randomness":               0
}

PLY6_SEARCH_PARAMS = {
    "max_depth":                6,
    "max_check_quiesc_depth":   16,  # 10 moves below max depth.
    "transposition_table":      True,
    "iterative_deepening":      True,
    "killer_moves":             True,
    "randomness":               0
}

MINIMAL_SEARCH_PARAMS = PLY1_SEARCH_PARAMS
DEFAULT_SEARCH_PARAMS = PLY4_SEARCH_PARAMS

########################################################################
# Evaluation of static positions.

# Material value of the pieces:
PRINCE_WEIGHT = 100
KNIGHT_WEIGHT = 10
SOLDIER_WEIGHT = 1

# Material value for each code found in board.code[]
piece_code_value = np.array(
    [
        0,
        PRINCE_WEIGHT, SOLDIER_WEIGHT, KNIGHT_WEIGHT,
        PRINCE_WEIGHT, SOLDIER_WEIGHT, KNIGHT_WEIGHT
    ]
)

# Material value from player's view, ordered by piece.code:
piece_weights = np.array([
    [  # From White's point of view (Prince, Soldier, Knight).
        [PRINCE_WEIGHT, SOLDIER_WEIGHT, KNIGHT_WEIGHT],
        [-PRINCE_WEIGHT, -SOLDIER_WEIGHT, -KNIGHT_WEIGHT]
    ],
    [  # From Black's point of view (Prince, Soldier, Knight).
        [-PRINCE_WEIGHT, -SOLDIER_WEIGHT, -KNIGHT_WEIGHT],
        [PRINCE_WEIGHT, SOLDIER_WEIGHT, KNIGHT_WEIGHT]
    ]
])

# Knights mobility is rewarded upto a max. per Knight:
# max mobility of a Knight = 23 moves, so 2 Knights max = 46 moves.
# 46 moves * 0.1 = 4.6 ≈ 1/2 Knight
KNIGHT_MOVE_VALUE = 0.1
MAX_K_MOVES_TO_REWARD = 12

# Prince-crown proximity is rewarded up to a max. value:
# Distance Range: [0, 12]
# Parameter range: ≈ (0, 10)
MAX_CROWN_DIST_REWARD = 5

# Reduce Prince-crown distance reward when 'prince_at_danger'.
# Parameter range: [0, 1]:
#   0.0 -> full reward regarless Prince unsafety.
#   0.5 -> cut half the reward if unsafe.
#   1.0 -> no reward if unsafe.
UNSAFETY_PENALTY_RATE = 0.50

# Penalize Soldiers lag penalty:
# Range: [0, 12] x 3 ≈ [0, 30]
SOLDIER_LAG_PENALTY = 0.05
SOLDIER_LAG_TOLERANCE = 2  # No penalty if dist ≤ this value.

# Soldiers to crown reward:
# Range: [0, 12] x 3 ≈ [0, 30]
SOLDIER_ADV_REWARD = 0.05
MAX_SOLDIER_ADV_REWARD = 10

# Unsafe Knight-count combinations for Prince of each side:
prince_at_danger = np.array(
    [
        [[0, 1], [0, 2], [1, 2], [2, 2]],
        [[1, 0], [2, 0], [2, 1], [2, 2]]
    ]
)

# Other:
# Subtract in non-terminal positions to choose faster wins.
STATIC_DEPTH_PENALTY = 0.005
# Subtract in terminal positions to choose faster wins.
END_DEPTH_PENALTY = 1


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

########################################################################
# Table used for game-tracing:
# Max initial depth dimensioned for trace.
DEFAULT_TRACE_LENGTH = 500
# Extension applied to depth every time current lenth is exceeded.
DEFAULT_TRACE_EXTENSION = int(DEFAULT_TRACE_LENGTH/10)

# Indices:
HASH_COL = 0  # Index of hash column: id of the position.
NODE_COUNT_COL = 1  # node_counter: nodes explored at that depth.
IRREVERSIBLE_COL = 2  # flag for board obtained after irreversible move.
N_TRACE_COLS = 3  # Number of columns required for the above data.

########################################################################
# Hash table used for transpositions.
HASH_SIZE_1 = 65537
HASH_SIZE_2 = 131071
HASH_SIZE_3 = 262147
HASH_SIZE_4 = 524287
HASH_SIZE_5 = 1048573

DEFAULT_HASH_SIZE = HASH_SIZE_5  # Max. size of the hash table.

HASH_IDX = 0    # The full hash value of the position.
DEPTH_IDX = 1   # The depth from which the position was explored.
VALUE_IDX = 2   # The value found for the position.
FLAG_IDX = 3    # The type of value (EXACT / LOWERBOUND / UPPERBOUND).
MOVE_IDX = 4    # The best move found in the position.
DEPTH_SRCH_IDX = 5  # The depth with whith the position was searched.

EXACT = 0
LOWER_BOUND = 1
UPPER_BOUND = 2

########################################################################
# Killer moves.
MAX_DEPTH_KILLER_MOVES = 20  # Will be ignored beyond this depth.


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
        - Store match: moves sequence from start to self.current_board_ply.
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
        Assumption: max. length overflow not checked here; expected to be
        handled by register_searched_board() during search.

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
        self.level_trace[
            self.current_board_ply, IRREVERSIBLE_COL
            ] = irreversible
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
        # pylint: disable=E1136  # pylint/issues/3139
        if ply_number >= self.level_trace.shape[0]:  # pylint: disable=E1136
            # Max depth exceeded: extend array.
            trace_patch = np.zeros((DEFAULT_TRACE_EXTENSION, N_TRACE_COLS))
            self.level_trace = np.concatenate(
                (self.level_trace, trace_patch), axis=0
                )
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
    - The depth from which the position was explored (plys from root).
    - The value found for the position.
    - The type of value (EXACT / LOWERBOUND / UPPERBOUND).
    - The best move found in the position.
    - The depth with whith the position was searched:
        a) full search:         plies to max-depth
        b) quiescence search:   0

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
            if value[DEPTH_SRCH_IDX] >= current_value[DEPTH_SRCH_IDX]:
                # The new value was more deeply explored, or is newer: replace.
                self.table[key] = value

    def retrieve(self, key):
        current_value = self.table.get(key, None)
        if current_value is not None and current_value[HASH_IDX] == key:
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

    def update_values(
        self, board, depth, value, alpha_orig, beta, move, depth_searched
    ):
        """
        Update the transposition table with the board passed
        and the values associated to it.
        """

        # Determine flag for the value.
        if value <= alpha_orig:
            flag = UPPER_BOUND
        elif value >= beta:
            flag = LOWER_BOUND
        else:
            flag = EXACT
        # Update transposition table.
        self.insert(
            board.hash, (board.hash, depth, value, flag, move, depth_searched)
        )


class Killer_Moves:
    """
    A list of moves indexed by ply or level of the search.
    (Killer moves = quiet moves that caused a beta-cutoff in a sibling node,
    to be tried in other positions at the same depth.)
    Capacity:
    - Two moves maximum per ply.
    - Limited depth: moves beyond certain depth are not stored.
    """
    def __init__(self, size=MAX_DEPTH_KILLER_MOVES):
        self.size = size
        self.killer_list = [[None, None] for _ in range(size)]

    def insert(self, move, ply):
        # Insert a move that just created a cut-off.
        # If both slots are full, the oldest one is dropped.
        if ply < self.size:
            if move != self.killer_list[ply][0]:
                # New move is not on top; shift right and insert.
                self.killer_list[ply][1] = self.killer_list[ply][0]
                self.killer_list[ply][0] = move
            # else:
            #   New move already on top: do nothing.

    def retrieve(self, ply):
        # Simply return content of list,
        # or an empty list if the ply exceeds capacity.
        try:
            list = self.killer_list[ply]
            return list
        except IndexError:
            return [None, None]

    def shift_plies(self, n_plies=2):
        # Adapt list after a move has been actually played in the game
        # so it can be reused in next move search. Each shift removes
        # first move and adds an empty one at the end.
        # (Default shift is 2, as next board will be two plies ahead.)
        for _ in range(n_plies):
            self.killer_list.pop(0)
            self.killer_list.append([None, None])


def is_killer(m1, m2, k1, k2, k3, k4):
    """
    Check if the move [m1, m2] is contained in killer moves list:
    [[k1, k2], [k3, k4]].
    This function is vectorized a v_is_killer() for use within
    np.where(...) in numpy arrays.
    """
    res = [m1, m2] == [k1, k2] or [m1, m2] == [k3, k4]
    return res


def play(
    board, params=DEFAULT_SEARCH_PARAMS, trace=None, max_time=float("inf"),
    t_table=None, killer_list=None, screen_traces=True
):
    # Capture initial time for time keeping.
    time_0 = time.time()

    # Register maximal depth set in parameters.
    params_copy = params.copy()  # Original parameters to keep untouched.
    do_iterative_deepening = params_copy["iterative_deepening"]
    max_depth = params_copy["max_depth"]
    max_quiesc_depth = params_copy["max_check_quiesc_depth"]
    quiesc_depth_delta = max_quiesc_depth - max_depth
    initial_depth = min(2, max_depth)
    depth_step = 1

    # Initialize depth parameters for iterative deepening.
    if do_iterative_deepening:
        params_copy["max_depth"] = initial_depth
        params_copy["max_check_quiesc_depth"] = \
            initial_depth + quiesc_depth_delta

    # Initiate loop arguments, Transposition Table and Killer moves.
    keep_iterating = True
    alpha, beta = [-float("inf"), float("inf")]
    depth = 0
    if params_copy["transposition_table"] and t_table is None:
        t_table = Transposition_table()
    if params_copy["killer_moves"] and killer_list is None:
        killer_list = Killer_Moves()
    search_trace = []

    # Iterative deepening loop.
    while keep_iterating:
        # Run search for move selection.
        # Reuse: transposition table, killer moves.
        move, result, game_end, game_status = negamax(
            board, depth, alpha, beta, params_copy,
            t_table, trace, killer_list, search_trace
            )
        # Display search status: move found after iteration.
        if screen_traces:
            print(
                "Searching at depth {:d}... {} ({:>+.5f}) \r".format(
                    params_copy["max_depth"],
                    utils.move_2_txt(move),
                    result
                ),
                end="", flush=True
            )
        # Update iteration parameters (not needed for TT).
        params_copy["max_depth"] += depth_step
        params_copy["max_check_quiesc_depth"] += depth_step
        time_1 = time.time()
        # Check all conditions for new iteration.
        # - set in search parameters,
        # - max_depth not reached yet,
        # - max time not exceeded,
        # - current search didn't find a win at that depth.
        keep_iterating = \
            do_iterative_deepening and \
            params_copy["max_depth"] <= max_depth and \
            time_1 - time_0 < max_time and \
            abs(result) < PLAYER_WINS - 100

    # Clear search status.
    if screen_traces:
        print("{}\r".format(utils.CLEAN_LINE), end="")

    # Adapt killer moves list for next move to play (2 plies fwd).
    killer_list.shift_plies()

    # Get Transposition Table's metrics.
    t_table_metrics = t_table.metrics()
    # t_table.clear()  # Not cleard so it's used in next turn.

    return move, result, game_end, game_status, \
        time_1 - time_0, t_table_metrics


def negamax(
    board, depth, alpha, beta, params=DEFAULT_SEARCH_PARAMS,
    t_table=None, trace=None, killer_list=None, search_trace=[]
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
        killer_list     A list of moves indexed by ply that worked well in
                        sibling nodes (may not be possible or even legal).
        search_trace:   A list storing current search thread from root node.

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
        return quiesce(
            board, depth, alpha, beta, params, t_table, trace,
            killer_list=killer_list, search_trace=search_trace
            )

    # 1. Register searched node, checking repetitions.
    if trace is not None:
        repetition = trace.register_searched_board(board, depth)
        if repetition and depth != 0:
            # The position already happenned in the game [excluding root node].
            return None, DRAW, True, DRAW_THREE_REPETITIONS

    # 2. Check position in transposition table.
    alpha_orig = alpha
    value = t_table.retrieve(board.hash)
    hash_move = None
    if value is not None:
        # Position found with enough depth; check value and flags.
        if value[DEPTH_SRCH_IDX] >= params["max_depth"] - depth:
            # Adjust 'stored_value' to current depth.
            stored_value = correct_eval_from_to_depth(
                value[VALUE_IDX], value[DEPTH_IDX], depth
            )
            # Adapt search to value flag.
            if value[FLAG_IDX] == EXACT:
                return value[MOVE_IDX], stored_value, False, ON_GOING
            elif value[FLAG_IDX] == LOWER_BOUND:
                alpha = max(alpha, stored_value)
            elif value[FLAG_IDX] == UPPER_BOUND:
                beta = min(beta, stored_value)
        # Check for alpha-beta cutoff.
        if alpha >= beta:
            return value[MOVE_IDX], stored_value, False, ON_GOING
        # Retrieve possibly registered move.
        hash_move = value[MOVE_IDX]

    # 3. Check for other end conditions:
    #   VICTORY_CROWNING / VICTORY_NO_PIECES_LEFT / DRAW_NO_PRINCES_LEFT
    childs_move, result, game_end, game_status = evaluate_terminal(
        board, depth)
    if game_end:
        # End of game: no move is returned.
        return None, result, game_end, game_status  # TODO: Return beta?

    # 4.0 Check for predictable ends (not for root node).
    if depth > 0:
        result = endgame_prediction(board, depth)
        if result is not None:
            # The position has a predictable end: no search needed.
            return None, result, False, ON_GOING

    # Prepare for tree search.
    best_move = None
    best_result = -np.Infinity  # Value to store in transposition table.
    n_legal_moves_tried = 0

    # 4.1 Null-move: not tried in negamax()
    pass

    # 4.2 Try hash-move (before generating pseudo-moves).
    if hash_move is not None:
        coord1, coord2 = hash_move
        # Try hash_move on board;
        # if it leads to a game end, we can use result_i.
        is_legal_i, is_dynamic_i, \
            result_i, game_end_i, game_status_i, \
            captured_piece, leaving_piece, old_hash, \
            opponent_in_check = \
            make_pseudomove(
                board, coord1, coord2, depth, params,
                search_trace=search_trace
            )
        # Assumption: it's legal.
        n_legal_moves_tried += 1
        # Unless it led to a final postion, search the move.
        if not game_end_i:
            childs_move, result_i, game_end_i, game_status_i = \
                negamax(
                    board, depth + 1, -beta, -alpha,
                    params, t_table, trace, killer_list, search_trace
                )
            result_i = -float(result_i)  # Switch to player's view.
        # Assess results from final position or search.
        if result_i > best_result:
            best_move = [coord1, coord2]
            best_result = result_i
        # And 'unmake' the move.
        board.unmake_move(
            coord1, coord2, captured_piece, leaving_piece, old_hash)
        search_trace.pop()
        if result_i >= beta:
            # Ignore rest of moves [fail-hard beta cutoff].
            # (No need to update transposition table with this known move.)
            # Update the list of killer moves if it's no capture.
            if board.board1d[coord2] is None:
                killer_list.insert([coord1, coord2], depth)
            return [coord1, coord2], beta, False, ON_GOING
        if result_i > alpha:
            # Update move choice with this better one for player.
            best_move, alpha = [coord1, coord2], result_i

    # 4.3 Generate and explore existing pseudomoves.
    moves, moves_count = generate_pseudomoves(board)
    assert (moves_count > 0),\
        "ERROR: No pseudomoves found despite game is not ended "\
        "and MAX_DEPTH has not been reached."
    # Remove already searched hash_move from pseudomoves list.
    # Note: if hash_move is "Prince leaving", it won't be in 'moves'.
    if hash_move is not None and hash_move[1] is not None:
        moves.remove(hash_move)

    # Preevaluate and sort pseudomoves.
    if killer_list is not None:
        k_moves = killer_list.retrieve(depth)
    else:
        k_moves = [None, None]
    moves = pre_evaluate_pseudomoves(board, moves, k_moves)

    # Explore each possible pseudomove.
    for pseudo_move in moves:  # [[24, 14], [24, 13]...]], [2, 3]...]
        coord1, coord2 = pseudo_move  # [24, 14]
        # Try pseudomove 'i' on board;
        # if it leads to a game end, we can use result_i.
        is_legal_i, is_dynamic_i, \
            result_i, game_end_i, game_status_i, \
            captured_piece, leaving_piece, old_hash, \
            opponent_in_check = \
            make_pseudomove(
                board, coord1, coord2, depth, params,
                search_trace=search_trace
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
                        params, t_table, trace, killer_list, search_trace
                    )
                result_i = -float(result_i)  # Switch to player's view.
            # Assess results from final position or search.
            if result_i > best_result:
                best_move = [coord1, coord2]
                best_result = result_i
            # And 'unmake' the move.
            board.unmake_move(
                coord1, coord2, captured_piece, leaving_piece, old_hash)
            search_trace.pop()
            if result_i >= beta:
                # Ignore rest of pseudomoves [fail-hard beta cutoff].
                # Update transposition table with best result found.
                t_table.update_values(
                    board, depth, result_i, alpha_orig, beta,
                    [coord1, coord2], params["max_depth"] - depth
                )
                # Update the list of killer moves if it's no capture.
                if board.board1d[coord2] is None:
                    killer_list.insert([coord1, coord2], depth)
                return [coord1, coord2], beta, False, ON_GOING
            if result_i > alpha:
                # Update move choice with this better one for player.
                best_move, alpha = [coord1, coord2], result_i
        else:
            # Simply 'unmake' the illegal move.
            board.unmake_move(
                coord1, coord2, captured_piece, leaving_piece, old_hash)
            search_trace.pop()

    # Check exploration results.
    if n_legal_moves_tried > 0:
        # A legal best move was found.
        # Update transposition table with best result found.
        t_table.update_values(
            board, depth, best_result, alpha_orig, beta,
            best_move, params["max_depth"] - depth
        )
        # Update the list of killer moves if it's no capture.
        if board.board1d[coord2] is None:
            killer_list.insert(best_move, depth)
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
            captured_piece, leaving_piece, old_hash, opponent_in_check = \
            make_pseudomove(
                board, coord1, coord2, depth, params,
                search_trace=search_trace
            )
        # And the new board must be assessed.
        childs_move, result_i, game_end_i, game_status_i = \
            negamax(
                board, depth + 1, -beta, -alpha,
                params, t_table, trace, killer_list, search_trace
            )
        best_result = -float(result_i)  # Switch to player's view.
        # And 'unmake' the move.
        board.unmake_move(
            coord1, coord2, captured_piece, leaving_piece, old_hash)
        search_trace.pop()
        # Update transposition table with best result found.
        t_table.update_values(
            board, depth, best_result, alpha_orig, beta,
            [coord1, coord2], params["max_depth"] - depth
        )
        # No update to list of killer moves (it's a forced move).
        # Return results.
        return best_move, best_result, False, ON_GOING

    # 6. The player is STALEMATED.
    return None, DRAW, True, DRAW_STALEMATE


def quiesce_WIP(
    board, depth, alpha, beta, params=DEFAULT_SEARCH_PARAMS,
    t_table=None, trace=None, player_in_check=None, killer_list=None,
    search_trace=[]
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
        player_in_check:
                        Boolean or None. A possible early detection of
                        the moving Prince being in check.
        killer_list     A list of moves indexed by ply that worked well in
                        sibling nodes (may not be possible or even legal).
        search_trace:   A list storing current search thread from root node.

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

    # 2. Check position in transposition table.
    alpha_orig = alpha
    if t_table:
        value = t_table.retrieve(board.hash)
    else:
        value = None
    hash_move = None
    if value is not None:
        # Position found; check value and flags.
        # No check on hash postion's depth: quiesce() has no limit.
        # Adjust 'stored_value' to current depth.
        stored_value = correct_eval_from_to_depth(
            value[VALUE_IDX], value[DEPTH_IDX], depth
        )
        # Adapt search to value flag.
        if value[FLAG_IDX] == EXACT:
            return value[MOVE_IDX], stored_value, False, ON_GOING
        elif value[FLAG_IDX] == LOWER_BOUND:
            alpha = max(alpha, stored_value)
        elif value[FLAG_IDX] == UPPER_BOUND:
            beta = min(beta, stored_value)
        # Check for alpha-beta cutoff.
        if alpha >= beta:
            return value[MOVE_IDX], stored_value, False, ON_GOING
        # Retrieve possibly registered move.
        hash_move = value[MOVE_IDX]

    # 3. Check for other end conditions:
    #   VICTORY_CROWNING / VICTORY_NO_PIECES_LEFT / DRAW_NO_PRINCES_LEFT
    childs_move, result, game_end, game_status = evaluate_terminal(
        board, depth)
    if game_end:
        # End of game: no move is returned.
        return None, result, game_end, game_status  # TODO: Return beta?

    # Prepare for tree search.
    best_move = None
    best_result = -np.Infinity  # Value to store in transposition table.
    n_legal_moves_found = 0
    n_legal_moves_tried = 0

    # 4.1. Null-move: Perform static evaluation if it is legal and not endgame.
    player_side = board.turn
    opponent_side = bd.WHITE if player_side == bd.BLACK else bd.BLACK
    is_endgame = board.piece_count[player_side][bd.KNIGHT] == 0

    # Detect if  player is in check (unless it's already passed as argument).
    if player_in_check is None:
        # See if board is not legal (would mean the player is in check).
        # The other case (>1 Princes) is not explored by calling method.
        board.turn = opponent_side  # Flip turns temporarily.
        player_in_check = not is_legal(board)
        board.turn = player_side  # Restablish original turn.

    # Evaluate 'stand pat' condition:
    # Player is NOT in check and it's not an endgame (or it's too deep).
    try_stand_pat = not player_in_check and \
        (not is_endgame or depth > params["max_non_dynamic_depth"])
    if try_stand_pat:
        # Null move heuristic is possible; evaluate it.
        best_move = None
        result_i = evaluate_static(board, depth)
        # Check result of null_move vs alpha-beta window.
        if result_i >= beta:
            return None, beta, False, ON_GOING  # [fail hard beta cutoff]
        if result_i > alpha:
            # Update move choice with this better one for player.
            alpha = result_i

    # 4.2 Try hash-move (before generating pseudo-moves),
    # regardless of whether it's dynamic or not.
    if hash_move is not None:
        coord1, coord2 = hash_move
        # Try hash_move on board;
        # if it leads to a game end, we can use result_i.
        is_legal_i, is_dynamic_i, \
            result_i, game_end_i, game_status_i, \
            captured_piece, leaving_piece, old_hash, \
            opponent_in_check = \
            make_pseudomove(
                board, coord1, coord2, depth, params,
                search_trace=search_trace
            )
        # Assumption: it's legal.
        n_legal_moves_found += 1
        n_legal_moves_tried += 1
        # Unless it led to a final position, search the move.
        if not game_end_i:
            childs_move, result_i, game_end_i, game_status_i = \
                quiesce(
                    board, depth + 1, -beta, -alpha,
                    params, t_table, trace, killer_list=killer_list,
                    search_trace=search_trace
                )
            result_i = -float(result_i)  # Switch to player's view.
        # Assess results from final position or search.
        if result_i > best_result:
            best_move = [coord1, coord2]
            best_result = result_i
        # And 'unmake' the move.
        board.unmake_move(
            coord1, coord2, captured_piece, leaving_piece, old_hash)
        search_trace.pop()
        if result_i >= beta:
            # Ignore rest of moves [fail-hard beta cutoff].
            # (No need to update transposition table with this known move.)
            # Update the list of killer moves if it's no capture.
            if board.board1d[coord2] is None:
                killer_list.insert([coord1, coord2], depth)
            return [coord1, coord2], beta, False, ON_GOING
        if result_i > alpha:
            # Update move choice with this better one for player.
            best_move, alpha = [coord1, coord2], result_i

    # 4.3. Generate and explore dynamic pseudomoves.
    moves, moves_count = generate_pseudomoves(board)
    assert(moves_count > 0),\
        "ERROR: No pseudomoves found despite game is not ended."

    # Remove already searched hash_move from list.
    # Note: if hash_move is "Prince leaving", it won't be in 'moves'.
    if hash_move is not None and hash_move[1] is not None:
        moves.remove(hash_move)

    # Preevaluate and sort pseudomoves.
    if killer_list is not None:
        k_moves = killer_list.retrieve(depth)
    else:
        k_moves = [None, None]
    moves = pre_evaluate_pseudomoves(board, moves, k_moves)

    # Explore each possible pseudomove in two passes:
    # 1st pass: dynamic moves (or all if player in check).
    # 2nd pass: postponed static moves if 'stand pat' was not used.

    non_dynamic_moves = []  # To store initially discarded static moves.
    moves_lists = [moves, non_dynamic_moves]
    search_static_moves = False  # Only activated if needed for 2nd pass.

    # Loop over the two moves lists: original moves and postponed static moves.
    for sublist in moves_lists:
        # Loop over moves in the sublist.
        for pseudo_move in sublist:  # [[24, 14], [24, 13]...]], [2, 3]...]
            coord1, coord2 = pseudo_move  # [24, 14]
            # Try pseudomove 'i' on board;
            # if it leads to a game end, we can use result_i.
            is_legal_i, is_dynamic_i, \
                result_i, game_end_i, game_status_i, \
                captured_piece, leaving_piece, old_hash, \
                opponent_in_check = \
                make_pseudomove(
                    board, coord1, coord2, depth, params,
                    check_dynamic=not(player_in_check),
                    search_trace=search_trace
                )
            # Check if it's legal.
            if is_legal_i:
                if sublist is moves:  # Don't count twice!
                    n_legal_moves_found += 1
                # Check if it's a dynamic move or static moves are ok.
                if is_dynamic_i or player_in_check or search_static_moves:
                    # A move worth searching in quiesce().
                    n_legal_moves_tried += 1
                    if not game_end_i:
                        # We need to recursively search this move deeper:
                        childs_move, result_i, game_end_i, game_status_i = \
                            quiesce(
                                board, depth + 1, -beta, -alpha,
                                params, t_table, trace,
                                player_in_check=opponent_in_check,
                                killer_list=killer_list,
                                search_trace=search_trace
                            )
                        result_i = -float(result_i)  # Switch to player's view.
                    # Assess results from final position or search.
                    if result_i > best_result:
                        # best_move = [coord1, coord2]  # This overwrote stand pat
                        best_result = result_i
                    # And 'unmake' the move.
                    board.unmake_move(
                        coord1, coord2, captured_piece, leaving_piece,
                        old_hash
                    )
                    search_trace.pop()
                    if result_i >= beta:
                        # Ignore rest of pseudomoves [fail hard beta cutoff].
                        # Update transposition table with best result found.
                        t_table.update_values(
                            board, depth, result_i, alpha_orig, beta,
                            [coord1, coord2], depth_searched=0
                        )
                        # Update the list of killer moves if it's no capture.
                        if board.board1d[coord2] is None:
                            killer_list.insert([coord1, coord2], depth)
                        return [coord1, coord2], beta, False, ON_GOING
                    if result_i > alpha:
                        # Update move choice with this better one for player.
                        best_move, alpha = [coord1, coord2], result_i
                else:
                    # Non-dynamic move; 'unmake' it and keep it for later.
                    board.unmake_move(
                        coord1, coord2, captured_piece, leaving_piece,
                        old_hash
                    )
                    search_trace.pop()
                    # Add only from 1st to 2nd list.
                    if sublist is moves:
                        non_dynamic_moves.append(pseudo_move)
            else:
                # Simply 'unmake' the illegal move.
                board.unmake_move(
                    coord1, coord2, captured_piece, leaving_piece, old_hash
                )
                search_trace.pop()
        # End of sublist search. Strategy on non-dynamic moves:
        # a) No static eval was done and no dynamic moves searched;
        #    search ALL non-dynamic moves.
        # b) No static eval was done and some move was searched
        #    (TT or dynamic); search a few extra non-dynamic moves.
        # c) otherwise, skip non-dynamic moves.
        if sublist is moves:
            if not try_stand_pat:
                if n_legal_moves_tried == 0:
                    # a) Search all non-dynamic moves.
                    search_static_moves = True
                else:
                    # b) Search a few static moves [TODO: validate 2].
                    search_static_moves = True
                    moves_lists[1] = moves_lists[1][0:2]
            else:
                # c) Skip non-dynamic moves.
                search_static_moves = False
                non_dynamic_moves.clear()

    # Check exploration results.
    if n_legal_moves_tried > 0:
        # A legal best move was found.
        # Update transposition table with best result found.
        t_table.update_values(
            board, depth, best_result, alpha_orig, beta,
            best_move, depth_searched=0
        )
        # Update the list of killer moves if it's no capture.
        if board.board1d[coord2] is None:
            killer_list.insert(best_move, depth)
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
            captured_piece, leaving_piece, old_hash, opponent_in_check = \
            make_pseudomove(
                board, coord1, coord2, depth, params, search_trace=search_trace
            )
        # And the new board must be searched.
        childs_move, result_i, game_end_i, game_status_i = \
            quiesce(
                board, depth + 1, -beta, -alpha,
                params, t_table, trace, killer_list=killer_list,
                search_trace=search_trace
            )
        best_result = -float(result_i)  # Switch to player's view.
        # And 'unmake' the move.
        board.unmake_move(
            coord1, coord2, captured_piece, leaving_piece, old_hash)
        search_trace.pop()
        # Update transposition table with best result found.
        t_table.update_values(
            board, depth, best_result, alpha_orig, beta,
            [coord1, coord2], depth_searched=0
        )
        # No update to list of killer moves (it's a forced move).
        # Return results.
        return best_move, best_result, False, ON_GOING

    if n_legal_moves_found == 0:
        # 6. The player is STALEMATED.
        return None, DRAW, True, DRAW_STALEMATE
    else:
        # 4.3 [unexplored by 4.2] The player has only non-dynamic moves.
        # Non-dynamic moves aren't explored; return initial static evaluation.
        # Update transposition table.
        if t_table:
            t_table.update_values(
                board, depth, alpha, alpha_orig, beta, None, depth_searched=0
            )
        # No update to list of killer moves (no moves known).
        return None, alpha, False, ON_GOING


def quiesce(
    board, depth, alpha, beta, params=DEFAULT_SEARCH_PARAMS,
    t_table=None, trace=None, player_in_check=None, killer_list=None,
    search_trace=[]
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
        player_in_check:
                        Boolean or None. A possible early detection of
                        the moving Prince being in check.
        killer_list     A list of moves indexed by ply that worked well in
                        sibling nodes (may not be possible or even legal).
        search_trace:   A list storing current search thread from root node.

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

    # 2. Check position in transposition table.
    alpha_orig = alpha
    if t_table:
        value = t_table.retrieve(board.hash)
    else:
        value = None
    hash_move = None
    if value is not None:
        # Position found; check value and flags.
        # No check on hash postion's depth: quiesce() has no limit.
        # Adjust 'stored_value' to current depth.
        stored_value = correct_eval_from_to_depth(
            value[VALUE_IDX], value[DEPTH_IDX], depth
        )
        # Adapt search to value flag.
        if value[FLAG_IDX] == EXACT:
            return value[MOVE_IDX], stored_value, False, ON_GOING
        elif value[FLAG_IDX] == LOWER_BOUND:
            alpha = max(alpha, stored_value)
        elif value[FLAG_IDX] == UPPER_BOUND:
            beta = min(beta, stored_value)
        # Check for alpha-beta cutoff.
        if alpha >= beta:
            return value[MOVE_IDX], stored_value, False, ON_GOING
        # Retrieve possibly registered move.
        hash_move = value[MOVE_IDX]

    # 3. Check for other end conditions:
    #   VICTORY_CROWNING / VICTORY_NO_PIECES_LEFT / DRAW_NO_PRINCES_LEFT
    childs_move, result, game_end, game_status = evaluate_terminal(
        board, depth)
    if game_end:
        # End of game: no move is returned.
        return None, result, game_end, game_status  # TODO: Return beta?

    # 4.0 Check for predictable ends (no neeed to check if it's root node).
    result = endgame_prediction(board, depth)
    if result is not None:
        # The position has a predictable end: no search needed.
        return None, result, False, ON_GOING

    # Prepare for tree search.
    best_move = None
    best_result = -np.Infinity  # Value to store in transposition table.
    n_legal_moves_tried = 0
    n_legal_moves_found = 0

    # 4.1. Null-move: Perform static evaluation if it is legal.
    player_side = board.turn
    opponent_side = bd.WHITE if player_side == bd.BLACK else bd.BLACK

    # Detect if player is in check (unless it's already passed as argument).
    if player_in_check is None:
        # See if board is not legal (would mean the player is in check).
        # The other case (>1 Princes) is not explored by calling method.
        board.turn = opponent_side  # Flip turns temporarily.
        player_in_check = not is_legal(board)
        board.turn = player_side  # Restablish original turn.

    if not player_in_check:
        # Null move is possible; evaluate it.
        best_move = None
        result_i = evaluate_static(board, depth)
        # Check result of null_move vs alpha-beta window.
        if result_i >= beta:
            return None, beta, False, ON_GOING  # [fail hard beta cutoff]
        if result_i > alpha:
            # Update move choice with this better one for player.
            alpha = result_i

    # 4.2 Try hash-move (before generating pseudo-moves),
    # regardless of whether it's dynamic or not.
    if hash_move is not None:
        coord1, coord2 = hash_move
        # Try hash_move on board;
        # if it leads to a game end, we can use result_i.
        is_legal_i, is_dynamic_i, \
            result_i, game_end_i, game_status_i, \
            captured_piece, leaving_piece, old_hash, \
            opponent_in_check = \
            make_pseudomove(
                board, coord1, coord2, depth, params,
                search_trace=search_trace
            )
        # Assumption: it's legal.
        n_legal_moves_tried += 1
        n_legal_moves_found += 1
        # Unless it led to a final position, search the move.
        if not game_end_i:
            childs_move, result_i, game_end_i, game_status_i = \
                quiesce(
                    board, depth + 1, -beta, -alpha,
                    params, t_table, trace, killer_list=killer_list,
                    search_trace=search_trace
                )
            result_i = -float(result_i)  # Switch to player's view.
        # Assess results from final position or search.
        if result_i > best_result:
            best_move = [coord1, coord2]
            best_result = result_i
        # And 'unmake' the move.
        board.unmake_move(
            coord1, coord2, captured_piece, leaving_piece, old_hash)
        search_trace.pop()
        if result_i >= beta:
            # Ignore rest of moves [fail-hard beta cutoff].
            # (No need to update transposition table with this known move.)
            # Update the list of killer moves if it's no capture.
            if board.board1d[coord2] is None:
                killer_list.insert([coord1, coord2], depth)
            return [coord1, coord2], beta, False, ON_GOING
        if result_i > alpha:
            # Update move choice with this better one for player.
            best_move, alpha = [coord1, coord2], result_i

    # 4.3. Generate and explore dynamic pseudomoves.
    moves, moves_count = generate_pseudomoves(board)
    assert(moves_count > 0),\
        "ERROR: No pseudomoves found despite game is not ended."

    # Remove already searched hash_move from list.
    # Note: if hash_move is "Prince leaving", it won't be in 'moves'.
    if hash_move is not None and hash_move[1] is not None:
        moves.remove(hash_move)

    # Preevaluate and sort pseudomoves.
    if killer_list is not None:
        k_moves = killer_list.retrieve(depth)
    else:
        k_moves = [None, None]
    moves = pre_evaluate_pseudomoves(board, moves, k_moves)

    # Explore each possible pseudomove.
    for pseudo_move in moves:  # [[24, 14], [24, 13]...]], [2, 3]...]
        coord1, coord2 = pseudo_move  # [24, 14]
        # Try pseudomove 'i' on board;
        # if it leads to a game end, we can use result_i.
        is_legal_i, is_dynamic_i, \
            result_i, game_end_i, game_status_i, \
            captured_piece, leaving_piece, old_hash, \
            opponent_in_check = \
            make_pseudomove(
                board, coord1, coord2, depth, params,
                check_dynamic=not(player_in_check),
                search_trace=search_trace)
        # Check if it's legal.
        if is_legal_i:
            n_legal_moves_found += 1
            # Check if it's a dynamic move.
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
                            params, t_table, trace,
                            player_in_check=opponent_in_check,
                            killer_list=killer_list, search_trace=search_trace
                        )
                    result_i = -float(result_i)  # Switch to player's view.
                # Assess results from final position or search.
                if result_i > best_result:
                    # best_move = [coord1, coord2]  # This overwrote stand pat.
                    best_result = result_i
                # And 'unmake' the move.
                board.unmake_move(
                    coord1, coord2, captured_piece, leaving_piece, old_hash)
                search_trace.pop()
                if result_i >= beta:
                    # Ignore rest of pseudomoves [fail hard beta cutoff].
                    # Update transposition table with best result found.
                    t_table.update_values(
                        board, depth, result_i, alpha_orig, beta,
                        [coord1, coord2], depth_searched=0
                    )
                    # Update the list of killer moves if it's no capture.
                    if board.board1d[coord2] is None:
                        killer_list.insert([coord1, coord2], depth)
                    return [coord1, coord2], beta, False, ON_GOING
                if result_i > alpha:
                    # Update move choice with this better one for player.
                    best_move, alpha = [coord1, coord2], result_i
            else:
                # Simply 'unmake' the not-searched move.
                board.unmake_move(
                    coord1, coord2, captured_piece, leaving_piece, old_hash)
                search_trace.pop()
        else:
            # Simply 'unmake' the illegal move.
            board.unmake_move(
                coord1, coord2, captured_piece, leaving_piece, old_hash)
            search_trace.pop()

    # Check exploration results.
    if n_legal_moves_tried > 0:
        # A legal best move was found.
        # Update transposition table with best result found.
        t_table.update_values(
            board, depth, best_result, alpha_orig, beta,
            best_move, depth_searched=0
        )
        # Update the list of killer moves if it's no capture.
        if board.board1d[coord2] is None:
            killer_list.insert(best_move, depth)
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
            captured_piece, leaving_piece, old_hash, opponent_in_check = \
            make_pseudomove(
                board, coord1, coord2, depth, params, search_trace=search_trace
            )
        # And the new board must be searched.
        childs_move, result_i, game_end_i, game_status_i = \
            quiesce(
                board, depth + 1, -beta, -alpha,
                params, t_table, trace, killer_list=killer_list,
                search_trace=search_trace
            )
        best_result = -float(result_i)  # Switch to player's view.
        # And 'unmake' the move.
        board.unmake_move(
            coord1, coord2, captured_piece, leaving_piece, old_hash)
        search_trace.pop()
        # Update transposition table with best result found.
        t_table.update_values(
            board, depth, best_result, alpha_orig, beta,
            [coord1, coord2], depth_searched=0
        )
        # No update to list of killer moves (it's a forced move).
        # Return results.
        return best_move, best_result, False, ON_GOING

    if n_legal_moves_found == 0:
        # 6. The player is STALEMATED.
        return None, DRAW, True, DRAW_STALEMATE
    else:
        # 4.3 [unexplored by 4.2] The player has only non-dynamic moves.
        # Non-dynamic moves aren't explored; return initial static evaluation.
        # Update transposition table.
        if t_table:
            t_table.update_values(
                board, depth, alpha, alpha_orig, beta, None, depth_searched=0
            )
        # No update to list of killer moves (no moves known).
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

    # 1. Basic material balance:
    material = np.multiply(board.piece_count, piece_weights[player_side]).sum()

    # 2. Mobility obtained by the Knights is rewarded, upto some limit:
    mobility_balance = (
        min(
            MAX_K_MOVES_TO_REWARD *
            board.piece_count[player_side][bd.KNIGHT],
            knights_mobility(board, player_side)
        ) -
        min(
            MAX_K_MOVES_TO_REWARD *
            board.piece_count[opponent_side][bd.KNIGHT],
            knights_mobility(board, opponent_side)
        )
    ) * KNIGHT_MOVE_VALUE

    # 3. Prince state:

    # 3.1. Crown proximity is rewarded, but less if Knights balance is unsafe.
    own_prince = board.prince[player_side]
    if own_prince is not None:
        # The player has a Prince. Check safety and distance to crown.
        own_prince_danger = board.piece_count[:, bd.KNIGHT] in \
            prince_at_danger[player_side]
        own_crown_distance = bd.distance_to_crown[own_prince.coord]
        own_crown_reward = MAX_CROWN_DIST_REWARD * \
            (1 - own_crown_distance/12) * \
            (1 - own_prince_danger * UNSAFETY_PENALTY_RATE)
    else:
        own_crown_reward = 0

    opp_prince = board.prince[opponent_side]
    if opp_prince is not None:
        # The opponent has a Prince. Check safety and distance to crown.
        opp_prince_danger = board.piece_count[:, bd.KNIGHT] in \
            prince_at_danger[opponent_side]
        opp_crown_distance = bd.distance_to_crown[opp_prince.coord]
        opp_crown_reward = MAX_CROWN_DIST_REWARD * \
            (1 - opp_crown_distance/12) * \
            (1 - opp_prince_danger * UNSAFETY_PENALTY_RATE)
    else:
        opp_crown_reward = 0

    crown_distance_balance = own_crown_reward - opp_crown_reward

    # 4. Soldiers.
    # 4.1 With enemy Knights, penalize Soldiers lagging behind their Prince.
    own_soldiers_lag_penalty = soldiers_lag(board, player_side)
    opp_soldiers_lag_penalty = soldiers_lag(board, opponent_side)
    soldiers_lag_penalty_balance = \
        - SOLDIER_LAG_PENALTY * \
        (own_soldiers_lag_penalty - opp_soldiers_lag_penalty)

    # 4.2 Without defense duties, reward Soldiers for approaching the crown.
    own_soldiers_adv_reward = soldiers_advance(board, player_side)
    opp_soldiers_adv_reward = soldiers_advance(board, opponent_side)
    soldiers_adv_reward_balance = \
        SOLDIER_ADV_REWARD * \
        (own_soldiers_adv_reward - opp_soldiers_adv_reward)

    # 5. Other factors.
    pre_eval = \
        material + \
        mobility_balance + \
        crown_distance_balance + \
        soldiers_lag_penalty_balance + \
        soldiers_adv_reward_balance

    # 4.1. Depth is penalized to encourage nearer wins.
    other = - depth*STATIC_DEPTH_PENALTY*np.sign(pre_eval)

    return pre_eval + other


def endgame_prediction(board, depth):
    """
    Input:
        board:      Board - The game position to evaluate.
        depth:      int - Depth of node in the search tree.

    Output:
        result:     float; predicted result in case it is predictable.
                    None; when it's not predictable.

    Endgames covered:
    - Prince vs Prince

    """

    # Check pieces:
    if board.piece_count[:, bd.KNIGHT].sum() == 0:
        # Find player's top piece.
        if board.piece_count[:, bd.SOLDIER].sum() == 0:
            # P vs P (no Soldiers)
            assert board.piece_count[:, bd.PRINCE].sum() == 2, \
                "Error: Expected 2 Princes but found {}".format(
                    board.piece_count[:, bd.PRINCE].sum()
                )
            return eval_princes_end(board, depth)
        else:
            # P+S vs P+S
            return princes_and_soldiers_end(board, depth)
    else:
        # Position with some Knight; not predictable.
        return None


def eval_princes_end(board, depth):
    """
    Evaluate a position where only two Princes are left on the board.
    Result based on:
    - Prince's distance to crown
    - and turn.

    1. If the Prince to play is closer to crown;
        the player wins.
    2. If the Prince to play is at the same distance as the opponent;
        the player loses.
    3. If the Prince to play is one position farther than the opponent;
        the player wins.
    4. Otherwise, the player loses.

    The result is penalized with:
        (depth + depth_to_final) * END_DEPTH_PENALTY
    """
    player_side = board.turn
    opponent_side = bd.WHITE if player_side == bd.BLACK else bd.BLACK

    player_prince_coord = board.prince[player_side].coord
    opponent_prince_coord = board.prince[opponent_side].coord

    player_dist_to_crown = bd.distance_to_crown[player_prince_coord]
    opponent_dist_to_crown = bd.distance_to_crown[opponent_prince_coord]

    if player_dist_to_crown < opponent_dist_to_crown:
        # Case 1. Player is closer: direct win.
        result = PLAYER_WINS
        depth_to_final = 2 * player_dist_to_crown - 1
        depth_penalty = - (depth + depth_to_final) * END_DEPTH_PENALTY
    elif player_dist_to_crown == opponent_dist_to_crown:
        # Case 2. Player at the same distance as opponent: a loss.
        result = OPPONENT_WINS
        depth_to_final = 2 * opponent_dist_to_crown
        depth_penalty = (depth + depth_to_final) * END_DEPTH_PENALTY
    elif player_dist_to_crown == opponent_dist_to_crown + 1:
        # Case 3. Player is one coord farther: a win.
        result = PLAYER_WINS
        depth_to_final = 2 * player_dist_to_crown - 1
        depth_penalty = - (depth + depth_to_final) * END_DEPTH_PENALTY
    else:
        # Case 4. Player loses in rest of cases.
        result = OPPONENT_WINS
        depth_to_final = 2 * opponent_dist_to_crown
        depth_penalty = (depth + depth_to_final) * END_DEPTH_PENALTY

    return result + depth_penalty


def princes_and_soldiers_end(board, depth):
    """
    Evaluate a position with:
    - no Knights
    - some Soldier (at least 1)
    - some Prince (1 or 2)
    Result based on:
    - Pieces' distance to crown
    - and turn.

    1. If the Prince to play is closer to crown than any other piece;
        the player wins.

    2. If the enemy's Prince is at least TWO steps closer to crown than any other piece;
        the opponet wins.

    The result is penalized with:
        (depth + depth_to_final) * END_DEPTH_PENALTY
    """
    player_side = board.turn
    opponent_side = bd.BLACK if player_side == bd.WHITE else bd.WHITE

    # Find out minimal distance to crown:
    # - of each player
    # - overall across both players
    min_dist_to_crown_of_side = (
        min(
            [bd.piece_color_distance_to_crown[p.type][p.color][p.coord]
                for p in board.pieces[bd.WHITE]]
        ),
        min(
            [bd.piece_color_distance_to_crown[p.type][p.color][p.coord]
                for p in board.pieces[bd.BLACK]]
        )
    )
    min_dist_to_crown = min(min_dist_to_crown_of_side)

    # 1. Check if the player to play has its Prince on top.
    try:
        if (
            bd.distance_to_crown[board.prince[player_side].coord] ==
            min_dist_to_crown and
            min_dist_to_crown_of_side[opponent_side] > min_dist_to_crown
        ):
            # The Prince to play is on top: it will win.
            result = PLAYER_WINS
            depth_to_final = 2 * min_dist_to_crown - 1
            depth_penalty = - (depth + depth_to_final) * END_DEPTH_PENALTY
            return result + depth_penalty
    except AttributeError:
        # This side has no Prince; try next case.
        pass

    # 2. Check if the opponent's Prince is on top by 2 or more steps.
    try:
        if (
            bd.distance_to_crown[board.prince[opponent_side].coord] ==
            min_dist_to_crown and
            min_dist_to_crown_of_side[player_side] > min_dist_to_crown + 1
        ):
            # The enemy's Prince is on top and can't be reached: it will win.
            result = OPPONENT_WINS
            depth_to_final = 2 * min_dist_to_crown
            depth_penalty = + (depth + depth_to_final) * END_DEPTH_PENALTY
            return result + depth_penalty
    except AttributeError:
        # This side has no Prince; try next case.
        pass

    # No more known cases.

    return None


def evaluate_terminal(board, depth):
    """
    Detect (most) terminal positions, evaluating them from playing side's
    perspective.

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
                    [Detected during search once moves are generated.]
                    DRAW_THREE_REPETITIONS
                    [Detected during search]
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
                    return True
                elif closest_piece.type == bd.SOLDIER:  # A Soldier
                    # Check proximity and position in its kingdom.
                    attacked = (piece_pos == 0) or \
                        (piece_pos == 1 and
                         bd.kingdoms[attacking_side][positions[piece_pos]])
                else:  # If it's a Prince; check if it's adjacent.
                    attacked = (piece_pos == 0)
            if attacked:
                return True  # No need to check the other directions.
        except IndexError:
            pass  # No pieces found in that direction; do nothing.
    return attacked


def position_attacked_NEW(board, pos, attacking_side):

    # Obtain a list of indices:
    # [[42, 43, 44], [40, 34, 33, 25, 24, ...], ...]
    position_lists = bd.knight_moves[pos]
    # Array of arrays:
    # [[None, None, None], [None, None, None, Piece_i, None, ...], ...]
    board_slices = itemgetter(*position_lists)(board.board1d)

    # Identify first piece on each array.
    # [[], ]
    first_in_board_slices = list(
        map(
            lambda x: list(dropwhile(lambda y: y[1] is None, enumerate(x))),
            board_slices
        )
    )

    # Pick only non empty lists headed by "attacking_side".
    # p_moves = bd.piece_moves[piece.type][piece.color][piece.coord]
    # Check for pieces of the color required, piece's moves:
    attacking_pieces = [
        x[0] for x in first_in_board_slices
        if len(x) > 0 and
        x[0][1].color == attacking_side and
        pos in bd.piece_moves_flat[x[0][1].type][x[0][1].color][x[0][1].coord]
    ]

    return len(attacking_pieces) > 0


def generate_pseudomoves(board, kill_moves=None):
    """
    Generate a list of (non-legally checked) moves for
    the playing side.

    Input:
        board:      Board - The game position to generate moves on.
        kill_moves: TBA

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


def pre_evaluate_pseudomoves(board, moves, k_moves=[None, None]):
    """
    Given a list of pseudomoves on a board, sort them for optimal seach.

    Input:
        board:      Board - the position where moves will be searched.
        moves:      a list of moves, e.g. [[1, 13], [1, 14], [26, 16]...]
        k_moves:    a list of TWO killer moves that might appear in 'moves'.
                    E.g: [None, None]; [[1, 13], None]; [[23, 24], [1, 14]]

    Output:
        ev_moves:   a new list of moves, e.g. [[26, 16], [1, 13], [1, 14]...]

    Heuristic implemented:
    1.  Winning / neutral captures, sorted by decreasing expected gain:
        1.a) if captured piece is not protected: full piece value.
        1.b) if captured piece is protected: piece value - own piece value.
    2.  Killer moves found in list (if any).
    3.  [If no enemy Knights] Prince and Soldiers approaches to the crown.
    4.  Non capture moves (unsorted).
    5.  Losing captures, sorted by increasing expected loss (same algorithm).

    Not covered:
    -   Checks / checkmates.
    -   Endgame (no Prince):
        -   Soldier's promotion / approaching missing Prince's position.
    """
    # Extend array with columns for evaluations.
    # - columns 0, 1: coord1 and coord2 of the move (coord2 is not None).
    # - column 2: move priority (higher value => higher priority).

    if moves != []:
        attacking_side = bd.WHITE if board.turn == bd.BLACK else bd.BLACK
        # Determine endgame condition (player has no Knights).
        is_endgame = board.piece_count[attacking_side][bd.KNIGHT] == 0

        # Initialize array with moves on columns '0' and '1'.
        ev_moves = np.zeros((len(moves), 3), dtype=np.intp)
        ev_moves[:, 0:2] = moves

        # Extract killer moves variables:
        if k_moves[0] is not None:
            k1, k2 = k_moves[0]
        else:
            k1, k2 = None, None
        if k_moves[1] is not None:
            k3, k4 = k_moves[1]
        else:
            k3, k4 = None, None

        # Estimate the value captured by each move in column '2'.
        ev_moves[:, 2] = piece_code_value[
            board.boardcode[ev_moves[:, 1]]
        ]

        # For capturing moves, correct outcome in column '2',
        # checking whether the opponent defends coord2.

        # Moves sorting:
        # 1a. good captures <- 10 x (capturing result) + 50   (>= 150)
        # 1b. even captures <- 10 x (capturing result) + 50   (= 50)
        # 2. killer moves <- 30                              (= 30)
        # 3. [endgame] moves towards the crown               (0, 12)
        # 4. non captures <- 0                              (= 0)
        # 5. bad captures <- 10 x (capturing result) + 5    (<= -50)
        # NOTE: all values as negatives below for faster .sort()

        if not is_endgame:
            # Middle-game preevaluation.
            ev_moves[:, 2] = np.where(
                ev_moves[:, 2] > 0,  # Condition: some value is captured.
                # <full value> - <capturer's value> if coord2 is defended.
                (
                    ev_moves[:, 2] -
                    v_position_attacked(
                        board, ev_moves[:, 1], attacking_side
                    ) *
                    piece_code_value[board.boardcode[ev_moves[:, 0]]]
                )*(-10) - 50,
                # Not a capture: value rest of conditions.
                v_is_killer(
                    ev_moves[:, 0], ev_moves[:, 1], k1, k2, k3, k4
                )*(-30)
            )
        else:
            # Endgame preevaluation.
            ev_moves[:, 2] = np.where(
                ev_moves[:, 2] > 0,  # Condition: some value is captured.
                # <full value> - <capturer's value> if coord2 is defended.
                (
                    ev_moves[:, 2] -
                    v_position_attacked(
                        board, ev_moves[:, 1], attacking_side
                    ) *
                    piece_code_value[board.boardcode[ev_moves[:, 0]]]
                )*(-10) - 50,
                # Not a capture: value rest of conditions.
                v_is_killer(
                    ev_moves[:, 0], ev_moves[:, 1], k1, k2, k3, k4
                )*(-30) -
                (
                    bd.np_distance_to_crown[ev_moves[:, 1]] <
                    bd.np_distance_to_crown[ev_moves[:, 0]]
                ) * \
                (12 - bd.np_distance_to_crown[ev_moves[:, 1]])
            )
        # Sort moves by higher evaluation.
        ev_moves.view('i8, i8, i8').sort(order=['f2'], axis=0)
        # ev_moves = ev_moves[::-1]

        # Discard auxiliary columns and return as a list.
        return np.intp(ev_moves[:, 0:2])

    else:
        return moves


def soldiers_lag(board, color):
    """
    Evaluate the amount of danger from Soldiers lagging behind their Prince,
    considering:
    a) player has no Prince or opponent has no Knights => no lag
    b) for Soldiers behind their Prince, a penalty proportional to
    their distance above a thresold of 1.
    """
    player_side = color
    opponent_side = bd.WHITE if player_side == bd.BLACK else bd.BLACK

    # Check preconditions.
    if board.prince[player_side] is None or \
       board.piece_count[opponent_side][bd.KNIGHT] == 0:
        # Player has no Prince, or enemy has no Knights.
        return 0
    else:
        # Player has a Prince and opponent has Knight(s).
        prince_coord = board.prince[player_side].coord
        prince_crown_dist = bd.distance_to_crown[prince_coord]
        # Check distances from Prince for Soldiers behind.
        soldiers_lag = sum(
            [
                max(
                    0,
                    bd.distance_from_to[p.coord][prince_coord] -
                    SOLDIER_LAG_TOLERANCE  # No penalty if dist ≤ this value.
                )
                for p in board.pieces[color]
                if p.type == bd.SOLDIER and
                bd.distance_to_crown[p.coord] > prince_crown_dist
            ]
        )
        return soldiers_lag


def soldiers_advance(board, color):
    """
    Evaluate reward from Soldiers approaching the crown,
    considering Prince's safety:
    a) player has a Prince and Knights balance is unsafe = no reward.
    b) otherwise, reward all Soldiers by their proximity to the crown.
    """
    player_side = color
    opponent_side = bd.WHITE if player_side == bd.BLACK else bd.BLACK

    # Check player's Prince safety.
    own_prince_danger = board.piece_count[:, bd.KNIGHT] in \
        prince_at_danger[player_side]
    if board.prince[player_side] is not None and own_prince_danger:
        # Player has a Prince and the Knights balance is unsafe.
        return 0.0
    else:
        # Sum Soldiers' progress towards crown (upto a top value).
        soldiers_reward = sum(
            [
                min(
                    MAX_SOLDIER_ADV_REWARD,
                    12 - bd.distance_to_crown[p.coord]
                )
                for p in board.pieces[color]
                if p.type == bd.SOLDIER
            ]
        )
        return soldiers_reward


def soldiers_dispersion(board, color, coord):
    """
    Calculate the sum of distances of Soldier of a given color
    to some given coordinate 'coord'.
    """
    dispersion = sum(
        [
            bd.distance_from_to[p.coord][coord]
            for p in board.pieces[color] if p.type == bd.SOLDIER
        ]
    )
    return dispersion


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


def make_pseudomove(
    board, coord1, coord2, depth, params, check_dynamic=False,
    search_trace=[]
):
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
        search_trace:   A list storing current search thread from root node.

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
                    (when no enemy Knights):
                    - Prince moves upwards
                    - Soldier moves leaving other Soldiers behind / on-pair

                    Conditions not checked:
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
        old_hash:       int - hash value of the board BEFORE the move.
        opponent_in_check:
                        Boolean or None.
                        Early detection of Prince in check only when
                        check_dynamic is True and is_dynamic becomes True
                        because the move is a check.
    """

    # Initialize vars. for later dynamism check before board changes.
    moving_side = board.turn
    piece_type = board.board1d[coord1].type
    opponent_in_check = None

    # And now, make the move.
    captured_piece, leaving_piece, old_hash = board.make_move(coord1, coord2)
    depth += 1
    search_trace.append([coord1, coord2])

    # Check if the move produced an illegal position.
    if not is_legal(board):
        return False, None, None, None, None, \
            captured_piece, leaving_piece, old_hash, opponent_in_check

    # Check if a Prince is crowning.
    if (coord2 == board.crown_position) and \
       (piece_type == bd.PRINCE):
        # A Prince was legally moved onto the crown!
        return True, True, PLAYER_WINS - depth*END_DEPTH_PENALTY, True, \
            VICTORY_CROWNING, captured_piece, leaving_piece, \
            old_hash, opponent_in_check

    # Check if it was the capture of the last piece.
    if board.piece_count[board.turn].sum() == 0:
        return True, True, PLAYER_WINS - depth*END_DEPTH_PENALTY, True, \
            VICTORY_NO_PIECES_LEFT, captured_piece, leaving_piece, \
            old_hash, opponent_in_check

    # Optionally, check dynamic conditions of the move.
    is_dynamic = False
    if check_dynamic:
        # Checked: captures, mated Prince leaves, Soldier promotion, checks,
        # (when no enemy Knights): Prince upwards, highest Soldier upwds.
        # NOT checked: Princeless Soldier -> throne
        # NOT checked: check evasion (calling node must search all moves)
        if captured_piece is not None or leaving_piece is not None:
            # Piece captured / mated Prince leaving / Soldier promotion.
            is_dynamic = True
        else:
            # Check on 'board' if it produced a check to the enemy.
            opponent_prince = board.prince[board.turn]
            if opponent_prince is not None and \
               not depth > params["max_check_quiesc_depth"]:
                # The move produces a check to the opponent, now to move.
                is_dynamic = position_attacked(
                    board, opponent_prince.coord, moving_side
                )
                # Flag check detection.
                opponent_in_check = is_dynamic
            if not is_dynamic and \
               board.piece_count[board.turn][bd.KNIGHT] == 0:
                # It's an endgame without Knights.
                if piece_type == bd.PRINCE:
                    # Check for moves towards crown.
                    is_dynamic = bd.distance_to_crown[coord1] > \
                        bd.distance_to_crown[coord2]
                elif piece_type == bd.SOLDIER:
                    # Check for moves of highest Soldier towards crown.
                    if bd.distance_to_crown[coord1] > \
                       bd.distance_to_crown[coord2]:
                        # Check if the rest of Soldiers are behind / on pair.
                        is_dynamic = bd.distance_to_crown[coord2] == min(
                            [
                                bd.distance_to_crown[p.coord]
                                for p in board.pieces[moving_side]
                                if p.type == bd.SOLDIER
                            ]
                        )

    # Report as a legal move, the dynamism of the move and other conditions.
    return True, is_dynamic, None, False, ON_GOING, \
        captured_piece, leaving_piece, old_hash, opponent_in_check


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
            captured_piece, leaving_piece, old_hash, opponent_in_check = \
            make_pseudomove(
                board, coord1, coord2,
                depth=0, params=MINIMAL_SEARCH_PARAMS, check_dynamic=False
            )
        # And now, 'unmake' the move:
        board.unmake_move(
            coord1, coord2, captured_piece, leaving_piece, old_hash)
        # search_trace.pop()
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
                    captured_piece, leaving_piece, old_hash, \
                    opponent_in_check = \
                    make_pseudomove(
                        board, move_coords[0], move_coords[1],
                        depth=0, params=MINIMAL_SEARCH_PARAMS,
                        check_dynamic=False
                    )
                # And now, 'unmake' the move:
                board.unmake_move(
                    move_coords[0], move_coords[1], captured_piece,
                    leaving_piece, old_hash)
                # search_trace.pop()
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
            txt_coord2 = "++" if coord2 is None \
                else utils.coord_2_algebraic[coord2]
            return False, "Error: {}{} is an illegal move.".format(
                utils.coord_2_algebraic[coord1],
                txt_coord2
            )


def correct_eval_from_to_depth(evaluation, from_depth, to_depth):
    """
    Adjust some previous 'evaluation' calculated at depth 'from_depth'
    to new depth 'to_depth'.
    It takes into account the two different depth penalties:
    - END_DEPTH_PENALTY assumed for |evaluation| >= PLAYER_WINS - 100
    - STATIC_DEPTH_PENALTY for any other evaluation.

    Note: from_depth <= to_depth for evaluation to be worthy.
    """

    if from_depth != to_depth:
        # Depth correction required.
        depth_delta = to_depth - from_depth  # 4 - 2 = 2
        delta_sign = -np.sign(evaluation)  # -1 for positive evals
        if abs(evaluation) >= PLAYER_WINS - 100:
            # An end-game evaluation.
            evaluation += delta_sign * depth_delta * END_DEPTH_PENALTY
        else:
            # A middle-game evaluation.
            evaluation += delta_sign * depth_delta * STATIC_DEPTH_PENALTY

    return evaluation


########################################################################
# Vectorized functions (used within numpy).
v_position_attacked = np.vectorize(position_attacked)
v_is_killer = np.vectorize(is_killer)


# Main program.
if __name__ == '__main__':
    # Manage arguments.
    file_name = None if (len(sys.argv) == 1) else sys.argv[1]

    # Initializations.
    board = bd.Board(file_name)
    game_trace = Gametrace(board)
    parameters = PLY4_SEARCH_PARAMS

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
