import argparse
import time
from datetime import datetime
from player import Player, MinimaxPlayer, GreedyPlayer, RandomPlayer
from gamestate import GameState
from decision_tree import DecisionTree

def parse_args():

    #PARAMETERS:
    #-n, m: board size (n x m)
    #-p1, p2: minimax, random, greedy
    #-d: decision tree depth
    #-p: alpha-beta pruning
    
    #EXAMPLE USAGE: python main.py -n 7 -m 7 -d 4 -p1 random -p2 minimax -p

    parser = argparse.ArgumentParser(description="A clobber AI simulator.")
    parser.add_argument("-n", type=int, help="board width", default=5)
    parser.add_argument("-m", type=int, help="board height", default=6)
    parser.add_argument("-p1", "--player1", type=str, help="algo for player1", choices={"minimax", "random", "greedy"}, default="minimax")
    parser.add_argument("-p2", "--player2", type=str, help="algo for player2", choices={"minimax", "random", "greedy"}, default="minimax")
    parser.add_argument("-d", "--depth", type=int, help="max decision tree depth", default=5)
    parser.add_argument('-p', "--pruning", action='store_true', help='enable alpha-beta pruning')

    return parser.parse_args()


def print_round_info(rounds, player, start_time):
    end_time = datetime.now()
    timestamp = end_time-start_time
    player_name = "player1" if rounds % 2 != 0 else "player2"
    print(f"[{timestamp}]Round {rounds} ::: Current move by {player_name} ({player.__class__.__name__}) ({player.color})")



def main():
    args = parse_args()
    print(f"Arguments: {args}") 
    
    player_classes = {"minimax": MinimaxPlayer, "random": RandomPlayer, "greedy": GreedyPlayer,}
    player1_class = player_classes.get(args.player1)
    player2_class = player_classes.get(args.player2)

    player1 = player1_class(color="B", goal="MAX", depth=args.depth, pruning=args.pruning) if player1_class == MinimaxPlayer else player1_class(color="B", goal="MAX")
    player2 = player2_class(color="W", goal="MIN", depth=args.depth, pruning=args.pruning) if player2_class == MinimaxPlayer else player2_class(color="W", goal="MIN")

    gamestate = GameState(n=args.n, m=args.m)
    rounds = 1
    current_player = player1
    gameover = False
    start_time = datetime.now()

    while not gameover:
        print_round_info(rounds, current_player, start_time)
        
        possible_moves = gamestate.get_possible_moves(current_player.color)
        
        if possible_moves:
            move = current_player.choose_move(gamestate, rounds)
            gamestate.make_move(move)
            current_player = player2 if current_player == player1 else player1
            rounds += 1
            gamestate.print_board()
            #explore decision tree with minmax and given depth
            #get the best calculated outcome and make the move that leads to it
        else:
            print("No moves available left!")
            gameover = True
        
    # wins the one who made the last actual move.
    final_end_time = datetime.now()
    winning_player = "Player1" if current_player == player2 else "Player2"
    print("Winner: ", winning_player)
    print("Round count: ", rounds)
    print("Total time: ", final_end_time-start_time)



if __name__ == "__main__":
    main()
