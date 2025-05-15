from dataclasses import dataclass
from typing import List, Optional
from copy import deepcopy

@dataclass
class GameState:
    n: int
    m: int
    board: List[List[str]]

    def __init__(self, n: int, m: int, board: Optional[List[List[str]]] = None):
        self.n = n
        self.m = m
        if board:
            #self.board = deepcopy(board)
            self.board = board
        else:
            self.board = self.generate_starting_board(n, m)
            
    def copy(self):
        return GameState(self.n, self.m, [row[:] for row in self.board])

        

    def generate_starting_board(self, n: int, m: int) -> List[List[str]]:
        new_board = []
        is_black = True
        for j in range(m):
            new_row = []
            if j > 0: #make sure its checkered
                is_black = new_board[j-1][0] == "W"
            for i in range(n):
                new_row.append("B" if is_black else "W")
                is_black = not is_black
            new_board.append(new_row)
        return new_board


    def print_board(self) -> None:
        for line in self.board:
            print(" ".join(line)) 
            
    
    def get_possible_moves(self, player_color: str) -> List["Move"]:
        enemy_color = "B" if player_color == "W" else "W"
        possible_moves = []
        
        for j in range(self.m):
            for i in range(self.n):
                if self.board[j][i] == player_color:
                    #optimally check the neighbours to determine moves
                    #j-1, i; j, i+1; j+1, i; j, i-1
                    for direction_j, direction_i in [(-1, 0), (1, 0), (0, -1), (0,1)]:
                        new_j, new_i = j + direction_j, i + direction_i
                        if 0 <= new_j < self.m and 0 <= new_i < self.n and self.board[new_j][new_i] == enemy_color: #can these ifs be in one line? or will there be error?
                                possible_moves.append(Move(i, j, new_i, new_j))
        
        return possible_moves
                    
       
    def make_move(self, move: "Move") -> None:
        color = self.board[move.from_y][move.from_x]
        #enemy_color = "B" if color == "W" else "B"
        self.board[move.from_y][move.from_x] = "_"
        self.board[move.to_y][move.to_x] = color
        
    def count_pieces(self, player_color: str) -> int:
        count = 0
        for  row in self.board:
            for piece in row:
                if piece == player_color: count += 1
        return count
        
         

@dataclass
class Move:
    from_x: int
    from_y: int
    to_x: int
    to_y: int