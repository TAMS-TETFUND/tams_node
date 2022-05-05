from datetime import datetime, timedelta
import time
from unicodedata import name

import PySimpleGUI as sg
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError

from app.appconfigparser import AppConfigParser
from app.basegui import BaseGUIWindow

from app.camera import Camera
from app.barcode import Barcode
from app.facerec import FaceRecognition
from app.windowdispatch import WindowDispatch
from manage import init_django

init_django()

from db.models import (
    AttendanceRecord,
    AttendanceSession,
    AcademicSession,
    EventType,
    Student,
    Sex,
    Staff,
    Course,
    Faculty,
    Semester,
    Department,
    face_enc_to_str,
    str_to_face_enc,
)

# initializing the configparser object
app_config = AppConfigParser()

# initializing WindowDispatch object
window_dispatch = WindowDispatch()


class HomeWindow(BaseGUIWindow):
    @classmethod
    def window(cls):
        column1 = [
            [
                sg.Push(),
                sg.Button(
                    image_data=cls.get_icon("new"),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="new_event",
                ),
                sg.Push(),
            ],
            [sg.Push(), sg.Text("New Event"), sg.Push()],
        ]
        column2 = [
            [
                sg.Push(),
                sg.Button(
                    image_data=cls.get_icon("right_arrow"),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="continue_attendance",
                ),
                sg.Push(),
            ],
            [sg.Push(), sg.Text("Continue Attendance"), sg.Push()],
        ]
        column3 = [
            [
                sg.Push(),
                sg.Button(
                    image_data=cls.get_icon("schedule"),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="schedule",
                ),
                sg.Push(),
            ],
            [sg.Push(), sg.Text("Scheduled/Recurring Events"), sg.Push()],
        ]
        layout = [
            [
                sg.Push(),
                sg.Button(
                    image_data=cls.get_icon("settings", 0.5),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="settings",
                ),
                sg.Button(
                    image_data=cls.get_icon("power", 0.5),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="quit",
                ),
            ],
            [sg.VPush()],
            [
                sg.Push(),
                sg.Column(column1),
                sg.Column(column2),
                sg.Column(column3),
                sg.Push(),
            ],
            [sg.VPush()],
            [sg.Text("_" * 80)],
            [sg.Push(), sg.Text("TAMS© 2022"), sg.Push()],
        ]

        window = sg.Window("Home Window", layout, **cls.window_init_dict())
        return window

    @classmethod
    def loop(cls, window, event, values):
        if event == "new_event":
            window_dispatch.open_window(EventMenuWindow)
        if event == "continue_attendance":
            if app_config.has_section("current_attendance_session"):
                if app_config.has_option(
                    "current_attendance_session", "initiator_id"
                ):
                    window_dispatch.open_window(ActiveEventSummaryWindow)
                else:
                    app_config["new_event"] = app_config[
                        "current_attendance_session"
                    ]
                    window_dispatch.open_window(NewEventSummaryWindow)
            else:
                sg.popup(
                    "No active attendance-taking event found.", title="No Event"
                )
        if event == "settings":
            window_dispatch.open_window(EnrolmentMenuWindow)
        if event == "quit":
            return HomeWindow.confirm_exit()
        return True

    @staticmethod
    def confirm_exit():
        clicked = sg.popup_ok_cancel(
            "System will shutdown. Do you want to continue?",
            title="Shutdown",
            keep_on_top=True,
        )
        if clicked == "OK":
            return False
        if clicked in ("Cancel", None):
            pass
        return True


class EventMenuWindow(BaseGUIWindow):
    @classmethod
    def window(cls):
        column1 = [
            [
                sg.Push(),
                sg.Button(
                    image_data=cls.get_icon("lecture"),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="lecture",
                ),
                sg.Push(),
            ],
            [sg.Push(), sg.Text("Lecture"), sg.Push()],
        ]

        column2 = [
            [
                sg.Push(),
                sg.Button(
                    image_data=cls.get_icon("lab"),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="lab",
                ),
                sg.Push(),
            ],
            [sg.Push(), sg.Text("Lab"), sg.Push()],
        ]

        column3 = [
            [
                sg.Push(),
                sg.Button(
                    image_data=cls.get_icon("test_script"),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="quiz",
                ),
                sg.Push(),
            ],
            [sg.Push(), sg.Text("Quiz"), sg.Push()],
        ]

        column4 = [
            [
                sg.Push(),
                sg.Button(
                    image_data=cls.get_icon("graduation_cap"),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="examination",
                ),
                sg.Push(),
            ],
            [sg.Push(), sg.Text("Examination"), sg.Push()],
        ]

        layout = [
            [
                sg.Push(),
                sg.Text("Take Attendance for:", font="Any 20"),
                sg.Push(),
            ],
            [sg.Text("_" * 80)],
            [sg.VPush()],
            [
                sg.Push(),
                sg.Column(column1),
                sg.Column(column2),
                sg.Column(column3),
                sg.Column(column4),
                sg.Push(),
            ],
            [sg.VPush()],
            [sg.Text("_" * 80)],
            [sg.Push(), sg.Button("<< Back", key="back"), sg.Push()],
        ]

        window = sg.Window("Event Menu", layout, **cls.window_init_dict())
        return window

    @classmethod
    def loop(cls, window, event, values):
        if event in (sg.WIN_CLOSED, "back"):
            window_dispatch.open_window(HomeWindow)
        if event in ("lecture", "examination", "lab", "quiz"):
            app_config["new_event"] = {}
            app_config["new_event"]["type"] = event
            if event in ("lecture", "lab"):
                recurring = sg.popup_yes_no(
                    f"Is this {event} a weekly activity?",
                    title="Event detail",
                    keep_on_top=True,
                )
                if recurring == "Yes":
                    app_config["new_event"]["recurring"] = "True"
                else:
                    app_config["new_event"]["recurring"] = "False"

            app_config.save()
            window_dispatch.open_window(AcademicSessionDetailsWindow)
        return True


