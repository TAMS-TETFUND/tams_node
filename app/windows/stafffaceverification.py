from typing import Any, List
import PySimpleGUI as sg

from app.windows.basecamera import FaceCameraWindow
import app.appconfigparser
from app.facerec import FaceRecognition
import app.windowdispatch
from db.models import str_to_face_enc, AttendanceSession

app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


class StaffFaceVerificationWindow(FaceCameraWindow):
    """This class is responsible for staff face verification and initiates attendance session."""
    __slots__ = ()

    @classmethod
    def process_image(
        cls, captured_face_encodings: Any, window: sg.Window
    ) -> None:
        """Process detected face."""
        if captured_face_encodings is None:
            cls.popup_auto_close_error("Eror. Image must have exactly one face")
            return
        tmp_staff = app_config.cp["tmp_staff"]
        if FaceRecognition.face_match(
            known_face_encodings=[
                str_to_face_enc(app_config.cp["tmp_staff"]["face_encodings"])
            ],
            face_encoding_to_check=captured_face_encodings,
        ):
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
            return
        else:
            cls.popup_auto_close_error(
                f"Error. Face did not match ({tmp_staff['staff_number']})",
            )
            return

    @staticmethod
    def cancel_camera() -> None:
        """ "Logic for when cancel button is pressed in camera window."""
        if app_config.cp.has_option(
            "current_attendance_session", "initiator_id"
        ):
            window_dispatch.dispatch.open_window("ActiveEventSummaryWindow")
        else:
            app_config.cp["new_event"] = app_config.cp[
                "current_attendance_session"
            ]
            window_dispatch.dispatch.open_window("NewEventSummaryWindow")
        return

    @classmethod
    def window_title(cls) -> List[Any]:
        """Title to GUI window."""
        course = app_config.cp.get(
            "current_attendance_session", "course", fallback=""
        ).split(":")
        event = app_config.cp.get(
            "current_attendance_session", "type", fallback=""
        )
        staff_fname = app_config.cp.get(
            "tmp_staff", "first_name", fallback="fname"
        )
        staff_lname = app_config.cp.get("tmp_staff", "last_name", fallback="")
        return [
            [
                sg.Push(),
                sg.Text(
                    f"Staff Consent for {course[0]} {event.capitalize()} Attendance",
                    key=cls.key("course"),
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Image(data=cls.get_icon("face_scanner", 0.3)),
                sg.Text(
                    f"Face Verification for: {staff_fname[0]}. {staff_lname}",
                    key=cls.key("staff_name"),
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
        staff_fname = app_config.cp.get(
            "tmp_staff", "first_name", fallback="fname"
        )
        staff_lname = app_config.cp.get("tmp_staff", "last_name", fallback="")

        window[cls.key("course")].update(
            f"Staff Consent for {course[0]} {event.capitalize()} Attendance"
        )
        window[cls.key("staff_name")].update(
            f"Face Verification for: {staff_fname[0]}. {staff_lname}"
        )

    @staticmethod
    def open_fingerprint() -> None:
        """Open window when fingerprint button is pressed in camera window."""
        window_dispatch.dispatch.open_window(
            "StaffFingerprintVerificationWindow"
        )
        return
