import math
from vec import Vec
from line import Line
from bezier import Bezier


class Matrix:
    def __init__(self, data):
        self.data = data

    def multiply_direction(self, other: Vec):
        els = [other.x, other.y, 0]
        x, y, _ = [sum([a * b for a, b in zip(els, row)]) for row in self.data]
        return Vec(x, y)

    def __mul__(self, other):
        if type(other) is Vec:
            els = [other.x, other.y, 1]
            x, y, _ = [sum([a * b for a, b in zip(els, row)]) for row in self.data]
            return Vec(x, y)
        if type(other) is Line:
            return Line(self * other.v1, self * other.v2)
        if type(other) is Bezier:
            return Bezier([self * v for v in other.control_points])
        raise Exception()

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
    return offset_by(point) @ Matrix(
        [
            [math.cos(a), -math.sin(a), 0],
            [math.sin(a), math.cos(a), 0],
            [0, 0, 1],
        ] 
    ) @ offset_by(-point)

def scale_around_point(point: Vec, scaling_factor):
    return offset_by(point) @ Matrix(
        [
            [scaling_factor, 0, 0],
            [0, scaling_factor, 0],
            [0, 0, 1],
        ] 
    ) @ offset_by(-point)


def reflect_over_line(l: Line):
    dir = l.direction.normalised
    tan = l.tangent.normalised
    # 0 degrees, (1, 0)
    # 45 degrees, (sqrt2, sqrt2)
    # 90 degrees, (0, 1)
    # dir.x * dot
    # x * dir.x , y
    # dir.dot(v) -> maintained
    # tan.dot(v) -> reflected

    centred_matrix = Matrix(
        [
            [dir.x * dir.x - tan.x * tan.x, dir.x * dir.y - tan.x * tan.y, 0],
            [dir.y * dir.x - tan.y * tan.x, dir.y * dir.y - tan.y * tan.y, 0],
            [0, 0, 1],
        ]
    )

    return offset_by(l.v1) @ centred_matrix @ offset_by(-l.v1)


def reflect_x_at(x):
    return Matrix([[-1, 0, x * 2], [0, 1, 0], [0, 0, 1]])


def reflect_y_at(y):
    return Matrix([[1, 0, 0], [0, -1, y * 2], [0, 0, 1]])


def offset_by(point: Vec):
    return Matrix([[1, 0, point.x], [0, 1, point.y], [0, 0, 1]])