class AcademicSessionDetailsWindow(BaseGUIWindow):
    @classmethod
    def window(cls):
        layout = [
            [sg.Push(), sg.Text("Academic Session Details"), sg.Push()],
            [sg.Text("_" * 80)],
            [sg.VPush()],
            [
                [cls.message_display_field()],
                sg.Text("Select Current Session:  "),
                sg.Combo(
                    AcademicSession.get_all_academic_sessions(),
                    default_value=AcademicSession.get_all_academic_sessions()[
                        0
                    ],
                    enable_events=True,
                    key="current_session",
                    expand_y=True,
                ),
            ],
            [
                sg.Text("Select Current Semester: "),
                sg.Combo(
                    Semester.labels,
                    default_value=Semester.labels[0],
                    enable_events=True,
                    key="current_semester",
                    expand_y=True,
                ),
            ],
            [sg.VPush()],
            [
                sg.Push(),
                sg.Button("<< Back", key="back"),
                sg.Button("Next >>", key="next"),
                sg.Button("Cancel", key="cancel"),
                sg.Push(),
            ],
        ]

        window = sg.Window(
            "Academic Session Details", layout, **cls.window_init_dict()
        )
        return window

    @classmethod
    def loop(cls, window, event, values):
        if event == "next":
            if cls.validate(values, window) is not None:
                return True

            app_config["DEFAULT"]["semester"] = values["current_semester"]
            app_config["DEFAULT"]["session"] = values["current_session"]
            app_config.save()
            window_dispatch.open_window(EventDetailWindow)
        elif event == "back":
            window_dispatch.open_window(EventMenuWindow)
        elif event == "cancel":
            window_dispatch.open_window(HomeWindow)
        return True

    @classmethod
    def validate(cls, values, window):
        required_fields = [
            (values["current_semester"], "current semester"),
            (values["current_session"], "current session"),
        ]
        if cls.validate_required_fields(required_fields, window) is not None:
            return True

        validation_val = cls.validate_semester(values["current_semester"])
        if validation_val is not None:
            cls.display_message(validation_val, window)
            return True

        validation_val = cls.validate_academic_session(
            values["current_session"]
        )
        if validation_val is not None:
            cls.display_message(validation_val, window)
            return True
        return None


class EventDetailWindow(BaseGUIWindow):
    @classmethod
    def window(cls):
        section1 = [
            [
                sg.Text("Faculty:  "),
                sg.Combo(
                    Faculty.get_all_faculties(),
                    default_value=cls.COMBO_DEFAULT,
                    enable_events=True,
                    key="course_faculty",
                    expand_y=True,
                ),
            ],
            [
                sg.Text("Department:  "),
                sg.Combo(
                    Department.get_departments(),
                    default_value=cls.COMBO_DEFAULT,
                    enable_events=True,
                    key="course_department",
                    expand_y=True,
                ),
            ],
        ]
        layout = [
            [sg.Push(), sg.Text("Event Details"), sg.Push()],
            [sg.Text("_" * 80)],
            [sg.VPush()],
            [
                [cls.message_display_field()],
                sg.Text("Select Course:  "),
                sg.Combo(
                    Course.get_courses(
                        semester=app_config.get("DEFAULT", "semester")
                    ),
                    default_value=cls.COMBO_DEFAULT,
                    enable_events=True,
                    key="selected_course",
                    expand_y=True,
                ),
            ],
            [
                sg.Image(
                    data=cls.get_icon("up_arrow", 0.25),
                    k="filter_courses_img",
                    enable_events=True,
                ),
                sg.Text(
                    "Filter Courses", enable_events=True, k="filter_courses"
                ),
            ],
            [
                sg.pin(
                    sg.Column(section1, k="sec1", visible=False, expand_y=True)
                )
            ],
            [sg.Text("_" * 80)],
            [
                sg.Text("Start Time: "),
                sg.Spin(
                    values=[str(a).zfill(2) for a in range(0, 24)],
                    initial_value="08",
                    expand_x=True,
                    expand_y=True,
                    key="start_hour",
                ),
                sg.Spin(
                    values=[str(a).zfill(2) for a in range(0, 60)],
                    initial_value="00",
                    expand_x=True,
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
                sg.Text("Duration: "),
                sg.Spin(
                    values=[str(a).zfill(2) for a in range(0, 12)],
                    initial_value="01",
                    expand_x=True,
                    expand_y=True,
                    key="duration",
                ),
                sg.Text("Hour(s)"),
            ],
            [
                sg.Push(),
                sg.Button("Next", k="next"),
                sg.Button("Cancel", k="cancel"),
                sg.Push(),
            ],
            [sg.VPush()],
        ]

        window = sg.Window("Event Details", layout, **cls.window_init_dict())
        return window

    @classmethod
    def loop(cls, window, event, values):
        if event.startswith("filter_courses"):
            window["filter_courses_img"].update(
                data=EventDetailWindow.get_icon("down_arrow", 0.25)
            )
            window["sec1"].update(visible=True)
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
                        semester=app_config.get("DEFAULT", "semester"),
                        faculty=values["course_faculty"],
                    ),
                    value=cls.COMBO_DEFAULT,
                )
        if event == "course_department":
            if values["course_department"] in (cls.COMBO_DEFAULT, None):
                window["selected_course"].update(
                    values=Course.get_courses(
                        semester=app_config.get("DEFAULT", "semester")
                    ),
                    value=cls.COMBO_DEFAULT,
                )
            else:
                window["selected_course"].update(
                    values=Course.get_courses(
                        semester=app_config.get("DEFAULT", "semester"),
                        department=values["course_department"],
                    ),
                    value=cls.COMBO_DEFAULT,
                )
        if event == "pick_date":
            event_date = sg.popup_get_date()
            if event_date is None:
                return True
            else:
                window["start_date"].update(
                    value=f"{event_date[1]}-{event_date[0]}-{event_date[2]}"
                )
            window.force_focus()
        if event == "next":
            if cls.validate(values, window) is not None:
                return True

            app_config["new_event"]["course"] = values["selected_course"]
            app_config["new_event"]["start_time"] = (
                values["start_hour"] + ":" + values["start_minute"]
            )
            app_config["new_event"]["start_date"] = values["start_date"]
            app_config["new_event"]["duration"] = values["duration"]
            app_config.save()
            window_dispatch.open_window(NewEventSummaryWindow)
        if event == "cancel":
            app_config.remove_section("new_event")
            app_config.save()
            window_dispatch.open_window(HomeWindow)
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

        start_datetime = f'{values["start_date"]} {values["start_hour"]}:{values["start_minute"]}'
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


