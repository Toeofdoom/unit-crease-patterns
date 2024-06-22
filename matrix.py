import math
from vec import Vec

class Matrix:
    def __init__(self, data):
        self.data = data

    def __mul__(self, vec):
        els = [vec.x, vec.y, 1]
        x, y, _ = [sum([a * b for a, b in zip(els, row)]) for row in self.data]
        return Vec(x, y)

    def __matmul__(self, mat):  # This is almost certainly wrong
        cols = [
            [sum([a * b for a, b in zip(col, row)]) for row in self.data]
            for col in mat.transposed().data
        ]
        return Matrix(cols).transposed()

    def transposed(self):
        return Matrix([[self.data[j][i] for j in range(0, 3)] for i in range(0, 3)])


def identity():
    return Matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])


def rotate_around_point(point: Vec, angle_degrees):
    a = math.radians(angle_degrees)
    return Matrix(
        [
            [math.cos(a), -math.sin(a), point.x * 2],
            [math.sin(a), math.cos(a), point.y * 2],
            [0, 0, 1],
        ]
    )


def reflect_over_line(v1: Vec, v2: Vec):
    raise Exception("unimplemented")


def reflect_x_at(x):
    return Matrix([[-1, 0, x * 2], [0, 1, 0], [0, 0, 1]])


def reflect_y_at(y):
    return Matrix([[1, 0, 0], [0, -1, y * 2], [0, 0, 1]])


def offset_by(point: Vec):
    return Matrix([[1, 0, point.x], [0, 1, point.y], [0, 0, 1]])
