from datetime import datetime, timezone
from typing import Any, Dict

import PySimpleGUI as sg

from app.basegui import BaseGUIWindow
import app.appconfigparser
import app.windowdispatch
from db.models import AttendanceSession, EventTypeChoices


app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


class ScheduledEventsWindow(BaseGUIWindow):
    """Window for accessing scheduled events."""

    @classmethod
    def window(cls) -> sg.Window:
        """Layout/appearance of GUI window."""
        # Django day of week are numbered 1-7 (sunday to saturday)
        # while Python's day of week are numbered 0-6
        # (Monday to saturday). A mapping is introduced to fix
        # compatibility issue.
        weekday_mapping = {
            0: (2, "MONDAY"),
            1: (3, "TUESDAY"),
            2: (4, "WEDNESDAY"),
            3: (5, "THURSDAY"),
            4: (6, "FRIDAY"),
            5: (7, "SATURDAY"),
            6: (1, "SUNDAY"),
        }
        today = datetime.now()
        table_headings = ["S/N", "Event", "Time", "Duration(H)"]
        weekday_events = AttendanceSession.objects.filter(
            event_type__in=(EventTypeChoices.LECTURE, EventTypeChoices.LAB),
            start_time__week_day=weekday_mapping[today.weekday()][0],
        )
        scheduled_events = AttendanceSession.objects.filter(
            start_time__day=today.day,
            start_time__month=today.month,
            start_time__year=today.year,
            initiator__isnull=True,
        )

        weekday_event_dict = list(
            weekday_events.values(
                "id", "course__code", "event_type", "start_time", "duration"
            )
        )
        scheduled_event_dict = list(
            scheduled_events.values(
                "id", "course__code", "event_type", "start_time", "duration"
            )
        )

        # save list index-to-AttendanceSession ID mapping to sections
        # of the configparser
        if scheduled_event_dict:
            app_config.cp["scheduled_events"] = {
                idx: k["id"] for idx, k in enumerate(scheduled_event_dict)
            }
        if weekday_event_dict:
            app_config.cp["weekly_events"] = {
                idx: k["id"] for idx, k in enumerate(weekday_event_dict)
            }

        scheduled_event_rows = []
        for idx, record in enumerate(scheduled_event_dict, 1):
            scheduled_event_rows.append(
                [
                    idx,
                    "".join(
                        [
                            "  ",
                            record["course__code"],
                            " ",
                            EventTypeChoices(record["event_type"]).label[:4],
                            ".  ",
                        ]
                    ),
                    record["start_time"].strftime("%H:%M"),
                    record["duration"],
                ]
            )

        weekly_event_rows = []
        for idx, record in enumerate(weekday_event_dict, 1):
            weekday = record["start_time"].weekday()
            event_weekday = weekday_mapping[weekday][1]
            weekly_event_rows.append(
                [
                    idx,
                    "".join(
                        [
                            record["course__code"],
                            " ",
                            EventTypeChoices(record["event_type"]).label[:4],
                            ".",
                        ]
                    ),
                    "".join(
                        [
                            event_weekday[:4],
                            " ",
                            record["start_time"].strftime("%H:%M"),
                        ]
                    ),
                    record["duration"],
                ]
            )

        layout = [
            [sg.Push(), sg.Text("Scheduled Events (Today)"), sg.Push()],
            [
                sg.Push(),
                sg.Table(
                    scheduled_event_rows,
                    headings=table_headings,
                    k="scheduled_events",
                    enable_click_events=True,
                    justification="center",
                ),
                sg.Push(),
            ],
            [sg.HorizontalSeparator()],
            [sg.Push(), sg.Text("Weekly Events"), sg.Push()],
            [
                sg.Table(
                    weekly_event_rows,
                    headings=table_headings,
                    k="weekly_events",
                    enable_click_events=True,
                    justification="center",
                )
            ],
            cls.navigation_pane(next_icon="next_disabled"),
        ]
        scrolled_layout = [
            [
                sg.Column(
                    layout,
                    scrollable=True,
                    vertical_scroll_only=True,
                    expand_y=True,
                    expand_x=False,
                    pad=(0, 0),
                    key="main_column",
                )
            ]
        ]
        window = sg.Window(
            "Scheduled Events", scrolled_layout, **cls.window_init_dict()
        )
        return window

    @classmethod
    def loop(
        cls, window: sg.Window, event: str, values: Dict[str, Any]
    ) -> bool:
        """Track user interaction with the window."""
        if event in ("home", "back"):
            window_dispatch.dispatch.open_window("HomeWindow")
            return True
        if "scheduled_events" in event and event[2][0] is not None:
            event_id = app_config.cp["scheduled_events"][str(event[2][0])]
            event_obj = AttendanceSession.objects.get(id=event_id)
            if event_obj.start_time.hour < datetime.now().hour - 1:
                cls.popup_auto_close_error("Event Time Expired")
                return True

            confirm_start = sg.popup_yes_no(
                "Starting scheduled event %s. Continue?"
                % event_obj.course.code,
                title="Start Event",
                keep_on_top=True,
            )
            if confirm_start != "Yes":
                return True

            event_detail_dict = {
                "course": f"{event_obj.course.code} : {event_obj.course.title}",
                "type": EventTypeChoices(event_obj.event_type).label,
                "recurring": event_obj.recurring,
                "start_time": event_obj.start_time.strftime("%H:%M"),
                "start_date": event_obj.start_time.strftime("%d-%m-%Y"),
                "duration": str(event_obj.duration).split(":")[0],
                "session_id": event_obj.id,
            }
            app_config.cp["new_event"] = event_detail_dict
            window_dispatch.dispatch.open_window("NewEventSummaryWindow")
            return True
        if "weekly_events" in event and event[2][0] is not None:
            existing_event_id = app_config.cp["weekly_events"][str(event[2][0])]
            existing_obj = AttendanceSession.objects.get(id=existing_event_id)
            if existing_obj.start_time.hour < datetime.now().hour - 1:
                cls.popup_auto_close_error("Event Time Expired.")
                return True

            confirm_start = sg.popup_yes_no(
                "Starting weekly event %s. Continue?"
                % existing_obj.course.code,
                title="Start Event",
                keep_on_top=True,
            )
            if confirm_start != "Yes":
                return True

            # There is need to create a new AttendanceSession obj
            # using data from the existing event like: course,
            today = datetime.now()
            new_event_dict = {
                "course": existing_obj.course,
                "event_type": existing_obj.event_type,
                "recurring": existing_obj.recurring,
                "start_time": datetime(
                    year=today.year,
                    month=today.month,
                    day=today.day,
                    hour=existing_obj.start_time.hour,
                    minute=existing_obj.start_time.minute,
                    tzinfo=timezone.utc,
                ),
                "duration": existing_obj.duration,
                "node_device": existing_obj.node_device,
                "session": existing_obj.session,
            }
            try:
                new_event_obj, _ = AttendanceSession.objects.get_or_create(
                    **new_event_dict
                )
            except Exception as e:
                cls.popup_auto_close_error(e)
                return True
            event_detail_dict = {
                "course": f"{new_event_obj.course.code} : {new_event_obj.course.title}",
                "type": EventTypeChoices(new_event_obj.event_type).label,
                "recurring": new_event_obj.recurring,
                "start_time": new_event_obj.start_time.strftime("%H:%M"),
                "start_date": new_event_obj.start_time.strftime("%d-%m-%Y"),
                "duration": str(new_event_obj.duration).split(":")[0],
                "session_id": new_event_obj.id,
            }
            app_config.cp["new_event"] = event_detail_dict
            window_dispatch.dispatch.open_window("NewEventSummaryWindow")
            return True
        return True
