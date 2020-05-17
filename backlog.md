# Backlog

## Project structure

### High

- Redistribute all files in module folders. DONE
- Run all tests from base directory.
- Add LICENSE file: GNU General Public License v3.0
- Add basic README.md
  - Basic description of the project.
  - Download and install instructions.
- Makefile:
  - run
  - test
  - profile
  - clean

  See: https://krzysztofzuraw.com/blog/2016/makefiles-in-python-projects.html


### Medium

- Add a good README.md
  - Game rules
  - Playing "The Crown"
  - Testing

- Pylint cleanup:
  - crownutils.py:
    Get rid of tuple 'distance_from_to':
      import pickle
      distance_from_to = (...)
      pickle.dump(distance_from_to, open('tuple.dump', 'wb'))
      recovered_tuple = pickle.load(open('tuple.dump', 'rb'))

## Bugs

### A
...

### B

- Negamax / Quiesce should discount depth from DRAW score (?).
- Regularize terminology:
  - terminal nodes (not end-game nodes, etc.)
  - null move -> stand pat
  - value/score (not result)
  - turn / side (not color)

## Optimizations

### (v1)
...

### (v2)

- Use killer moves from previous plies (now using current ply only)?

- Keep more info in hash table:
  - list of pseudo_moves? (to save calls to generate_pms)
  - player_in_check? (to save calls to position_attacked)
  - static_evaluation? (to save calls to evaluate_static)
  - ...
  
- Optimize position_attacked() [30% to 50% of time spent]
  - Use itemgetter?
  - Use special version of knight_moves[], even_knight_moves[]
    - even-shaped vectors => parallelism
    - even_knight_moves.reshape -> 1 x N shape
    - use .boardcode[even_knight_moves[reshaped_even_knight_moves]]
    - reshape to original?
      [
        [None, None, 4, ...],
        [None, 1, ...],
        [2, None, ...]
        [None, None, ...]
      ]
    - Capture first per row and detect attack. (how?)
    - ...
- knights_mobility()
  - Estimate just blank positions, ignoring capture / friendly piece distinction.
  - Avoid using knights_mobility() or count_knight_pseudomoves() by making generate_pseudomoves() count mobility of Knights!

### (v3)
- Multiprocessing of tree nodes seach (shared hash table).
- Define 'beams' to:
  - Generate_pseudo_moves based on their 'shadows'.
  - Calculate position_attacked()?


## Tree search efficiency

### (v1)

...

### (v2)

- Add principal variation (without iterative deepening?).
- Try "soft-fail" alpha beta pruning?
  - In search.
  - In values stored in transposition table.
- Try Aspiration windows (https://www.chessprogramming.org/Aspiration_Windows) ?


## Game-play

### (v2)
- Define several playing styles:
  - Give Knight mobility a higher value.
  - Impatient Prince? (premature bonus for going up).
  - Highly offensive (e.g. Soldiers attack?)
  - ...
  
- Extend quiescence search. Tactical moves:
  - Prince moves upwards (in absence of opponent's Knights)?
  - Soldier moves to throne (in absence of Prince)?

### (v2)
- Detect THREE repetitions draw at play time (keeping x2 in tree search).

## Tree search (v1)

- Improve evaluation function:
  - Add small noise to leave nodes evaluation for diverse game.
  - Middle game situations depending on Knights' balance.
  - Encourage exchanging material when in advantage.
  - Middle game: (v2)
    - Prince's safety? (e.g. soldiers and prince in kingdom)
    - Soldiers' structure??
  - End-game:
    - Prince distance to crown
    - Obstacles to crown?

- Don't let quiesce() use null-move's result if it's too different from static evaluation;
it means there's a big threat. Instead, force full search (like when 'player_in_check').
E.g. in test_quiesce_01.cor black misses the imminent check-mate.

## Environment and versioning

- Enable vs code from CLI:
export PATH="$PATH:/Applications/Visual\ Studio\ Code.app/Contents/Resources/app/bin"



## Research (v3)

### ML agents.

- TBD

### Tree search optimization

- Explore refutation of null move in quiesce():
  - Currently a node returns the best of:
    - null move (if possible).
    - all its dynamic moves (captures, checks, check-evasion, promotion/crowning)
  - This misses non-quiescent positions with huge threats (e.g. test_quiesce_01, test_quiesce_03).
  - The null_move could be corrected through opponent's refutations (in those refutation searches, null_move would be disabled).
  - If the refutation is sufficiently severe (e.g. ≈ 1 Soldier), maybe the node is not quiet:
    a) explore defenses as "dynamic" moves in main search?
    b) full search one more level?
    c) Evaluate minJ(null_move, refutation value)? [Wrong: too pessimistice; it assumes captures and other threats are unavoidable!]