class NewEventSummaryWindow(BaseGUIWindow):
    @classmethod
    def window(cls):
        new_event_dict = app_config["new_event"]
        layout = [
            [
                sg.Push(),
                sg.Text(
                    "New {} Event".format(new_event_dict["type"].capitalize())
                ),
                sg.Push(),
            ],
            [sg.Text("_" * 80)],
            [sg.VPush()],
            [cls.message_display_field()],
            [sg.Text(f"Course: {new_event_dict['course']}")],
            [
                sg.Text(
                    f"Session Details: {new_event_dict['session']} {new_event_dict['semester']}"
                )
            ],
            [
                sg.Text(
                    f"Start Time: {new_event_dict['start_date']} {new_event_dict['start_time']}"
                )
            ],
            [sg.Text(f"Duration: {new_event_dict['duration']} Hours")],
            [sg.VPush()],
            [sg.Text("_" * 80)],
            [
                sg.Button("Start Event", k="start_event"),
                sg.Button("Schedule Event", k="schedule_event"),
                sg.Button("Edit Details", k="edit"),
                sg.Button("Cancel", k="cancel"),
            ],
        ]
        window = sg.Window(
            "New Event Summary", layout, **cls.window_init_dict()
        )
        return window

    @classmethod
    def loop(cls, window, event, values):
        if event in ("start_event" "schedule_event"):
            new_event = dict(app_config["new_event"])
            attendance_session_model_kwargs = {
                "course_id": Course.str_to_course(new_event["course"]),
                "session": AcademicSession.objects.get(
                    session__iexact=new_event["session"]
                ),
                "event_type": EventType.str_to_value(new_event["type"]),
                "start_time": datetime.strptime(
                    f"{new_event['start_date']} {new_event['start_time']}",
                    "%d-%m-%Y %H:%M",
                ),
                "duration": timedelta(hours=int(new_event["duration"])),
                "recurring": eval(new_event["recurring"]),
            }
            try:
                att_session = AttendanceSession.objects.create(
                    **attendance_session_model_kwargs
                )
            except IntegrityError:
                cls.display_message("Event has already been created", window)
                att_session = AttendanceSession.objects.get(
                    **attendance_session_model_kwargs
                )
            app_config["current_attendance_session"] = app_config.section_dict(
                "new_event"
            )
            app_config["current_attendance_session"]["session_id"] = str(
                att_session.id
            )
            app_config.remove_section("new_event")
            app_config.save()

            if att_session.initiator:
                app_config["current_attendance_session"]["initiator_id"] = str(
                    att_session.initiator.id
                )
                window_dispatch.open_window(ActiveEventSummaryWindow)
                return True

            if event == "start_event":
                window_dispatch.open_window(StaffBarcodeCameraWindow)

            if event == "schedule_event":
                sg.popup(
                    "Event saved to scheduled events",
                    title="Event saved",
                    keep_on_top=True,
                )
                window_dispatch.open_window(HomeWindow)

        if event == "cancel":
            app_config.remove_section("new_event")
            app_config.save()
            window_dispatch.open_window(HomeWindow)
        return True


