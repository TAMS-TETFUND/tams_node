from typing import Any, Dict
import PySimpleGUI as sg

from app.basegui import BaseGUIWindow
from app.guiutils import (
    StaffBiometricVerificationRouterMixin,
)
import app.appconfigparser
import app.windowdispatch
from db.models import Staff

app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


class ActiveEventSummaryWindow(
    StaffBiometricVerificationRouterMixin, BaseGUIWindow
):
    """This window presents the details of an attendance session that
    has been initiated."""

    @classmethod
    def window(cls) -> sg.Window:
        """Construct layout/appearance of window."""
        event_dict = app_config.cp["current_attendance_session"]
        try:
            initiator = Staff.objects.get(pk=event_dict.get("initiator_id"))
        except Exception as e:
            initiator = None
        layout = [
            [
                sg.Push(),
                sg.Text(
                    "On-going {} Event".format(event_dict.get("type", "").capitalize()),
                    key=cls.key("window_title")
                ),
                sg.Push(),
            ],
            [sg.HorizontalSeparator()],
            [sg.VPush()],
            [cls.message_display_field()],
            [sg.Text(f"Course: {event_dict.get('course', '')}", key=cls.key("course")),],
            [
                sg.Text(
                    f"Session Details: {event_dict.get('session', '')} "
                    f"{event_dict.get('semester', '')}",
                    key=cls.key("session_details")
                )
            ],
            [
                sg.Text(
                    f"Start Time: {event_dict.get('start_date', '')} "
                    f"{event_dict.get('start_time', '')}",
                    key=cls.key("start_date_time")
                )
            ],
            [sg.Text(f"Duration: {event_dict.get('duration', '')} Hours", key=cls.key("duration"))],
            [
                sg.Text(
                    f"Consenting Staff: "
                    f"{'Unknown' if initiator is None else initiator.first_name}"
                    f" {'' if initiator is None else initiator.last_name}",
                    key=cls.key("initiator")
                )
            ],
            [sg.VPush()],
            [
                sg.Button("Continue Event", k=cls.key("continue_event")),
            ],
            [sg.HorizontalSeparator()],
            cls.navigation_pane(
                next_icon="next_disabled", back_icon="back_disabled"
            ),
        ]
        return layout

    @classmethod
    def loop(
        cls, window: sg.Window, event: str, values: Dict[str, Any]
    ) -> bool:
        """Track user interaction with window."""
        if event == cls.key("continue_event"):
            active_event = app_config.cp["current_attendance_session"]

            try:
                initiator = Staff.objects.filter(
                    pk=active_event.get("initiator_id")
                )
            except Staff.DoesNotExist:
                sg.popup(
                    "System error. Please try creating event again",
                    title="Error",
                    keep_on_top=True,
                )
                window_dispatch.dispatch.open_window("HomeWindow")
                return True

            app_config.cp["tmp_staff"] = app_config.cp.dict_vals_to_str(
                initiator.values(
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
            return True

        if event in (cls.key("cancel"), cls.key("home")):
            window_dispatch.dispatch.open_window("HomeWindow")
        return True

    @classmethod
    def refresh_dynamic_fields(cls, window: sg.Window) -> None:
        event_dict = app_config.cp["current_attendance_session"]
        try:
            initiator = Staff.objects.get(pk=event_dict.get("initiator_id"))
        except Exception as e:
            initiator = None

        window[cls.key("window_title")].update("On-going {} Event".format(event_dict.get("type", "").capitalize()))
        window[cls.key("course")].update(f"Course: {event_dict.get('course','')}")
        window[cls.key("session_details")].update(
            f"Session Details: {event_dict.get('session', '')} "
            f"{event_dict.get('semester', '')}"
        )
        window[cls.key("start_date_time")].update(
            f"Start Time: {event_dict.get('start_date', '')} "
            f"{event_dict.get('start_time', '')}"
        )
        window[cls.key("duration")].update(
            f"Duration: {event_dict.get('duration', '')} Hours"
        )
        window[cls.key("initiator")].update(
            f"Consenting Staff: "
                    f"{'Unknown' if initiator is None else initiator.first_name}"
                    f" {'' if initiator is None else initiator.last_name}"
        )