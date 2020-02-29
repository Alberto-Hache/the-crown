# Backlog


## Rules (v1)

- Load position: check if it's legal.
  - No Princes can be taken.
  - No Soldiers in their Prince's starting position.
  - Number of Princes, Knights, Soldiers per side.
- Detect repetition of positions.

## Game-play (v1)
- Detect natural game end and leave.
- Track:
  - Time spent for the move.
  - Display move played.
- Allow starting game from:
  - some given position
  - some playing level/style
- Define several playing styles.
  - Give Knight mobility a higher value.
  - Impatient Prince? (premature bonus for going up).
  - ...

## Tree search (v1)

- Review null move in quiesce()
  - Rename to stand pat.
  - Review misvalued position in game game_record_23F2020.
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
