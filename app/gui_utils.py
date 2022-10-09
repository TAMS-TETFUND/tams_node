from typing import Iterable, Optional
import PySimpleGUI as sg

import app.appconfigparser
from app.basegui import BaseGUIWindow
import app.windowdispatch
from app.opmodes import OperationalMode, OpModes

from manage import django_setup

django_setup()

from db.models import (
    Student,
    SemesterChoices,
    AcademicSession,
    Staff,
    Faculty,
    Department,
    SexChoices,
)


app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


def update_device_op_mode() -> None:
    """Update operational mode of node device in app's configparser.

    Node device can operate in 3 different modes. The mode
    a given node device is running would depend on available
    biometric verification devices. The 3 modes, defined in app.opmodes
    are: FACE, FINGERPRINT, BIMODAL.
    If only a camera connection is detected, the app's operational mode
    would be FACE mode. If only a fingerprint scanner connection is
    detected, the app's operational mode would be FINGERPRINT mode. If
    both fingerprint scanner and camera is detected, the operational mode
    would be BIMODAL.
    """
    app_config.cp.remove_option("tmp_settings", "op_mode")
    try:
        device_op_mode = OperationalMode.check_all_modes()
    except RuntimeError as e:
        sg.popup(e, title="Error", keep_on_top=True)
    else:
        app_config.cp["tmp_settings"]["op_mode"] = str(device_op_mode)


class StaffBiometricVerificationRouterMixin:
    @staticmethod
    def staff_verification_window() -> None:
        """Mixin for routing staff verification task to appropriate window."""
        update_device_op_mode()
        if "op_mode" not in app_config.cp["tmp_settings"]:
            window_dispatch.dispatch.open_window("HomeWindow")
            return

        tmp_staff = app_config.cp["tmp_staff"]
        device_op_mode = app_config.cp.getint("tmp_settings", "op_mode")
        if device_op_mode == OpModes.FINGERPRINT.value:
            if tmp_staff["fingerprint_template"] in (None, "None", ""):
                BaseGUIWindow.popup_auto_close_error(
                    "No fingerprint registration data found"
                )
            else:
                window_dispatch.dispatch.open_window(
                    "StaffFingerprintVerificationWindow"
                )
            return
        if device_op_mode == OpModes.FACE.value:
            if tmp_staff["face_encodings"] in (None, "None", ""):
                BaseGUIWindow.popup_auto_close_error(
                    "No facial registration data found"
                )
            else:
                window_dispatch.dispatch.open_window(
                    "StaffFaceVerificationWindow"
                )
            return
        if device_op_mode == OpModes.BIMODAL.value:
            if tmp_staff["fingerprint_template"] in (None, "None", ""):
                if tmp_staff["face_encodings"] in (None, "None", ""):
                    BaseGUIWindow.popup_auto_close_error(
                        "No biometric data found for staff"
                    )
                    return
                else:
                    window_dispatch.dispatch.open_window(
                        "StaffFaceVerificationWindow"
                    )
                    return
            else:
                window_dispatch.dispatch.open_window(
                    "StaffFingerprintVerificationWindow"
                )
                return


class StaffIDInputRouterMixin:
    """Mixin to hadle routing of user to window for staff id input.
    Routing will depend on presence/absence of camera module in device."""

    @staticmethod
    def staff_id_input_window() -> None:
        """Set staff ID input window based on current operational mode.

        Will open the StaffBarcodeCameraWindow if a camera is connected.
        If camera is not detected, the StaffNumberInputWindow (keypad-based)
        will be opened.
        """
        update_device_op_mode()
        if "op_mode" not in app_config.cp["tmp_settings"]:
            window_dispatch.dispatch.open_window("HomeWindow")
            return

        if app_config.cp.getint("tmp_settings", "op_mode") in (
            OpModes.FACE.value,
            OpModes.BIMODAL.value,
        ):
            window_dispatch.dispatch.open_window("StaffBarcodeCameraWindow")
        else:
            window_dispatch.dispatch.open_window("StaffNumberInputWindow")
        return


