# Backlog

## Bugs
- BUG? Review null move in quiesce()
  - Review misvalued position in game game_record_23F2020.

## Game-play (v1)

- Define several playing styles.
  - Give Knight mobility a higher value.
  - Impatient Prince? (premature bonus for going up).
  - ...

- Allow starting game from:
  - some given position - DONE
  - some playing level/style
  
## Tree search (v1)

- Improve evaluation function:
  - End-game:
    - Prince distance to crown
    - Obstacles to crown?
  - Add small noise to leave nodes evaluation for diverse game.
  - Middle game: (v2)
    - Prince's safety?
    - Soldiers' structure?
  - Middle game situations depending on Knights' balance.

## Environment and versioning

- Enable vs code from CLI:
export PATH="$PATH:/Applications/Visual\ Studio\ Code.app/Contents/Resources/app/bin"

- Lock first full version (0.0.0?) with:
git tag v0.0.0
git push --tags

## Tree search efficiency (v2)

- Profiling of v1: bottlenecks?
- Pre-evaluation of moves (extend make pseudo-move()?) for move sorting?
  - Static exchange evaluation?
- Extend quiescence search. Tactical moves:
  - Prince moves upwards (in absence of opponent's Knights)?
  - Soldier moves to throne (in absence of Prince)?
- Add hash-tables for repetitions.
- Add killer-move heuristic? 
  - A single move
  - Extend to two moves?
- Add progressive depth search (based on hash tables).
- Try "soft-fail" alpha beta pruning?


## Optimizations (v2)

- Remove board3d field from Board class.
- Change board copying for make/turnback moves.
- position_attacked() with several return() points?
- generate_pseudo_moves based on 'beams' - 'shadows'.
- position_attacked() with itemgetter.


## Research (v3)
# ML agents.
- TBD

# Tree search optimization
-  Explore refutation of null move in quiesce():
    - Currently a node returns the best of:
      - null move (if possible).
      - all its dynamic moves (captures, checks, check-evasion, promotion/crowning)
    - This misses non-quiescent positions with huge threats (e.g. test_quiesce_01, test_quiesce_03).
    - The null_move could be corrected through opponent's refutations (in those refutation searches, null_move would be disabled).
    - If the refutation is sufficiently severe (e.g. ≈ 1 Soldier), maybe the node is not quiet:
      a) explore defenses as "dynamic" moves in main search?
      b) full search one more level?
      c) Evaluate minJ(null_move, refutation value)? [Wrong: too pessimistice; it assumes captures and other threats are unavoidable!]

