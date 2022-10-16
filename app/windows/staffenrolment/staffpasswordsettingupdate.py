import time

import PySimpleGUI as sg

import app.appconfigparser
import app.windowdispatch
from app.opmodes import OperationalMode
from .staffpasswordsetting import StaffPasswordSettingWindow


app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


class StaffPasswordSettingUpdateWindow(StaffPasswordSettingWindow):
    """Update staff password"""
    @classmethod
    def next_window(cls):
        if not OperationalMode.check_camera():
            cls.popup_auto_close_warn("Camera not connected.")
            time.sleep(2)
            if not OperationalMode.check_fingerprint():
                cls.popup_auto_close_warn("Fingerprint scanner not connected")
                window_dispatch.dispatch.open_window("HomeWindow")
            else:
                update_fingerprint = sg.popup_yes_no("Update fingerprint?", keep_on_top=True)
                if update_fingerprint == "Yes":
                    window_dispatch.dispatch.open_window(
                        "StaffFingerprintEnrolmentWindow"
                    )
                    return
        else:
            update_face = sg.popup_yes_no("Update face capture?", keep_on_top=True)
            if update_face == "Yes":
                window_dispatch.dispatch.open_window("StaffFaceEnrolmentUpdateWindow")
                return
        send_staff_data()
        window_dispatch.dispatch.open_window("HomeWindow")
        return
