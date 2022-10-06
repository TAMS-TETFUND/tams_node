import PySimpleGUI as sg

from app.attendancelogger import AttendanceLogger
from app.windows.basecamera import FaceCameraWindow
import app.appconfigparser
from app.gui_utils import StudentRegNumberInputRouterMixin
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
    def process_image(cls, captured_face_encodings, window):
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
    def cancel_camera():
        """should navigate user back to the attendance session landing page"""
        window_dispatch.dispatch.open_window("AttendanceSessionLandingWindow")

    @classmethod
    def window_title(cls):
        course = app_config.cp["current_attendance_session"]["course"].split(
            ":"
        )
        event = app_config.cp["current_attendance_session"]["type"]
        student_fname = app_config.cp["tmp_student"]["first_name"]
        student_lname = app_config.cp["tmp_student"]["last_name"]
        student_reg_number = app_config.cp["tmp_student"]["reg_number"]
        return [
            [
                sg.Push(),
                sg.Text(f"{course[0]} {event.capitalize()} Attendance"),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Image(data=cls.get_icon("face_scanner", 0.3)),
                sg.Text(
                    f"Face Verification for: {student_fname[0]}. {student_lname} ({student_reg_number})",
                ),
                sg.Push(),
            ],
        ]

    @staticmethod
    def open_fingerprint():
        window_dispatch.dispatch.open_window(
            "StudentFingerprintVerificationWindow"
        )
        return
