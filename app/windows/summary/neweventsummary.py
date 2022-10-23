from typing import Any, Dict, List
import PySimpleGUI as sg
from datetime import datetime, timedelta

from app.basegui import BaseGUIWindow
from app.guiutils import (
    StaffIDInputRouterMixin,
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
)

app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


class NewEventSummaryWindow(StaffIDInputRouterMixin, BaseGUIWindow):
    """This window presents details selected by the user in the new
    attendance session about to be initiated."""
    __slots__ = ()

    @classmethod
    def window(cls) -> List[Any]:
        """Construct layout/appearance of window."""
        new_event_dict = app_config.cp["new_event"]
        layout = [
            [
                sg.Push(),
                sg.Text("New Event: "),
                sg.Text(
                    "({})".format(new_event_dict.get("type", "").capitalize()),
                    key=cls.key("window_title")
                ),
                sg.Push(),
            ],
            [sg.HorizontalSeparator()],
            [sg.VPush()],
            [cls.message_display_field()],
            [sg.Text(f"Course: {new_event_dict.get('course','')}", key=cls.key("course"))],
            [
                sg.Text(
                    f"Session Details: {new_event_dict.get('session', '')} "
                    f"{new_event_dict.get('semester', '')}",
                    key=cls.key("session_details")
                )
            ],
            [
                sg.Text(
                    f"Start Time: {new_event_dict.get('start_date', '')} "
                    f"{new_event_dict.get('start_time', '')}",
                    key=cls.key("start_date_time")
                )
            ],
            [sg.Text(f"Duration: {new_event_dict.get('duration', '')} Hours", key=cls.key("duration"))],
            [sg.VPush()],
            [
                sg.Button("Start Event", k=cls.key("start_event")),
                sg.Button("Schedule Event", k=cls.key("schedule_event")),
                sg.Button("Edit Details", k=cls.key("edit")),
            ],
            [sg.HorizontalSeparator()],
            cls.navigation_pane(
                back_icon="back_disabled", next_icon="next_disabled"
            ),
        ]
        return layout

    @classmethod
    def loop(
        cls, window: sg.Window, event: str, values: Dict[str, Any]
    ) -> bool:
        """Track user interaction with window."""
        if event in (cls.key("start_event"), cls.key("schedule_event")):
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
                window_dispatch.dispatch.open_window("ActiveEventSummaryWindow")
                return True

            if event == cls.key("start_event"):
                cls.staff_id_input_window()

            if event == cls.key("schedule_event"):
                sg.popup(
                    "Event saved to scheduled events",
                    title="Event saved",
                    keep_on_top=True,
                )
                window_dispatch.dispatch.open_window("HomeWindow")

        if event == cls.key("home"):
            app_config.cp.remove_section("new_event")
            window_dispatch.dispatch.open_window("HomeWindow")
        return True
    
    @classmethod
    def refresh_dynamic_fields(cls, window: sg.Window) -> None:
        new_event_dict = app_config.cp["new_event"]
        window[cls.key("window_title")].update(new_event_dict.get("type", fallback=""))
        window[cls.key("course")].update(f"Course: {new_event_dict.get('course','')}")
        window[cls.key("session_details")].update(
            f"Session Details: {new_event_dict.get('session', '')} "
            f"{new_event_dict.get('semester', '')}"
        )
        window[cls.key("start_date_time")].update(
            f"Start Time: {new_event_dict.get('start_date', '')} "
            f"{new_event_dict.get('start_time', '')}"
        )
        window[cls.key("duration")].update(
            f"Duration: {new_event_dict.get('duration', '')} Hours"
        )