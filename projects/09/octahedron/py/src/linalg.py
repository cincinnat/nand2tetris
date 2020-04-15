import math


class Vector:
    def __init__(self, v):
        assert len(v) == 3
        self._data = v

    @property
    def x(self):
        return self._data[0]

    @property
    def y(self):
        return self._data[1]

    @property
    def z(self):
        return self._data[2]

    def __getitem__(self, i):
        return self._data[i]

    def __eq__(self, other):
        return self._data == other._data

    def __ne__(self, other):
        return self._data != other._data

    def norm(self):
        n = math.sqrt(sum(x*x for x in self._data))
        return Vector([x/n for x in self._data])

    def dot(self, other):
        return sum((self._data[i] * other._data[i] for i in range(3)),
            start=self._data[0].__class__(0))


class Matrix:
    def __init__(self, value):
        if hasattr(value, '__iter__'):
            value = list(value)
            assert len(value) == 9
            self._data = value
        else:
            self._data = [value] * 9

    def __matmul__(self, other):
        m = [0] * 9
        for i in range(3):
            for j in range(3):
                m[i*3+j] = sum((self[i,k] * other[k,j] for k in range(3)),
                    start=self._data[0].__class__(0))
        return Matrix(m)

    def __mul__(self, other):
        if isinstance(other, Vector):
            v = [0] * 3
            for i in range(3):
                v[i] = sum((self[i, j] * other[j] for j in range(3)),
                    start=self._data[0].__class__(0))
            return Vector(v)
        else:
            return Matrix(x * other for x in self._data)

    def __getitem__(self, pos):
        i, j = pos
        return self._data[i*3 + j]

    def __eq__(self, other):
        return self._data == other._data

    def __ne__(self, other):
        return self._data != other._data
