# Reversi game mechanics author:
#   Dr inż. Piotr Syga
# Source:
#   https://syga.kft.pwr.edu.pl/courses/siiiw/reversi.py

# Contains ANSI color codes!
# if you want to use this code's stdout i'd reccommend using sed or ansi2txt

import sys
import copy
import time
from colorama import Fore, Back
from colorama import init
init(autoreset=True)

def eprint(string):
    print(string, file=sys.stderr)

class Reversi:
    def __init__(self):
        self.board = [[0] * 8 for _ in range(8)]
        self.board[3][3] = self.board[4][4] = 1
        self.board[3][4] = self.board[4][3] = 2
        self.current_player = 1

    @classmethod
    def from_stdin(cls):
        result_board = []
        while len(result_board) < 8:
            line = sys.stdin.readline().rstrip()
            if line != "":
                result_board.append(map(lambda str : int(str), line.split(" ")))
        new_reversi = cls()
        new_reversi.current_player = new_reversi.determine_player_turn(result_board)
        new_reversi.board = result_board
        return new_reversi
    
    def to_string(self):
        string_board = ""
        for row in self.board:
            string_board += " ".join(map(str, row)) + "\n"
        return string_board
    
    def determine_player_turn(board):
        ones = 0
        twos = 0
        for row in board:
            for col in row:
                match col:
                    case 0: continue
                    case 1: ones += 1
                    case 2: twos += 1
        if ones == twos:
            return 1
        return 2

    def get_valid_moves(self, player):
        moves = []
        for row in range(8):
            for col in range(8):
                if self.is_valid_move(row, col, player):
                    moves.append((row, col))
        return moves
    
    def is_valid_move(self, row, col, player):
        if self.board[row][col] != 0:
            return False
        for d_row in range(-1, 2):
            for d_col in range(-1, 2):
                if d_row == 0 and d_col == 0:
                    continue
                if self.is_valid_direction(row, col, d_row, d_col, player):
                    return True
        return False
    
    def is_valid_direction(self, row, col, d_row, d_col, player):
        opponent = 3 - player
        r, c = row + d_row, col + d_col
        if r < 0 or r >= 8 or c < 0 or c >= 8 or self.board[r][c] != opponent:
            return False
        while 0 <= r < 8 and 0 <= c < 8:
            if self.board[r][c] == 0:
                return False
            if self.board[r][c] == player:
                return True
            r, c = r + d_row, c + d_col
        return False
    
    def make_move(self, row, col):
        self.board[row][col] = self.current_player
        for d_row in range(-1, 2):
            for d_col in range(-1, 2):
                if d_row == 0 and d_col == 0:
                    continue
                if self.is_valid_direction(row, col, d_row, d_col, self.current_player):
                    self.flip_direction(row, col, d_row, d_col)
        self.current_player = 3 - self.current_player
    
    def flip_direction(self, row, col, d_row, d_col):
        r, c = row + d_row, col + d_col
        while self.board[r][c] != self.current_player:
            self.board[r][c] = self.current_player
            r, c = r + d_row, c + d_col
    
    def finish_check(self):
        valid_moves = self.get_valid_moves(self.current_player)
        if valid_moves:
            return False
        valid_moves = self.get_valid_moves(3 - self.current_player)
        if valid_moves:
            return False
        return True
    
    def get_winner(self):
        counts = [0, 0, 0]
        for row in range(8):
            for col in range(8):
                counts[self.board[row][col]] += 1
        if counts[1] > counts[2]:
            return 1
        elif counts[2] > counts[1]:
            return 2
        else:
            return 0
    
    # Various strategy components
    def pieces_score(self, pov):
        score = 0
        for row in self.board:
            for col in row:
                if col == pov:
                    score += 1
        return score
    
    def flexibility_score(self, pov):
        return len(self.get_valid_moves(pov))
    
    def blocking_score(self, pov):
        return len(self.get_valid_moves(3 - pov))
    
    def opponents_neighbors_score(self, pov):
        score = 0
        opponent = 3 - pov
        for row in range(8):
            for col in range(8):
                if self.board[row][col] == opponent:
                    neighbors = self.get_neighbors(row, col)
                    score += neighbors.count(pov)
        return score
    
    def opportunities_score(self, pov):
        score = 0
        opponent = 3 - pov
        for row in range(8):
            for col in range(8):
                if self.board[row][col] == opponent:
                    neighbors = self.get_neighbors(row, col)
                    score += neighbors.count(0)
        return score

    def get_weighted_score(self, weight_list, pov):
        return self.pieces_score(pov)              * weight_list[0] + \
               self.blocking_score(pov)            * weight_list[1] + \
               self.flexibility_score(pov)         * weight_list[2] + \
               self.opponents_neighbors_score(pov) * weight_list[3] + \
               self.opportunities_score(pov)       * weight_list[4]

    # Utility
    def get_neighbors(self, row, col):
        neighbors = []
        origin = (row-1, col-1)
        size = (3, 3)
        if origin[0] < 0:
            origin = (0, origin[1])
            size = (size[0]-1, size[1])
        elif origin[0] + size[1] >= 8:
            origin = (6, origin[1])
            size = (size[0]-1, size[1])
        
        if origin[1] < 0:
            origin = (origin[0], 0)
            size = (size[0], size[1]-1)
        elif origin[1] + size[1] >= 8:
            origin = (origin[0], 6)
            size = (size[0], size[1]-1)
        

        for height in range(size[0]):
            for width in range(size[1]):
                scanned_point = (origin[0]+height, origin[1] + width)
                if scanned_point[0] == row and scanned_point[1] == col:
                    continue
                neighbors.append(self.board[scanned_point[0]][scanned_point[1]])
        return neighbors

