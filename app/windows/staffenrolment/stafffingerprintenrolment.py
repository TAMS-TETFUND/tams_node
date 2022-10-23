from typing import List

import PySimpleGUI as sg

from app.windows.basefingerprintverfication import FingerprintEnrolmentWindow
import app.appconfigparser
import app.windowdispatch
from .utils import send_staff_data


app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


class StaffFingerprintEnrolmentWindow(FingerprintEnrolmentWindow):
    """This class provides methods tailored to staff fingerprint enrolement."""
    __slots__ = ()

    @classmethod
    def process_fingerprint(cls, fingerprint_data: List[int]) -> None:
        """Process captured fingerprint template."""
        app_config.cp["new_staff"]["fingerprint_template"] = str(
            fingerprint_data
        )
        send_staff_data()
        cls.popup_auto_close_success("Staff enrolment successful")
        window_dispatch.dispatch.open_window("StaffEnrolmentWindow")
        return

    @staticmethod
    def cancel_fp_enrolment() -> None:
        """Next window when user presses cancel button on GUI window."""
        confirm = sg.popup_yes_no(
            "Staff details will be saved with no biometric data. Continue?",
            keep_on_top=True,
        )
        if confirm == "Yes":
            send_staff_data()
            window_dispatch.dispatch.open_window("HomeWindow")
        return

    @classmethod
    def window_title(cls) -> str:
        """Title of the GUI window."""
        return "Student Fingerprint Verification"

