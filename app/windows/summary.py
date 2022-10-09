from typing import Any, Dict
import PySimpleGUI as sg
from datetime import datetime, timedelta

from app.basegui import BaseGUIWindow
from app.gui_utils import (
    StaffIDInputRouterMixin,
    StaffBiometricVerificationRouterMixin,
)
import app.appconfigparser
import app.windowdispatch
from db.models import (
    Course,
    AcademicSession,
    EventTypeChoices,
    AttendanceSession,
    AttendanceSessionStatusChoices,
    NodeDevice,
    Staff,
)

app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


class NewEventSummaryWindow(StaffIDInputRouterMixin, BaseGUIWindow):
    """This window presents details selected by the user in the new
    attendance session about to be initiated."""

    @classmethod
    def window(cls) -> sg.Window:
        """Construct layout/appearance of window."""
        new_event_dict = app_config.cp["new_event"]
        layout = [
            [
                sg.Push(),
                sg.Text(
                    "New {} Event".format(new_event_dict["type"].capitalize())
                ),
                sg.Push(),
            ],
            [sg.HorizontalSeparator()],
            [sg.VPush()],
            [cls.message_display_field()],
            [sg.Text(f"Course: {new_event_dict['course']}")],
            [
                sg.Text(
                    f"Session Details: {new_event_dict['session']} "
                    f"{new_event_dict['semester']}"
                )
            ],
            [
                sg.Text(
                    f"Start Time: {new_event_dict['start_date']} "
                    f"{new_event_dict['start_time']}"
                )
            ],
            [sg.Text(f"Duration: {new_event_dict['duration']} Hours")],
            [sg.VPush()],
            [
                sg.Button("Start Event", k="start_event"),
                sg.Button("Schedule Event", k="schedule_event"),
                sg.Button("Edit Details", k="edit"),
            ],
            [sg.HorizontalSeparator()],
            cls.navigation_pane(
                back_icon="back_disabled", next_icon="next_disabled"
            ),
        ]
        window = sg.Window(
            "New Event Summary", layout, **cls.window_init_dict()
        )
        return window

    @classmethod
    def loop(cls, window: sg.Window, event: str, values: Dict[str, Any]) -> bool:
        """Track user interaction with window."""
        if event in ("start_event", "schedule_event"):
            new_event = dict(app_config.cp["new_event"])
            attendance_session_model_kwargs = {
                "course_id": Course.str_to_course(new_event["course"]),
                "session": AcademicSession.objects.get(
                    session__iexact=new_event["session"]
                ),
                "event_type": EventTypeChoices.str_to_value(new_event["type"]),
                "start_time": datetime.strptime(
                    f"{new_event['start_date']} {new_event['start_time']} +0100",
                    "%d-%m-%Y %H:%M %z",
                ),
                "node_device_id": NodeDevice.objects.first().id,
                "duration": timedelta(hours=int(new_event["duration"])),
                "recurring": eval(new_event["recurring"]),
            }

            try:
                att_session, created = AttendanceSession.objects.get_or_create(
                    **attendance_session_model_kwargs
                )
            except Exception:
                cls.display_message("Unknown system error", window)

            if not created:
                if att_session.status != AttendanceSessionStatusChoices.ACTIVE:
                    cls.popup_auto_close_error(
                        "Attendance for this event has ended"
                    )
                    app_config.cp.remove_section("current_attendance_session")
                    app_config.cp.remove_section("new_event")
                    window_dispatch.dispatch.open_window("HomeWindow")
                    return True
                cls.popup_auto_close_warn("Event has already been created")

            app_config.cp[
                "current_attendance_session"
            ] = app_config.cp.section_dict("new_event")
            app_config.cp["current_attendance_session"]["session_id"] = str(
                att_session.id
            )
            app_config.cp.remove_section("new_event")

            if att_session.initiator:
                app_config.cp["current_attendance_session"][
                    "initiator_id"
                ] = str(att_session.initiator.id)
                window_dispatch.dispatch.open_window(ActiveEventSummaryWindow)
                return True

            if event == "start_event":
                cls.staff_id_input_window()

            if event == "schedule_event":
                sg.popup(
                    "Event saved to scheduled events",
                    title="Event saved",
                    keep_on_top=True,
                )
                window_dispatch.dispatch.open_window("HomeWindow")

        if event == "home":
            app_config.cp.remove_section("new_event")
            window_dispatch.dispatch.open_window("HomeWindow")
        return True


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
    def loop(cls, window: sg.Window, event: str, values: Dict[str, Any]) -> bool:
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