class StudentBiometricVerificationRouterMixin:
    """Mixin for routing student verification task to appropriate window."""

    @staticmethod
    def student_verification_window() -> None:
        """Open valid student verification window for attendance logging.

        The logic is to open a verification window which the current
        device operational mode supports. The logic also has to confirm
        that the student being verified has valid biometric data that
        would be required by the verification window.
        """
        update_device_op_mode()
        if "op_mode" not in app_config.cp["tmp_settings"]:
            window_dispatch.dispatch.open_window("HomeWindow")
            return

        tmp_student = app_config.cp["tmp_student"]
        device_op_mode = app_config.cp.getint("tmp_settings", "op_mode")
        if device_op_mode == OpModes.FINGERPRINT.value:
            if tmp_student["fingerprint_template"] in (None, "None", ""):
                BaseGUIWindow.popup_auto_close_error(
                    "No fingerprint registration data found"
                )
            else:
                window_dispatch.dispatch.open_window(
                    "StudentFingerprintVerificationWindow"
                )
            return
        if device_op_mode == OpModes.FACE.value:
            if tmp_student["face_encodings"] in (None, "None", ""):
                BaseGUIWindow.popup_auto_close_error(
                    "No facial registration data found"
                )
            else:
                window_dispatch.dispatch.open_window(
                    "StudentFaceVerificationWindow"
                )
            return
        if device_op_mode == OpModes.BIMODAL.value:
            if tmp_student["fingerprint_template"] in (None, "None", ""):
                if tmp_student["face_encodings"] in (None, "None", ""):
                    BaseGUIWindow.popup_auto_close_error(
                        "No biometric data found for student"
                    )
                    return
                else:
                    window_dispatch.dispatch.open_window(
                        "StudentFaceVerificationWindow"
                    )
                    return
            else:
                window_dispatch.dispatch.open_window(
                    "StudentFingerprintVerificationWindow"
                )
                return


class StudentRegNumberInputRouterMixin:
    """Mixin to handle routing of student to window for student
    reg number input. Routing will depend on presence/absence of camera module in device"""

    @staticmethod
    def student_reg_number_input_window() -> None:
        """Set student reg number input window based on current operational mode.

        Will open the StudentBarcodeCameraWindow if a camera is connected.
        If camera is not detected, the StudentRegNumInputWindow (keypad-based)
        will be opened.
        """
        update_device_op_mode()
        if "op_mode" not in app_config.cp["tmp_settings"]:
            window_dispatch.dispatch.open_window("HomeWindow")
            return

        if app_config.cp.getint("tmp_settings", "op_mode") in (
            OpModes.FACE.value,
            OpModes.BIMODAL.value,
        ):
            window_dispatch.dispatch.open_window("StudentBarcodeCameraWindow")
        else:
            window_dispatch.dispatch.open_window("StudentRegNumInputWindow")
        return


class ValidationMixin:
    """Mixin to handle input field validations."""

    @staticmethod
    def validate_required_field(req_field: Iterable[str]) -> Optional[str]:
        """Check if a input field has not been modified by user."""
        field_value, field_name_for_display = req_field
        if field_value in (None, "", "--select--"):
            return "Invalid value provided in {}".format(field_name_for_display)
        else:
            return None

    @classmethod
    def validate_required_fields(
        cls, req_fields: Iterable[str], window: sg.Window
    ) -> Optional[bool]:
        """Check if a list of input fields have valid input from user."""
        for field in req_fields:
            validation_value = cls.validate_required_field(field)
            if validation_value is not None:
                BaseGUIWindow.display_message(validation_value, window)
                return True
        return None

    @staticmethod
    def validate_semester(semester: str) -> Optional[str]:
        """Validate user's input to a semester input field."""
        if semester not in SemesterChoices.labels:
            return "Invalid value for semester"
        else:
            return None

    @staticmethod
    def validate_academic_session(session: str) -> Optional[str]:
        """Validate user's input to an academic session input field."""
        if not AcademicSession.is_valid_session(session):
            return "Invalid value for academic session"
        else:
            return None

    @staticmethod
    def validate_student_reg_number(reg_no: str) -> Optional[str]:
        """Validate user's input to a student reg number input field."""
        if not Student.is_valid_student_reg_number(reg_no):
            return f"Invalid format for student registration number ({reg_no})"
        else:
            return None

    @staticmethod
    def validate_staff_number(staff_no: str) -> Optional[str]:
        """Validate user's input to a staff number input field."""
        if not Staff.is_valid_staff_number(staff_no):
            return "Invalid value for staff number"
        else:
            return None

    @staticmethod
    def validate_faculty(faculty: str) -> Optional[str]:
        """Validate user's input to a faculty input field."""
        if faculty.lower() not in [
            fac.lower() for fac in Faculty.get_all_faculties()
        ]:
            return "Invalid value in faculty"
        else:
            return None

    @staticmethod
    def validate_department(department: str) -> Optional[str]:
        """Validate user's input to a department input field."""
        if department.lower() not in [
            dept.lower() for dept in Department.get_departments()
        ]:
            return "Invalid value in department"
        else:
            return None

    @staticmethod
    def validate_sex(sex: str) -> Optional[str]:
        """Validate user's input to a sex input field."""
        if sex not in SexChoices.labels:
            return "Invalid value in sex"
        else:
            return None

    @staticmethod
    def validate_int_field(field_value: str, field_name: str) -> Optional[str]:
        """Validate user's input to an input field that requires an int."""
        try:
            field_val_int = int(field_value)
        except Exception:
            return f"Enter a numeric value for {field_name}"
        else:
            return None

    @staticmethod
    def validate_text_field(field_value: str, field_name: str) -> Optional[str]:
        """Validate user's input to an input text field."""
        if len(field_value) == 0:
            return f"{field_name.capitalize()} cannot be blank"
        else:
            return None
