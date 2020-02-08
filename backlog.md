# Backlog

## Tree search

- Detect end of game by Prince's crowning.
- Detect and handle checkmate -> Prince out + opponent's turn again.
- Detect other ends: no pieces left, no Princes left, stalemate, ... (more?)
- game_play: add function to check if a position is legal
  - No princes can be taken.
  - No soldiers in their prince's starting position.
  - DON'T CHECK: Number of princes, knights, soldiers per side.

- Extend make_move():
  - to detect if the move is legal (Prince safe or absent; no Soldier on the throne of its still present Prince).
  - pre-evaluate move?
- First version of mini-max with alpha-beta prunning (depth = 2; evaluation = -1/0/1).
- Profiling of first version: bottlenecks?
- Improved evaluation function? (material + mobility...).
- Add quiescence search.
- Add killer-move heuristic [single move].
- Extend kille-move heuristic to two moves?
- Add hash-tables for repetitions.
- Add heuristic move sorting?
- Add progressive depth search (based on hash tables).

## Rules

- Load position: check if it's legal.
  - No princes can be taken.
  - No soldiers in their prince's starting position.
  - Number of princes, knights, soldiers per side.

- Detect repetition of positions?

## Optimizations

- position_attacked() with several return() points?
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
