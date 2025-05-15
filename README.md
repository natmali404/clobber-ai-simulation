# **Minimax algorithm with alpha-beta pruning on a decision tree**

## A Clobber AI simulation

### 0. **Running the simulation**

Parameters:
-n, -m: board size (n x m)
-p1, -p2: player type (minimax, random, greedy)
-d: decision tree depth (int > 0)
-p: alpha-beta pruning (off by default)

Example use:

```
python main.py -n 7 -m 7 -d 4 -p1 random -p2 minimax -p
```

Run a game on a 7x7 board with a tree depth = 4. Player1 plays a random strategy, Player2 uses minimax with alpha-beta pruning.

```
python main.py -d 3 -p1 minimax -p2 greedy
```

Run a game on a default 5x6 board with a tree depth = 4. Player1 uses minimax without pruning, Player2 plays a greedy strategy.

### 1. **Intro**

The goal of this project is to simulate a game-playing AI for the game Clobber using the Minimax algorithm, enhanced with alpha-beta pruning.

Clobber is a two-player turn-based game played on a rectangular grid. Each cell initially contains either a white or black piece, corresponding to one of the two players. On their turn, a player moves one of their own pieces onto an adjacent opponent's piece, effectively capturing it. The player who cannot make a move on their turn loses.

This report outlines the theoretical basis of the Minimax algorithm, defines the problem formally, describes the used heuristics and presents the implementation details of the Clobber.

#### **Used Python libraries**

- time - for performance measurement
- cProfile - for performance analysis
- dataclasses, typing - for type hints and overall better experience
- argparse - for parsing arguments and running the simulation
- random - for algorithms

### 2. **Method Description**

#### **Minimax algorithm**

Minimax is a recursive algorithm used for decision-making in two-player games. It assumes both players play optimally: one player (Max) tries to maximize their score, while the opponent (Min) tries to minimize it. The algorithm constructs a game tree of all possible future moves, evaluates terminal nodes using a heuristic function, and backtracks to determine the optimal current move.

#### **Alpha-Beta Pruning**

Alpha-beta pruning is an optimization technique for Minimax. It eliminates branches in the game tree that cannot possibly affect the final decision, reducing the number of nodes evaluated. Two values are maintained during traversal:

- Alpha: the best value found so far for the Max player.
- Beta: the best value found so far for the Min player.

If at any point Beta ≤ Alpha, further exploration of that branch is stopped.

### 3. **Problem Definition and My Solution**

#### **Game state**

A game state in Clobber is represented as a 2D grid (matrix), where each cell contains either:

- 'W' for a white piece,
- 'B' for a black piece,
- '\_' for an empty cell (after a piece has moved).

```python
# a relevant fragment of my gamestate class

from dataclasses import dataclass
from typing import List

@dataclass
class GameState:
    n: int
    m: int
    board: List[List[str]]


    # board generation
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


    # calculating possible moves for a given player
    def get_possible_moves(self, player_color: str) -> List["Move"]:
        enemy_color = "B" if player_color == "W" else "W"
        possible_moves = []

        for j in range(self.m):
            for i in range(self.n):
                if self.board[j][i] == player_color:
                    #j-1, i; j, i+1; j+1, i; j, i-1
                    for direction_j, direction_i in [(-1, 0), (1, 0), (0, -1), (0,1)]:
                        new_j, new_i = j + direction_j, i + direction_i
                        if 0 <= new_j < self.m and 0 <= new_i < self.n and self.board[new_j][new_i] == enemy_color:
                                possible_moves.append(Move(i, j, new_i, new_j))

        return possible_moves
```

#### **Move**

A move consists of selecting a player's piece and moving it to an adjacent (orthogonal) cell containing an opponent's piece. The opponent's piece is removed, and the player piece occupies the new cell.

```python
@dataclass
class Move:
    from_x: int
    from_y: int
    to_x: int
    to_y: int
```

#### **Goal function**

The objective of the AI is to make moves that increase the chance of winning. The heuristic evaluation function estimates how favorable a given game state is for a player. It is based on factors such as:

- Number of available moves (mobility),
- Number of remaining pieces,
- Central control (preference for center tiles)

Below are implemented heuristics. They are calculated using weights. Weights change depending on the game progress.

**Implemented strategy:**

- EARLY GAME: mobility prioritization (available moves)
- MID GAME: middle control prioritization
- END GAME: piece count prioritization

```python
#eval methods
def evaluate(gamestate: GameState, player_color: str, rounds: int):
    h1 = mobility_heuristic(gamestate, player_color)
    h2 = piece_advantage_heuristic(gamestate, player_color)
    h3 = central_control_heuristic(gamestate, player_color)

    w1, w2, w3 = dynamic_weights(rounds)

    return w1 * h1 + w2 * h2 + w3 * h3


def dynamic_weights(rounds):
    base_weights = (1, 1, 1)
    if rounds < 10:
        return (base_weights[0] + 2, base_weights[1], base_weights[2])
    elif rounds < 20:
        return (base_weights[0], base_weights[1], base_weights[2] + 2)
    else:
        return (base_weights[0], base_weights[1] + 2, base_weights[2])


#heuristics implementation
def mobility_heuristic(state: GameState, player_color: str):
    return len(state.get_possible_moves(player_color))

def piece_advantage_heuristic(state: GameState, player_color: str):
    my_pieces = state.count_pieces(player_color)
    opponent_pieces = state.count_pieces("B" if player_color == "W" else "W")
    return my_pieces - opponent_pieces

def central_control_heuristic(state: GameState, player_color: str):
    height = len(state.board)
    width = len(state.board[0])
    center_row, center_col = height // 2, width // 2
    score = 0
    for r in range(height):
        for c in range(width):
            if state.board[r][c] == player_color:
                distance = abs(center_row - r) + abs(center_col - c)
                score += (height + width) - distance
    return score
```