class Searchtree:

    class Node:
        def __init__(self, game, move):
            self.children = []
            self.score = 0
            self.game = game
            self.move = move


    def __init__(self, game, player, depth, strategy_table, algo):
        self.player = player
        self.depth = depth
        self.strategy_table = strategy_table
        self.root = self.Node(copy.deepcopy(game), ())
        self.current = self.root
        match algo:
            case "minmax": self.run = lambda current_node: self.run_minmax(current_node, 0)
            case "alphabeta": self.run = lambda current_node: self.run_alphabeta(current_node, 0, float('-inf'), float('inf'))
        self.last_move_time = 0
        self.last_nodes_visited = 0
    
    def make_best_move(self):
        self.last_nodes_visited = 0
        start_time = time.process_time()
        self.run(self.current)
        end_time = time.process_time()
        self.last_move_time = end_time - start_time

        best_child = self.current.children[0]
        best_score = best_child.score
        for child in self.current.children:
            if child.score > best_score:
                best_score = child.score
                best_child = child
        self.current = best_child
        return best_child.move

    def get_algo_move_time(self):
        return self.last_move_time
    def get_algo_nodes_visited(self):
        return self.last_nodes_visited
    
    def make_enemy_move(self, move):
        for child in self.current.children:
            if child.move == move:
                self.current = child
                return

        new_game = copy.deepcopy(self.current.game)
        new_game.make_move(move[0], move[1])

        newChild = self.Node(new_game, move)

        self.current.children.append(newChild)
        self.current = newChild
    
    def make_children_for_node(self, node):
        for move in node.game.get_valid_moves(node.game.current_player):
            child_exists_flag = False
            for child in node.children:
                if child.move == move:
                    child_exists_flag = True
                    break
            if child_exists_flag:
                continue

            new_game = copy.deepcopy(node.game)
            new_game.make_move(move[0], move[1])

            node.children.append(
                self.Node(
                    new_game,
                    move)
                )

    def run_minmax(self, node, curr_depth):
        self.last_nodes_visited += 1
        if node.game.finish_check():
            winner = node.game.get_winner()
            if winner == 0:
                return 0
            elif winner == self.player:
                return float('inf')
            else:
                return float('-inf')
        
        if curr_depth == self.depth:
            return node.game.get_weighted_score(self.strategy_table, self.player)
        
        self.make_children_for_node(node)

        if node.game.current_player == self.player:
            max_score = float('-inf')
            for child in node.children:
                result = self.run_minmax(child, curr_depth+1)
                if result > max_score:
                    max_score = result
            node.score = max_score
            return max_score

        else:
            min_score = float('inf')
            for child in node.children:
                result = self.run_minmax(child, curr_depth+1)
                if result < min_score:
                    min_score = result
            node.score = min_score
            return min_score


    def run_alphabeta(self, node, curr_depth, alpha, beta):
        self.last_nodes_visited += 1
        if node.game.finish_check():
            winner = node.game.get_winner()
            if winner == 0:
                return 0
            elif winner == self.player:
                return float('inf')
            else:
                return float('-inf')
        
        if curr_depth == self.depth:
            return node.game.get_weighted_score(self.strategy_table, self.player)
        
        self.make_children_for_node(node)

        if node.game.current_player == self.player:
            for child in node.children:
                result = self.run_alphabeta(child, curr_depth+1, alpha, beta)
                if result > alpha:
                    alpha = result
                if alpha >= beta:
                    node.score = alpha
                    return alpha
            node.score = alpha
            return alpha

        else:
            for child in node.children:
                result = self.run_alphabeta(child, curr_depth+1, alpha, beta)
                if result < beta:
                    beta = result
                if alpha >= beta:
                    node.score = beta
                    return beta
            node.score = beta
            return beta




