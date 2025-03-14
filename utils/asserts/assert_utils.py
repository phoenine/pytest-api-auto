from typing import Any, Union


def equal(actual_value: Any, expect_value: Any):
    assert actual_value == expect_value


def not_equal(actual_value: Any, expect_value: Any):
    assert actual_value != expect_value


def less_than(actual_value: Union[int, float], expect_value: Union[int, float]):
    assert actual_value < expect_value


def greater_than(actual_value: Union[int, float], expect_value: Union[int, float]):
    assert actual_value > expect_value


def length_equal(actual_value: str, expect_value: int):
    assert len(actual_value) == expect_value


def length_gt(actual_value: str, expect_value: int):
    assert len(actual_value) > expect_value


def length_lt(actual_value: str, expect_value: int):
    assert len(actual_value) < expect_value


def contains(actual_value: Any, expect_value: Any):
    assert expect_value in actual_value


def starts_with(actual_value: Any, expect_value: Any):
    assert str(actual_value).startswith(str(expect_value))


def ends_with(check_value: Any, expect_value: Any):
    assert str(check_value).endswith(str(expect_value))
