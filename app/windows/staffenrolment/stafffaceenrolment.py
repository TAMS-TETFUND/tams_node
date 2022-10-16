from typing import Any

import PySimpleGUI as sg

from app.basegui import BaseGUIWindow
import app.appconfigparser
import app.windowdispatch
from app.opmodes import OperationalMode
from app.windows.basecamera import FaceCameraWindow
from db.models import face_enc_to_str
from .utils import send_staff_data

app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


class StaffFaceEnrolmentWindow(FaceCameraWindow):
    """This window is used to capture face encodings for a new staff
    being enrolled."""

    @classmethod
    def process_image(
        cls, captured_face_encodings: Any, window: sg.Window
    ) -> None:
        """Process detected face."""
        if captured_face_encodings is None:
            cls.popup_auto_close_error(
                "Error. Image must have exactly one face"
            )
            return
        new_staff = app_config.cp["new_staff"]

        new_staff["face_encodings"] = face_enc_to_str(captured_face_encodings)

        cls.next_window() 

    @classmethod
    def next_window(cls):
        if not OperationalMode.check_fingerprint():
            BaseGUIWindow.popup_auto_close_warn("Fingerprint scanner not available")
            send_staff_data()
            BaseGUIWindow.popup_auto_close_success("Staff enrolment saved.")
            return
        window_dispatch.dispatch.open_window("StaffFingerprintEnrolmentWindow")
        return
    
    @staticmethod
    def cancel_camera() -> None:
        """ "Logic for when cancel button is pressed in camera window."""
        if OperationalMode.check_fingerprint():
            window_dispatch.dispatch.open_window("StaffFingerprintEnrolmentWindow")
            return
        confirm = sg.popup_yes_no(
            # "Staff details will be saved with no biometric data. Continue?",
            "Save changes?",
            keep_on_top=True,
        )
        if confirm == "Yes":
            send_staff_data()
            window_dispatch.dispatch.open_window("HomeWindow")
        return