# Reversi game mechanics author:
#   Dr inż. Piotr Syga
# Source:
#   https://syga.kft.pwr.edu.pl/courses/siiiw/reversi.py

import sys

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
            string_board += " ".join(row) + "\n"
    
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

    def get_valid_moves(self):
        moves = []
        for row in range(8):
            for col in range(8):
                if self.is_valid_move(row, col):
                    moves.append((row, col))
        return moves
    
    def is_valid_move(self, row, col):
        if self.board[row][col] != 0:
            return False
        for d_row in range(-1, 2):
            for d_col in range(-1, 2):
                if d_row == 0 and d_col == 0:
                    continue
                if self.is_valid_direction(row, col, d_row, d_col):
                    return True
        return False
    
    def is_valid_direction(self, row, col, d_row, d_col):
        opponent = 3 - self.current_player
        r, c = row + d_row, col + d_col
        if r < 0 or r >= 8 or c < 0 or c >= 8 or self.board[r][c] != opponent:
            return False
        while 0 <= r < 8 and 0 <= c < 8:
            if self.board[r][c] == 0:
                return False
            if self.board[r][c] == self.current_player:
                return True
            r, c = r + d_row, c + d_col
        return False
    
    def make_move(self, row, col):
        self.board[row][col] = self.current_player
        for d_row in range(-1, 2):
            for d_col in range(-1, 2):
                if d_row == 0 and d_col == 0:
                    continue
                if self.is_valid_direction(row, col, d_row, d_col):
                    self.flip_direction(row, col, d_row, d_col)
        self.current_player = 3 - self.current_player
    
    def flip_direction(self, row, col, d_row, d_col):
        r, c = row + d_row, col + d_col
        while self.board[r][c] != self.current_player:
            self.board[r][c] = self.current_player
            r, c = r + d_row, c + d_col
    
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
    def pieces_score(self):
        score = 0
        for row in self.board:
            for col in row:
                if col == self.current_player:
                    score += 1
        return score
    
    def flexibility_score(self):
        return len(self.get_valid_moves())
    
    def opponents_neighbors_score(self):
        score = 0
        opponent = 3 - self.current_player
        for row in range(8):
            for col in range(8):
                if self.board[row][col] == opponent:
                    neighbors = self.get_neighbors(row, col)
                    score += neighbors.count(self.current_player)
        return score
    
    def opportunities_score(self):
        score = 0
        opponent = 3 - self.current_player
        for row in range(8):
            for col in range(8):
                if self.board[row][col] == opponent:
                    neighbors = self.get_neighbors(row, col)
                    score += neighbors.count(0)
        return score

    def get_weighted_score(self, weight_list):
        return self.pieces_score()              * weight_list[0] + \
               self.flexibility_score()         * weight_list[1] + \
               self.opponents_neighbors_score() * weight_list[2] + \
               self.opportunities_score()       * weight_list[3]

    # Utility functions
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


def main():
    game = Reversi()
    print(game.get_neighbors(3,3))
    print(game.pieces_score())
    print(game.flexibility_score())
    print(game.opponents_neighbors_score())
    print(game.opportunities_score())
    counter = 0
    while True:
        valid_moves = game.get_valid_moves()
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
    main()
