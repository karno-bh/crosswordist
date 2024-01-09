from math import sin, cos, pi


class WrongMatrixDimension(Exception):
    pass


class FlatMatrix:

    def __init__(self, width: int, height: int, new_state=None, initial_val=0):

        self._width = width
        self._height = height
        if new_state:
            self._data = new_state
        else:
            self._data = [initial_val for _ in range(width * height)]

    @property
    def data(self):
        return list(self._data)

    def __idx(self, i: int, j: int):
        return j * self._width + i

    def get(self, i: int, j: int):
        return self._data[self.__idx(i, j)]

    def set(self, i: int, j: int, val, clone=True):
        if clone:
            new_state = list(self._data)
            new_state[self.__idx(i, j)] = val
            return FlatMatrix(self._width, self._height, new_state)
        self._data[self.__idx(i, j)] = val
        return self

    def out_of_range(self, i, j):
        max_horizontal = self._width - 1
        max_vertical = self._height - 1
        return j < 0 or j > max_vertical or i < 0 or i > max_horizontal

    def __eq__(self, other):
        return self._data == other._data

    def __str__(self):
        buf = []
        for j in range(self._height):
            for i in range(self._width):
                placeholder = "{0}" if i == 0 else " {0}"
                buf += placeholder.format(self._data[self.__idx(i, j)])
            buf += "\n"
        return ''.join(buf)

    def pretty_log(self, replace):
        buf = []
        for j in range(self._height - 1, -1, -1):
            for i in range(self._width):
                placeholder = "{0}" if i == 0 else " {0}"
                buf += placeholder.format(replace[self._data[self.__idx(i, j)]])
            buf += "\n"
        return ''.join(buf)

    def __mul__(self, other):
        if isinstance(other, FlatMatrix):
            if self._width != other._height:
                raise WrongMatrixDimension("Other instance is FlatMatrix "
                                           "but current matrix width != other matrix height")
            result = FlatMatrix(self._height, other._width)
            possible_zero = 0
            if isinstance(self._data[0], float):
                possible_zero = 0.0
            for i in range(self._height):
                for j in range(other._width):
                    res_el = possible_zero
                    for k in range(self._width):
                        res_el += self.get(k, i) * other.get(j, k)
                    result.set(j, i, res_el, clone=False)
            return result

        if isinstance(other, list):
            if self._width != len(other):
                raise WrongMatrixDimension("Other instance is list but "
                                           "current matrix width != other list length")
            possible_zero = 0
            if isinstance(self._data[0], float):
                possible_zero = 0.0
            result = []
            for i in range(self._height):
                res_el = possible_zero
                for j in range(self._width):
                    res_el += self.get(j, i) * other[j]
                result.append(res_el)
            return result

        raise TypeError("Either FlatMatrix or list are supported")


def identity(elem_type=int):
    data = [
        1, 0, 0,
        0, 1, 0,
        0, 0, 1,
    ]
    if elem_type is not int:
        data = [elem_type(e) for e in data]
    return FlatMatrix(3, 3, new_state=data)


def translate(x, y, elem_type=int):
    data = [
        1, 0, x,
        0, 1, y,
        0, 0, 1,
    ]
    if elem_type is not int:
        data = [elem_type(e) for e in data]
    return FlatMatrix(3, 3, new_state=data)


def scale(w, h, elem_type=int):
    data = [
        w, 0, 0,
        0, h, 0,
        0, 0, 1,
    ]
    if elem_type is not int:
        data = [elem_type(e) for e in data]
    return FlatMatrix(3, 3, new_state=data)


def rotate(theta, elem_type=float):
    data = [
        cos(theta), -sin(theta), 0.,
        sin(theta),  cos(theta), 0.,
        0.,          0., 1.,
    ]
    if elem_type is not float:
        data = [elem_type(e) for e in data]
    return FlatMatrix(3, 3, new_state=data)


ROT_INT_90 = rotate(pi / 2, elem_type=int)
ROT_INT_NEG_90 = rotate(-pi / 2, elem_type=int)


def point(x, y):
    return [x, y, 1]
