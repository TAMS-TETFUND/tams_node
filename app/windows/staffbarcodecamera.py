from typing import Any, List
import PySimpleGUI as sg

from app.windows.basecamera import BarcodeCameraWindow
import app.appconfigparser
from app.guiutils import StaffBiometricVerificationRouterMixin, ValidationMixin
import app.windowdispatch
from db.models import Staff


app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


class StaffBarcodeCameraWindow(
    ValidationMixin, StaffBiometricVerificationRouterMixin, BarcodeCameraWindow
):
    """window responsible for processing staff number
    from qr code during attendance session initiation"""
    __slots__ = ()
    
    @classmethod
    def process_barcode(
        cls, identification_num: str, window: sg.Window
    ) -> None:
        """Process a decoded identification number."""
        val_check = cls.validate_staff_number(identification_num)
        if val_check is not None:
            cls.popup_auto_close_error(val_check)
            return

        staff = Staff.objects.filter(staff_number=identification_num)

        if not staff.exists():
            cls.popup_auto_close_error(
                "No staff found with given staff ID. "
                "Ensure you have been duly registered on the system."
            )
            return

        app_config.cp["tmp_staff"] = app_config.cp.dict_vals_to_str(
            staff.values(
                "staff_number",
                "first_name",
                "last_name",
                "department__name",
                "department__faculty__name",
                "face_encodings",
                "fingerprint_template",
            ).first()
        )

        cls.staff_verification_window()
        return

    @classmethod
    def window_title(cls) -> List[Any]:
        """Title of GUI window."""
        course = app_config.cp.get(
            "current_attendance_session", "course", fallback=""
        ).split(":")
        event = app_config.cp.get(
            "current_attendance_session", "type", fallback=""
        )
        return [
            [
                sg.Push(),
                sg.Text(f"{course[0]} {event.capitalize()} Attendance Consent"),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Image(data=cls.get_icon("qr_code", 0.3)),
                sg.Text(
                    "Present QR Code on Staff ID Card to authorize attendance",
                    font=("Helvetica", 11),
                ),
                sg.Push(),
            ],
        ]

    @classmethod
    def launch_keypad(cls) -> None:
        """Window to open when the keyboard icon is pressed in GUI window."""
        window_dispatch.dispatch.open_window("StaffNumberInputWindow")
        return
