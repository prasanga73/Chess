"""
This is our maon driver. It will be responsible for handling user input
and displaying the current GameState object.
"""
import sys
import time

sys.path.append(".")

# from Chess import ChessEngine, SmartMoveFinder
import ChessEngine
import SmartMoveFinder

from ChessEngine import *
from SmartMoveFinder import *
import pygame as p
import os
from multiprocessing import Process, Queue

# our current path information:
current_path = os.path.dirname(__file__)  # Where your .py file is located
image_path = os.path.join(current_path, "images")  # The image folder path

# 400 is another good option and it depends on how good the
# images you have in terms of quality and resolution and 512 is a power of 2
BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 270
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
# the chess board is 8x8 :)
DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
# for animation later on
MAX_FPS = 15
IMAGES = {}


"""
As loading the images can be a costly process, we need to
initialize a global dictonary for images just once in the main.
Also, we put the loading images code in its own function, so we could
adapt that code easily later on or add another piece sets !!
"""


def loadImages():
    pieces = ["wp", "wN", "wB", "wR", "wQ", "wK", "bp", "bN", "bB", "bR", "bQ", "bK"]
    for piece in pieces:
        img = os.path.join(image_path, piece + ".png")
        IMAGES[piece] = p.transform.scale(p.image.load(img), (SQ_SIZE, SQ_SIZE))


""" The follwoing is the drive of our code which will handle user inputs and updating the graphics """

def menu_screen():
    """
    Displays the menu screen and lets the user select the game mode.
    Returns True if Player vs Player is selected, False if Player vs AI is selected.
    """
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    p.display.set_caption("Chess - Select Mode")
    clock = p.time.Clock()
    font = p.font.SysFont("Arial", 32)
    running = True
    while running:
        screen.fill(p.Color("white"))
        
        # Draw buttons
        p.draw.rect(screen, p.Color("lightblue"), p.Rect(100, 200, 300, 50))  # PvP Button
        p.draw.rect(screen, p.Color("lightgreen"), p.Rect(100, 300, 300, 50))  # PvAI Button
        
        # Draw button text
        pvp_text = font.render("Player vs Player", True, p.Color("black"))
        pvai_text = font.render("Player vs AI", True, p.Color("black"))
        screen.blit(pvp_text, (120, 210))
        screen.blit(pvai_text, (120, 310))
        
        p.display.flip()
        clock.tick(30)
        
        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                sys.exit()
            elif e.type == p.MOUSEBUTTONDOWN:
                x, y = e.pos
                if 100 <= x <= 400 and 200 <= y <= 250:  # PvP Button Clicked
                    return True
                elif 100 <= x <= 400 and 300 <= y <= 350:  # PvAI Button Clicked
                    return False

current_move = []
def main():
    p.init()
    # Display the menu screen and get user choice
    playerTwo = menu_screen()  # Player vs Player if True, Player vs AI if False
    playerOne = True  # Both players are human in PvP mode; one AI in PvAI mode
    
    p.display.set_caption("Chess")
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    moveLogFont = p.font.SysFont("Arial", 20, False, False)
    gs = GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    animate = False
    loadImages()
    running = True
    sqSelected = ()
    playerClicks = []
    gameOver = False
    AIThinking = False
    moveFinderProcess = None
    moveUndone = False
    
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col) or col >= 8:
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2 and humanTurn:
                        move = Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
        # key handler

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: # undo when 'z' is pressed
                    gs.undoMove()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = True
                    animate = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True
                if e.key == p.K_r:  # reset the game when 'r' is pressed
                    gs = GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    running = True
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = False


        # AI move finder

        if not gameOver and not humanTurn and not moveUndone:
            if not AIThinking:
                AIThinking = True
                returnQueue = Queue()
                current_move.append(str(gs.moveLog[-1]))
                moveFinderProcess = Process(
                    target=SmartMoveFinder.findBestMoveMinMax,
                    args=(gs, validMoves, returnQueue,current_move),
                )
                moveFinderProcess.start()
            if not moveFinderProcess.is_alive():
                AIMove = returnQueue.get()
                if AIMove is None:
                    AIMove = SmartMoveFinder.findRandomMoves(validMoves)
                current_move.append(str(AIMove))
                gs.makeMove(AIMove)
                moveMade = True
                animate = True
                AIThinking = False

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
            moveUndone = False
            
        drawGameState(screen, gs, validMoves, sqSelected, moveLogFont)
        if gs.checkmate or gs.stalemate:
            gameOver = True
            text = (
                "Stalemate"
                if gs.stalemate
                else "Black wins by checkmate"
                if gs.whiteToMove
                else "White wins by checkmate"
            )
            drawEndGameText(screen, text)
        clock.tick(MAX_FPS)
        p.display.flip()


def drawGameState(screen, gs, validMoves, sqSelected, moveLogFont):
    drawBoard(screen)  # draw the squares on the board right :)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)  # just draw the pieces on the top of the board
    drawMoveLog(screen, gs, moveLogFont)


def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(
                screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            )


""" highlight the square selected and valid moves for the piece selected """


def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        # make sure that each user can use highlighting ability for its own pieces
        if gs.board[r][c][0] == ("w" if gs.whiteToMove else "b"):
            # 1. highlight the selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(
                100
            )  # zero value is full transparentand 255 means no transperency
            s.fill(p.Color("blue"))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            # 2. highlight moves from that selected square
            s.fill(p.Color("yellow"))
            for move in validMoves:
                if (
                    move.startRow == r and move.startCol == c
                ):  # then those are the valid moves for that particular piece
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":  # it's really a piece and not an empty square
                screen.blit(
                    IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                )


""" the animation function """


def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10  # frames to move one square
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (
            move.startRow + dR * frame / frameCount,
            move.startCol + dC * frame / frameCount,
        )
        drawBoard(screen)
        drawPieces(screen, board)
        # erase the move from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(
            move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE
        )
        p.draw.rect(screen, color, endSquare)
        # draw the captured piece back onto the top of the rect
        if move.pieceCaptured != "--":
            if move.isEnpassantMove:
                enpassantRow = (
                    (move.endRow + 1)
                    if move.pieceCaptured[0] == "b"
                    else (move.endRow - 1)
                )
                endSquare = p.Rect(
                    move.endCol * SQ_SIZE, enpassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE
                )
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # draw the moving piece
        screen.blit(
            IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        )
        p.display.flip()
        clock.tick(120)


def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, p.Color("Gray"))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(
        BOARD_WIDTH / 2 - textObject.get_width() / 2,
        BOARD_HEIGHT / 2 - textObject.get_height() / 2,
    )
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color("Black"))
    screen.blit(textObject, textLocation.move(2, 2))


def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i // 2 + 1) + ". " + str(moveLog[i]) + " "
        if i + 1 < len(moveLog):
            moveString += str(moveLog[i + 1])
        moveTexts.append(moveString)
    padding = 5
    textY = padding
    lineSpacing = 5
    movesPerRow = 3
    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i + j] + "  "
        textObject = font.render(text, True, p.Color("white"))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing


if __name__ == "__main__":
    main()
