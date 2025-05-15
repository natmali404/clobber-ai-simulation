from typing import List, Optional
from dataclasses import dataclass
from gamestate import GameState, Move
from heuristics import evaluate

@dataclass
class Node:
    gamestate: GameState
    parent: Optional["Node"]
    move: Move #edge that leads to this node
    children: List["Node"] #child nodes
    score: int
    
    def __init__(self, gamestate, parent=None, move=None):
        self.gamestate = gamestate
        self.parent = parent
        self.move = move 
        self.children = []
        self.score = 0 #? moze -inf?

    def add_child(self, child_node):
        self.children.append(child_node)
        
        

@dataclass
class DecisionTree:
    root: Node
    def minimax(self, node: Node, depth: int, player_color: str, player_goal: str, rounds: int):

        #search tree from the node (root).
        #if childless node (leaf) or end of depth, we return for the player whos making the move:
        #if leaf - game result, if depth - heuristics result
        possible_moves = node.gamestate.get_possible_moves(player_color)
        if depth == 0 or not possible_moves:
            node.score = evaluate(node.gamestate, player_color, rounds)
            return node.score
            
        #else for each child node we use minimax recursively
        #assign the max/min value from the child nodes to the current node (max/min depends on what the player is)
        
        #prepare dummy enemy
        opponent_color = "W" if player_color == "B" else "B"
        opponent_goal = "MIN" if player_goal == "MAX" else "MAX"
        
        if player_goal == "MAX":
            max_evaluation = float("-inf") #...
            best_child = None
            
            for move in possible_moves:
                new_state = node.gamestate.copy()
                new_state.make_move(move)
                child = Node(gamestate=new_state, parent=node, move=move)
                #node.add_child(child)
                if node == self.root:
                    node.add_child(child)
                evaluation = self.minimax(child, depth-1, opponent_color, opponent_goal, rounds)
                if evaluation > max_evaluation:
                    max_evaluation = evaluation
                    best_child = child
            node.score = max_evaluation
            if node == self.root: #??
                return best_child.move
            return max_evaluation
        
        else: #player_goal == "MIN"
            min_evaluation = float("inf")
            best_child = None
            for move in possible_moves:
                new_state = node.gamestate.copy()
                new_state.make_move(move)
                child = Node(new_state, parent=node, move=move)
                node.add_child(child)
                evaluation = self.minimax(child, depth-1, opponent_color, opponent_goal, rounds)
                if evaluation < min_evaluation:
                    min_evaluation = evaluation
                    best_child = child
            node.score = min_evaluation
            if node == self.root:
                return best_child.move
            return min_evaluation
        
    
    def alphabeta(self, node: Node, depth: int, player_color: str, player_goal: str, rounds: int, alpha: float = float("-inf"), beta: float = float("inf")):

        possible_moves = node.gamestate.get_possible_moves(player_color)
        if depth == 0 or not possible_moves:
            node.score = evaluate(node.gamestate, player_color, rounds)
            return node.score

        opponent_color = "W" if player_color == "B" else "B"
        opponent_goal = "MIN" if player_goal == "MAX" else "MAX"

        if player_goal == "MAX":
            max_evaluation = float("-inf")
            best_child = None

            for move in possible_moves:
                new_state = node.gamestate.copy()
                new_state.make_move(move)
                child = Node(gamestate=new_state, parent=node, move=move)
                if node == self.root:
                    node.add_child(child)
                
                evaluation = self.alphabeta(child, depth - 1, opponent_color, opponent_goal, rounds, alpha, beta)
                if evaluation > max_evaluation:
                    max_evaluation = evaluation
                    best_child = child

                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break  #pruning

            node.score = max_evaluation
            if node == self.root:
                return best_child.move
            return max_evaluation

        else:  #player_goal == "MIN"
            min_evaluation = float("inf")
            best_child = None

            for move in possible_moves:
                new_state = node.gamestate.copy()
                new_state.make_move(move)
                child = Node(gamestate=new_state, parent=node, move=move)
                node.add_child(child)

                evaluation = self.alphabeta(child, depth - 1, opponent_color, opponent_goal, rounds, alpha, beta)
                if evaluation < min_evaluation:
                    min_evaluation = evaluation
                    best_child = child

                beta = min(beta, evaluation)
                if beta <= alpha:
                    break  #pruning

            node.score = min_evaluation
            if node == self.root:
                return best_child.move
            return min_evaluation

          
    
    def update_root(self, new_state):
        self.root = Node(gamestate=new_state)
        self.root.children.clear()