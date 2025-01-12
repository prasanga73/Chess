import random

# assign the king any value which means you can't really lose
# your king as it would be a checkmate before that happened
pieceScore = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "p": 1}

# this is just a way to give some squares some prefrence than other when moving the each piece
knightScores = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 3, 3, 3, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 3, 3, 3, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
]

bishopScores = [
    [4, 3, 2, 1, 1, 2, 3, 4],
    [3, 4, 3, 2, 2, 3, 4, 3],
    [2, 3, 4, 3, 3, 4, 3, 2],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [2, 3, 4, 3, 3, 4, 3, 2],
    [3, 4, 3, 2, 2, 3, 4, 3],
    [4, 3, 2, 1, 1, 2, 3, 4],
]

queenScores = [
    [1, 1, 1, 3, 1, 1, 1, 1],
    [1, 2, 3, 3, 3, 1, 1, 1],
    [1, 4, 3, 3, 3, 4, 2, 1],
    [1, 2, 3, 3, 3, 2, 2, 1],
    [1, 2, 3, 3, 3, 2, 2, 1],
    [1, 4, 3, 3, 3, 4, 2, 1],
    [1, 1, 2, 3, 3, 1, 1, 1],
    [1, 1, 1, 3, 1, 1, 1, 1],
]

rockScores = [
    [4, 3, 4, 4, 4, 4, 3, 4],
    [4, 4, 4, 4, 4, 4, 4, 4],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [4, 4, 4, 4, 4, 4, 4, 4],
    [4, 3, 4, 4, 4, 4, 3, 4],
]

whitePawnScores = [
    [8, 8, 8, 8, 8, 8, 8, 8],
    [8, 8, 8, 8, 8, 8, 8, 8],
    [5, 6, 6, 7, 7, 6, 6, 5],
    [2, 3, 3, 5, 5, 3, 3, 2],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [1, 1, 1, 0, 0, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0],
]

blackPawnScores = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 0, 0, 1, 1, 1],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [2, 3, 3, 5, 5, 3, 3, 2],
    [5, 6, 6, 7, 7, 6, 6, 5],
    [8, 8, 8, 8, 8, 8, 8, 8],
    [8, 8, 8, 8, 8, 8, 8, 8],
]

# map eaching of the pieces to the appropriate 2d array
piecePositionScores = {
    "N": knightScores,
    "B": bishopScores,
    "Q": queenScores,
    "R": rockScores,
    "bp": blackPawnScores,
    "wp": whitePawnScores,
}

CHECKMATE = 1000
STALEMATE = 0
# represents how many moves the computer should look ahead
# before deciding on its best move
MAX_DEPTH = 4
nextMove = None


"""
this is created first to just test the AI moving the pieces
so it wouldn't really so much important to get those moves correct yet
"""


def piece_value(piece):
    values = {
        "p": 1,
        "N": 3,
        "B": 3,
        "R": 5,
        "Q": 9,
        "K": 0,  # The King has no value for the purposes of evaluation
    }
    if piece == "--":
        return 0
    piece_type = piece[1].lower()  # Ignore color (e.g., "wP" or "bP")
    return values.get(piece_type, 0)


def findRandomMoves(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]


"""
this is a helper method to make the first calls
for the actual algorithm
"""

import csv

# Function to load the CSV file into a list of openings
def load_openings(file_path):
    opening_moves = []
    with open(file_path, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        for row in reader:
            # Clean up the moves and split by spaces
            moves = row[0].strip().split(',')
            opening_moves.append(moves)
    return opening_moves

def find_best_move(openings, current_moves):
    # Loop through each opening sequence in the list

    for opening in openings:
        
        
        # Compare current moves with the opening's moves
        if current_moves == opening[:len(current_moves)]:  # Check if the current sequence matches the start of the opening
            if len(opening) > len(current_moves):  # If there's a next move in the sequence
                return opening[len(current_moves)]  # Return the next move
            else:
                return None  # No more moves in this opening
    return None  # No match found in any openings

def findBestMoveMinMax(gs, validMoves, returnQueue,currentmove):
    global nextMove
    nextMove = None
    print("current move is: ",currentmove)
    file_path = 'opening_table.csv'
    openings = load_openings(file_path)
    best_move = find_best_move(openings,currentmove)
    # print(currentmove)
    print("Best move is:",best_move)
    if best_move is not None:
        for move in validMoves:
            if best_move == str(move):
                returnQueue.put(move)
                return

    findMoveNegaMaxAlphaBeta(
        gs, validMoves, MAX_DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1
    )
    returnQueue.put(nextMove)
    # print(returnQueue.get())


"""
implementing the nega-max algorithm
"""


# # Initialize the history table as a dictionary, not a list
# history_table = {}

# def historyHeuristic(move):
#     # Retrieve the score for the move from the history table, default to 0 if not found
#     return history_table.get((move.startRow,move.startCol, move.endRow,move.endCol), 0)

# def updateHistory(move, score):
#     # Update the score for the given move in the history table
#     history_table[(move.startRow,move.startCol, move.endRow,move.endCol)] = score

def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove
    
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)

    # move ordering - could improve the algorithm a little bit
    capture_moves = []
    non_capture_moves = []

    # Separate capture moves and non-capture moves
    for move in validMoves:
        gs.makeMove(move)
        if move.pieceCaptured!="--":
            capture_moves.append(move)
        else:
            non_capture_moves.append(move)
        gs.undoMove()

    # Sort capture moves first by piece value, then by historical score
    # capture_moves.sort(key=lambda move: piece_value(move.pieceCaptured), reverse=True)
    
    # Combine capture moves and non-capture moves
    ordered_moves = capture_moves + non_capture_moves
    
    # print([str(move) for move in ordered_moves[:10]])  # Print the first 10 ordered moves
    
    maxScore = -CHECKMATE
    
    # Explore up to the first 10 moves (based on ordered list)
    for move in ordered_moves[:20]:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        
        # Recursively call NegaMax with Alpha-Beta pruning
        score = -findMoveNegaMaxAlphaBeta(
            gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier
        )
        
        # If we found a better score, update the maxScore and the best move
        if score > maxScore:
            maxScore = score
            if depth == MAX_DEPTH:
                nextMove = move
                print(move, score)  # Print the move and its score for debugging

        gs.undoMove()
        
        # Alpha-Beta pruning
        if maxScore > alpha:
            alpha = maxScore
            # if nextMove is not None:
            #     updateHistory(nextMove, maxScore)  # Update the history table with the move and score

        if alpha >= beta:
            break
    
    return maxScore

"""
a little bit more instructive score board method instead of
the naive solution that's implemented in scoreMaterial()
notes:
 1. postive score is good for white and negative score is good for black
"""


def scoreBoard(gs):
    # checking for those two basic cases here instead of doing
    # that in the findMoveMinMax()
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE  # black wins
        else:
            return CHECKMATE  # white wins
    elif gs.stalemate:
        return STALEMATE
    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != "--":
                pps = 0
                fac = 0.1
                color = square[0]
                piece = square[1]
                if piece != "K":
                    pps += (
                        piecePositionScores[piece if piece != "p" else square][row][col]
                        * fac
                    )
                if color == "w":
                    score += pieceScore[piece] + pps
                elif color == "b":
                    score -= pieceScore[piece] + pps
    return score
