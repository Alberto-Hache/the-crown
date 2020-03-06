# Backlog

## Bugs
- Track root node in metrics (not counting now).
- BUG? Review null move in quiesce()
  - Review misvalued position in game game_record_23F2020.
  - Rename to stand pat?

## Environment and versioning

- Split program output in three separate flows :
  - Screen (game play) (OST)
  - Game moves (text file .txt? .gam?)
  - Metrics (txt? csv?)
  NOTE: use <https://realpython.com/python-csv/>

- Enable vs code from CLI:
export PATH="$PATH:/Applications/Visual\ Studio\ Code.app/Contents/Resources/app/bin"

- Lock first full version (0.0.0?) with:
git tag v0.0.0
git push --tags

## Game-play (v1)

- Track:
  - Move metrics:
    - Time spent for the move.
    - Full search nodes; quiescence search nodes:

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
  - Add small noise to leave nodes evaluation for diverse game.
  - Middle game: (v2)
    - Prince's safety?
    - Soldiers' structure?

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
