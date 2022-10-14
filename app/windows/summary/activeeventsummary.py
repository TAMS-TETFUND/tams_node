from typing import Any, Dict
import PySimpleGUI as sg

from app.basegui import BaseGUIWindow
from app.gui_utils import (
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
            print(e)
            initiator = None
        layout = [
            [
                sg.Push(),
                sg.Text(
                    "On-going {} Event".format(event_dict["type"].capitalize())
                ),
                sg.Push(),
            ],
            [sg.HorizontalSeparator()],
            [sg.VPush()],
            [cls.message_display_field()],
            [sg.Text(f"Course: {event_dict['course']}")],
            [
                sg.Text(
                    f"Session Details: {event_dict['session']} "
                    f"{event_dict['semester']}"
                )
            ],
            [
                sg.Text(
                    f"Start Time: {event_dict['start_date']} "
                    f"{event_dict['start_time']}"
                )
            ],
            [sg.Text(f"Duration: {event_dict['duration']} Hours")],
            [
                sg.Text(
                    f"Consenting Staff: "
                    f"{'Unknown' if initiator is None else initiator.first_name}"
                    f" {'' if initiator is None else initiator.last_name}"
                )
            ],
            [sg.VPush()],
            [
                sg.Button("Continue Event", k="continue_event"),
            ],
            [sg.HorizontalSeparator()],
            cls.navigation_pane(
                next_icon="next_disabled", back_icon="back_disabled"
            ),
        ]
        window = sg.Window(
            "Active Event Summary", layout, **cls.window_init_dict()
        )
        return window

    @classmethod
    def loop(
        cls, window: sg.Window, event: str, values: Dict[str, Any]
    ) -> bool:
        """Track user interaction with window."""
        if event == "continue_event":
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

        if event in ("cancel", "home"):
            window_dispatch.dispatch.open_window("HomeWindow")
        return True
