from traju.helpers import *


def test_vector_like():
    assert vector_like([1, 2, 3]) == [1, 2, 3]
    assert vector_like(42) == [42]
    assert vector_like('str') == ['str']
    assert vector_like(()) == []


def test_apart():
    assert apart(lambda x: x <= 1, [1, 2, 3]) == ([2, 3], [1])
    assert apart(lambda x: x % 2 == 0, [1, 2, 3]) == ([1, 3], [2])
    assert apart(bool, []) == ([], [])
    assert apart(bool, [True, True, True]) == ([], [True, True, True])
