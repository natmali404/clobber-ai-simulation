from dataclasses import dataclass
from typing import List

@dataclass
class GameState:
    n: int
    m: int
    board: List[List[str]]

    def __init__(self, n: int, m: int):
        self.n = n
        self.m = m
        self.board = self.generate_starting_board(n, m)


    def generate_starting_board(self, n: int, m: int) -> List[List[str]]:
        new_board = []
        is_black = True
        for j in range(m):
            new_row = []
            if j > 0: #make sure its checkered
                is_black = True if new_board[j-1][0] == "B" else "W"
            for i in range(n):
                new_row.append("B" if is_black else "W")
                is_black = not is_black
            new_board.append(new_row)
        return new_board

    def print_board(self) -> None:
        for line in self.board:
            print(" ".join(line)) 



@dataclass
class Move:
    from_x: int
    from_y: int
    to_x: int
    to_y: int