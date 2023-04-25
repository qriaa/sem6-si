# Autor mechaniki Reversi:
#   Dr inż. Piotr Syga
# Źródło:
#   https://syga.kft.pwr.edu.pl/courses/siiiw/reversi.py


class Reversi:
    def __init__(self):
        self.board = [[0] * 8 for _ in range(8)]
        self.board[3][3] = self.board[4][4] = 1
        self.board[3][4] = self.board[4][3] = 2
        self.current_player = 1
    
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

def main():
    game = Reversi()
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