class Game:

    class Player:
        def __init__(self, tag, get_move_fun, enemy_move_fun, metadata_getter):
            self.tag = tag
            self.move_fun = get_move_fun
            self.enemy_move_fun = enemy_move_fun
            self.metadata_getter = metadata_getter


        @classmethod
        def get_human_player(cls):
            def get_human_move():
                row, col = map(int, input("Enter row and column: ").split())
                return (row, col)
            return cls("human", get_human_move, None, None)

        @classmethod
        def get_minmax_player(cls, minmax_searchtree):
            return cls("bot",
                       minmax_searchtree.make_best_move,
                       minmax_searchtree.make_enemy_move,
                       (minmax_searchtree.get_algo_move_time,
                            minmax_searchtree.get_algo_nodes_visited))

        @classmethod
        def get_alphabeta_player(cls, alphabeta_searchtree):
            return cls("bot",
                       alphabeta_searchtree.make_best_move,
                       alphabeta_searchtree.make_enemy_move,
                       (alphabeta_searchtree.get_algo_move_time,
                            alphabeta_searchtree.get_algo_nodes_visited))

        def get_move(self):
            return self.move_fun()
        
        def enemy_move(self, move):
            if self.enemy_move_fun is None:
                return
            self.enemy_move_fun(move)
        
        def get_metadata(self):
            if self.metadata_getter == None:
                return
            return (self.metadata_getter[0](), self.metadata_getter[1]())


    def __init__(self, reversi, player1, player2):
        self.game = reversi
        self.player1 = player1
        self.player2 = player2
        self.rounds = 0

    
    def play(self):
        counter = 0
        while True:
            valid_moves = self.game.get_valid_moves(self.game.current_player)
            if not valid_moves:
                counter += 1
                if counter == 2:
                    break
                else:
                    print("No valid moves")
                    self.game.current_player = 3 - self.game.current_player
                    continue
            counter = 0
            self.rounds += 1

            color_board(self.game.board)

            active_player = None
            match self.game.current_player:
                case 1: active_player = self.player1
                case 2: active_player = self.player2
            if active_player.tag == "human":
                print(f"Valid moves: {valid_moves}")

            print(f"Player {self.game.current_player}'s turn:")
            match self.game.current_player:
                case 1: move = self.player1.get_move()
                case 2: move = self.player2.get_move()
            print(f"Player {self.game.current_player}'s move is: {move}")
            if move in valid_moves:
                self.game.make_move(*move)
                match self.game.current_player:
                    # Game has already changed current_player,
                    # therefore players below are not swapped
                    case 1: self.player1.enemy_move(move)
                    case 2: self.player2.enemy_move(move)
            else:
                print("Invalid move")
                self.game.current_player = 3 - self.game.current_player
            

            if active_player.tag == "bot":
                move_metadata = active_player.get_metadata()
                eprint(f"Time to calculate: {round(move_metadata[0], 6)}; Nodes visited: {move_metadata[1]}")

        color_board(self.game.board)
        winner = self.game.get_winner()
        if winner == 0:
            print("Tie.")
        else:
            print(f"Player {winner} wins. Rounds: {self.rounds}")

