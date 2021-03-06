import numpy as np


class Board:
    EMPTY, BLACK, WHITE = 0, 1, -1
    print_EMPTY, print_BLACK, print_WHITE = '.', '■', '□'
    directions = [np.array([-1, 0]),
                  np.array([-1, 1]),
                  np.array([0, 1]),
                  np.array([1, 1]),
                  np.array([1, 0]),
                  np.array([1, -1]),
                  np.array([0, -1]),
                  np.array([-1, -1])]

    def __init__(self):
        self.reset()
        self.show_moves_BLACK = False
        self.show_moves_WHITE = False

    # self.board = np.array([[self.EMPTY]*8]*8)

    def reset(self):
        self.board = np.array([[self.EMPTY] * 8] * 8)
        self.board[3][3] = self.WHITE
        self.board[3][4] = self.BLACK
        self.board[4][3] = self.BLACK
        self.board[4][4] = self.WHITE
        self.frontier = [(2, 2, self.BLACK),
                         (2, 3, self.BLACK),
                         (4, 5, self.BLACK),
                         (5, 4, self.BLACK),
                         (5, 5, self.BLACK),
                         (3, 2, self.BLACK),
                         (3, 5, self.BLACK),
                         (2, 5, self.BLACK),
                         (2, 4, self.BLACK),
                         (5, 3, self.BLACK),
                         (5, 2, self.BLACK),
                         (4, 2, self.BLACK),
                         (2, 2, self.WHITE),
                         (2, 3, self.WHITE),
                         (4, 5, self.WHITE),
                         (5, 4, self.WHITE),
                         (5, 5, self.WHITE),
                         (3, 2, self.WHITE),
                         (3, 5, self.WHITE),
                         (2, 5, self.WHITE),
                         (2, 4, self.WHITE),
                         (5, 3, self.WHITE),
                         (5, 2, self.WHITE),
                         (4, 2, self.WHITE),
                         ]

    def inverted_board(self):
        return -1*self.board
       
    def check_move(self, row, column, player):
        if (row, column, player) in self.frontier and self.board[row][column] == self.EMPTY:
            for d in self.directions:
                pos = np.array([row, column])
                path_ok = 0
                for _ in range(8):
                    pos += d
                    if pos[0] < 0 or pos[0] >= 8 or pos[1] < 0 or pos[1] >= 8:
                        break

                    if self.board[pos[0]][pos[1]] == self.EMPTY or (
                            self.board[pos[0]][pos[1]] == player and path_ok == 0):
                        break

                    if self.board[pos[0]][pos[1]] == player * (-1):
                        path_ok = 1

                    if self.board[pos[0]][pos[1]] == player and path_ok == 1:
                        path_ok = 2
                        break

                if path_ok == 2:
                    return True
        return False

    def move(self, row, column, player):
        if self.check_move(row, column, player):
            flip_pieces = []
            for d in self.directions:
                pos = np.array([row, column])
                path_ok = 0
                temp_flip_pieces = []
                for _ in range(8):
                    pos += d
                    if pos[0] < 0 or pos[0] >= 8 or pos[1] < 0 or pos[1] >= 8:
                        break

                    if self.board[pos[0]][pos[1]] == self.EMPTY or (
                            self.board[pos[0]][pos[1]] == player and path_ok == 0):
                        break

                    if self.board[pos[0]][pos[1]] == player * (-1):
                        temp_flip_pieces.append((pos[0], pos[1]))
                        path_ok = 1

                    if self.board[pos[0]][pos[1]] == player and path_ok == 1:
                        path_ok = 2
                        break

                if path_ok == 2:
                    flip_pieces.extend(temp_flip_pieces)

            self.board[row][column] = player
            try:
                del self.frontier[self.frontier.index((row, column, player))]
            except:
                pass

            for p in flip_pieces:
                self.board[p[0]][p[1]] = player

            for d in self.directions:
                new_row = row + d[0]
                new_column = column + d[1]
                if 0 <= new_row < 8 and 0 <= new_column < 8 and self.board[new_row][new_column] == self.EMPTY and (
                new_row, new_column, (-1) * player) not in self.frontier:
                    self.frontier.append((new_row, new_column, (-1) * player))
                    self.frontier.append((new_row, new_column, player))

    def possible_moves(self, player):
        moves = []
        for row, col, pl in self.frontier:
            if pl == player and self.check_move(row, col, pl):
                moves.append((row, col, pl))
        return moves

    def finished(self):
        for move in self.frontier:
            if self.check_move(move[0], move[1], move[2]):
                return False
        return True

    def score(self):
        b = 0
        w = 0
        for i in range(8):
            for j in range(8):
                if self.board[i][j] == self.BLACK:
                    b += 1

                if self.board[i][j] == self.WHITE:
                    w += 1
        return (b, w)

    def __str__(self):
        s = ""
        for i in range(8):
            for j in range(8):
                if self.board[i][j] == self.EMPTY:
                    if (i, j, self.BLACK) in self.frontier and self.show_moves_BLACK and self.check_move(i, j,
                                                                                                         self.BLACK):
                        s += "+ "
                    elif (i, j, self.WHITE) in self.frontier and self.show_moves_WHITE and self.check_move(i, j,
                                                                                                           self.WHITE):
                        s += "x "
                    else:
                        s += self.print_EMPTY + " "
                if self.board[i][j] == self.BLACK:
                    s += self.print_BLACK + " "
                if self.board[i][j] == self.WHITE:
                    s += self.print_WHITE + " "
            s += "\n"
        return s
