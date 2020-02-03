# Backlog

## Moves generation

- Create and pass tests for evaluate().
- Create pseudo_mov_generator(board, side)

## Tree search

- First version of mini-max with alpha-beta prunning (depth = 2; evaluation = -1/0/1)
- Improved evaluation function? (material + mobility...).
- Add quiescence search.
- Add killer-move heuristic.
- Add hash-tables for repetitions.
- Add heuristic move sorting?
- Add progressive depth search (based on hash tables).

## Rules

- game_play: add function to check if a position is legal? [Better check pseudo-moves once done?]
  - No princes can be taken.
  - No soldiers in their prince's starting position.
  - Number of princes, knights, soldiers per side.

- Detect repetition of positions?

## Optimizations

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
