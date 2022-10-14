import json
from typing import Dict, Any

import PySimpleGUI as sg

from app.nodedevicedatasynch import NodeDataSynch
from app.windows.loading import LoadingWindow
import app.windowdispatch

window_dispatch = app.windowdispatch.WindowDispatch()


class NodeDeviceSynchWindow(LoadingWindow):
    """Synch node device with server."""
    @classmethod
    def loop(
        cls, window: sg.Window, event: str, values: Dict[str, Any]
    ) -> bool:
        """Track user interaction with window."""
        try:
            NodeDataSynch.node_attendance_sync()
            msg = "Attendance Successfully Synced!"
        except Exception as e:
            print(e)
            err_msg = f"Error: {json.loads(str(e))['detail']}"
            return True
        cls.popup_auto_close_success(message=msg, duration=5)
        NodeDataSynch.start_data_sync()
        cls.popup_auto_close_success("Synch Successful")
        window_dispatch.dispatch.open_window("HomeWindow")
        return True
