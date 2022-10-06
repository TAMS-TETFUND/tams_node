import PySimpleGUI as sg
from datetime import datetime, timedelta

from app.basegui import BaseGUIWindow
from app.gui_utils import ValidationMixin
import app.appconfigparser
import app.windowdispatch
from db.models import Course, Faculty, Department


app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


class EventDetailWindow(ValidationMixin, BaseGUIWindow):
    """Window to for user to specify event deatils like: course,
    start date, and event duration"""

    @classmethod
    def window(cls):
        combo_props = {"size": 32}
        field_label_props = {"size": 12}
        section1 = [
            [
                sg.Text("Faculty:", **field_label_props),
                sg.Combo(
                    Faculty.get_all_faculties(),
                    default_value=cls.COMBO_DEFAULT,
                    enable_events=True,
                    key="course_faculty",
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
                    key="course_department",
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
                        semester=app_config.cp.get("DEFAULT", "semester")
                    ),
                    default_value=cls.COMBO_DEFAULT,
                    enable_events=True,
                    key="selected_course",
                    expand_y=True,
                    size=32,
                ),
            ],
            [
                sg.Image(
                    data=cls.get_icon("up_arrow", 0.25),
                    k="filter_courses_img",
                    enable_events=True,
                ),
                sg.Text(
                    "Filter Courses",
                    enable_events=True,
                    k="filter_courses",
                    text_color=cls.UI_COLORS["dull_yellow"],
                ),
            ],
            [
                sg.pin(
                    sg.Column(section1, k="sec1", visible=False, expand_y=True)
                )
            ],
            [sg.HorizontalSeparator()],
            [
                sg.Text("Start Time:", **field_label_props),
                sg.Spin(
                    values=[str(a).zfill(2) for a in range(0, 24)],
                    initial_value="08",
                    expand_y=True,
                    key="start_hour",
                ),
                sg.Spin(
                    values=[str(a).zfill(2) for a in range(0, 60)],
                    initial_value="00",
                    expand_y=True,
                    key="start_minute",
                ),
                sg.Input(
                    default_text=datetime.strftime(datetime.now(), "%d-%m-%Y"),
                    key="start_date",
                    size=(20, 1),
                    expand_y=True,
                ),
                sg.Button(
                    image_data=cls.get_icon("calendar", 0.25),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="pick_date",
                    expand_y=True,
                ),
            ],
            [
                sg.Text("Duration:", **field_label_props),
                sg.Spin(
                    values=[str(a).zfill(2) for a in range(0, 12)],
                    initial_value="01",
                    expand_y=True,
                    key="duration",
                ),
                sg.Text("Hour(s)"),
            ],
            [sg.VPush()],
            [sg.Button("Submit", key="submit")],
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
                    key="main_column",
                )
            ]
        ]

        window = sg.Window(
            "Event Details",
            scrolled_layout,
            return_keyboard_events=True,
            **cls.window_init_dict(),
        )
        return window

    @classmethod
    def loop(cls, window, event, values):
        if event.startswith("filter_courses"):
            window["filter_courses_img"].update(
                data=EventDetailWindow.get_icon("down_arrow", 0.25)
            )
            window["sec1"].update(visible=True)
            window.refresh()
            window["main_column"].contents_changed()

        if event == "course_faculty":
            if values["course_faculty"] in (cls.COMBO_DEFAULT, None):
                window["course_department"].update(
                    values=Department.get_departments(), value=cls.COMBO_DEFAULT
                )
            else:
                window["course_department"].update(
                    values=Department.get_departments(values["course_faculty"]),
                    value=cls.COMBO_DEFAULT,
                )
                window["selected_course"].update(
                    values=Course.get_courses(
                        semester=app_config.cp.get("DEFAULT", "semester"),
                        faculty=values["course_faculty"],
                    ),
                    value=cls.COMBO_DEFAULT,
                )
        if event == "course_department":
            if values["course_department"] in (cls.COMBO_DEFAULT, None):
                window["selected_course"].update(
                    values=Course.get_courses(
                        semester=app_config.cp.get("DEFAULT", "semester")
                    ),
                    value=cls.COMBO_DEFAULT,
                )
            else:
                window["selected_course"].update(
                    values=Course.get_courses(
                        semester=app_config.cp.get("DEFAULT", "semester"),
                        department=values["course_department"],
                    ),
                    value=cls.COMBO_DEFAULT,
                )
        if event == "pick_date":
            event_date = sg.popup_get_date(
                close_when_chosen=True, keep_on_top=False, modal=False
            )
            if event_date is None:
                return True
            else:
                window["start_date"].update(
                    value=f"{event_date[1]}-{event_date[0]}-{event_date[2]}"
                )
            window.force_focus()
        if event in ("next", "submit"):
            if cls.validate(values, window) is not None:
                window.refresh()
                window["main_column"].contents_changed()
                return True

            app_config.cp["new_event"]["course"] = values["selected_course"]
            app_config.cp["new_event"]["start_time"] = (
                    values["start_hour"] + ":" + values["start_minute"]
            )
            app_config.cp["new_event"]["start_date"] = values["start_date"]
            app_config.cp["new_event"]["duration"] = values["duration"]
            window_dispatch.dispatch.open_window("NewEventSummaryWindow")
        if event == "home":
            app_config.cp.remove_section("new_event")
            window_dispatch.dispatch.open_window("HomeWindow")

        return True

    @classmethod
    def validate(cls, values, window):

        required_fields = [
            (values["selected_course"], "selected course"),
            (values["start_hour"], "start time"),
            (values["start_date"], "start time"),
            (values["duration"], "duration"),
        ]
        validation_val = cls.validate_required_fields(required_fields, window)
        if validation_val is not None:
            return True

        if Course.str_to_course(values["selected_course"]) is None:
            cls.display_message("Invalid course selected", window)
            return True

        for val_check in (
                cls.validate_int_field(values["start_hour"], "start time"),
                cls.validate_int_field(values["start_minute"], "start time"),
        ):
            if val_check is not None:
                cls.display_message(val_check, window)
                return True

        if (
                cls.validate_int_field(values["duration"], "duration") is not None
                or int(values["duration"]) <= 0
        ):
            cls.display_message("Invalid value in duration", window)
            return True

        start_datetime = (
            f'{values["start_date"]} '
            f'{values["start_hour"]}:{values["start_minute"]}'
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