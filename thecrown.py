import board as bd
import game_play as game

if __name__ == "__main__":
    print("Welcome to The Crown!")
    board = bd.Board()
    game_end = False
    while not game_end:
        board.print_char()
        move, result, game_end, end_status = game.play(board)
        if move[0] is not None:
            board.make_move(move)
        else:
            print("No move found.")
