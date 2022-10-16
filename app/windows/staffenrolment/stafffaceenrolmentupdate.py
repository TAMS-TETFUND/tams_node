import json
import time
from typing import Any, Dict, List, Optional

import PySimpleGUI as sg

import app.appconfigparser
import app.windowdispatch
from app.opmodes import OperationalMode
from .stafffaceenrolment import StaffFaceEnrolmentWindow
from .utils import send_staff_data

app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


class StaffFaceEnrolmentUpdateWindow(StaffFaceEnrolmentWindow):
    """Update staff face capture."""
    @classmethod
    def next_window(cls):
        if not OperationalMode.check_fingerprint():
            cls.popup_auto_close_warn("Fingerprint scanner not connected")
            send_staff_data()
            window_dispatch.dispatch.open_window("HomeWindow")
        else:
            update_fingerprint = sg.popup_yes_no("Update fingerprint?", keep_on_top=True)
            if update_fingerprint == "Yes":
                window_dispatch.dispatch.open_window(
                    "StaffFingerprintEnrolmentWindow"
                )