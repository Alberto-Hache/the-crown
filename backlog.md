# Backlog

## Tree search (v1)

- Detect and handle checkmate -> Prince out + opponent's turn again.
- Detect other ends: no pieces left, no Princes left, stalemate, ... (more?)
- Improved evaluation function:
  - foster earlier ends
  - Add small noise to leave nodes evaluation for diverse game
  - Positional evaluation: [for v2]
    - material
    - mobility
    - Prince's safety
    - ...
- First version of mini-max with alpha-beta prunning (depth = 2; evaluation = -1/0/1).

## Tree search (v2)

- Profiling of v1: bottlenecks?
- Extend make pseudo-move() to pre-evaluate move?
- Add quiescence search.
  - Piece captures
  - Checks and replies to checks
  - Soldier promotions
  - Prince Crowning
  - Prince moves upwards?
  - (no move)
- Add killer-move heuristic
  - single move
  - Extend to two moves?
- Add hash-tables for repetitions.
- Add heuristic move sorting?
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
