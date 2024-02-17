#!/usr/bin/env python3
#Importing libraries
from FourConnect import * 
import csv
import math

class GameTreePlayer:
    
    def __init__(self):
        self.number_of_calls = 0 #Storing number of recursive calls in the game

    def opponent_block_heuristic(self,board): #Heuristic to count number of top pieces of each player in every column and return a score based on it
        ply1 = 0 # Player 1 score
        ply2 = 0 # Player 2 score
        dict = {3:100, 4:80 , 2:80, 1:60, 5:60, 0:40, 6:40 } # Mapping each column to reward
        for col in range(7): #Iterate through every coumn
            for row in range(6): # Find the first non-occupied row
                if board[row][col] == 1:
                    ply1 = ply1 + dict[col] # Update player 1 score
                    break
                elif board[row][col] == 2:
                    ply2 = ply2 + dict[col] # Update player 2 score
                    break
        
        return ply2-ply1    


    def check_sequence(self,seq,player): # Helper function to check sequences and return a score based on it 
        if seq.count(player) == 3: # If three consecutive pieces of the player
            return 100
        elif seq.count(player) == 2 and seq.count(0) == 1: # If two pieces of the player and one empty place 
            return 80
        elif seq.count(player) == 2 and seq.count(0) == 0: # If two pieces of the player and no empty place
            return 40
        elif seq.count(player) == 1 and seq.count(0) == 2: # If only one piece of the player
            return 30
        else:
            return 10 # In other cases

    def sequence_count_heuristic(self,board): # Heuristic to check sequences of 3 vertically, horizontally and diagonally, and return a score based on it 
        ply2 = 0 # Player 2 score
        ply1 = 0 # Player 1 score

        # Getting sequence of three horizontally
        for row in range(6):
            for col in range(5):
                sequence = board[row][col:col + 3]
                ply1 = ply1 + self.check_sequence(sequence, 1)
                ply2 = ply2+ self.check_sequence(sequence, 2)
        
        # Getting sequence of three vertically
        for col in range(7):
            for row in range(4):
                sequence = [board[row + i][col] for i in range(3)]
                ply1 = ply1 + self.check_sequence(sequence, 1)
                ply2 = ply2+ self.check_sequence(sequence, 2)

        # Getting sequence of three diagonally
        for row in range(4):
            for col in range(5):
                sequence = [board[row + i][col + i] for i in range(3)]
                ply1 = ply1 + self.check_sequence(sequence, 1)
                ply2 = ply2+ self.check_sequence(sequence, 2)
    
        # Getting sequence of three diagonally    
        for row in range(2, 6):
            for col in range(5):
                sequence = [board[row - i][col + i] for i in range(3)]
                ply1 = ply1+ self.check_sequence(sequence, 1)
                ply2 = ply2 + self.check_sequence(sequence, 2)

        return ply2-ply1

    def column_weight_heuristic(self, board): # Heuristic to calculate number of pieces of each player in each column and assign a weighted reward
        score = 0 # Total score
        ply1 = 0 # Player 1 score
        ply2 = 0 # Player 2 score
        for col in range(7): # Counting number of pieces of each player in each column
            for row in range(6):
                if board[row][col] == 1:
                    ply1+=1
                elif board[row][col] == 2:
                    ply2+=1 
            
            # Center column has highest reward and reward decreases as we move away from the center
            # Update the score
            if col == 0 or col == 6:
                score = score + (ply2-ply1)*10
            elif col == 1 or col == 5:
                score = score + (ply2 - ply1)*40
            elif col == 2 or col == 4:
                score = score + (ply2-ply1)*60
            elif col == 3:
                score = score + (ply2 - ply1)*100
            
            # Reset for next column
            ply1 = 0
            ply2 = 0
        
        return score

    def evaluate_state(self, board):
        # Function to evaluate the state

        # Check for horizontal wins
        for row in range(len(board)):
            for col in range(len(board[0]) - 3):
                if board[row][col] == board[row][col + 1] == board[row][col + 2] == board[row][col + 3] and board[row][col] != 0:
                    return -1000000 if board[row][col] == 1 else 1000000

        # Check for vertical wins
        for col in range(len(board[0])):
            for row in range(len(board) - 3):
                if board[row][col] == board[row + 1][col] == board[row + 2][col] == board[row + 3][col] and board[row][col] != 0:
                    return -1000000 if board[row][col] == 1 else 1000000

        # Check for positively sloped diagonal wins
        for row in range(len(board) - 3):
            for col in range(len(board[0]) - 3):
                if board[row][col] == board[row + 1][col + 1] == board[row + 2][col + 2] == board[row + 3][col + 3] and board[row][col] != 0:
                    return -1000000 if board[row][col] == 1 else 1000000

        # Check for negatively sloped diagonal wins
        for row in range(3, len(board)):
            for col in range(len(board[0]) - 3):
                if board[row][col] == board[row - 1][col + 1] == board[row - 2][col + 2] == board[row - 3][col + 3] and board[row][col] != 0:
                    return -1000000 if board[row][col] == 1 else 1000000

        # If the current state not a winning state for either players, evaluate the state using any of the heuristics
        #Evaluation Function 1 
        #return self.opponent_block_heuristic(board)
    

        #Evaluation Function 2 : 
        #return self.column_weight_heuristic(board)

        #Evaluation Function 3: 
        return self.sequence_count_heuristic(board)

    def is_terminal(self, board): # Check if state is a terminal state either because of a winning state or no further possible moves
        return abs(self.evaluate_state(board)) == 1000000 or sum(row.count(0) for row in board) == 0

    def min_value(self,board, alpha, beta, depth): # Returns the min value of a node with alpha-beta pruning 
        self.number_of_calls+=1
        if depth == 0 or self.is_terminal(board):
            return self.evaluate_state(board)
        value = math.inf

        for col in range(len(board[0])):
            if board[0][col] == 0:
                new_board = [row[:] for row in board]
                for row in range(len(new_board) - 1, -1, -1):
                    if new_board[row][col] == 0:
                        new_board[row][col] = 1
                        break
                value = min(value, self.max_value(new_board, alpha, beta, depth - 1))
                beta = min(beta, value)
                if beta <= alpha:
                    break

        return value

    def max_value(self, board, alpha, beta, depth): # Returns the max value of a node with alpha-beta pruning 
        self.number_of_calls+=1
        if depth == 0 or self.is_terminal(board):
            return self.evaluate_state(board)
        
        value = -math.inf

        for col in range(len(board[0])):
            if board[0][col] == 0:
                new_board = [row[:] for row in board]
                for row in range(len(new_board) - 1, -1, -1):
                    if new_board[row][col] == 0:
                        new_board[row][col] = 2
                        break
                value = max(value, self.min_value(new_board, alpha, beta, depth - 1))
                alpha = max(alpha, value)
                if beta <= alpha:
                    break

        return value

    def get_best_move(self, board): # Return the best action using minimax algorithm for a given state
        alpha = -math.inf
        beta = math.inf
        best_move = -1
        max_val = -math.inf

        for col in range(len(board[0])):
            if board[0][col] == 0:
                new_board = [row[:] for row in board]
                for row in range(len(new_board) - 1, -1, -1):
                    if new_board[row][col] == 0:
                        new_board[row][col] = 2
                        break
                value = self.min_value(new_board, alpha, beta, 5)
                if value > max_val:
                    max_val = value
                    best_move = col

        return best_move
    

    def get_best_move_with_move_ordering(self, board): # Return the best action for a given state with move ordering
        alpha = -math.inf
        beta = math.inf
        best_move = -1
        max_val = -math.inf

        move_values = []

        # Appending (action, action_value) pairs to the move_values list 
        for col in range(len(board[0])): # Iterating through all possible columns/actions 
            if board[0][col] == 0: # If the column is filled and no empty spaces present
                new_board = [row[:] for row in board] # Deep copy of the current state
                for row in range(len(new_board) - 1, -1, -1): # Finding the first non-empty row
                    if new_board[row][col] == 0: # If an action is possible
                        new_board[row][col] = 2 # Simulate the AI player's move
                        move_value = self.column_weight_heuristic(new_board) # Get the state value
                        move_values.append((col, move_value)) # Append
                        break

        # Sort the actions based on move values
        move_values.sort(key=lambda x: x[1], reverse=True)

        # Return the best action using minimax algorithm with alpha-beta pruning
        for col, _ in move_values:
            new_board = [row[:] for row in board]  # Make a deep copy
            for row in range(len(new_board) - 1, -1, -1):
                if new_board[row][col] == 0:
                    new_board[row][col] = 2  # Simulate AI player's move
                    break

            value = self.min_value(new_board, alpha, beta, 3)
            if value > max_val:
                max_val = value
                best_move = col

        return best_move

    
    
    def FindBestAction(self,currentState): # Function to return the best action for AI player given the current state
        

        return self.get_best_move(currentState)

        #return self.get_best_move_with_move_ordering(currentState)



