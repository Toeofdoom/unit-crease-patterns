import math
from vec import Vec

class Line:
    def __init__(self, v1: Vec, v2: Vec):
        self.v1 = v1
        self.v2 = v2

    @property
    def angle_radians(self) -> float:
        direction = self.v1 - self.v2
        return math.atan(direction.y / direction.x)

    def intersection(self, other: "Line"):
        xdiff = (self[0][0] - self[1][0], other[0][0] - other[1][0])
        ydiff = (self[0][1] - self[1][1], other[0][1] - other[1][1])

        def det(a, b):
            return a[0] * b[1] - a[1] * b[0]

        div = det(xdiff, ydiff)
        if div == 0:
            raise Exception("lines do not intersect")

        d = (det(*self), det(*other))
        x = det(d, xdiff) / div
        y = det(d, ydiff) / div
        return Vec(x, y)

    def __getitem__(self, key):
        if key == 0:
            return self.v1
        if key == 1:
            return self.v2
        if key == "x1":
            return self.v1.x
        if key == "y1":
            return self.v1.y
        if key == "x2":
            return self.v2.x
        if key == "y2":
            return self.v2.y
        raise IndexError
    
    def keys(self):
        return ["x1","y1","x2","y2"]

    def __len__(self):
        return 2

    def __repr__(self):
        return f"({self.v1}, {self.v2})"
    
    def as_vec_d(self) -> tuple[Vec, float]:
        y = (self.v2.x - self.v1.x)
        x = -(self.v2.y - self.v1.y)
        d = y * self.v1.y + self.v1.x*x
        return Vec(x, y), d