class ActiveEventSummaryWindow(BaseGUIWindow):
    @classmethod
    def window(cls):
        new_event_dict = app_config["current_attendance_session"]
        layout = [
            [
                sg.Push(),
                sg.Text(
                    "On-going {} Event".format(
                        new_event_dict["type"].capitalize()
                    )
                ),
                sg.Push(),
            ],
            [sg.Text("_" * 80)],
            [sg.VPush()],
            [cls.message_display_field()],
            [sg.Text(f"Course: {new_event_dict['course']}")],
            [
                sg.Text(
                    f"Session Details: {new_event_dict['session']} {new_event_dict['semester']}"
                )
            ],
            [
                sg.Text(
                    f"Start Time: {new_event_dict['start_date']} {new_event_dict['start_time']}"
                )
            ],
            [sg.Text(f"Duration: {new_event_dict['duration']} Hours")],
            [sg.VPush()],
            [sg.Text("_" * 80)],
            [
                sg.Button("Continue Event", k="continue_event"),
                sg.Button("Cancel", k="cancel"),
            ],
        ]
        window = sg.Window(
            "Active Event Summary", layout, **cls.window_init_dict()
        )
        return window

    @classmethod
    def loop(cls, window, event, values):
        if event == "continue_event":
            active_event = app_config["current_attendance_session"]

            try:
                initiator = Staff.objects.get(
                    id=active_event.getint("initiator_id")
                )
            except ObjectDoesNotExist:
                sg.popup(
                    "System error. Please try creating event again",
                    title="Error",
                )
                window_dispatch.open_window(HomeWindow)
                return True

            app_config["tmp_staff"] = initiator.values(
                "id",
                "staff_number",
                "first_name",
                "last_name",
                "department__name",
                "department__faculty__name",
                "face_encodings",
                "fingerprint_template",
            )
            app_config.save()
            window_dispatch.open_window(StaffFaceCameraWindow)
        return True


class VerifyAttendanceInitiatorWindow(BaseGUIWindow):
    @classmethod
    def window(cls):
        column1 = [
            [
                sg.Push(),
                sg.Button(
                    image_data=cls.get_icon("face_scanner"),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="facial_verification",
                ),
                sg.Push(),
            ],
            [sg.Push(), sg.Text("Face ID"), sg.Push()],
        ]

        column2 = [
            [
                sg.Push(),
                sg.Button(
                    image_data=cls.get_icon("fingerprint"),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="fingerprint_verification",
                ),
                sg.Push(),
            ],
            [sg.Push(), sg.Text("Fingerprint"), sg.Push()],
        ]

        layout = [
            [
                sg.Text(
                    "Only registered staff can initiate attendance taking."
                ),
                sg.Push(),
            ],
            [sg.Text("Verify identity via:"), sg.Push()],
            [sg.Text("_" * 80)],
            [sg.VPush()],
            [sg.Push(), sg.Column(column1), sg.Column(column2), sg.Push()],
            [sg.VPush()],
            [sg.Text("_" * 80)],
            [sg.Push(), sg.Button("<< Back", key="back"), sg.Push()],
        ]

        window = sg.Window(
            "Verify Attendance Initiator", layout, **cls.window_init_dict()
        )
        return window

    @classmethod
    def loop(cls, window, event, values):
        if event in (sg.WIN_CLOSED, "back"):
            window_dispatch.open_window(HomeWindow)
            sg.popup(
                "Event has been saved as a scheduled event",
                title="Event saved",
                keep_on_top=True,
            )
        if event == "facial_verification":
            window_dispatch.open_window(HomeWindow)
        return True


class AttendanceSessionLandingWindow(BaseGUIWindow):
    @classmethod
    def window(cls):
        event_dict = dict(
            app_config["current_attendance_session"]
        )  # this event dict should not be coming from new_event section
        layout = [
            [sg.Text("Attendance Session Details")],
            [sg.Text("_" * 80)],
            [sg.Text(f"Course: {event_dict['course']}")],
            [
                sg.Text(
                    f"Session Details: {event_dict['session']} {event_dict['semester']}"
                )
            ],
            [
                sg.Text(
                    f"Start Time: {event_dict['start_date']} {event_dict['start_time']}"
                )
            ],
            [sg.Text(f"Duration: {event_dict['duration']} Hour(s)")],
            [
                sg.Text(f"Number of students marked: "),
                sg.Text("", k="students_marked"),
            ],
            [sg.Text("_" * 80)],
            [
                sg.Button("Take Attendance", k="start_attendance"),
                sg.Button("End Attendance", k="end_attendance"),
                sg.Button("Go back home", k="home"),
            ],
        ]

        window = sg.Window(
            "Attendance Session Page", layout, **cls.window_init_dict()
        )
        return window

    @classmethod
    def loop(cls, window, event, values):
        if event == "home":
            window_dispatch.open_window(HomeWindow)

        if event == "start_attendance":
            window_dispatch.open_window(StudentBarcodeCameraWindow)

        if event == "end_attendance":
            app_config.remove_section("current_attendance_session")
            window_dispatch.open_window(HomeWindow)


