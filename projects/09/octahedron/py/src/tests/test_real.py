import pytest

from ..real import Real

precision = 1 / (1<<Real.n) * 10


def test_real():
    assert Real(.9).to_float() == pytest.approx(.9, abs=precision)
    assert Real(0).to_float() == 0
    assert Real(-.5).to_float() == pytest.approx(-.5, abs=precision)


def test_sum():
    assert Real(.5).to_float() == pytest.approx(.5, abs=precision)
    assert Real(.4).to_float() == pytest.approx(.4, abs=precision)
    assert Real(.9).to_float() == pytest.approx(.9, abs=precision)
    assert (Real(.5) + Real(.4)).to_float() == pytest.approx(.9, abs=precision)
    assert (Real(.4) - Real(.7)).to_float() == pytest.approx(-.3, abs=precision)


def test_mul():
    assert (Real(.9) * Real(.8)).to_float() == pytest.approx(.9 * .8, abs=precision)
    assert (Real(.9) * Real(-.8)).to_float() == pytest.approx(.9 * -.8, abs=precision)


def test_div():
    assert (Real(.1) / Real(.2)).to_float() == pytest.approx(.1/.2, abs=precision)
    assert (Real(-.1) / Real(.2)).to_float() == pytest.approx(-.1/.2, abs=precision)


def test_neg():
    assert (-Real(.9)).to_float() == pytest.approx(-.9, abs=precision)
