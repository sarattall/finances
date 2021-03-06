from pynance.models import Security, USD, MYR, Amount
from nose.tools import *
from operator import le, ge, lt, gt


class TestAmounts:

    def setup(self):
        pass

    def teardown(self):
        pass

    def test_comparisons(self):
        assert_greater_equal(Amount(12, USD), Amount(4, USD))
        assert_greater(Amount(12, USD), Amount(4, USD))
        assert_less_equal(Amount(2, USD), Amount(4, USD))
        assert_less(Amount(2, USD), Amount(4, USD))
        assert_greater_equal(Amount(4, USD), Amount(4, USD))
        assert_less_equal(Amount(4, USD), Amount(4, USD))

        assert_greater_equal(Amount(12, USD), 0)
        assert_greater(Amount(12, USD), 0)
        assert_less_equal(Amount(-2, USD), 0.0)
        assert_less(Amount(-2, USD), 0)
        assert_greater_equal(Amount(0, USD), 0)
        assert_less_equal(Amount(0, USD), 0.0)

        assert_raises(ValueError, lt, Amount(4, USD), Amount(8, MYR))

    def test_inequality(self):
        assert_not_equals(Amount(2, USD), Amount(4, USD))
        assert_not_equals(Amount(20, USD), Amount(40, USD))

    def test_fuzzy_equality(self):
        assert_equals(Amount(1.0, USD), Amount(1, USD))
        assert_equals(Amount(1.001, USD), Amount(1, USD))
        assert_equals(Amount(80.0, MYR), Amount(80, MYR))
        assert_equals(Amount(79.995, MYR), Amount(80, MYR))

        assert_equals(Amount(0.0, MYR), 0)
        assert_equals(Amount(0, MYR), 0.0)
        assert_equals(Amount(0.0, MYR), 0.0)
        assert_equals(Amount(0, MYR), 0)

        assert_not_equals(Amount(79.994, MYR), Amount(80, MYR))
        assert_not_equals(Amount(1.01, USD), Amount(1, USD))

    def test_amount_multiplication(self):
        one = Amount(1, USD)
        ten = Amount(10, USD)

        assert_equals(one * 5, Amount(5, USD))
        assert_equals(5 * one, Amount(5, USD))
        assert_equals(one * 5.001, Amount(5.001, USD))

        assert_equals(0.5 * ten, Amount(5, USD))
        assert_equals(ten * 0.4, Amount(4, USD))

    def test_amount_addition_with_primitives(self):
        assert_equals(Amount(100, USD) + 10, Amount(110, USD))
        assert_equals(Amount(100, USD) + 7.5, Amount(107.5, USD))

        assert_equals(10 + Amount(100, USD), Amount(110, USD))
        assert_equals(7.5 + Amount(100, USD), Amount(107.5, USD))

    def test_amount_subtraction_with_primitives(self):
        assert_equals(Amount(100, USD) - 10, Amount(90, USD))
        assert_equals(Amount(100, USD) - 7.5, Amount(92.5, USD))

        assert_equals(100 - Amount(10, USD), Amount(90, USD))
        assert_equals(100 - Amount(7.5, USD), Amount(92.5, USD))

    def test_amount_addition(self):
        one = Amount(1, USD)
        ten = Amount(10, USD)
        hundred = Amount(100, USD)
        thousand = Amount(1000, USD)

        assert_equals(one + ten + hundred + thousand, Amount(1111, USD))
        assert_equals(0 + one, one)
        assert_equals(one + 0, one)

        assert_equals(9 + one, ten)
        assert_equals(one + 9, ten)

        assert_equals(one + 0.001, Amount(1.001, USD))
        assert_equals(0.001 + one, Amount(1.001, USD))

    def test_amount_subtraction(self):
        one = Amount(1, USD)
        ten = Amount(10, USD)
        hundred = Amount(100, USD)
        thousand = Amount(1000, USD)

        assert_equals(thousand - hundred - ten - one, Amount(889, USD))

        assert_equals(0 - one, Amount(-1, USD))
        assert_equals(one - 0, one)

        assert_equals(hundred - thousand, Amount(-900, USD))

        assert_equals(ten - 9, one)
        assert_equals(11 - ten, one)

        assert_equals(one - 0.001, Amount(0.999, USD))
        assert_equals(0.001 - one, Amount(-0.999, USD))

    def test_amount_equality(self):
        assert_equals(Amount(10, USD), Amount(10, USD))
        assert_not_equals(Amount(10, USD), Amount(20, USD))

        assert_equals(Amount(10.001, USD), Amount(10.001, USD))
        assert_not_equals(Amount(10.001, USD), Amount(-10.001, USD))

    def test_amount_hash(self):
        amount_set = set()
        amount_set.add(Amount(10, USD))
        amount_set.add(Amount(10, USD))

        assert_equals(len(amount_set), 1)