class StaffNumberInputWindow(BaseGUIWindow):
    @classmethod
    def window(cls):
        INPUT_BUTTON_SIZE = (10, 2)
        column1 = [
            [
                sg.Button("1", s=INPUT_BUTTON_SIZE),
                sg.Button("2", s=INPUT_BUTTON_SIZE),
                sg.Button("3", s=INPUT_BUTTON_SIZE),
            ],
            [
                sg.Button("4", s=INPUT_BUTTON_SIZE),
                sg.Button("5", s=INPUT_BUTTON_SIZE),
                sg.Button("6", s=INPUT_BUTTON_SIZE),
            ],
            [
                sg.Button("7", s=INPUT_BUTTON_SIZE),
                sg.Button("8", s=INPUT_BUTTON_SIZE),
                sg.Button("9", s=INPUT_BUTTON_SIZE),
            ],
            [
                sg.Button("Submit", key="submit", s=INPUT_BUTTON_SIZE),
                sg.Button("0", s=INPUT_BUTTON_SIZE),
                sg.Button("Clear", key="clear", s=INPUT_BUTTON_SIZE),
            ],
        ]

        layout = [
            [
                sg.Text(
                    "Only registered staff can initiate attendance taking.",
                    justification="center",
                )
            ],
            [sg.Text("_" * 80)],
            [sg.VPush()],
            [cls.message_display_field()],
            [
                sg.Push(),
                sg.Text("Staff Number:    SS."),
                sg.Input(
                    size=(15, 1), justification="left", key="staff_number_input"
                ),
                sg.Push(),
            ],
            [sg.Push(), sg.Column(column1), sg.Push()],
            [sg.VPush()],
            [sg.Push(), sg.Button("<< Back", key="back"), sg.Push()],
        ]

        window = sg.Window(
            "Staff Number Input", layout, **cls.window_init_dict()
        )
        return window

    @classmethod
    def loop(cls, window, event, values):
        if event == "back":
            window_dispatch.open_window(HomeWindow)
            sg.popup(
                "Event has been saved as a scheduled event",
                title="Event saved",
                keep_on_top=True,
            )
            return True

        keys_entered = None
        if event in "0123456789":
            keys_entered = values["staff_number_input"]
            keys_entered += event
        elif event == "clear":
            keys_entered = ""
        elif event == "submit":
            if cls.validate(values, window) is not None:
                return True

            keys_entered = values["staff_number_input"]
            app_config["new_event"]["initiator_staff_num"] = (
                "SS." + keys_entered
            )
            app_config.save()
            window_dispatch.open_window(VerifyAttendanceInitiatorWindow)
            return True
        window["staff_number_input"].update(keys_entered)
        return True

    @classmethod
    def validate(cls, values, window):
        for val_check in (
            cls.validate_required_field(
                (values["staff_number_input"], "staff number")
            ),
            cls.validate_staff_number("SS." + values["staff_number_input"]),
        ):
            if val_check is not None:
                cls.display_message(val_check, window)
                return True
        return None


class CameraWindow(BaseGUIWindow):
    @classmethod
    def window(cls):
        layout = [
            [cls.window_title()],
            [cls.message_display_field()],
            [sg.Push(), sg.Image(filename="", key="image_display"), sg.Push()],
            [
                sg.Push(),
                sg.Button(
                    image_data=cls.get_icon("camera", 0.5),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="capture",
                ),
                sg.Button(
                    image_data=cls.get_icon("cancel", 0.5),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="cancel",
                ),
                cls.get_keyboard_button(),
                sg.Push(),
            ],
        ]
        window = sg.Window("Camera", layout, **cls.window_init_dict())
        return window

    @classmethod
    def get_keyboard_button(cls):
        if isinstance(cls, BarcodeCameraWindow):
            return sg.pin(
                sg.Button(
                    image_data=cls.get_icon("keyboard", 0.5),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="keyboard",
                    visible=True,
                )
            )
        else:
            return sg.pin(
                sg.Button(
                    image_data=cls.get_icon("keyboard", 0.5),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="keyboard",
                    visible=False,
                )
            )

    @classmethod
    def window_title(cls):
        raise NotImplementedError


class FaceCameraWindow(CameraWindow):
    @classmethod
    def loop(cls, window, event, values):
        with Camera() as cam:
            while True:
                event, values = window.read(timeout=20)
                img = cam.feed()
                face_count = FaceRecognition.face_count(img)
                if event == "capture":
                    if face_count > 1:
                        cls.display_message("Multiple faces detected", window)
                    elif face_count == 0:
                        cls.display_message(
                            "Camera did not find a face", window
                        )
                    else:
                        cls.hide_message_display_field(window)

                    if face_count == 1:
                        captured_encodings = FaceRecognition.face_encodings(img)
                        cls.process_image(captured_encodings, window)

                if event == "cancel":
                    cls.cancel_camera()

                if face_count > 0:
                    face_locations = FaceRecognition.face_locations(img)
                    for face_location in face_locations:
                        FaceRecognition.draw_bounding_box(face_location, img)

                window["image_display"].update(data=cam.feed_to_bytes(img))
        return True

    @classmethod
    def process_image(cls, captured_face_encodings, window):
        raise NotImplementedError

    @staticmethod
    def cancel_camera():
        raise NotImplementedError

    @classmethod
    def window_title(cls):
        return [
            sg.Push(),
            sg.Image(data=cls.get_icon("face_scanner", 0.5)),
            sg.Text("Position Face", font=("Any", 20)),
        ]


class StudentFaceCameraWindow(FaceCameraWindow):
    @classmethod
    def process_image(cls, captured_face_encodings, window):
        if captured_face_encodings is None:
            cls.display_message(
                "Eror. Image must have exactly one face", window
            )
            return False

        if FaceRecognition.face_match(
            [str_to_face_enc(app_config["tmp_student"]["face_encodings"])],
            captured_face_encodings,
        ):
            AttendanceRecord.objects.create(
                attendance_session_id=app_config.getint(
                    "current_attendance_sesson", "session_id"
                ),
                student_id=app_config.getint("tmp_student", "id"),
            )
            sg.popup_auto_close(
                f"{app_config['tmp_student']['reg_number']} checked in",
                image=cls.get_icon("ok"),
                title="Success",
                auto_close_duration=3,
            )
            window_dispatch.open_window(StudentBarcodeCameraWindow)
            return True
        else:
            cls.display_message(
                f"Error. Face did not match ({app_config['tmp_student']['reg_number']})",
                window,
            )
            return False

    @staticmethod
    def cancel_camera():
        """should navigate user back to the attendance session landing page"""
        window_dispatch.open_window(AttendanceSessionLandingWindow)


