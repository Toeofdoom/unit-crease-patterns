import math

class Vec:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def copy(self) -> "Vec":
        return Vec(self.x, self.y)
    
    @property
    def magnitude(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y)
    
    @property
    def normalised(self) -> float:
        return self * (1 / self.magnitude)
    
    def dot(self, other: "Vec") -> float:
        return self.x * other.x + self.y * other.y
    
    def __neg__(self):
        return Vec(-self.x, -self.y)
    
    def __mul__(self, n: float):
        return Vec(self.x * n, self.y * n)

    def __add__(self, v: "Vec"):
        return Vec(self.x + v.x, self.y + v.y)

    def __sub__(self, v: "Vec"):
        return Vec(self.x - v.x, self.y - v.y)

    def __div__(self, n: float | int):
        return Vec(self.x / n, self.y / n)

    @property
    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def dist(self, v: "Vec") -> float:
        return (self - v).length

    def __iter__(self):
        yield self.x
        yield self.y

    def __getitem__(self, key):
        if key == 0 or key == "x":
            return self.x
        if key == 1 or key == "y":
            return self.y
        raise IndexError
    
    def keys(self):
        return ["x","y"]

    def __repr__(self):
        return f"({self.x}, {self.y})"
    
    # supports quick unpacking for svg funcs
    # Also supports readers thinking "why would you do this??"

    @property
    def v1(self):
        return {"x1": self.x, "y1": self.y}

    @property
    def v2(self):
        return {"x2": self.x, "y2": self.y}

    @property
    def c(self):
        return {"cx": self.x, "cy": self.y}
    
    @property
    def bla(self):
        return Vec(f"{self.x.value}{self.x.unit}", f"{self.y.value}{self.y.unit}")