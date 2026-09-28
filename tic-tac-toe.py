class Game:

    def __init__(self):
        self.player = "X"
        self.position = [str(i) for i in range(9)]
        self.score={"X":0,"O":0}

#print the board in 3x3format
    def board(self):
        print(f"\n {self.position[0]} | {self.position[1]} | {self.position[2]}")
        print("---|---|---")
        print(f" {self.position[3]} | {self.position[4]} | {self.position[5]}")
        print("---|---|---")
        print(f" {self.position[6]} | {self.position[7]} | {self.position[8]}")

#to reset the board to start a new game
    def reset(self):
        self.player = "X"
        self.position = [str(i) for i in range(9)]

#place the player's mark on the board
    def move(self, pos):
        try:        
            if pos == " ":
                print("empty input.Please enter an input between 0-8")
                return False
            pos=int(pos)
            if pos < 0 or pos > 8:
                print("Cell position must be between 0 and 8.")
                return False
            if self.position[pos] == "X" or self.position[pos] == "O":
                print(f"cell {pos} is already filled")
                return False

            self.position[pos] = self.player
            return True
        except IndexError:
            print("Cell position must be between 0 and 8.")
            return False

#to check whether a player has won
    def check_winner(self):
        winning_lines = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),(0, 3, 6), (1, 4, 7), (2, 5, 8),
            (0, 4, 8), (2, 4, 6)]
        for a, b, c in winning_lines:
            if self.position[a] == self.position[b] == self.position[c] and self.position[a] in ("X", "O"):
                return self.position[a]
        return None
#check whether the board is completely filled
    def cell_full(self):
        for cell in self.position:
            if cell != "X" and cell != "O":
                return False
        return True

game = Game() # Create an object of the Game class


def start():
    game.reset()
    print(" Welcome to tic-tac-toe ")
    print(" Let's begin the game ")

    while True:
        game.board()     
        print(f"now  player {game.player}'s turn ")

        while True:
            try:
                cell = input(f"enter the cell position from 0-8 to place {game.player}:- ")
                if game.move(cell):
                    break
            except ValueError:
                print("please enter an value between 0-8")

                
        winner = game.check_winner()
        if winner:
            game.board()
            print(f"Player {winner} wins!")
            game.score[winner] +=1
            break

        if game.cell_full():
            game.board()
            print("It's a draw!")
            break

        if game.player == "X":
            game.player = "O"
        else:
            game.player = "X"
        print('-'*87)


def main():
    while True:
        start()
        print("\n SCORE")
        print(f"Player X : {game.score['X']}")
        print(f"Player O : {game.score['O']}")
       
        while True:
            try:
                play=input("\nDo you want to play again? (yes/no): ").lower()
                if play=="y" or play =="yes":
                    break
                elif play =="n" or play=="no":
                    print("\n FINAL SCORE ")
                    print(f"Player X : {game.score['X']}")
                    print(f"Player O : {game.score['O']}")
                    
                    print("\nThank you for playing Tic-Tac-Toe!")
                    exit() 
                else: 
                    raise ValueError ("Enter yes or no ")
            except ValueError as e:
                print(e)


main()
