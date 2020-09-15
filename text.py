from typing import List


class Solution:

    def solveSudoku(self, board: List[List[str]]) -> None:
        """
        Do not return anything, modify board in-place instead.
        """
        rows = [[True]*10 for i in range(10)]
        cols = [[True]*10 for i in range(10)]
        subs = [[True]*10 for i in range(10)]

        def getSubIndex(i, j):
            return 3*int(i/3)+int(j/3)

        def findNext(row, col):
            for i in range(row, 9):
                if i == row:
                    for j in range(col+1, 9):
                        if board[i][j] == ".":
                            return i, j
                else:
                    for j in range(9):
                        if board[i][j] == ".":
                            return i, j
            return 9, 0

        def backtrace(row, col):

            if row == 9:
                return True

            nr, nc = findNext(row, col)
            subIndex = getSubIndex(row, col)
            for i in range(1, 10):
                if rows[row][i] and cols[col][i] and subs[subIndex][i]:
                    rows[row][i] = False
                    cols[col][i] = False
                    subs[subIndex][i] = False
                    board[row][col] = str(i)

                    flag = backtrace(nr, nc)
                    if flag:
                        return True

                    board[row][col] = "."
                    rows[row][i] = True
                    cols[col][i] = True
                    subs[subIndex][i] = True

        for i in range(9):
            for j in range(9):
                if not board[i][j] == '.':
                    rows[i][int(board[i][j])] = False
                    cols[j][int(board[i][j])] = False
                    subs[getSubIndex(i, j)][int(board[i][j])] = False

        if board[0][0] == ".":
            backtrace(0, 0)
        else:
            row, col = findNext(0, 0)
            backtrace(row, col)


if __name__ == "__main__":
    pass
    solution = Solution()
    grid = [["5", "3", ".", ".", "7", ".", ".", ".", "."], ["6", ".", ".", "1", "9", "5", ".", ".", "."], [".", "9", "8", ".", ".", ".", ".", "6", "."], ["8", ".", ".", ".", "6", ".", ".", ".", "3"], ["4", ".", ".", "8",
                                                                                                                                                                                                         ".", "3", ".", ".", "1"], ["7", ".", ".", ".", "2", ".", ".", ".", "6"], [".", "6", ".", ".", ".", ".", "2", "8", "."], [".", ".", ".", "4", "1", "9", ".", ".", "5"], [".", ".", ".", ".", "8", ".", ".", "7", "9"]]
    # print(solution.findNext(0, 2, grid))
    solution.solveSudoku(grid)
    for i in range(9):
        print(grid[i])