class StaffFaceCameraWindow(FaceCameraWindow):
    @classmethod
    def process_image(cls, captured_face_encodings, window):
        if captured_face_encodings is None:
            cls.display_message(
                "Error. Image must have exactly one face", window
            )
            return False

        if FaceRecognition.face_match(
            [str_to_face_enc(app_config["tmp_staff"]["face_encodings"])],
            captured_face_encodings,
        ):
            cls.display_message(
                f"{app_config['tmp_staff']['staff_number']} authorized attendance-marking",
                window,
            )

            att_session = AttendanceSession.objects.get(
                id=app_config.getint("current_attendance_session", "session_id")
            )
            att_session.initiator_id = app_config.getint("tmp_staff", "id")
            att_session.save()
            app_config["current_attendance_session"][
                "initiator_id"
            ] = app_config["tmp_staff"]["id"]
            app_config.save()

            window_dispatch.open_window(AttendanceSessionLandingWindow)
            return True
        else:
            cls.display_message(
                f"Error. Face did not match ({app_config['tmp_staff']['staff_number']})",
                window,
            )
            return False

    @staticmethod
    def cancel_camera():
        """should navigate user back to the attendance initiator verification window"""
        window_dispatch.open_window(NewEventSummaryWindow)


class BarcodeCameraWindow(CameraWindow):
    @classmethod
    def loop(cls, window, event, values):
        with Camera() as cam:
            while True:
                img = cam.feed()
                barcodes = Barcode.decode_image(img)
                event, values = window.read(timeout=20)
                if event == "capture":
                    if len(barcodes) == 0:
                        cls.display_message("No ID detected")
                    else:
                        cls.process_barcode(
                            Barcode.decode_barcode(barcodes[0]), window
                        )
                        return True
                if event == "keyboard":
                    cls.launch_keypad()

                if event == "cancel":
                    cls.cancel_camera()

                if len(barcodes) > 0:
                    cls.process_barcode(
                        Barcode.decode_barcode(barcodes[0]), window
                    )
                    return True
                window["image_display"].update(data=cam.feed_to_bytes(img))
        return True

    @classmethod
    def process_barcode(cls, identification_num, window):
        raise NotImplementedError

    @classmethod
    def launch_keypad(cls):
        raise NotImplementedError

    @staticmethod
    def cancel_camera():
        window_dispatch.open_window(HomeWindow)

    @classmethod
    def window_title(cls):
        return [
            [
                sg.Push(),
                sg.Image(data=cls.get_icon("qr_code", 0.5)),
                sg.Text("Present ID Card", font=("Any", 20)),
                sg.Push(),
            ],
            [
                sg.Text(
                    "A staff must authorize the commencement of attendance-marking"
                )
            ],
        ]


class StudentBarcodeCameraWindow(BarcodeCameraWindow):
    """window responsible for processing student registration number
    during attendance marking"""

    @classmethod
    def process_barcode(cls, identification_num, window):
        val_check = cls.validate_student_reg_number(identification_num)
        if val_check is not None:
            cls.display_message(val_check, window)
            return False

        try:
            student = Student.objects.get(reg_no=identification_num)
        except ObjectDoesNotExist:
            cls.display_message(
                "No student found with given registration number", window
            )
            return False
        app_config["tmp_student"] = student.values(
            "reg_number",
            "first_name",
            "last_name",
            "level_of_study",
            "department__name",
            "department__faculty__name",
            "face_encodings",
            "fingerprint_template",
        )
        app_config.save()
        window_dispatch.open_window(StudentFaceCameraWindow)
        return True

    @staticmethod
    def cancel_camera():
        window_dispatch.open_window(AttendanceSessionLandingWindow)


class StaffBarcodeCameraWindow(BarcodeCameraWindow):
    @classmethod
    def process_barcode(cls, identification_num, window):
        val_check = cls.validate_staff_number(identification_num)
        if val_check is not None:
            cls.display_message(val_check, window)
            return False

        try:
            staff = Staff.objects.get(staff_number=identification_num)
        except ObjectDoesNotExist:
            cls.display_message("No staff found with given staff ID", window)
            return False

        app_config["tmp_staff"] = {}
        app_config["tmp_staff"] = staff.values(
            "id",
            "staff_number",
            "first_name",
            "last_name",
            "department__name",
            "department__faculty__name",
            "face_encodings",
            "fingerprint_template",
        )
        app_config.save()
        window_dispatch.open_window(StaffFaceCameraWindow)
        return True


# enrolment windows should not be available on all node devices;
# should only be available on node devices that will be used for
# enrolment
class EnrolmentMenuWindow(BaseGUIWindow):
    @classmethod
    def window(cls):
        layout = [
            [sg.VPush()],
            [
                sg.Push(),
                sg.Button("Staff Enrolment", key="staff_enrolment"),
                sg.Button("Student Enrolment", key="student_enrolment"),
                sg.Push(),
            ],
            [sg.VPush()],
            [sg.Button("<< Back", k="back")],
        ]
        window = sg.Window("Enrolment Window", layout, **cls.window_init_dict())
        return window

    @classmethod
    def loop(cls, window, event, values):
        if event == "back":
            window_dispatch.open_window(HomeWindow)
        if event == "staff_enrolment":
            window_dispatch.open_window(StaffEnrolmentWindow)
        if event == "student_enrolment":
            window_dispatch.open_window(StudentEnrolmentWindow)
        return True


