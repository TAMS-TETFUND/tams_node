import PySimpleGUI as sg

from app.windows.basecamera import BarcodeCameraWindow
import app.appconfigparser
from app.gui_utils import (
    StudentRegNumberInputRouterMixin,
    StudentBiometricVerificationRouterMixin,
    ValidationMixin,
)
import app.windowdispatch
from db.models import Student, AttendanceRecord


app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


class StudentBarcodeCameraWindow(
    ValidationMixin,
    StudentBiometricVerificationRouterMixin,
    StudentRegNumberInputRouterMixin,
    BarcodeCameraWindow,
):
    """window responsible for processing student registration number
    from qr code during attendance marking"""

    @classmethod
    def process_barcode(cls, identification_num, window):
        val_check = cls.validate_student_reg_number(identification_num)
        if val_check is not None:
            cls.popup_auto_close_error(val_check)
            return

        if "blocked_reg_numbers" in app_config.cp[
            "current_attendance_session"
        ] and identification_num in app_config.cp["current_attendance_session"][
            "blocked_reg_numbers"
        ].split(
            ","
        ):
            cls.popup_auto_close_error(
                f"{identification_num} not allowed any more retries.",
                title="Not Allowed",
            )
            return

        student = Student.objects.filter(reg_number=identification_num)
        if not student.exists():
            cls.popup_auto_close_error(
                "No student found with given registration number."
                "Ensure you have been duly registered on the system."
            )
            return

        app_config.cp["tmp_student"] = app_config.cp.dict_vals_to_str(
            student.values(
                "reg_number",
                "first_name",
                "last_name",
                "level_of_study",
                "department__name",
                "department__faculty__name",
                "face_encodings",
                "fingerprint_template",
            ).first()
        )

        tmp_student = app_config.cp["tmp_student"]
        if AttendanceRecord.objects.filter(
            attendance_session_id=app_config.cp.get(
                "current_attendance_session", "session_id"
            ),
            student_id=tmp_student["reg_number"],
        ).exists():
            cls.popup_auto_close_warn(
                f"{tmp_student['first_name']} {tmp_student['last_name']} "
                f"({tmp_student['reg_number']}) already checked in"
            )
            return

        cls.student_verification_window()
        return

    @staticmethod
    def cancel_camera():
        window_dispatch.dispatch.open_window("AttendanceSessionLandingWindow")

    @classmethod
    def window_title(cls):
        course = app_config.cp["current_attendance_session"]["course"].split(
            ":"
        )
        event = app_config.cp["current_attendance_session"]["type"]
        return [
            [
                sg.Push(),
                sg.Text(f"{course[0]} {event.capitalize()} Attendance"),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Image(data=cls.get_icon("qr_code", 0.3)),
                sg.Text(
                    "Present Student ID Card (Barcode)", font=("Helvetica", 11)
                ),
                sg.Push(),
            ],
        ]

    @classmethod
    def launch_keypad(cls):
        window_dispatch.dispatch.open_window("StudentRegNumInputWindow")
        return
