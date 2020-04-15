

class Real:
    ''' Qm.n

    Qm.n: range: [-2^m, 2^m - precision], precision: 1/n

    https://en.wikipedia.org/wiki/Q_(number_format)
    http://x86asm.net/articles/fixed-point-arithmetic-and-tricks/
    http://www.cs.uu.nl/docs/vakken/mov/2015/slides/lecture9%20-%20fixed%20point.pdf
    https://doc.xdevs.com/docs/_Materials/FixedPointArithmetic.pdf
    '''
    m = 1
    n = 14

    def __init__(self, value):
        # this is bit of a hack, we assume that value is a raw value if
        # it is a float
        if isinstance(value, int):
            self._value = value
        else:
            self._value = int(value * (1 << self.n))

    def __add__(self, other):
        return Real(self._value + other._value)

    def __sub__(self, other):
        return Real(self._value - other._value)

    def __mul__(self, other):
        x = self._value >> (self.n//2)
        y = other._value >> (self.n - self.n//2)
        return Real(x * y)

    def __truediv__(self, other):
        return Real((self._value << self.n) // other._value)

    def __neg__(self):
        return Real(-self._value)

    def __eq__(self, other):
        return self._value == other._value

    def __str__(self):
        return f'{self.to_float():05f}'

    def to_float(self):
        return self._value / (1 << self.n)
