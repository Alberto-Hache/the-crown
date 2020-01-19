import board as bd
import game_play as game

if __name__ == "__main__":
    print("Welcome to The Crown!")
    board = bd.Board()
    game_end = False
    while not game_end:
        board.print_char()
        move, game_end, result = game.play(board)
        board.make_move(move)
