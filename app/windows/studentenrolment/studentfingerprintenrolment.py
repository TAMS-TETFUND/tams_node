from typing import List

import PySimpleGUI as sg

from app.windows.basefingerprintverfication import FingerprintEnrolmentWindow
import app.appconfigparser
import app.windowdispatch
from .utils import send_student_data


app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


class StudentFingerprintEnrolmentWindow(FingerprintEnrolmentWindow):
    """This class provides methods tailored to student fingerprint enrolment."""
    __slots__ = ()

    @classmethod
    def process_fingerprint(cls, fingerprint_data: List[int]) -> None:
        """Process captured fingerprint template."""
        app_config.cp["new_student"]["fingerprint_template"] = str(
            fingerprint_data
        )
        send_student_data()
        cls.popup_auto_close_success("Student enrolment successful")
        window_dispatch.dispatch.open_window("StudentEnrolmentWindow")
        return

    @staticmethod
    def cancel_fp_enrolment() -> None:
        """Next window when user presses cancel button on GUI window."""
        confirm = sg.popup_yes_no(
            "Student details will be saved with no fingerprint biometric data. Continue?",
            keep_on_top=True,
        )
        if confirm == "Yes":
            app_config.cp.remove_section("new_student")
            window_dispatch.dispatch.open_window("HomeWindow")
        return

    @classmethod
    def window_title(cls) -> str:
        """Title of the GUI window."""
        return "Student Fingerprint Enrolment"

