from typing import Any

import PySimpleGUI as sg

from app.basegui import BaseGUIWindow
import app.appconfigparser
import app.windowdispatch
from app.opmodes import OperationalMode
from app.windows.basecamera import FaceCameraWindow
from db.models import face_enc_to_str
from .utils import send_student_data


app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


class StudentFaceEnrolmentWindow(FaceCameraWindow):
    """This window is used to capture face encodings for a new student
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
        app_config.cp["new_student"]["face_encodings"] = face_enc_to_str(
            captured_face_encodings
        )

        if not OperationalMode.check_fingerprint():
            BaseGUIWindow.popup_auto_close_warn(
                "Fingerprint scanner not available"
            )

            # save student if fingerprint enrolment not available
            send_student_data()
            BaseGUIWindow.popup_auto_close_success(
                "Student enrolment successful"
            )

            window_dispatch.dispatch.open_window("StudentEnrolmentWindow")
            return

        window_dispatch.dispatch.open_window(
            "StudentFingerprintEnrolmentWindow"
        )
        return

    @staticmethod
    def cancel_camera() -> None:
        """ "Logic for when cancel button is pressed in camera window."""
        confirm = sg.popup_yes_no(
            "Student details will be saved with no biometric data. Continue?",
            keep_on_top=True,
        )
        if confirm == "Yes":
            send_student_data()
            BaseGUIWindow.popup_auto_close_success("Save successful")
            window_dispatch.dispatch.open_window("HomeWindow")
        return