def print_board(board):
    print("   0 1 2 3 4 5 6 7 ")
    print("  +-+-+-+-+-+-+-+-+")
    for row in range(8):
        print(row, end=" |")
        for col in range(8):
            if board[row][col] == 0:
                print("0", end="|")
            elif board[row][col] == 1:
                print("1", end="|")
            else:
                print("2", end="|")
        print("\n  +-+-+-+-+-+-+-+-+")

def color_board(board):
    for row in range(8):
        for col in range(8):
            match board[row][col]:
                case 0: print(Back.LIGHTBLACK_EX + "0", end="")
                case 1: print(Back.WHITE + "1", end="")
                case 2: print(Fore.WHITE + Back.BLACK + "2", end="")
            print(Back.LIGHTBLACK_EX + " ", end="")
        print()

def validate_player(input):
    if input in ("human", "minmax", "alphabeta"):
        return True
    else:
        return False


if __name__ == "__main__":
    print("REVERSI")
    reversi = Reversi()

    available_strategies = {
        "aggressive": [4.0, 2.0, 0.5, 1.5, 2.0],
        "controlling": [1.0, 5.0, 5.0, 1.0, 1.0],
        "balanced": [1.0, 2.0, 2.0, 1.0, 1.0],
        "custom": None
    }
    available_weights = ["pieces", "flexibility", "blocking", "opponents' neighbors", "opportunities"]

    player_types = []
    algorithms = [None, None]
    for n in range(1,3):
        while True:
            player = input(f"Player {n} is a [human, minmax, alphabeta]: ")
            if validate_player(player.lower()):
                break
        weight_table = None
        if player in ("minmax, alphabeta"):
            depth = 1
            while True:
                try:
                    depth = int(input("Choose search depth for the algorithm: "))
                except ValueError:
                    continue
                break

            print("Available strategies: ")
            for key, val in available_strategies.items():
                print(f"{key}: {val}")
            while True:
                choice = input(f"Choose a strategy for the bot: ")
                if choice in available_strategies.keys():
                    break
            if choice != "custom":
                weight_table = available_strategies[choice]
            else:
                weight_table = []
                for weight in available_weights:
                    while True:
                        try:
                            val = float(input(f"Input weight of {weight} score as float: "))
                            weight_table.append(val)
                            break
                        except ValueError:
                            continue
            algorithms[n-1] = Searchtree(
                reversi,
                n,
                depth,
                weight_table,
                player
            )
        player_types.append(player)
    players = []
    for i in range(2):
        match player_types[i]:
            case "human":
                players.append(Game.Player.get_human_player())
            case "minmax":
                players.append(Game.Player.get_minmax_player(algorithms[i]))
            case "alphabeta":
                players.append(Game.Player.get_alphabeta_player(algorithms[i]))
    
    game = Game(reversi, players[0], players[1])
    game.play()




    
    


