Two Princes battle for the empty throne!

![The Crown](/thecrown/docs/TheCrown_logo_S.png)

*Copyright (c) 1989 Alberto Hernández Marcos*

## A game inspired in chess

*The Crown* is a chess-inspired board game in which two players battle for their Prince's crowning on a triangular board. Each opponent has six pieces, placed at a vertex of the triangle. The remaining vertex, which they will fight to conquer, is called the *crown* or *crowning box*.

<img src="thecrown/docs/TheCrown_StartingPosition.png" width="250">

*Starting position of The Crown*

The game puts most of chess' original flavour (captures, checks, promotions, strategies...) on a different landscape, simplifying gameplay to three piece types: Prince, Knight and Soldier who move pretty much like their square-world relatives.

**Game Rules**

(coming soon...)

## A program to play "The Crown"

Since not many people knew the game, this year I decided to build a program to play against and... actually learn it! The version in this repo CAN finally play really good matches from opening to endgame (and keeps teaching me my own game...).

I really hope you enjoy it!

### Prerequisites

- Python 3.7+
- pip

### Installation

Clone this repo into your computer with *git* (if you don't have it, [learn how here]).

[learn how here]: https://git-scm.com/book/en/v2/Getting-Started-Installing-Git

```bash
$ git clone https://github.com/Alberto-Hache/the-crown.git
```

Now go to the newly created directory and run the included *Makefile* to install the required libraries:


```bash
$ cd the-crown
$ make init
```

(Or you can use *pip* if you prefer.)

```bash
$ cd the-crown
$ pip install -r requirements.txt
```

### Testing the program

Once *The Crown* is installed, you can test it by running it with default arguments. 
Make sure you are at the home directory (./the-crown), and for there type:

```bash
$ make run
```

This should start a machine-vs-machine game in good-old-fashioned text mode on your terminal with search depth 3 (which, if you know some game theory, is a bit shallow, but plays at a reasonable level)...

```bash
$ make run
python ./crown.py
Starting The Crown!
[starting position]
               .
           13 / \ 
             /---\
         11 / \ / \ 
           /---.---\
        9 / \ / \ / \ 
         /---.---.---\
      7 / \ / \ / \ / \ 
       /---.---.---.---\
    5 /s\ / \ / \ / \ /S\ 
     /---.---.---.---.---\
  3 /k\ /s\ / \ / \ /S\ /K\ 
   /---.---.---.---.---.---\
1 /p\ /k\ /s\ / \ /S\ /K\ /P\ 
 ·---·---·---·---·---·---·---·
  a / b / c / d / e / f / g
White to move.

Move:   e3d3 (+0.88500)                                                         
Params: full_depth=3, check_depth=8, hash_max=1048573, rnd=0.00
Search: 846 nodes, 0.48 sec, max depth=11, hash use=260
```

### Further testing

To run all unit tests just use:

```bash
$ make test
```

This will run a thorough set of tests on all core functionality:

- Overall gameplay
- Board management functionality
- Auxiliary functions

### Author

Alberto Hernández Marcos

I created this game in 1989, during my last year as a Software Engineer student. My passion for chess inspired this deliberately simplified version of the greatest game ever conceived. After slight retouches to the original rules and having enjoyed numerous games with both human and machine players, I think I got what I aimed for: an interesting, simpler variation with a very straightforward goal, respecting and keeping most chess concepts.

### License

This project is licensed under GNU General Public License 3.0 - see the [LICENSE.md] file for details.

[LICENSE.md]: LICENSE
