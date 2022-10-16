from typing import Any, List
import PySimpleGUI as sg

from app.attendancelogger import AttendanceLogger
from app.windows.basecamera import FaceCameraWindow
import app.appconfigparser
from app.guiutils import StudentRegNumberInputRouterMixin
from app.facerec import FaceRecognition
import app.windowdispatch
from db.models import str_to_face_enc

app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


class StudentFaceVerificationWindow(
    StudentRegNumberInputRouterMixin, FaceCameraWindow
):
    """This class carries out student face verification and calls the
    uses the AttendanceLogger class to log attendance.
    """

    @classmethod
    def process_image(
        cls, captured_face_encodings: Any, window: sg.Window
    ) -> None:
        """Process detected face."""
        if captured_face_encodings is None:
            cls.popup_auto_close_error("Eror. Image must have exactly one face")
            return
        tmp_student = app_config.cp["tmp_student"]

        if tmp_student["face_encodings"] in ("", None):
            cls.popup_auto_close_error(
                "Student's Facial biometric data not found"
            )
            cls.student_reg_number_input_window()
            return

        if FaceRecognition.face_match(
            known_face_encodings=[
                str_to_face_enc(tmp_student["face_encodings"])
            ],
            face_encoding_to_check=captured_face_encodings,
        ):
            if AttendanceLogger.log_attendance(app_config.cp):
                cls.popup_auto_close_success(AttendanceLogger.message)
                app_config.cp.remove_section("tmp_student")

            else:
                cls.popup_auto_close_error(AttendanceLogger.message)

            cls.student_reg_number_input_window()
            return
        else:
            AttendanceLogger.log_failed_attempt(app_config.cp)
            cls.popup_auto_close_error(
                f"Error. Face did not match "
                f"({app_config.cp['tmp_student']['reg_number']})\n"
                f"You have {4 - app_config.cp.getint('failed_attempts', tmp_student['reg_number'])} attempts left",
                title="No Face",
            )
            return

    @staticmethod
    def cancel_camera() -> None:
        """ "Logic for when cancel button is pressed in camera window."""
        window_dispatch.dispatch.open_window("AttendanceSessionLandingWindow")

    @classmethod
    def window_title(cls) -> List[Any]:
        """Title to GUI window."""
        course = app_config.cp.get(
            "current_attendance_session", "course", fallback=""
        ).split(":")
        event = app_config.cp.get(
            "current_attendance_session", "type", fallback=""
        )
        student_fname = app_config.cp.get(
            "tmp_student", "first_name", fallback="first_name"
        )
        student_lname = app_config.cp.get(
            "tmp_student", "last_name", fallback=""
        )
        student_reg_number = app_config.cp.get(
            "tmp_student", "reg_number", fallback=""
        )
        return [
            [
                sg.Push(),
                sg.Text(
                    f"{course[0]} {event.capitalize()} Attendance",
                    key=cls.key("course"),
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Image(data=cls.get_icon("face_scanner", 0.3)),
                sg.Text(
                    f"Face Verification for: {student_fname[0]}. {student_lname} ({student_reg_number})",
                    key=cls.key("student_name"),
                ),
                sg.Push(),
            ],
        ]

    @classmethod
    def refresh_dynamic_fields(cls, window: sg.Window) -> None:
        course = app_config.cp.get(
            "current_attendance_session", "course", fallback=""
        ).split(":")
        event = app_config.cp.get(
            "current_attendance_session", "type", fallback=""
        )
        student_fname = app_config.cp.get(
            "tmp_student", "first_name", fallback="first_name"
        )
        student_lname = app_config.cp.get(
            "tmp_student", "last_name", fallback=""
        )
        student_reg_number = app_config.cp.get(
            "tmp_student", "reg_number", fallback=""
        )

        window[cls.key("course")].update(
            f"{course[0]} {event.capitalize()} Attendance"
        )
        window[cls.key("student_name")].update(
            f"Face Verification for: {student_fname[0]}. {student_lname} ({student_reg_number})"
        )

    @staticmethod
    def open_fingerprint() -> None:
        """Open window when fingerprint button is pressed in camera window."""
        window_dispatch.dispatch.open_window(
            "StudentFingerprintVerificationWindow"
        )
        return
