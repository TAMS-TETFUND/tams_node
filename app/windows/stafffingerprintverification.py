import PySimpleGUI as sg

from app.fingerprint import FingerprintScanner
from app.windows.basefingerprint import FingerprintGenericWindow
from app.gui_utils import (
    StaffBiometricVerificationRouterMixin,
    StaffIDInputRouterMixin,
)
import app.appconfigparser
import app.windowdispatch
from app.opmodes import OperationalMode
from db.models import AttendanceSession


app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


class StaffFingerprintVerificationWindow(
    StaffIDInputRouterMixin,
    StaffBiometricVerificationRouterMixin,
    FingerprintGenericWindow,
):
    """This window provides an interface for verifying staff
    fingerprint during attendance initiation."""

    @classmethod
    def loop(cls, window, event, values):
        if event == "cancel":
            if app_config.cp.has_option(
                "current_attendance_session", "initiator_id"
            ):
                window_dispatch.dispatch.open_window("ActiveEventSummaryWindow")
            else:
                app_config.cp["new_event"] = app_config.cp[
                    "current_attendance_session"
                ]
                window_dispatch.dispatch.open_window("NewEventSummaryWindow")
            return True

        if event == "camera":
            if not OperationalMode.check_camera():
                cls.popup_auto_close_error("Camera not connected")
            else:
                window_dispatch.dispatch.open_window(
                    "StaffFaceVerificationWindow"
                )
            return True

        tmp_staff = app_config.cp["tmp_staff"]
        try:
            fp_template = eval(tmp_staff.get("fingerprint_template"))
        except Exception as e:
            cls.popup_auto_close_error(
                "Invalid fingerprint data from staff registration", duration=5
            )
            app_config.cp.remove_section("tmp_staff")
            cls.staff_id_input_window()
            return True

        if fp_template in (None, ""):
            cls.popup_auto_close_error(
                "No valid fingerprint data from staff registration", duration=5
            )
            cls.staff_id_input_window()
            return True

        try:
            fp_scanner = FingerprintScanner()
        except RuntimeError as e:
            sg.popup(
                e,
                title="Error",
                keep_on_top=True,
            )
            cls.staff_verification_window()
            return True

        cls.display_message("Waiting for fingerprint...", window)

        try:
            fp_response = fp_scanner.fp_capture()
        except RuntimeError as e:
            cls.popup_auto_close_error("Connection to fingerprint scanner lost")
            cls.staff_verification_window()
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
            window_dispatch.dispatch.open_window(
                "AttendanceSessionLandingWindow"
            )
            return True

        if fp_scanner.verify_match():
            att_session = AttendanceSession.objects.get(
                id=app_config.cp.get("current_attendance_session", "session_id")
            )
            att_session.initiator_id = tmp_staff.get("staff_number")
            att_session.save()
            app_config.cp["current_attendance_session"][
                "initiator_id"
            ] = tmp_staff["staff_number"]
            cls.popup_auto_close_success(
                f"{tmp_staff['first_name'][0].upper()}. "
                f"{tmp_staff['last_name'].capitalize()} "
                f"authorized attendance-marking",
            )

            app_config.cp.remove_section("tmp_staff")
            window_dispatch.dispatch.open_window(
                "AttendanceSessionLandingWindow"
            )
            return True
        elif not fp_scanner.verify_match():
            cls.popup_auto_close_error(
                "Fingerprint did not match registration data"
            )
            return True

        cls.popup_auto_close_success(
            f"{tmp_staff['last_name']} {tmp_staff['first_name'][0]}. checked in"
        )
        window_dispatch.dispatch.open_window("AttendanceSessionLandingWindow")
        return True

    @classmethod
    def window_title(cls):
        return "Staff Fingerprint Verification"
