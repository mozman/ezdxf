# Copyright (c) 2018 Manfred Moitzi
# License: MIT License


class GaussianElimination(object):
    def __init__(self, matrix):
        self.matrix = matrix
        self.rank = len(matrix)
        self.x = [0.0] * self.rank

    def run(self):
        self.eliminate()
        self.substitute()

    def eliminate(self):
        a = self.matrix
        for i in range(self.rank):
            max_ = i
            for j in range(i + 1, self.rank):
                if abs(a[j][i]) > abs(a[max_][i]):
                    max_ = j
                tmp = a[i]
                a[i] = a[max_]
                a[max_] = tmp
            for j in range(i + 1, self.rank):
                tmp = a[j][i] / a[i][i]
                for k in reversed(range(self.rank)):
                    a[j][k] -= a[i][k] * tmp

    def substitute(self):
        a = self.matrix
        x = self.x
        for j in reversed(range(self.rank)):
            tmp = 0.0
            for k in range(j + 1, self.rank):
                tmp += a[j][k] * x[k]
            x[j] = (a[j][self.rank] - tmp) / a[j][j]


def gaussian_elimination(matrix):
    solver = GaussianElimination(matrix)
    solver.run()
    return solver.x
