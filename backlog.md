# Backlog

## Tree search (v1)

- Improved evaluation function:
  - Positional evaluation: [for v2]
    - material - DONE
    - Knight mobility
    - Prince distance to crown
    - Prince's safety?
  - Add small noise to leave nodes evaluation for diverse game

## Tree search (v2)

- Profiling of v1: bottlenecks?
- Pre-evaluation of moves (extend make pseudo-move()?) for  move sorting?
- Add quiescence search.
  - Piece captures
  - Checks and replies to checks
  - Soldier promotions
  - Prince Crowning
  - Prince moves upwards?
  - Soldier moves to throne (in absence of Prince)?
  - (no move) assumed to guarantee the static evaluation
- Add hash-tables for repetitions.
- Add killer-move heuristic
  - A single move
  - Extend to two moves?
- Add progressive depth search (based on hash tables).

## Rules (v1)

- Load position: check if it's legal.
  - No princes can be taken.
  - No soldiers in their prince's starting position.
  - Number of princes, knights, soldiers per side.

## Rules (v2)

- Detect repetition of positions.

## Optimizations (v2)

- position_attacked() with several return() points?
- generate_pseudo_moves based on 'beams' - 'shadows'.
- position_attacked() with itemgetter:

### Try optmization to 'game_play.position_attacked()'

>>> from operator import itemgetter
>>> help(itemgetter)

>>> itemgetter(1)
operator.itemgetter(1)
>>> itemgetter(1)("abcd")
'b'
>>> dropwhile(itemgetter(1), enumerate(m))
<itertools.dropwhile object at 0x10538caa0>
>>> list(dropwhile(itemgetter(1), enumerate(m)))
[(0, None), (1, None), (2, [1, 2, 3]), (3, None), (4, [1, 2, 3]), (5, None)]
>>> list(dropwhile(lambda x: x[1] is not None, enumerate(m)))
[(0, None), (1, None), (2, [1, 2, 3]), (3, None), (4, [1, 2, 3]), (5, None)]
>>> list(dropwhile(lambda x: x[1] is None, enumerate(m)))
[(2, [1, 2, 3]), (3, None), (4, [1, 2, 3]), (5, None)]
>>> m
[None, None, [1, 2, 3], None, [1, 2, 3], None]
>>> list(dropwhile(lambda x: x[1] is None, enumerate(m)))
[(2, [1, 2, 3]), (3, None), (4, [1, 2, 3]), (5, None)]
>>> list(dropwhile(lambda x: x[1] is None, enumerate(m)))
[(2, [1, 2, 3]), (3, None), (4, [1, 2, 3]), (5, None)]
>>> next(dropwhile(lambda x: x[1] is None, enumerate(m)))
(2, [1, 2, 3])
>>> next(dropwhile(lambda x: x[1] is None, enumerate([])))
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
>>> next(dropwhile(lambda x: x[1] is None, enumerate([])))
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
>>> m
[None, None, [1, 2, 3], None, [1, 2, 3], None]
>>> 
