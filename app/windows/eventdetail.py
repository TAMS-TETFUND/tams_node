from typing import Any, Dict, List, Optional
import PySimpleGUI as sg
from datetime import datetime, timedelta

from app.basegui import BaseGUIWindow
from app.guiutils import ValidationMixin
import app.appconfigparser
import app.windowdispatch
from db.models import Course, Faculty, Department


app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


class EventDetailWindow(ValidationMixin, BaseGUIWindow):
    """Window to for user to specify event deatils like: course,
    start date, and event duration"""
    __slots__ = ()

    @classmethod
    def window(cls) -> List[Any]:
        """Construct layout/appearance of window."""
        combo_props = {"size": 30}
        field_label_props = {"size": 12}
        section1 = [
            [
                sg.Text("Faculty:", **field_label_props),
                sg.Combo(
                    Faculty.get_all_faculties(),
                    default_value=cls.COMBO_DEFAULT,
                    enable_events=True,
                    key=cls.key("course_faculty"),
                    expand_y=True,
                    **combo_props,
                ),
            ],
            [
                sg.Text("Department:", **field_label_props),
                sg.Combo(
                    Department.get_departments(),
                    default_value=cls.COMBO_DEFAULT,
                    enable_events=True,
                    key=cls.key("course_department"),
                    expand_y=True,
                    **combo_props,
                ),
            ],
        ]
        column1 = [
            [sg.Push(), sg.Text("Event Details"), sg.Push()],
            [sg.HorizontalSeparator()],
            [sg.VPush()],
            [cls.message_display_field()],
            [
                sg.Text("Select Course:", **field_label_props),
                sg.Combo(
                    Course.get_courses(
                        semester=app_config.cp.get("DEFAULT", "semester", fallback="")
                    ),
                    default_value=cls.COMBO_DEFAULT,
                    enable_events=True,
                    key=cls.key("selected_course"),
                    expand_y=True,
                    size=31,
                ),
            ],
            [
                sg.Image(
                    data=cls.get_icon("up_arrow", 0.25),
                    k=cls.key("filter_courses_img"),
                    enable_events=True,
                ),
                sg.Text(
                    "Filter Courses",
                    enable_events=True,
                    k=cls.key("filter_courses"),
                    text_color=cls.UI_COLORS["dull_yellow"],
                ),
            ],
            [
                sg.pin(
                    sg.Column(
                        section1,
                        k=cls.key("sec1"),
                        visible=False,
                        expand_y=True,
                    )
                )
            ],
            [sg.HorizontalSeparator()],
            [
                sg.Text("Start Time:", **field_label_props),
                sg.Spin(
                    values=[str(a).zfill(2) for a in range(0, 24)],
                    initial_value="08",
                    expand_y=True,
                    key=cls.key("start_hour"),
                ),
                sg.Spin(
                    values=[str(a).zfill(2) for a in range(0, 60)],
                    initial_value="00",
                    expand_y=True,
                    key=cls.key("start_minute"),
                ),
                sg.Input(
                    default_text=datetime.strftime(datetime.now(), "%d-%m-%Y"),
                    key=cls.key("start_date"),
                    size=(19, 1),
                    expand_y=True,
                ),
                sg.Button(
                    image_data=cls.get_icon("calendar", 0.25),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key=cls.key("pick_date"),
                    expand_y=True,
                ),
            ],
            [
                sg.Text("Duration:", **field_label_props),
                sg.Spin(
                    values=[str(a).zfill(2) for a in range(0, 12)],
                    initial_value="01",
                    expand_y=True,
                    key=cls.key("duration"),
                ),
                sg.Text("Hour(s)"),
            ],
            [sg.Button("Submit", key=cls.key("submit"))],
            [sg.VPush()],
            cls.navigation_pane(back_icon="back_disabled"),
        ]

        scrolled_layout = [
            [
                sg.Column(
                    column1,
                    scrollable=True,
                    vertical_scroll_only=True,
                    expand_y=True,
                    expand_x=True,
                    pad=(0, 0),
                    key=cls.key("main_column"),
                )
            ]
        ]
        return scrolled_layout

    @classmethod
    def loop(
        cls, window: sg.Window, event: str, values: Dict[str, Any]
    ) -> bool:
        """Track user interaction with window."""
        if event.startswith("".join([cls.key_prefix(), "filter_courses"])):
            window[cls.key("filter_courses_img")].update(
                data=EventDetailWindow.get_icon("down_arrow", 0.25)
            )
            window[cls.key("sec1")].update(visible=True)
            window.refresh()
            window[cls.key("main_column")].contents_changed()

        if event == cls.key("course_faculty"):
            if values[cls.key("course_faculty")] in (cls.COMBO_DEFAULT, None):
                window[cls.key("course_department")].update(
                    values=Department.get_departments(), value=cls.COMBO_DEFAULT
                )
            else:
                window[cls.key("course_department")].update(
                    values=Department.get_departments(
                        values[cls.key("course_faculty")]
                    ),
                    value=cls.COMBO_DEFAULT,
                )
                window[cls.key("selected_course")].update(
                    values=Course.get_courses(
                        semester=app_config.cp.get("DEFAULT", "semester", fallback=""),
                        faculty=values[cls.key("course_faculty")],
                    ),
                    value=cls.COMBO_DEFAULT,
                )
        if event == cls.key("course_department"):
            if values[cls.key("course_department")] in (
                cls.COMBO_DEFAULT,
                None,
            ):
                window[cls.key("selected_course")].update(
                    values=Course.get_courses(
                        semester=app_config.cp.get("DEFAULT", "semester", fallback="")
                    ),
                    value=cls.COMBO_DEFAULT,
                )
            else:
                window[cls.key("selected_course")].update(
                    values=Course.get_courses(
                        semester=app_config.cp.get("DEFAULT", "semester", fallback=""),
                        department=values[cls.key("course_department")],
                    ),
                    value=cls.COMBO_DEFAULT,
                )
        if event == cls.key("pick_date"):
            event_date = sg.popup_get_date(
                close_when_chosen=True, no_titlebar=False
            )
            if event_date is None:
                return True
            else:
                window[cls.key("start_date")].update(
                    value=f"{event_date[1]}-{event_date[0]}-{event_date[2]}"
                )
            window.force_focus()
        if event in (cls.key("next"), cls.key("submit")):
            if cls.validate(values, window) is not None:
                window.refresh()
                window[cls.key("main_column")].contents_changed()
                return True

            app_config.cp["new_event"]["course"] = values[
                cls.key("selected_course")
            ]
            app_config.cp["new_event"]["start_time"] = (
                values[cls.key("start_hour")]
                + ":"
                + values[cls.key("start_minute")]
            )
            app_config.cp["new_event"]["start_date"] = values[
                cls.key("start_date")
            ]
            app_config.cp["new_event"]["duration"] = values[cls.key("duration")]
            app_config.cp.save()

            window_dispatch.dispatch.open_window("NewEventSummaryWindow")
        if event == cls.key("home"):
            app_config.cp.remove_section("new_event")
            window_dispatch.dispatch.open_window("HomeWindow")

        return True

    @classmethod
    def validate(
        cls, values: Dict[str, Any], window: sg.Window
    ) -> Optional[bool]:
        """Validate values supplied by user in the window input fields."""

        required_fields = [
            (values[cls.key("selected_course")], "selected course"),
            (values[cls.key("start_hour")], "start time"),
            (values[cls.key("start_date")], "start time"),
            (values[cls.key("duration")], "duration"),
        ]
        validation_val = cls.validate_required_fields(required_fields, window)
        if validation_val is not None:
            return True

        if Course.str_to_course(values[cls.key("selected_course")]) is None:
            cls.display_message("Invalid course selected", window)
            return True

        for val_check in (
            cls.validate_int_field(values[cls.key("start_hour")], "start time"),
            cls.validate_int_field(
                values[cls.key("start_minute")], "start time"
            ),
        ):
            if val_check is not None:
                cls.display_message(val_check, window)
                return True

        if (
            cls.validate_int_field(values[cls.key("duration")], "duration")
            is not None
            or int(values[cls.key("duration")]) <= 0
        ):
            cls.display_message("Invalid value in duration", window)
            return True

        start_datetime = (
            f'{values[cls.key("start_date")]} '
            f'{values[cls.key("start_hour")]}:{values[cls.key("start_minute")]}'
        )
        try:
            start_date = datetime.strptime(start_datetime, "%d-%m-%Y %H:%M")
        except ValueError:
            cls.display_message("Invalid start date", window)
            return True

        current_dt = datetime.now() - timedelta(hours=1)

        if current_dt > start_date:
            cls.display_message(
                "Date and time must not be earlier than current date and time",
                window,
            )
            return True

        return None

    @classmethod
    def refresh_dynamic_fields(cls, window: sg.Window) -> None:
        cls.hide_message_display_field(window)
        return super().refresh_dynamic_fields(window)