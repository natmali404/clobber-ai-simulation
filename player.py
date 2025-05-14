from dataclasses import dataclass

@dataclass
class Player:
    color: str
    goal: str
    heuristics: str = "default"
       