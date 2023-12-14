"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    xCount = 0
    oCount = 0
    playerTurn = X

    for i in range(3):
        for j in range(3):
            if board[i][j] == X:
                xCount += 1
            elif board[i][j] == O:
                oCount += 1

    if xCount > oCount:
        playerTurn = O
    
    return playerTurn


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actionList = set()

    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                actionList.add((i, j))
    
    return actionList


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    result = copy.deepcopy(board)

    try:
        result[action[0]][action[1]] = player(board)
    except NameError:
        print('Invalid Action')
        raise

    return result


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Check rows
    if board[0][0] != EMPTY and board[0][0] == board[0][1] and board[0][0] == board[0][2]:
        return board[0][0]
    elif board[1][0] != EMPTY and board[1][0] == board[1][1] and board[1][0] == board[1][2]:
        return board[1][0]
    elif board[2][0] != EMPTY and board[2][0] == board[2][1] and board[2][0] == board[2][2]:
        return board[2][0]
    
    # Check columns
    elif board[0][0] != EMPTY and board[0][0] == board[1][0] and board[1][0] == board[2][0]:
        return board[0][0]
    elif board[0][1] != EMPTY and board[0][1] == board[1][1] and board[1][1] == board[2][1]:
        return board[0][1]
    elif board[0][2] != EMPTY and board[0][2] == board[1][2] and board[1][2] == board[2][2]:
        return board[0][2]
    
    # Check diagonals
    elif board[0][0] != EMPTY and board[0][0] == board[1][1] and board[1][1] == board[2][2]:
        return board[0][0]
    elif board[0][2] != EMPTY and board[0][2] == board[1][1] and board[1][1] == board[2][0]:
        return board[0][2]
    else:
        return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    isOver = False
    fullBoard = True

    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                fullBoard = False

    if winner(board) is not None or (fullBoard == True and winner(board) is None):
        isOver = True
    
    return isOver


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if (terminal(board)):
        if winner(board) == X:
            return 1
        elif winner(board) == O:
            return -1
        else:
            return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None

    if player(board) == X:
        _, move = max_value(board, -math.inf, math.inf)
        return move
    else:
        _, move = min_value(board, -math.inf, math.inf)
        return move

def max_value(board, alpha, beta):
    if terminal(board):
        return utility(board), None

    v = -math.inf
    move = None

    for action in actions(board):
        aux, _ = min_value(result(board, action), alpha, beta)
        if aux > v:
            v = aux
            move = action

        alpha = max(alpha, v)
        if alpha >= beta:
            break

        if v == 1:
            break

    return v, move

def min_value(board, alpha, beta):
    if terminal(board):
        return utility(board), None

    v = math.inf
    move = None

    for action in actions(board):
        aux, _ = max_value(result(board, action), alpha, beta)
        if aux < v:
            v = aux
            move = action

        beta = min(beta, v)
        if beta <= alpha:
            break

        if v == -1:
            break 

    return v, move