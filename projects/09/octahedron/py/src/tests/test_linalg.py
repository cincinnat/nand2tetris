from ..linalg import Vector, Matrix


def test_vector():
    v1 = Vector([1, 2, 3])
    v2 = Vector([1, 2, 3])

    assert v1[0] == v1.x == 1
    assert v1[1] == v1.y == 2
    assert v1[2] == v1.z == 3
    assert v1 == v2


def test_matrix():
    m1 = Matrix(list(range(9)))
    m2 = Matrix(list(range(9)))

    for i in range(3):
        for j in range(3):
            assert m1[i, j] == i*3 + j
    assert m1 == m2


def test_matrix_matmul():
    m1 = Matrix([
        1, 2, 3,
        4, 5, 6,
        7, 8, 9,
    ])
    m2 = Matrix([
        9, 8, 7,
        6, 5, 4,
        3, 2, 1,
    ])
    expected = Matrix([
        30, 24, 18,
        84, 69, 54,
        138, 114, 90,
    ])

    assert m1 @ m2 == expected


def test_matrix_vector_mul():
    m = Matrix([
        1, 2, 3,
        4, 5, 6,
        7, 8, 9,
    ])
    v = Vector([1, 2, 3])
    expected = Vector([14, 32, 50])

    assert m * v == expected


def test_matrix_scalar_mul():
    m = Matrix([
        1, 2, 3,
        4, 5, 6,
        7, 8, 9,
    ])
    c = 2
    expected = Matrix([
        2, 4, 6,
        8, 10, 12,
        14, 16, 18,
    ])

    assert m * c == expected
