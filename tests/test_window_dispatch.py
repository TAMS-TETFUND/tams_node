import pytest
import PySimpleGUI as sg

from app.windowdispatch import WindowDispatch
from app.gui import HomeWindow

@pytest.fixture
def dispatch_obj():
    dispatch_obj = WindowDispatch()
    return dispatch_obj

def test_open_window(dispatch_obj):
    dispatch_obj.open_window(HomeWindow)

    assert isinstance(dispatch_obj.current_window, sg.Window)
