import argparse
from player import Player
from gamestate import GameState

#parameters: board size n x m, heuristics, depth d
def parse_args():
    parser = argparse.ArgumentParser(description="A clobber AI simulator.")

    parser.add_argument("-n", type=int, help="board width", default=5)
    parser.add_argument("-m", type=int, help="board height", default=6)
    # parser.add_argument("-h1", "--heuristic1", type=str, help="heuristics for player1")
    # parser.add_argument("-h2", "--heuristic2", type=str, help="heuristics for player2")
    # parser.add_argument("d", type=int, help="max decision tree depth", default=5)

    return parser.parse_args()


def main():
    args = parse_args()
    print(f"Arguments: {args}") 
    # player1 = Player(color="B", goal="MAX", heuristics=args.heuristic1)
    # player2 = Player(color="W", goal="MIN", heuristics=args.heuristic2)
    player1 = Player(color="B", goal="MAX")
    player2 = Player(color="W", goal="MIN")

    #create game
    gamestate = GameState(n=args.n, m=args.m)
    gamestate.print_board()



if __name__ == "__main__":
    main()