def LoadTestcaseStateFromCSVfile():
    testcaseState=list()

    with open(r'/Users/nishil/Documents/BITS/AI/Assignment 2 /assignment2/testcase_hard1.csv', 'r') as read_obj: 
       	csvReader = csv.reader(read_obj)
        for csvRow in csvReader:
            row = [int(r) for r in csvRow]
            testcaseState.append(row)
        return testcaseState


def PlayGame():

    # Function to simulate the game 
    
    wins = 0 # Track total wins
    loss = 0 # Track total losses
    draw = 0 # Track draws
    moves = [] # List of moves taken when won
    totalcalls = 0 # Track total recursive calls

    #Play 50 games 
    for i in range(50):
        fourConnect = FourConnect()
        fourConnect.PrintGameState()
        gameTree = GameTreePlayer()
 
        move=0
        while move<42: #At most 42 moves are possible
            if move%2 == 0: #Myopic player always moves first
                fourConnect.MyopicPlayerAction()
            else:
                currentState = fourConnect.GetCurrentState()
                gameTreeAction = gameTree.FindBestAction(currentState)
                fourConnect.GameTreePlayerAction(gameTreeAction)
            #fourConnect.PrintGameState()
            move += 1
            if fourConnect.winner!=None:
                break

        if fourConnect.winner==None:
            print("Game is drawn.")
        else:
            print("Winner : Player {0}\n".format(fourConnect.winner))
        print("Moves : {0}".format(move))

        if fourConnect.winner == 2:
            wins= wins+1
            moves.append(move)
        elif fourConnect.winner == 1:
            loss = loss + 1
        else:
            draw = draw + 1
        totalcalls+=gameTree.number_of_calls
        
    print("\n")
    print("Stats : Wins = {0} Losses = {1}  Draw = {2} \n".format(wins,loss,draw))
    avgmoves = sum(moves)/len(moves)
    print("Average moves per win : ", avgmoves)
    print("Average Recursive Calls Per Game : ", (totalcalls/50))




def RunTestCase():

    fourConnect = FourConnect()
    gameTree = GameTreePlayer()
    testcaseState = LoadTestcaseStateFromCSVfile()
    fourConnect.SetCurrentState(testcaseState)
    fourConnect.PrintGameState()

    move=0
    while move<5: #Player 2 must win in 5 moves
        if move%2 == 1: 
            fourConnect.MyopicPlayerAction()
        else:
            currentState = fourConnect.GetCurrentState()
            gameTreeAction = gameTree.FindBestAction(currentState)
            fourConnect.GameTreePlayerAction(gameTreeAction)
        fourConnect.PrintGameState()
        move += 1
        if fourConnect.winner!=None:
            break
    
    print("Roll no : 2021AAPS2499G")
    
    if fourConnect.winner==2:
        print("Player 2 has won. Testcase passed.")
    else:
        print("Player 2 could not win in 5 moves. Testcase failed.")
    print("Moves : {0}".format(move))
    

def main():
    
    #PlayGame()
    
    RunTestCase()


if __name__=='__main__':
    main()