class StaffEnrolmentWindow(BaseGUIWindow):
    """The GUI for enrolment of staff"""

    @classmethod
    def window(cls):
        column1 = [
            [sg.Push(), sg.Text("Staff Enrolment"), sg.Push()],
            [cls.message_display_field()],
            [
                sg.Text("Staff Number:  "),
                sg.Input(
                    size=(15, 1), justification="left", key="staff_number_input"
                ),
            ],
            [
                sg.Text("First Name: "),
                sg.Input(
                    expand_x=True, justification="left", key="staff_first_name"
                ),
            ],
            [
                sg.Text("Last Name: "),
                sg.Input(
                    expand_x=True, justification="left", key="staff_last_name"
                ),
            ],
            [
                sg.Text("Other Names: "),
                sg.Input(
                    expand_x=True, justification="left", key="staff_other_names"
                ),
            ],
            [
                sg.Text("Sex:  "),
                sg.Combo(
                    values=Sex.labels,
                    default_value=cls.COMBO_DEFAULT,
                    key="staff_sex",
                ),
            ],
            [
                sg.Text("Faculty: "),
                sg.Combo(
                    values=Faculty.get_all_faculties(),
                    default_value=cls.COMBO_DEFAULT,
                    enable_events=True,
                    expand_x=True,
                    key="staff_faculty",
                ),
            ],
            [
                sg.Text("Department: "),
                sg.Combo(
                    values=Department.get_departments(),
                    default_value=cls.COMBO_DEFAULT,
                    enable_events=True,
                    expand_x=True,
                    key="staff_department",
                ),
            ],
        ]
        layout = [
            [sg.VPush()],
            [
                sg.Push(),
                sg.Column(column1, vertical_scroll_only=True),
                sg.Push(),
            ],
            [
                sg.Button("Submit", key="submit"),
                sg.Button("Cancel", key="cancel"),
            ],
            [sg.VPush()],
        ]
        window = sg.Window("Staff Enrolment", layout, **cls.window_init_dict())
        return window

    @classmethod
    def loop(cls, window, event, values):
        if event == "staff_faculty":
            if values["staff_faculty"] in (cls.COMBO_DEFAULT, None):
                window["staff_faculty"].update(
                    values=Faculty.get_all_faculties(), value=cls.COMBO_DEFAULT
                )
            else:
                window["staff_department"].update(
                    values=Department.get_departments(
                        faculty=values["staff_faculty"]
                    ),
                    value=cls.COMBO_DEFAULT,
                )
        if event == "submit":
            if cls.validate(values, window) is not None:
                return True

            app_config["new_staff"] = {}
            app_config["new_staff"] = {
                "staff_number": values["staff_number_input"],
                "first_name": values["staff_first_name"],
                "last_name": values["staff_last_name"],
                "sex": Sex.str_to_value(values["staff_sex"]),
                "department": Department.get_id(values["staff_department"]),
            }
            app_config.save()
            window_dispatch.open_window(StaffFaceEnrolmentWindow)
        if event == "cancel":
            window_dispatch.open_window(HomeWindow)
        return True

    @classmethod
    def validate(cls, values, window):
        req_fields = [
            (values["staff_number_input"], "staff number"),
            (values["staff_first_name"], "first name"),
            (values["staff_last_name"], "last name"),
            (values["staff_sex"], "sex"),
            (values["staff_faculty"], "faculty"),
            (values["staff_department"], "department"),
        ]
        validation_val = cls.validate_required_fields(req_fields, window)
        if validation_val is not None:
            return True

        for field in req_fields[1:3]:
            validation_val = cls.validate_text_field(*field)
            if validation_val is not None:
                cls.display_message(validation_val, window)
                return True

        for criteria in (
            cls.validate_staff_number(values["staff_number_input"]),
            cls.validate_sex(values["staff_sex"]),
            cls.validate_faculty(values["staff_faculty"]),
            cls.validate_department(values["staff_department"]),
        ):
            if criteria is not None:
                cls.display_message(criteria, window)
                return True
        return None


class StaffFaceEnrolmentWindow(FaceCameraWindow):
    @classmethod
    def process_image(cls, captured_face_encodings, window):
        if captured_face_encodings is None:
            cls.display_message(
                "Error. Image must have exactly one face", window
            )
            return False

        app_config["new_staff"]["face_encodings"] = face_enc_to_str(
            captured_face_encodings
        )
        app_config.save()
        new_staff_dict = app_config.section_dict("new_staff")
        department = Department.objects.get(id=new_staff_dict.pop("department"))
        Staff.objects.create_user(department=department, **new_staff_dict)

        window_dispatch.open_window(HomeWindow)