#### **Decision Tree**

The decision tree is built using a depth-limited search. Each node represents a game state. It contains a move that led to the game state, its parent, its children (further possible gamestates) and a score, calculated using the heuristics.

The tree alternates between Max and Min levels. At a certain depth, the leaf nodes are evaluated heuristically.

```python
# node implementation

@dataclass
class Node:
    gamestate: GameState
    parent: Optional["Node"]
    move: Move
    children: List["Node"]
    score: int

    def __init__(self, gamestate, parent=None, move=None):
        self.gamestate = gamestate
        self.parent = parent
        self.move = move
        self.children = []
        self.score = 0

    def add_child(self, child_node):
        self.children.append(child_node)


@dataclass
class DecisionTree:
    root: Node
```

#### Minimax (traditional) implementation within the DecisionTree class

```python
def minimax(self, node: Node, depth: int, player_color: str, player_goal: str, rounds: int):

        #search tree from the node (root)
        #if childless node (leaf) or end of depth, we return for the player whos making the move
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
            max_evaluation = float("-inf")
            best_child = None

            for move in possible_moves:
                new_state = node.gamestate.copy()
                new_state.make_move(move)
                child = Node(gamestate=new_state, parent=node, move=move)
                if node == self.root:
                    node.add_child(child)
                evaluation = self.minimax(child, depth-1, opponent_color, opponent_goal, rounds)
                if evaluation > max_evaluation:
                    max_evaluation = evaluation
                    best_child = child
            node.score = max_evaluation
            if node == self.root:
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
```

#### Minimax with alpha-beta pruning implementation within the DecisionTree class

```python
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
```

#### **Game progress**

The game itself is played within a simple loop in main(). While the gameover condition wasn't met, the players keep making moves. The player who made the last viable move is the winner.

```python
def main():
    args = parse_args()

    #gameplay preparation
    player_classes = {"minimax": MinimaxPlayer, "random": RandomPlayer, "greedy": GreedyPlayer,}
    player1_class = player_classes.get(args.player1)
    player2_class = player_classes.get(args.player2)

    player1 = player1_class(color="B", goal="MAX", depth=args.depth, pruning=args.pruning) if player1_class == MinimaxPlayer else player1_class(color="B", goal="MAX")
    player2 = player2_class(color="W", goal="MIN", depth=args.depth, pruning=args.pruning) if player2_class == MinimaxPlayer else player2_class(color="W", goal="MIN")

    gamestate = GameState(n=args.n, m=args.m)
    rounds = 1
    current_player = player1
    gameover = False

    #gameplay
    while not gameover:
        print_round_info(rounds, current_player)

        possible_moves = gamestate.get_possible_moves(current_player.color)

        if possible_moves:
            move = current_player.choose_move(gamestate, rounds)
            gamestate.make_move(move)
            current_player = player2 if current_player == player1 else player1
            rounds += 1
            gamestate.print_board()
        else:
            print("No moves available left!")
            gameover = True

    winning_player = "Player1" if current_player == player2 else "Player2"
    print("Winner: ", winning_player)
    print("Round count: ", rounds)
```

#### **Players**

There are three different players defined in the game:

- MinimaxPlayer - playes "by the rules", using decision tree and minimax algorithm
- RandomPlayer - always chooses the random possible move
- GreedyPlayer - analyses all currently possible moves and makes the best one without looking forward into the future moves

```python
@dataclass
class MinimaxPlayer(Player):
    depth: int
    pruning: bool = False

    def choose_move(self, gamestate: GameState, rounds: int):
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
```

### 4. **Results**

#### Game length with two Minimax players (with pruning and depth=4), according to board size:

- 5x6 (default): ~10 seconds, 24 rounds
- 7x7: ~2 minutes, 30 rounds

#### Winrate of Minimax vs Greedy

- case MinimaxPlayer="B" (starts first): MinimaxPlayer wins pretty much every single time.
- case MinimaxPlayer="W" (starts second): MinimaxPlayer wins in around 50% of games.

A conclusion can be drawn that **Minimax leads to a better game performance than Greedy**.

Similar results are achieved with Minimax vs Random, although Minimax has a bigger winrate in such case.

### 5. Areas for improvement and further development

cProfile analysis shows that the most performance-heavy methods are:

- get_possible_moves() in GameState
- minimax() and alphabeta() in DecisionTree
- central_control_heuristic()

Further optimizations could be made there.

Also, more heuristics and a better weight system could be considered. More testing is needed.

### 6. Sources

    - https://en.wikipedia.org/wiki/Clobber
    - https://www.geeksforgeeks.org/minimax-algorithm-in-game-theory-set-4-alpha-beta-pruning/
    - https://docs.python.org/3/library/argparse.html
    - https://nesi.github.io/perf-training/python-scatter/profiling-cprofile
