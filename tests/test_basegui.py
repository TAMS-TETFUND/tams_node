import pytest

from app.basegui import BaseGUIWindow


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ((None, "test_field"), "Invalid value provided in test_field"),
        ((5, "test_field"), None),
        ((None,), None)
    ]
)
def test_validate_required_field(test_input, expected):
    assert BaseGUIWindow.validate_required_field(test_input,) == expected

