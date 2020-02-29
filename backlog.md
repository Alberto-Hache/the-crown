# Backlog


## Rules (v1)

- Load position: check if it's legal.
  - No Princes can be taken.
  - No Soldiers in their Prince's starting position.
  - Number of Princes, Knights, Soldiers per side.
- Detect repetition of positions.

## Game-play (v1)
- Check human typed moves are valid.
- Detect natural game end and leave.
- Track:
  - Time spent for the move.
  - Display move played.
- Allow starting game from:
  - some given position
  - some playing level/style
- Define several playing styles.
  - Give K mobility a higher value.
  - Impatient Prince? (premature bonus for going up).
  - ...

## Tree search (v1)

- Improved evaluation function:
  - Positional evaluation:
    - material - DONE
    - Knight mobility - DONE
    - Prince distance to crown
    - Prince's safety?
  - Add small noise to leave nodes evaluation for diverse game.

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