class StudentEnrolmentWindow(BaseGUIWindow):
    @classmethod
    def window(cls):
        column1 = [
            [sg.Push(), sg.Text("Student Enrolment"), sg.Push()],
            [cls.message_display_field()],
            [
                sg.Text("Registration Number:  "),
                sg.Input(
                    size=(15, 1),
                    justification="left",
                    key="student_reg_number_input",
                ),
            ],
            [
                sg.Text("First Name: "),
                sg.Input(
                    expand_x=True,
                    justification="left",
                    key="student_first_name",
                ),
            ],
            [
                sg.Text("Last Name: "),
                sg.Input(
                    expand_x=True, justification="left", key="student_last_name"
                ),
            ],
            [
                sg.Text("Other Names: "),
                sg.Input(
                    expand_x=True,
                    justification="left",
                    key="student_other_names",
                ),
            ],
            [
                sg.Text("Sex:  "),
                sg.Combo(
                    values=Sex.labels,
                    default_value=cls.COMBO_DEFAULT,
                    key="student_sex",
                ),
            ],
            [
                sg.Text("Level of study:  "),
                sg.Input(
                    size=(5, 1),
                    justification="left",
                    key="student_level_of_study",
                ),
            ],
            [
                sg.Text("Possible year of graduation:  "),
                sg.Input(
                    size=(10, 1),
                    justification="left",
                    key="student_possible_grad_yr",
                ),
            ],
            [
                sg.Text("Faculty: "),
                sg.Combo(
                    values=Faculty.get_all_faculties(),
                    default_value=cls.COMBO_DEFAULT,
                    expand_x=True,
                    enable_events=True,
                    key="student_faculty",
                ),
            ],
            [
                sg.Text("Department: "),
                sg.Combo(
                    values=Department.get_departments(),
                    default_value=cls.COMBO_DEFAULT,
                    expand_x=True,
                    enable_events=True,
                    key="student_department",
                ),
            ],
        ]
        layout = [
            [sg.VPush()],
            [
                sg.Push(),
                sg.Column(column1, vertical_scroll_only=True),
                sg.Push(),
            ],
            [
                sg.Button("Submit", key="submit"),
                sg.Button("Cancel", key="cancel"),
            ],
            [sg.VPush()],
        ]
        window = sg.Window(
            "Student Enrolment", layout, **cls.window_init_dict()
        )
        return window

    @classmethod
    def loop(cls, window, event, values):
        window.force_focus()
        if event == "student_faculty":
            if values["student_faculty"] in (cls.COMBO_DEFAULT, None):
                window["student_faculty"].update(
                    values=Faculty.get_all_faculties(), value=cls.COMBO_DEFAULT
                )
            else:
                window["student_department"].update(
                    values=Department.get_departments(
                        faculty=values["student_faculty"]
                    ),
                    value=cls.COMBO_DEFAULT,
                )
        if event == "submit":
            if cls.validate(values, window) is not None:
                return True

            app_config["new_student"] = {}
            app_config["new_student"] = {
                "reg_number": values["student_reg_number_input"],
                "first_name": values["student_first_name"],
                "last_name": values["student_last_name"],
                "other_names": values["student_other_names"],
                "level_of_study": values["student_level_of_study"],
                "possible_grad_yr": values["student_possible_grad_yr"],
                "sex": Sex.str_to_value(values["student_sex"]),
                "department": Department.get_id(values["student_department"]),
            }
            app_config.save()
            window_dispatch.open_window(StudentFaceEnrolmentWindow)
        if event == "cancel":
            window_dispatch.open_window(HomeWindow)
        return True

    @classmethod
    def validate(cls, values, window):
        req_fields = [
            (values["student_reg_number_input"], "registration number"),
            (values["student_first_name"], "first name"),
            (values["student_last_name"], "last name"),
            (values["student_sex"], "sex"),
            (values["student_level_of_study"], "level of study"),
            (values["student_possible_grad_yr"], "possible year of graduation"),
            (values["student_faculty"], "faculty"),
            (values["student_department"], "department"),
        ]
        if cls.validate_required_fields(req_fields, window) is not None:
            return True

        for field in req_fields[1:3]:
            validation_val = cls.validate_text_field(*field)
            if validation_val is not None:
                cls.display_message(validation_val, window)
                return True

        for criteria in (
            cls.validate_student_reg_number(values["student_reg_number_input"]),
            cls.validate_sex(values["student_sex"]),
            cls.validate_faculty(values["student_faculty"]),
            cls.validate_department(values["student_department"]),
            cls.validate_int_field(
                values["student_level_of_study"], "level of study"
            ),
            cls.validate_int_field(
                values["student_possible_grad_yr"],
                "possible year of graduation",
            ),
        ):
            if criteria is not None:
                cls.display_message(criteria, window)
                return True

        if Student.objects.filter(
            reg_number=values["student_reg_number_input"]
        ).exists():
            cls.display_message(
                f"Student with registration number {values['student_reg_number_input']} already exists",
                window,
            )
            return True
        return None


class StudentFaceEnrolmentWindow(FaceCameraWindow):
    @classmethod
    def process_image(cls, captured_face_encodings, window):
        if captured_face_encodings is None:
            cls.display_message(
                "Error. Image must have exactly one face", window
            )
            return False

        app_config["new_student"]["face_encodings"] = face_enc_to_str(
            captured_face_encodings
        )
        app_config.save()
        new_student_dict = app_config.section_dict("new_student")
        department = Department.objects.get(
            id=new_student_dict.pop("department")
        )

        Student.objects.create(department=department, **new_student_dict)
        window_dispatch.open_window(HomeWindow)

    @staticmethod
    def cancel_camera():
        window_dispatch.open_window(HomeWindow)


class AttendanceMenuWindow(BaseGUIWindow):
    @classmethod
    def window(cls):
        layout = [
            [sg.VPush()],
            [sg.Push(), sg.Button("Start Attendance Taking"), sg.Push()],
            [sg.Push(), sg.Button("End Attendance Taking"), sg.Push()],
            [sg.VPush()],
        ]


def main():
    window_dispatch.open_window(HomeWindow)
    loop_exit_code = True
    while True:
        window = window_dispatch.current_window
        event, values = window.read(timeout=500)
        current_window = window_dispatch.find_window(window)
        if current_window:
            loop_exit_code = eval(current_window).loop(window, event, values)
        if not loop_exit_code:
            break
        if event == sg.WIN_CLOSED:
            break
    window.close()


if __name__ == "__main__":
    main()
