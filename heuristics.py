from gamestate import GameState

#positional - closer to the center=better
#movecount - more available moves=better
#piecedifference - more of my pieces=better

#evaluation method
def evaluate(gamestate: GameState, player_color: str, rounds: int):
    h1 = mobility_heuristic(gamestate, player_color)
    h2 = piece_advantage_heuristic(gamestate, player_color)
    h3 = central_control_heuristic(gamestate, player_color)
    
    w1, w2, w3 = dynamic_weights(rounds)

    return w1 * h1 + w2 * h2 + w3 * h3
    
    
#heuristics
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
                #smaller distance = bigger score
                score += (height + width) - distance
    return score


#weighted heuristics, based on the game pacing
def dynamic_weights(rounds):
    base_weights = (1, 1, 1)
    #EARLY GAME: mobility, MID GAME: control, END GAME: piece count
    if rounds < 10:
        return (base_weights[0] + 2, base_weights[1], base_weights[2])
    elif rounds < 20:
        return (base_weights[0], base_weights[1], base_weights[2] + 2)
    else:
        return (base_weights[0], base_weights[1] + 2, base_weights[2])

   