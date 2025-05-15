from dataclasses import dataclass
import random
from decision_tree import DecisionTree, Node
from gamestate import GameState
from heuristics import evaluate

@dataclass
class Player:
    color: str
    
    def choose_move(self, gamestate: GameState, rounds: int):
        #this is abstract
        raise NotImplementedError("This should be implemented by subclasses")
    
    def get_color(self):
        return self.color
    
@dataclass
class MinimaxPlayer(Player):
    depth: int
    goal: str
    pruning: bool = False
    
    #max_depth
    def choose_move(self, gamestate: GameState, rounds: int):
        #tree = DecisionTree(Node(gamestate))
        tree = DecisionTree(Node(gamestate.copy()))
        if self.pruning:
            best_move = tree.alphabeta(tree.root, self.depth, self.color, self.goal, rounds)
        else:
            best_move = tree.minimax(tree.root, self.depth, self.color, self.goal, rounds)
        
        return best_move
    
@dataclass
class RandomPlayer(Player):
    def choose_move(self, gamestate: GameState, rounds: int):
        possible_moves = gamestate.get_possible_moves(self.color)
        if not possible_moves:
            return None
        return random.choice(possible_moves)
    
@dataclass
class GreedyPlayer(Player):
    def choose_move(self, gamestate: GameState, rounds: int):
        possible_moves = gamestate.get_possible_moves(self.color)
        if not possible_moves:
            return None
        
        best_move = None
        best_score = float("-inf") if self.goal == "MAX" else float("inf")
        
        for move in possible_moves:
            new_state = gamestate.copy()
            new_state.make_move(move)
            score = evaluate(new_state, self.color, rounds)
            
            if self.goal == "MAX" and score > best_score:
                best_score = score
                best_move = move
            elif self.goal == "MIN" and score < best_score:
                best_score = score
                best_move = move
        
        return best_move
       