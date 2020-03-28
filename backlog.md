# Backlog

## Bugs

### A
- Negamax / Quiesce should discount depth from DRAW score (?).

### B
- Make Gametrace size flexible (not limited to DEFAULT_TRACE_LENGTH).
- Regularize terminology: value/score (not result), color / turn / side?

## Optimizations

### (v1)

...

### (v2)
- Optimize position_attacked() [30% to 50% of time spent]
  - Use itemgetter?
  - Use beams?
  - Quick previous discards (e.g. Knight off-rank?, too far away Soldier/Prince?)
  ...
- Avoid using knights_mobility() or count_knight_pseudomoves() by making generate_pseudomoves() count mobility of Knights!
- Generate_pseudo_moves based on 'beams' - 'shadows'.


## Tree search efficiency

### (v1)

- Add hash-tables for transpositions.
  - Value (exact, lower- / upper-bound) - DONE
  - Best move
- Pre-evaluation of moves (extend make pseudo-move()?) for move sorting?
  - Static exchange evaluation?
  - Adapt to game status (middle game | end game)?
- Add killer-move heuristic.
- Add principal variation (without progressive deepening?).

### (v2)
- Add progressive deepening:
  - reusing hash table
  - reusing principal variation
  - reusing killer moves?
- Try "soft-fail" alpha beta pruning?
  - In search.
  - In values stored in transposition table.
- Try Aspiration windows (https://www.chessprogramming.org/Aspiration_Windows) ?


## Game-play

### (v1)
- Define several playing styles.
  - Give Knight mobility a higher value.
  - Impatient Prince? (premature bonus for going up).
  - ...

- Allow starting game from some playing level/style.
  
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
