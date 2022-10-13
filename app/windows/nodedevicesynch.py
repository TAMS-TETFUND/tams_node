from typing import Dict, Any
import PySimpleGUI as sg
from app.nodedevicedatasynch import NodeDataSynch
from app.windows.loading import LoadingWindow
import app.windowdispatch

window_dispatch = app.windowdispatch.WindowDispatch()

class NodeDeviceSynchWindow(LoadingWindow):
    """Synch node device with server."""
    @classmethod
    def loop(cls, window: sg.Window, event: str, values: Dict[str, Any]) -> bool:
        """Track user interaction with window."""
        NodeDataSynch.start_data_sync()
        cls.popup_auto_close_success("Synch Successful")
        window_dispatch.dispatch.open_window("HomeWindow")
        return True