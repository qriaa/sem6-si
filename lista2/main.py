# Reversi game mechanics author:
#   Dr inż. Piotr Syga
# Source:
#   https://syga.kft.pwr.edu.pl/courses/siiiw/reversi.py

import sys
import copy

class Reversi:
    def __init__(self):
        self.board = [[0] * 8 for _ in range(8)]
        self.board[3][3] = self.board[4][4] = 1
        self.board[3][4] = self.board[4][3] = 2
        self.current_player = 1

    @classmethod
    def from_stdin(self):
        result_board = []
        while len(result_board) < 8:
            line = sys.stdin.readline().rstrip()
            if line != "":
                result_board.append(map(lambda str : int(str), line.split(" ")))
        self.current_player = self.determine_player_turn(result_board)
        self.board = result_board
    
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
                    case 0:
                        continue
                    case 1:
                        ones += 1
                    case 2:
                        twos += 1
        if ones == twos:
            return 1
        else:
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
               self.flexibility_score(pov)         * weight_list[1] + \
               self.opponents_neighbors_score(pov) * weight_list[2] + \
               self.opportunities_score(pov)       * weight_list[3]

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

class Minimax:

    class Node:
        def __init__(self, game, move):
            self.children = []
            self.score = 0
            self.game = game
            self.move = move

    def __init__(self, game, player, depth, strategy_table):
        self.player = player
        self.depth = depth
        self.strategy_table = strategy_table
        self.root = self.Node(copy.deepcopy(game), ())
        self.current = self.root
    
    def run(self, node, curr_depth):
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

        if node.game.current_player == self.player:
            max_score = float('-inf')
            for child in node.children:
                result = self.run(child, curr_depth+1)
                if result > max_score:
                    max_score = result
            node.score = max_score
            return max_score

        else:
            min_score = float('inf')
            for child in node.children:
                result = self.run(child, curr_depth+1)
                if result < min_score:
                    min_score = result
            node.score = min_score
            return min_score
    
    def make_best_move(self):
        self.run(self.current, 0)
        best_score = float('-inf')
        best_child = None
        for child in self.current.children:
            if child.score > best_score:
                best_score = child.score
                best_child = child
        self.current = best_child
        return best_child.move
    
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

    


                







def main2():
    game = Reversi()
    algo = Minimax(game, 2, 4, [1, 1, 1, 1])
    while True:
        valid_moves = game.get_valid_moves(game.current_player)
        if not valid_moves:
            counter += 1
            if counter == 2:
                break
            else:
                print("No valid moves")
                game.current_player = 3 - game.current_player
                continue
        if game.current_player == 1:
            print(f"Player {game.current_player}'s turn")
            print(game.to_string())
            print(f"Valid moves: {valid_moves}")
            row, col = map(int, input("Enter row and column: ").split())
            if (row, col) in valid_moves:
                game.make_move(row, col)
                algo.make_enemy_move((row, col))
            else:
                print("Invalid move")
                game.current_player = 3 - game.current_player
        else:
            print("Minmax's move")
            best_move = algo.make_best_move()
            print(f"Its move is: {best_move}")
            game.make_move(best_move[0], best_move[1])




def main():
    game = Reversi(1)
    counter = 0
    while True:
        valid_moves = game.get_valid_moves(game.current_player)
        if not valid_moves:
            counter += 1
            if counter == 2:
                break
            else:
                print("No valid moves")
                game.current_player = 3 - game.current_player
                continue
        print(f"Player {game.current_player}'s turn")
        print_board(game.board)
        print(f"Valid moves: {valid_moves}")
        row, col = map(int, input("Enter row and column: ").split())
        if (row, col) in valid_moves:
            game.make_move(row, col)
        else:
            print("Invalid move")
            game.current_player = 3 - game.current_player

    print_board(game.board)
    winner = game.get_winner()
    if winner == 0:
        print("It's a tie!")
    else:
        print(f"Player {winner} wins!")
    
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

if __name__ == "__main__":
    main2()
