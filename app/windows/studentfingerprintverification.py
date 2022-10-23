from typing import Any, Dict
import PySimpleGUI as sg

from app.attendancelogger import AttendanceLogger
from app.fingerprint import FingerprintScanner
from app.windows.basefingerprint import FingerprintGenericWindow
from app.guiutils import StudentRegNumberInputRouterMixin
import app.appconfigparser
import app.windowdispatch
from app.opmodes import OperationalMode


app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


class StudentFingerprintVerificationWindow(
    StudentRegNumberInputRouterMixin, FingerprintGenericWindow
):
    """This window provides an interface for verifying student fingerprint
    during attendance logging."""
    __slots__ = ()
    
    @classmethod
    def loop(
        cls, window: sg.Window, event: str, values: Dict[str, Any]
    ) -> bool:
        """Track user interaction with window."""
        if event == cls.key("cancel"):
            window_dispatch.dispatch.open_window(
                "AttendanceSessionLandingWindow"
            )
            return True
        if event == cls.key("camera"):
            if not OperationalMode.check_camera():
                cls.popup_auto_close_error("Camera not connected")
            else:
                window_dispatch.dispatch.open_window(
                    "StudentFaceVerificationWindow"
                )
            return True

        tmp_student = app_config.cp["tmp_student"]
        try:
            fp_template = eval(tmp_student.get("fingerprint_template"))
        except Exception as e:
            cls.popup_auto_close_error(
                "Invalid fingerprint data from student registration", duration=5
            )
            cls.student_reg_number_input_window()

            return True

        if fp_template in (None, ""):
            cls.popup_auto_close_error(
                "No valid fingerprint data from student registration",
                duration=5,
            )
            cls.student_reg_number_input_window()
            return True

        try:
            fp_scanner = FingerprintScanner()
        except RuntimeError as e:
            cls.popup_auto_close_error(e, duration=5)
            cls.student_reg_number_input_window()
            return True

        cls.display_message("Waiting for fingerprint...", window)
        try:
            fp_response = fp_scanner.fp_capture()
        except RuntimeError:
            cls.popup_auto_close_error("Connection to fingerprint scanner lost")
            cls.student_reg_number_input_window()
            return True
        if not fp_response:
            cls.display_message(fp_scanner.error, window)
            return True

        if not fp_scanner.image_2_tz():
            cls.display_message(fp_scanner.error, window)
            return True

        if not fp_scanner.send_fpdata(fp_template, slot=2):
            cls.popup_auto_close_error(
                "Error processing registration data. Contact admin", duration=5
            )
            cls.student_reg_number_input_window()
            return True

        if fp_scanner.verify_match():
            if AttendanceLogger.log_attendance(app_config.cp):
                cls.popup_auto_close_success(AttendanceLogger.message)
                app_config.cp.remove_section("tmp_student")

            else:
                cls.popup_auto_close_error(AttendanceLogger.message)

            cls.student_reg_number_input_window()
            return True
        elif not fp_scanner.verify_match():
            AttendanceLogger.log_failed_attempt(app_config.cp)
            cls.popup_auto_close_error(
                f"Fingerprint did not match registration data.\n"
                f"{app_config.cp['tmp_student']['reg_number']}."
                f"You have {4 - app_config.cp.getint('failed_attempts', tmp_student['reg_number'])}"
            )
            return True

        return True

    @classmethod
    def window_title(cls) -> str:
        """Title of GUI window."""
        return "Student Fingerprint Verification"
