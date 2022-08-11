import json

from datetime import datetime, timedelta
import time

import PySimpleGUI as sg
import requests
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.utils import timezone
from requests import HTTPError

import __main__
from app import networkinterface
from app.gui_utils import (
    StaffBiometricVerificationRouterMixin,
    StaffIDInputRouterMixin,
    StudentRegNumberInputRouterMixin,
    StudentBiometricVerificationRouterMixin,
    ValidationMixin,
    update_device_op_mode,
)
from app.camerafacerec import CamFaceRec
from app.appconfigparser import AppConfigParser
from app.basegui import BaseGUIWindow
from app.fingerprint import FingerprintScanner
from app.attendancelogger import AttendanceLogger
from app.barcode import Barcode
from app.facerec import FaceRecognition
from app.networkinterface import WLANInterface, connect_to_wifi
from app.nodedevicedatasynch import NodeDataSynch
from app.opmodes import OperationalMode
from app.camera2 import Camera
from app.nodedeviceinit import DeviceRegistration
from app.serverconnection import ServerConnection

from db.models import (
    AttendanceRecord,
    AttendanceSession,
    AcademicSession,
    AttendanceSessionStatusChoices,
    EventTypeChoices,
    Student,
    SexChoices,
    Staff,
    Course,
    Faculty,
    SemesterChoices,
    Department,
    face_enc_to_str,
    str_to_face_enc, EventTypeChoices, SemesterChoices, SexChoices, RecordTypesChoices, AttendanceSessionStatusChoices,
    NodeDevice,
)

# initializing the configparser object
app_config = AppConfigParser()

# initializing WindowDispatch object
# window_dispatch = WindowDispatch()
window_dispatch = __main__.window_dispatch

# setting the operational mode of device
app_config["tmp_settings"] = {}
update_device_op_mode()


class HomeWindow(BaseGUIWindow):
    """GUI Home Window for node devices."""

    @classmethod
    def window(cls):
        column1 = [
            [
                sg.Push(),
                sg.Button(
                    image_data=cls.get_icon("new", 0.9),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="new_event",
                    use_ttk_buttons=True,
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text("New", key="new_event_txt", enable_events=True),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text("Event", key="new_event_txt", enable_events=True),
                sg.Push(),
            ],
        ]
        column2 = [
            [
                sg.Push(),
                sg.Button(
                    image_data=cls.get_icon("right_arrow"),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="continue_attendance",
                    use_ttk_buttons=True,
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text(
                    "Continue",
                    key="continue_attendance_txt",
                    enable_events=True,
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text(
                    "Attendance",
                    key="continue_attendance_txt_2",
                    enable_events=True,
                ),
                sg.Push(),
            ],
        ]
        column3 = [
            [
                sg.Push(),
                sg.Button(
                    image_data=cls.get_icon("schedule"),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="schedule",
                    use_ttk_buttons=True,
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text("Scheduled &", key="schedule_txt", enable_events=True),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text(
                    "Recurring Events", key="schedule_txt_2", enable_events=True
                ),
                sg.Push(),
            ],
        ]
        layout = [
            [
                sg.Push(),
                sg.Button(
                    image_data=cls.get_icon("settings", 0.5),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="settings",
                    use_ttk_buttons=True,
                ),
                sg.Button(
                    image_data=cls.get_icon("power", 0.5),
                    button_color=cls.ICON_BUTTON_COLOR,
                    use_ttk_buttons=True,
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
            [sg.HorizontalSeparator()],
            [sg.Push(), sg.Text("TAMS© 2022"), sg.Push()],
        ]

        window = sg.Window("Home Window", layout, **cls.window_init_dict())
        return window

    @classmethod
    def loop(cls, window, event, values):
        if event in ("new_event", "new_event_txt"):
            if not DeviceRegistration.is_registered():
                cls.popup_auto_close_warn("Device setup incomplete. Contact admin")
                return True
            window_dispatch.open_window(EventMenuWindow)
        if event in (
                "continue_attendance",
                "continue_attendance_txt",
                "continue_attendance_txt_2",
        ):
            if app_config.has_section("current_attendance_session"):
                current_att_session = app_config["current_attendance_session"]
                session_strt_time = datetime.strptime(
                    f"{current_att_session['start_date']} {current_att_session['start_time']} +0100",
                    "%d-%m-%Y %H:%M %z",
                )

                # handling expired attendance sessions
                if timezone.now() - session_strt_time > timedelta(hours=24):
                    try:
                        attendance_session = AttendanceSession.objects.get(
                            id=current_att_session["session_id"]
                        )
                    except Exception as e:
                        cls.popup_auto_close_error("Invalid session. Create new session.")
                        app_config.remove_section("current_attendance_session")
                        app_config.remove_section("failed_attempts")
                        app_config.remove_section("tmp_student")
                        app_config.remove_section("tmp_staff")
                        return True
                    else:
                        if attendance_session.initiator is None:
                            attendance_session.delete()
                        else:
                            attendance_session.status = (
                                AttendanceSessionStatusChoices.ENDED
                            )
                            attendance_session.save()

                    cls.popup_auto_close_warn(
                        f"{current_att_session['course']} {current_att_session['type']} "
                        f"attendance session has expired"
                    )
                    app_config.remove_section("current_attendance_session")
                    app_config.remove_section("failed_attempts")
                    app_config.remove_section("tmp_student")
                    app_config.remove_section("tmp_staff")
                    return True

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
                    "No active attendance-taking session found.",
                    title="No Event",
                    keep_on_top=True,
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
            return True
        return True


class EventMenuWindow(BaseGUIWindow):
    """
    A window which presents options for the user to choose the
    event type for the attendance session.
    """

    @classmethod
    def window(cls):
        column1 = [
            [
                sg.Push(),
                sg.Button(
                    image_data=cls.get_icon("lecture"),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="lecture",
                    use_ttk_buttons=True,
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text("Lecture", key="lecture_txt", enable_events=True),
                sg.Push(),
            ],
        ]

        column2 = [
            [
                sg.Push(),
                sg.Button(
                    image_data=cls.get_icon("lab"),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="lab",
                    use_ttk_buttons=True,
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text("Lab", key="lab_txt", enable_events=True),
                sg.Push(),
            ],
        ]

        column3 = [
            [
                sg.Push(),
                sg.Button(
                    image_data=cls.get_icon("test_script"),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="quiz",
                    use_ttk_buttons=True,
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text("Quiz", key="quiz_txt", enable_events=True),
                sg.Push(),
            ],
        ]

        column4 = [
            [
                sg.Push(),
                sg.Button(
                    image_data=cls.get_icon("graduation_cap"),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="examination",
                    use_ttk_buttons=True,
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text(
                    "Examination", key="examination_txt", enable_events=True
                ),
                sg.Push(),
            ],
        ]

        layout = [
            [
                sg.Push(),
                sg.Text("Take Attendance for:", font="Helvetica 20"),
                sg.Push(),
            ],
            [sg.HorizontalSeparator()],
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
            [sg.HorizontalSeparator()],
            cls.navigation_pane(next_icon="next_disabled"),
        ]
        window = sg.Window("Event Menu", layout, **cls.window_init_dict())
        return window

    @classmethod
    def loop(cls, window, event, values):
        if event in (sg.WIN_CLOSED, "back", "cancel", "home"):
            window_dispatch.open_window(HomeWindow)
        if event in (
                "lecture",
                "examination",
                "lab",
                "quiz",
                "lecture_txt",
                "examination_txt",
                "lab_txt",
                "quiz_txt",
        ):
            event = event.split("_")[0]
            app_config["new_event"] = {}
            app_config["new_event"]["type"] = event
            app_config["new_event"]["recurring"] = "False"
            if event in ("lecture", "lab"):
                recurring = sg.popup_yes_no(
                    f"Is this {event} a weekly activity?",
                    title="Event detail",
                    keep_on_top=True,
                )
                if recurring == "Yes":
                    app_config["new_event"]["recurring"] = "True"

            window_dispatch.open_window(AcademicSessionDetailsWindow)
        return True


class AcademicSessionDetailsWindow(ValidationMixin, BaseGUIWindow):
    """Window to choose the academic session and academic semester for
    new attendance event."""

    @classmethod
    def window(cls):
        all_academic_sessions = AcademicSession.get_all_academic_sessions()
        layout = [
            [sg.Push(), sg.Text("Academic Session Details"), sg.Push()],
            [sg.HorizontalSeparator()],
            [sg.VPush()],
            [
                [cls.message_display_field()],
                sg.Text("Select Current Session:   "),
                sg.Combo(
                    all_academic_sessions,
                    default_value=(
                        all_academic_sessions[0]
                        if all_academic_sessions
                        else cls.COMBO_DEFAULT
                    ),
                    enable_events=True,
                    key="current_session",
                    expand_y=True,
                    expand_x=True,
                ),
            ],
            [
                sg.Push(),
                sg.Text(
                    "New Academic Session?", k="new_session", enable_events=True
                ),
            ],
            [
                sg.Text("Select Current SemesterChoices: "),
                sg.Combo(
                    SemesterChoices.labels,
                    default_value=SemesterChoices.labels[0],
                    enable_events=True,
                    key="current_semester",
                    expand_y=True,
                    expand_x=True,
                ),
            ],
            [sg.VPush()],
            cls.navigation_pane(),
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
            window_dispatch.open_window(EventDetailWindow)
        elif event == "back":
            window_dispatch.open_window(EventMenuWindow)
        elif event == "home":
            window_dispatch.open_window(HomeWindow)
        elif event == "new_session":
            window_dispatch.open_window(NewAcademicSessionWindow)
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

        if not AcademicSession.objects.filter(
                session=values["current_session"]
        ).exists():
            cls.display_message(
                "Academic Session has not been registered.", window
            )
            return True
        return None


class NewAcademicSessionWindow(ValidationMixin, BaseGUIWindow):
    """Window to create a new academic session."""

    @classmethod
    def window(cls):
        current_year = datetime.now().year
        allowed_yrs = [x for x in range(current_year, current_year + 4)]
        layout = [
            [sg.Push(), sg.Text("Add New Academic Session"), sg.Push()],
            [sg.HorizontalSeparator()],
            cls.message_display_field(),
            [sg.VPush()],
            [
                sg.Text("Session:", size=12),
                sg.Spin(
                    values=allowed_yrs,
                    initial_value=current_year,
                    k="session_start",
                    expand_x=True,
                    enable_events=True,
                ),
                sg.Text("/"),
                sg.Spin(
                    values=allowed_yrs[1:],
                    initial_value=(current_year + 1),
                    k="session_end",
                    expand_x=True,
                    enable_events=True,
                ),
            ],
            [sg.Check("Is this the current session?", k="is_current_session")],
            [
                sg.Push(),
                sg.Button(
                    "Create",
                    k="create_session",
                    font="Helvetica 12",
                ),
            ],
            [sg.VPush()],
            cls.navigation_pane(next_icon="next_disabled"),
        ]
        window = sg.Window(
            "New Academic Session",
            layout,
            **cls.window_init_dict(),
        )
        return window

    @classmethod
    def loop(cls, window, event, values):
        if event == "back":
            window_dispatch.open_window(AcademicSessionDetailsWindow)
        if event == "home":
            window_dispatch.open_window(HomeWindow)

        if event == "create_session":
            for val in ("session_start", "session_end"):
                try:
                    val_int = int(values[val])
                except ValueError:
                    cls.display_message(
                        "Enter numeric values for Academic Session Years",
                        window,
                    )
                    return True

                new_session = (
                        str(values["session_start"])
                        + "/"
                        + str(values["session_end"])
                )
                is_current_session = values["is_current_session"]
                val_check = cls.validate_academic_session(new_session)
                if val_check is not None:
                    cls.display_message(val_check, window)
                    return True

                try:
                    new_session = AcademicSession.objects.create(
                        session=new_session,
                        is_current_session=is_current_session,
                    )
                except IntegrityError as e:
                    cls.display_message(
                        "Error. You may be trying to create a"
                        " session that already exists",
                        window,
                    )
                    print(e)
                    return True

                cls.popup_auto_close_success(
                    f"Academic session {new_session.session} created successfully"
                )
                window_dispatch.open_window(HomeWindow)
                return True

        if event == "session_start":
            try:
                session_start_int = int(values["session_start"])
            except ValueError:
                cls.display_message(
                    "Enter numeric values for Academic Session", window
                )
                return True
            else:
                if session_start_int > 0:
                    window["session_end"].update(value=session_start_int + 1)
                else:
                    window["session_end"].update(value=0)
                return True

        if event == "session_end":
            try:
                session_end_int = int(values["session_end"])
            except ValueError:
                cls.display_message(
                    "Enter numeric values for Academic Session", window
                )
                return True
            else:
                if session_end_int > 0:
                    window["session_start"].update(value=session_end_int - 1)
                else:
                    window["session_start"].update(value=0)
                return True
        return True


class EventDetailWindow(ValidationMixin, BaseGUIWindow):
    """Window to for user to specify event deatils like: course,
    start date, and event duration"""

    @classmethod
    def window(cls):
        field_label_props = {"size": 18}
        section1 = [
            [
                sg.Text("Faculty:", **field_label_props),
                sg.Combo(
                    Faculty.get_all_faculties(),
                    default_value=cls.COMBO_DEFAULT,
                    enable_events=True,
                    key="course_faculty",
                    expand_y=True,
                    expand_x=True,
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
                    expand_x=True,
                ),
            ],
        ]
        layout = [
            [sg.Push(), sg.Text("Event Details"), sg.Push()],
            [sg.HorizontalSeparator()],
            [sg.VPush()],
            [
                [cls.message_display_field()],
                sg.Text("Select Course:", **field_label_props),
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
                sg.Text("Duration:", **field_label_props),
                sg.Spin(
                    values=[str(a).zfill(2) for a in range(0, 12)],
                    initial_value="01",
                    expand_x=True,
                    expand_y=True,
                    key="duration",
                ),
                sg.Text("Hour(s)"),
            ],
            [sg.VPush()],
            [sg.Button("Submit", key="submit")],
            cls.navigation_pane(back_icon="back_disabled"),
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
        if event in ("next", "submit"):
            if cls.validate(values, window) is not None:
                return True

            app_config["new_event"]["course"] = values["selected_course"]
            app_config["new_event"]["start_time"] = (
                    values["start_hour"] + ":" + values["start_minute"]
            )
            app_config["new_event"]["start_date"] = values["start_date"]
            app_config["new_event"]["duration"] = values["duration"]
            window_dispatch.open_window(NewEventSummaryWindow)
        if event == "home":
            app_config.remove_section("new_event")
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


class NewEventSummaryWindow(StaffIDInputRouterMixin, BaseGUIWindow):
    """This window presents details selected by the user in the new
    attendance session about to be initiated."""

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
    def loop(cls, window, event, values):
        if event in ("start_event", "schedule_event"):
            new_event = dict(app_config["new_event"])
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
                att_session, created = AttendanceSession.objects.get_or_create(**attendance_session_model_kwargs)
            except Exception:
                cls.display_message("Unknown system error", window)

            if not created:
                if att_session.status != AttendanceSessionStatusChoices.ACTIVE:
                    cls.popup_auto_close_error("Attendance for this event has ended")
                    app_config.remove_section("current_attendance_session")
                    app_config.remove_section("new_event")
                    window_dispatch.open_window(HomeWindow)
                    return True
                cls.popup_auto_close_warn("Event has already been created")

            app_config["current_attendance_session"] = app_config.section_dict(
                "new_event"
            )
            app_config["current_attendance_session"]["session_id"] = str(
                att_session.id
            )
            app_config.remove_section("new_event")

            if att_session.initiator:
                app_config["current_attendance_session"]["initiator_id"] = str(
                    att_session.initiator.id
                )
                window_dispatch.open_window(ActiveEventSummaryWindow)
                return True

            if event == "start_event":
                cls.staff_id_input_window()

            if event == "schedule_event":
                sg.popup(
                    "Event saved to scheduled events",
                    title="Event saved",
                    keep_on_top=True,
                )
                window_dispatch.open_window(HomeWindow)

        if event == "home":
            app_config.remove_section("new_event")
            window_dispatch.open_window(HomeWindow)
        return True


class ActiveEventSummaryWindow(
    StaffBiometricVerificationRouterMixin, BaseGUIWindow
):
    """This window presents the details of an attendance session that
    has been initiated."""

    @classmethod
    def window(cls):
        event_dict = app_config["current_attendance_session"]
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
    def loop(cls, window, event, values):
        if event == "continue_event":
            active_event = app_config["current_attendance_session"]

            try:
                initiator = Staff.objects.filter(
                    pk=active_event.get("initiator_id")
                )
            except ObjectDoesNotExist:
                sg.popup(
                    "System error. Please try creating event again",
                    title="Error",
                    keep_on_top=True,
                )
                window_dispatch.open_window(HomeWindow)
                return True

            app_config["tmp_staff"] = app_config.dict_vals_to_str(
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
            window_dispatch.open_window(HomeWindow)
        return True


class AttendanceSessionLandingWindow(
    StudentRegNumberInputRouterMixin, BaseGUIWindow
):
    """This is the landing window for the active attendance session."""

    @classmethod
    def window(cls):
        event_dict = dict(app_config["current_attendance_session"])
        layout = [
            [sg.VPush()],
            [sg.Text("Attendance Session Details")],
            [sg.HorizontalSeparator()],
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
                sg.Text(f"Number of valid check-ins: "),
                sg.Text(
                    "{}".format(cls.valid_check_in_count()), k="valid_checks"
                ),
            ],
            [sg.VPush()],
            [
                sg.Button("Take Attendance", k="start_attendance"),
                sg.Button(
                    "End Attendance",
                    k="end_attendance",
                    **cls.cancel_button_kwargs(),
                ),
            ],
            [sg.HorizontalSeparator()],
            cls.navigation_pane(
                back_icon="back_disabled", next_icon="next_disabled"
            ),
        ]

        window = sg.Window(
            "Attendance Session Page", layout, **cls.window_init_dict()
        )
        return window

    @classmethod
    def loop(cls, window, event, values):
        if event == "home":
            confirm = sg.popup_yes_no(
                "Leaving attendance-taking. Do you wish to continue?",
                title="Go back?",
                keep_on_top=True,
            )
            if confirm == "Yes":
                window_dispatch.open_window(HomeWindow)
            return True

        if event == "start_attendance":
            cls.student_reg_number_input_window()

        if event == "end_attendance":
            confirm = sg.popup_yes_no(
                "This will permanently end attendance-taking for this event. "
                "Do you wish to continue?",
                title="End Attendance Session?",
                keep_on_top=True,
            )
            if confirm == "Yes":
                att_session = AttendanceSession.objects.get(
                    id=app_config.get(
                        "current_attendance_session", "session_id"
                    )
                )
                att_session.status = AttendanceSessionStatusChoices.ENDED
                att_session.save()
                app_config.remove_section("current_attendance_session")
                app_config.remove_section("failed_attempts")
                app_config.remove_section("tmp_student")
                app_config.remove_section("tmp_staff")
                window_dispatch.open_window(HomeWindow)
        return True

    @staticmethod
    def valid_check_in_count():
        return AttendanceRecord.objects.filter(
            attendance_session=app_config.get(
                "current_attendance_session", "session_id"
            ),
            record_type=RecordTypesChoices.SIGN_IN,
        ).count()


class StaffNumberInputWindow(
    ValidationMixin, StaffBiometricVerificationRouterMixin, BaseGUIWindow
):
    """This window will provide an on-screen keypad for staff to enter
    their staff id/number by button clicks."""

    @classmethod
    def window(cls):
        INPUT_BUTTON_SIZE = (8, 2)
        column1 = [
            [
                sg.Button("1", s=INPUT_BUTTON_SIZE),
                sg.Button("2", s=INPUT_BUTTON_SIZE),
                sg.Button("3", s=INPUT_BUTTON_SIZE),
                sg.Button("0", s=INPUT_BUTTON_SIZE),
            ],
            [
                sg.Button("4", s=INPUT_BUTTON_SIZE),
                sg.Button("5", s=INPUT_BUTTON_SIZE),
                sg.Button("6", s=INPUT_BUTTON_SIZE),
                sg.Button("/", s=INPUT_BUTTON_SIZE),
            ],
            [
                sg.Button("7", s=INPUT_BUTTON_SIZE),
                sg.Button("8", s=INPUT_BUTTON_SIZE),
                sg.Button("9", s=INPUT_BUTTON_SIZE),
                sg.Button("AC", key="clear", s=INPUT_BUTTON_SIZE),
            ],
            [
                sg.Push(),
                sg.Button("Submit", key="submit", s=INPUT_BUTTON_SIZE),
                sg.Push(),
            ],
        ]

        layout = [
            [sg.VPush()],
            [cls.message_display_field()],
            [
                sg.Push(),
                sg.Text("Staff Number:    SS."),
                sg.Input(
                    size=(15, 1),
                    justification="left",
                    key="staff_number_input",
                    focus=True,
                ),
                sg.Push(),
            ],
            [sg.Push(), sg.Column(column1), sg.Push()],
            [sg.VPush()],
            cls.navigation_pane(),
        ]
        scrolled_layout = [
            [
                sg.Column(
                    layout,
                    scrollable=True,
                    vertical_scroll_only=True,
                    expand_y=True,
                    key="main_column",
                )
            ]
        ]

        window = sg.Window(
            "Staff Number Input", scrolled_layout, **cls.window_init_dict()
        )
        return window

    @classmethod
    def loop(cls, window, event, values):
        if event in ("back", "home"):
            cls.back_nav_key_handler()
            return True

        keys_pressed = None
        if event in "0123456789":
            keys_pressed = values["staff_number_input"]
            keys_pressed += event
            window["staff_number_input"].update(keys_pressed)
            return True

        elif event == "clear":
            window["staff_number_input"].update("")
            cls.hide_message_display_field(window)
            cls.resize_column(window)
            return True

        elif event in ("submit", "next"):
            if cls.validate(values, window) is not None:
                cls.resize_column(window)
                return True

            keys_pressed = values["staff_number_input"]
            staff_number_entered = "SS." + keys_pressed

            staff = Staff.objects.filter(staff_number=staff_number_entered)

            if not staff.exists():
                cls.display_message(
                    "No staff found with given staff ID. "
                    "\nEnsure you have been duly registered on the system.",
                    window,
                )
                cls.resize_column(window)
                return True
            cls.process_staff(staff)
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

    @staticmethod
    def resize_column(window):
        window.refresh()
        window["main_column"].contents_changed()

    @classmethod
    def process_staff(cls, staff):
        app_config["tmp_staff"] = app_config.dict_vals_to_str(
            staff.values(
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
        return

    @staticmethod
    def back_nav_key_handler():
        window_dispatch.open_window(HomeWindow)
        sg.popup(
            "Event details saved.",
            title="Event saved",
            keep_on_top=True,
        )
        return


class AttendanceSignOutWindow(BaseGUIWindow):
    @classmethod
    def window(cls):
        event_dict = dict(app_config["current_attendance_session"])
        student_dict = dict(app_config["tmp_student"])
        student_attendance = AttendanceRecord.objects.filter(
            attendance_session_id=app_config.get(
                "current_attendance_session", "session_id"
            ),
            student_id=student_dict["reg_number"],
        )
        layout = [
            [sg.VPush()],
            [sg.Text("Student Attendance Details")],
            [sg.HorizontalSeparator()],
            [
                sg.Text("STATUS: SIGNED IN!"),
            ],
            [sg.Text(f"Course: {event_dict['course']}")],
            [
                sg.Text(
                    f"Student Name: {student_dict['first_name']} {student_dict['last_name']}"
                )
            ],
            [
                sg.Text(
                    f"Registration Number: {student_dict['reg_number']} "
                )
            ],
            [
                sg.Text(
                    f"Sign In Time: {student_attendance[0].check_in_by}"
                )
            ],
            [sg.VPush()],
            [
                sg.Button("Sign Out", k="sign_out", **cls.cancel_button_kwargs(), ),
                sg.Button(
                    "Back",
                    k="back",
                ),
            ],
            [sg.HorizontalSeparator()],
            cls.navigation_pane(
                back_icon="back_disabled", next_icon="next_disabled"
            ),
        ]

        window = sg.Window(
            "Student Attendance Session Page", layout, **cls.window_init_dict()
        )
        return window

    @classmethod
    def loop(cls, window, event, values):
        if event in ("home", "back"):
            window_dispatch.open_window(HomeWindow)
            return True
        if event == "sign_out":
            # TODO: implement this
            window_dispatch.open_window(StudentFaceVerificationWindow)

        return True


class StudentRegNumInputWindow(
    ValidationMixin, StudentBiometricVerificationRouterMixin, BaseGUIWindow
):
    """Window provides an interface for students to enter their registration
    numbers by button clicks."""

    @classmethod
    def window(cls):
        INPUT_BUTTON_SIZE = (8, 2)
        column1 = [
            [
                sg.Button("1", s=INPUT_BUTTON_SIZE),
                sg.Button("2", s=INPUT_BUTTON_SIZE),
                sg.Button("3", s=INPUT_BUTTON_SIZE),
                sg.Button("0", s=INPUT_BUTTON_SIZE),
            ],
            [
                sg.Button("4", s=INPUT_BUTTON_SIZE),
                sg.Button("5", s=INPUT_BUTTON_SIZE),
                sg.Button("6", s=INPUT_BUTTON_SIZE),
                sg.Button("/", s=INPUT_BUTTON_SIZE),
            ],
            [
                sg.Button("7", s=INPUT_BUTTON_SIZE),
                sg.Button("8", s=INPUT_BUTTON_SIZE),
                sg.Button("9", s=INPUT_BUTTON_SIZE),
                sg.Button("AC", key="clear", s=INPUT_BUTTON_SIZE),
            ],
            [
                sg.Push(),
                sg.Button("Submit", key="submit", s=INPUT_BUTTON_SIZE),
                sg.Push(),
            ],
        ]

        layout = [
            [sg.VPush()],
            [cls.message_display_field()],
            [
                sg.Push(),
                sg.Text("Registration Number:  "),
                sg.Input(
                    size=(25, 1),
                    justification="left",
                    key="reg_num_input",
                    focus=True,
                ),
                sg.Push(),
            ],
            [sg.Push(), sg.Column(column1), sg.Push()],
            [sg.VPush()],
            cls.navigation_pane(),
        ]
        scrolled_layout = [
            [
                sg.Column(
                    layout,
                    scrollable=True,
                    vertical_scroll_only=True,
                    key="main_column",
                    expand_y=True,
                )
            ]
        ]

        window = sg.Window(
            "Reg Number Input", scrolled_layout, **cls.window_init_dict()
        )
        return window

    @classmethod
    def loop(cls, window, event, values):
        if event == "back":
            cls.back_nav_key_handler()
            return True
        if event == "home":
            window_dispatch.open_window(HomeWindow)
            return True

        keys_pressed = None
        if event in "0123456789/":
            keys_pressed = values["reg_num_input"]
            keys_pressed += event
            window["reg_num_input"].update(keys_pressed)
            return True

        elif event == "clear":
            window["reg_num_input"].update("")
            cls.hide_message_display_field()
            cls.resize_column(window)
            return True

        elif event in ("submit", "next"):
            if cls.validate(values, window) is not None:
                cls.resize_column(window)
                return True

            reg_number_entered = values["reg_num_input"]

            student = Student.objects.filter(reg_number=reg_number_entered)
            if not student.exists():
                cls.display_message(
                    "No student found with given registration number.", window
                )
                cls.resize_column(window)
                return True
            cls.process_student(student, window)
        return True

    @classmethod
    def process_student(cls, student, window):
        app_config["tmp_student"] = app_config.dict_vals_to_str(
            student.values(
                "reg_number",
                "first_name",
                "last_name",
                "level_of_study",
                "department__name",
                "department__faculty__name",
                "face_encodings",
                "fingerprint_template",
            ).first()
        )

        tmp_student = app_config["tmp_student"]
        if AttendanceRecord.objects.filter(
            attendance_session_id=app_config.get(
                "current_attendance_session", "session_id"
            ),
            student_id=tmp_student["reg_number"],
        ).exists():
            record = AttendanceRecord.objects.get(student_id=tmp_student["reg_number"],
                                                  attendance_session_id=app_config.get(
                                                      "current_attendance_session", "session_id"
                                                  ), )
            # check if the student is signed out and prevent re-entry
            if record.record_type == RecordTypesChoices.SIGN_OUT:
                cls.display_message(
                    "Student already signed out!", window
                )
                cls.resize_column(window)
                return True

            window_dispatch.open_window(AttendanceSignOutWindow)
            return True
        cls.student_verification_window()

    @classmethod
    def validate(cls, values, window):
        for val_check in (
                cls.validate_required_field(
                    (values["reg_num_input"], "registration number")
                ),
                cls.validate_student_reg_number(values["reg_num_input"]),
        ):
            if val_check is not None:
                cls.display_message(val_check, window)
                return True
        return None

    @staticmethod
    def resize_column(window):
        window.refresh()
        window["main_column"].contents_changed()

    @staticmethod
    def back_nav_key_handler():
        window_dispatch.open_window(AttendanceSessionLandingWindow)
        return


class CameraWindow(BaseGUIWindow):
    """A base class. This window provides the general camera window
    layout."""

    @classmethod
    def window(cls):
        layout = [
            [sg.Push(), sg.Column(cls.window_title()), sg.Push()],
            [
                sg.Push(),
                sg.Image(filename="", key="image_display", enable_events=True),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Button(
                    image_data=cls.get_icon("camera", 0.6),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="capture",
                    use_ttk_buttons=True,
                ),
                cls.get_fingerprint_button(),
                cls.get_keyboard_button(),
                sg.Button(
                    image_data=cls.get_icon("cancel", 0.6),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="cancel",
                    use_ttk_buttons=True,
                ),
                sg.Push(),
            ],
        ]
        window = sg.Window("Camera", layout, **cls.window_init_dict())
        return window

    @classmethod
    def get_keyboard_button(cls):
        if issubclass(cls, BarcodeCameraWindow):
            return sg.pin(
                sg.Button(
                    image_data=cls.get_icon("keyboard", 0.6),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="keyboard",
                    visible=True,
                    use_ttk_buttons=True,
                )
            )
        else:
            return sg.pin(
                sg.Button(
                    image_data=cls.get_icon("keyboard", 0.6),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="keyboard",
                    visible=False,
                    use_ttk_buttons=True,
                )
            )

    @classmethod
    def get_fingerprint_button(cls):
        if "verification" in cls.__name__.lower():
            return sg.pin(
                sg.Button(
                    image_data=cls.get_icon("fingerprint", 0.6),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="fingerprint",
                    visible=True,
                    use_ttk_buttons=True,
                )
            )
        else:
            return sg.pin(
                sg.Button(
                    image_data=cls.get_icon("fingerprint", 0.6),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="fingerprint",
                    visible=False,
                    disabled=True,
                    use_ttk_buttons=True,
                )
            )

    @classmethod
    def window_title(cls):
        raise NotImplementedError


class FaceCameraWindow(CameraWindow):
    """This is a base class. Implements facial recognition with camera."""

    @classmethod
    def loop(cls, window, event, values):
        with CamFaceRec() as cam_facerec:
            while True:
                event, values = window.read(timeout=20)

                if event == "cancel":
                    cls.cancel_camera()
                    return True

                if event == "fingerprint":
                    if not OperationalMode.check_fingerprint():
                        cls.popup_auto_close_error(
                            "Fingerprint scanner not connected"
                        )
                    else:
                        cls.open_fingerprint()
                    return True

                if (
                        event in ("capture", "image_display")
                        and cam_facerec.deque_not_empty()
                ):
                    cam_facerec.load_facerec_attrs()
                    if cam_facerec.face_count > 1:
                        cls.popup_auto_close_error(
                            "Multiple faces detected",
                        )
                    elif cam_facerec.face_count == 0:
                        cls.popup_auto_close_error(
                            "Bring face closer to camera"
                        )

                    if cam_facerec.face_count == 1:
                        captured_encodings = cam_facerec.face_encodings()
                        cls.process_image(captured_encodings, window)
                        return True

                window["image_display"].update(
                    data=Camera.feed_to_bytes(cam_facerec.img_bbox)
                )

    @classmethod
    def process_image(cls, captured_face_encodings, window):
        raise NotImplementedError

    @staticmethod
    def cancel_camera():
        raise NotImplementedError

    @staticmethod
    def open_fingerprint():
        raise NotImplementedError

    @classmethod
    def window_title(cls):
        return [
            [
                sg.Push(),
                sg.Image(data=cls.get_icon("face_scanner", 0.4)),
                sg.Text("Position Face", font=("Helvetica", 14)),
                sg.Push(),
            ]
        ]


class StudentFaceVerificationWindow(
    StudentRegNumberInputRouterMixin, FaceCameraWindow
):
    """This class carries out student face verification and calls the 
    uses the AttendanceLogger class to log attendance.
    """

    @classmethod
    def process_image(cls, captured_face_encodings, window):
        if captured_face_encodings is None:
            cls.popup_auto_close_error("Eror. Image must have exactly one face")
            return
        tmp_student = app_config["tmp_student"]

        if tmp_student["face_encodings"] in ("", None):
            cls.popup_auto_close_error(
                "Student's Facial biometric data not found"
            )
            cls.student_reg_number_input_window()
            return

        if FaceRecognition.face_match(
                known_face_encodings=[
                    str_to_face_enc(tmp_student["face_encodings"])
                ],
                face_encoding_to_check=captured_face_encodings,
        ):
            if AttendanceLogger.log_attendance(app_config):
                cls.popup_auto_close_success(AttendanceLogger.message)
                app_config.remove_section("tmp_student")

            else:
                cls.popup_auto_close_error(AttendanceLogger.message)

            cls.student_reg_number_input_window()
            return
        else:
            AttendanceLogger.log_failed_attempt(app_config)
            cls.popup_auto_close_error(
                f"Error. Face did not match "
                f"({app_config['tmp_student']['reg_number']})\n"
                f"You have {4 - app_config.getint('failed_attempts', tmp_student['reg_number'])} attempts left",
                title="No Face",
            )
            return

    @staticmethod
    def cancel_camera():
        """should navigate user back to the attendance session landing page"""
        window_dispatch.open_window(AttendanceSessionLandingWindow)

    @classmethod
    def window_title(cls):
        course = app_config["current_attendance_session"]["course"].split(":")
        event = app_config["current_attendance_session"]["type"]
        student_fname = app_config["tmp_student"]["first_name"]
        student_lname = app_config["tmp_student"]["last_name"]
        student_reg_number = app_config["tmp_student"]["reg_number"]
        return [
            [
                sg.Push(),
                sg.Text(f"{course[0]} {event.capitalize()} Attendance"),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Image(data=cls.get_icon("face_scanner", 0.3)),
                sg.Text(
                    f"Face Verification for: {student_fname[0]}. {student_lname} ({student_reg_number})",
                ),
                sg.Push(),
            ],
        ]

    @staticmethod
    def open_fingerprint():
        window_dispatch.open_window(StudentFingerprintVerificationWindow)
        return


class StaffFaceVerificationWindow(FaceCameraWindow):
    """This class is responsible for staff face verification and initiates attendance session."""

    @classmethod
    def process_image(cls, captured_face_encodings, window):
        if captured_face_encodings is None:
            cls.popup_auto_close_error("Eror. Image must have exactly one face")
            return
        tmp_staff = app_config["tmp_staff"]
        if FaceRecognition.face_match(
                known_face_encodings=[
                    str_to_face_enc(app_config["tmp_staff"]["face_encodings"])
                ],
                face_encoding_to_check=captured_face_encodings,
        ):
            att_session = AttendanceSession.objects.get(
                id=app_config.get("current_attendance_session", "session_id")
            )
            att_session.initiator_id = tmp_staff.get("staff_number")
            att_session.save()
            app_config["current_attendance_session"][
                "initiator_id"
            ] = tmp_staff["staff_number"]
            cls.popup_auto_close_success(
                f"{tmp_staff['first_name'][0].upper()}. "
                f"{tmp_staff['last_name'].capitalize()} "
                f"authorized attendance-marking",
            )

            app_config.remove_section("tmp_staff")
            window_dispatch.open_window(AttendanceSessionLandingWindow)
            return
        else:
            cls.popup_auto_close_error(
                f"Error. Face did not match ({tmp_staff['staff_number']})",
            )
            return

    @staticmethod
    def cancel_camera():

        if app_config.has_option("current_attendance_session", "initiator_id"):
            window_dispatch.open_window(ActiveEventSummaryWindow)
        else:
            app_config["new_event"] = app_config["current_attendance_session"]
            window_dispatch.open_window(NewEventSummaryWindow)
        return

    @classmethod
    def window_title(cls):
        course = app_config["current_attendance_session"]["course"].split(":")
        event = app_config["current_attendance_session"]["type"]
        staff_fname = app_config["tmp_staff"]["first_name"]
        staff_lname = app_config["tmp_staff"]["last_name"]
        return [
            [
                sg.Push(),
                sg.Text(
                    f"Staff Consent for {course[0]} {event.capitalize()} Attendance"
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Image(data=cls.get_icon("face_scanner", 0.3)),
                sg.Text(
                    f"Face Verification for: {staff_fname[0]}. {staff_lname}",
                ),
                sg.Push(),
            ],
        ]

    @staticmethod
    def open_fingerprint():
        window_dispatch.open_window(StaffFingerprintVerificationWindow)
        return


class BarcodeCameraWindow(CameraWindow):
    """Base class. This implements Barcode decoding with camera."""

    @classmethod
    def loop(cls, window, event, values):
        with Camera() as cam:
            while True:
                img = cam.feed()
                barcodes = Barcode.decode_image(img)
                event, values = window.read(timeout=20)
                if event in ("capture", "image_display"):
                    if len(barcodes) == 0:
                        cls.popup_auto_close_error("No ID detected")
                    else:
                        cls.process_barcode(
                            Barcode.decode_barcode(barcodes[0]), window
                        )
                        return True

                if event == "keyboard":
                    cls.launch_keypad()
                    return True

                if event == "cancel":
                    cls.cancel_camera()
                    return True

                if len(barcodes) > 0:
                    cls.process_barcode(
                        Barcode.decode_barcode(barcodes[0]), window
                    )
                    return True
                img_bnw = cam.image_to_grayscale(img)
                window["image_display"].update(data=cam.feed_to_bytes(img_bnw))
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
                sg.Image(data=cls.get_icon("qr_code", 0.3)),
                sg.Text("Present ID Card", font=("Helvetica", 14)),
                sg.Push(),
            ],
        ]


class StudentBarcodeCameraWindow(
    ValidationMixin, StudentBiometricVerificationRouterMixin, StudentRegNumberInputRouterMixin, BarcodeCameraWindow
):
    """window responsible for processing student registration number
    from qr code during attendance marking"""

    @classmethod
    def process_barcode(cls, identification_num, window):
        val_check = cls.validate_student_reg_number(identification_num)
        if val_check is not None:
            cls.popup_auto_close_error(val_check)
            return

        if "blocked_reg_numbers" in app_config[
            "current_attendance_session"
        ] and identification_num in app_config["current_attendance_session"][
            "blocked_reg_numbers"
        ].split(
            ","
        ):
            cls.popup_auto_close_error(
                f"{identification_num} not allowed any more retries.",
                title="Not Allowed",
            )
            return

        student = Student.objects.filter(reg_number=identification_num)
        if not student.exists():
            cls.popup_auto_close_error(
                "No student found with given registration number."
                "Ensure you have been duly registered on the system."
            )
            return

        app_config["tmp_student"] = app_config.dict_vals_to_str(
            student.values(
                "reg_number",
                "first_name",
                "last_name",
                "level_of_study",
                "department__name",
                "department__faculty__name",
                "face_encodings",
                "fingerprint_template",
            ).first()
        )

        tmp_student = app_config["tmp_student"]
        if AttendanceRecord.objects.filter(
                attendance_session_id=app_config.get(
                    "current_attendance_session", "session_id"
                ),
                student_id=tmp_student["reg_number"],
        ).exists():
            cls.popup_auto_close_warn(
                f"{tmp_student['first_name']} {tmp_student['last_name']} "
                f"({tmp_student['reg_number']}) already checked in"
            )
            return

        cls.student_verification_window()
        return

    @staticmethod
    def cancel_camera():
        window_dispatch.open_window(AttendanceSessionLandingWindow)

    @classmethod
    def window_title(cls):
        course = app_config["current_attendance_session"]["course"].split(":")
        event = app_config["current_attendance_session"]["type"]
        return [
            [
                sg.Push(),
                sg.Text(f"{course[0]} {event.capitalize()} Attendance"),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Image(data=cls.get_icon("qr_code", 0.3)),
                sg.Text(
                    "Present Student ID Card (Barcode)", font=("Helvetica", 11)
                ),
                sg.Push(),
            ],
        ]

    @classmethod
    def launch_keypad(cls):
        window_dispatch.open_window(StudentRegNumInputWindow)
        return


class StaffBarcodeCameraWindow(
    ValidationMixin, StaffBiometricVerificationRouterMixin, BarcodeCameraWindow
):
    """window responsible for processing staff number
    from qr code during attendance session initiation"""

    @classmethod
    def process_barcode(cls, identification_num, window):
        val_check = cls.validate_staff_number(identification_num)
        if val_check is not None:
            cls.popup_auto_close_error(val_check)
            return

        staff = Staff.objects.filter(staff_number=identification_num)

        if not staff.exists():
            cls.popup_auto_close_error(
                "No staff found with given staff ID. "
                "Ensure you have been duly registered on the system."
            )
            return

        app_config["tmp_staff"] = app_config.dict_vals_to_str(
            staff.values(
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
        return

    @classmethod
    def window_title(cls):
        course = app_config["current_attendance_session"]["course"].split(":")
        event = app_config["current_attendance_session"]["type"]
        return [
            [
                sg.Push(),
                sg.Text(f"{course[0]} {event.capitalize()} Attendance Consent"),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Image(data=cls.get_icon("qr_code", 0.3)),
                sg.Text(
                    "Present QR Code on Staff ID Card to authorize attendance",
                    font=("Helvetica", 11),
                ),
                sg.Push(),
            ],
        ]

    @classmethod
    def launch_keypad(cls):
        window_dispatch.open_window(StaffNumberInputWindow)
        return


# enrolment windows should not be available on all node devices;
# should only be available on node devices that will be used for
# enrolment


class NodeDeviceRegistrationWindow(ValidationMixin, BaseGUIWindow):
    """
        This window will be collect information for node device registration
        """

    @classmethod
    def window(cls):
        field_label_props = {"size": (22, 1)}
        input_props = {"size": (23, 1)}
        combo_props = {"size": 22}
        layout = [
            [sg.Push(), sg.Text("Node Details"), sg.Push()],
            [cls.message_display_field()],
            [
                sg.Text("Server IP adress:", **field_label_props),
                sg.InputText(key="server_ip_address", default_text="127.0.0.1", **input_props),
            ],
            [
                sg.Text("Server Port:", **field_label_props),
                sg.InputText(key="server_port", default_text="8080", **input_props),
            ],
            [
                sg.Text("Admin Username:", **field_label_props),
                sg.InputText(key="admin_username", **input_props),
            ],
            [
                sg.Text("Initial Password:", **field_label_props),
                sg.InputText(key="password", password_char="*", **input_props),
            ],
            [sg.Button("Submit", key="submit")],
            cls.navigation_pane(),
        ]

        window = sg.Window(
            "Node Registration Window", layout, **cls.window_init_dict()
        )
        return window

    @classmethod
    def loop(cls, window, event, values):
        if event in ("home", "back"):
            window_dispatch.open_window(HomeWindow)
            return True

        if event in ("submit", "next"):
            required_fields = [
                (values["server_ip_address"], "Server IP address"),
                (values["server_port"], "Server port"),
                (values["admin_username"], "Admin Username"),
                (values["password"], "Password"),
            ]
            if (
                    cls.validate_required_fields(required_fields, window)
                    is not None
            ):
                return True
            
            conn = ServerConnection()
            conn.token_authentication(
                server_address=values['server_ip_address'], 
                server_port=values['server_port'], 
                username=values['admin_username'], 
                password=values['password'] 
            )
            DeviceRegistration.register_device(conn)
            cls.popup_auto_close_success("Registered succesfully!")
            window_dispatch.open_window(HomeWindow)
        return True


class EnrolmentMenuWindow(BaseGUIWindow):
    """This window provides links to student and staff enrolment."""

    @classmethod
    def window(cls):
        layout = [
            [sg.VPush()],
            [sg.Button("Staff Enrolment", key="staff_enrolment")],
            [sg.Button("Student Enrolment", key="student_enrolment")],
            [sg.Button("Staff Enrolment Update", key="staff_enrolment_update")],
            [
                sg.Button(
                    "Student Enrolment Update", key="student_enrolment_update"
                )
            ],
            [sg.Button("Register Device", key="register_device")],
            [sg.Button("Synch Device", key="synch_device")],
            [sg.VPush()],
            cls.navigation_pane(next_icon="next_disabled"),
        ]
        window = sg.Window("Enrolment Window", layout, **cls.window_init_dict())
        return window

    @classmethod
    def loop(cls, window, event, values):
        if event in ("back", "home"):
            window_dispatch.open_window(HomeWindow)
        if event == "staff_enrolment":
            window_dispatch.open_window(StaffEnrolmentWindow)
        if event == "student_enrolment":
            window_dispatch.open_window(StudentEnrolmentWindow)
        if event == "staff_enrolment_update":
            window_dispatch.open_window(StaffEnrolmentUpdateIDSearch)
        if event == "student_enrolment_update":
            window_dispatch.open_window(StudentEnrolmentUpdateIDSearch)
        if event == "register_device":
            window_dispatch.open_window(NodeDeviceRegistrationWindow)
        if event == "synch_device":
            window_dispatch.open_window(ServerConnectionDetailsWindow)
        return True


class StaffEnrolmentWindow(ValidationMixin, BaseGUIWindow):
    """The GUI window for enrolment of staff biodata"""

    @classmethod
    def window(cls):
        field_label_props = {"size": 16}
        combo_props = {"size": 28}
        input_props = {"size": 29}
        column1 = [
            [sg.Push(), sg.Text("Staff Enrolment"), sg.Push()],
            [sg.HorizontalSeparator()],
            [cls.message_display_field()],
            [
                sg.Text("Staff Number:", **field_label_props),
                sg.Input(
                    justification="left",
                    key="staff_number_input",
                    focus=True,
                    **input_props,
                ),
            ],
            [
                sg.Text("First Name:", **field_label_props),
                sg.Input(
                    justification="left", key="staff_first_name", **input_props
                ),
            ],
            [
                sg.Text("Last Name:", **field_label_props),
                sg.Input(
                    justification="left", key="staff_last_name", **input_props
                ),
            ],
            [
                sg.Text("Other Names:", **field_label_props),
                sg.Input(
                    justification="left", key="staff_other_names", **input_props
                ),
            ],
            [
                sg.Text("SexChoices:", **field_label_props),
                sg.Combo(
                    values=SexChoices.labels,
                    default_value=cls.COMBO_DEFAULT,
                    key="staff_sex",
                    **combo_props,
                ),
            ],
            [
                sg.Text("Faculty:", **field_label_props),
                sg.Combo(
                    values=Faculty.get_all_faculties(),
                    default_value=cls.COMBO_DEFAULT,
                    enable_events=True,
                    key="staff_faculty",
                    **combo_props,
                ),
            ],
            [
                sg.Text("Department:", **field_label_props),
                sg.Combo(
                    values=Department.get_departments(),
                    default_value=cls.COMBO_DEFAULT,
                    enable_events=True,
                    key="staff_department",
                    **combo_props,
                ),
            ],
        ]
        layout = [
            [sg.VPush()],
            [
                sg.Push(),
                sg.Column(column1),
                sg.Push(),
            ],
            [
                sg.Button("Submit", key="submit"),
                sg.Button("Cancel", key="cancel", **cls.cancel_button_kwargs()),
            ],
            [sg.VPush()],
        ]

        scrolled_layout = [
            [
                sg.Column(
                    layout,
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
            "Staff Enrolment", scrolled_layout, **cls.window_init_dict()
        )
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
                window.refresh()
                window["main_column"].contents_changed()
                return True

            values["staff_number_input"] = values["staff_number_input"].upper()

            app_config["new_staff"] = {
                "username": values["staff_number_input"],
                "staff_number": values["staff_number_input"],
                "first_name": values["staff_first_name"],
                "last_name": values["staff_last_name"],
                "other_names": values["staff_other_names"],
                "department": Department.get_id(values["staff_department"]),
                "sex": SexChoices.str_to_value(values["staff_sex"]),
            }

            new_staff_dict = app_config.section_dict("new_staff")
            department = Department.objects.get(
                id=new_staff_dict.pop("department")
            )

            if Staff.objects.filter(
                    staff_number=new_staff_dict["staff_number"]
            ).exists():
                staff = Staff.objects.filter(
                    staff_number=new_staff_dict["staff_number"]
                )
                staff.update(**new_staff_dict)
            else:
                Staff.objects.create_user(
                    department=department, **new_staff_dict
                )

            cls.next_window()
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

    @classmethod
    def next_window(cls):
        window_dispatch.open_window(StaffPasswordSettingWindow)


class StaffPasswordSettingWindow(BaseGUIWindow):
    """This window is used for setting password for the new staff being
    enrolled."""

    @classmethod
    def window(cls):
        field_label_props = {"size": 25}
        layout = [
            [sg.Text("Set Password")],
            [sg.HorizontalSeparator()],
            [cls.message_display_field()],
            [
                sg.Text("Password:", **field_label_props),
                sg.Input(
                    key="staff_password",
                    expand_x=True,
                    enable_events=True,
                    password_char="*",
                    focus=True,
                ),
            ],
            [
                sg.Text("Confirm Password:", **field_label_props),
                sg.Input(
                    key="staff_password_confirm",
                    expand_x=True,
                    password_char="*",
                ),
            ],
            [
                sg.Button("Submit", key="submit"),
                sg.Button("Cancel", key="cancel", **cls.cancel_button_kwargs()),
            ],
            cls.navigation_pane(
                next_icon="next_disabled", back_icon="back_disabled"
            ),
        ]
        window = sg.Window(
            "Staff Password Setup", layout, **cls.window_init_dict()
        )
        return window

    @classmethod
    def loop(cls, window, event, values):
        if event in ("staff_password", "staff_password_confirm"):
            if values["staff_password"] != values["staff_password_confirm"]:
                cls.display_message(
                    "Re-enter the same password in the 'Confirm Password' field",
                    window,
                )
            else:
                cls.display_message("", window)

        if event in ("cancel", "submit"):
            new_staff = app_config["new_staff"]
            try:
                staff = Staff.objects.get(
                    staff_number=new_staff["staff_number"]
                )
            except Exception as e:
                cls.display_message(e, window)
                return True

            if event == "submit":
                for field in (
                        values["staff_password"],
                        values["staff_password_confirm"],
                ):
                    if field in (None, ""):
                        cls.display_message(
                            "Enter password and confirmation", window
                        )
                        return True
                staff.set_password(values["staff_password"])
                staff.save()

                if not OperationalMode.check_camera():
                    cls.popup_auto_close_warn("Camera not connected.")
                    time.sleep(2)
                    if not OperationalMode.check_fingerprint():
                        cls.popup_auto_close_warn(
                            "Fingerprint scanner not connected"
                        )
                        window_dispatch.open_window(HomeWindow)
                    else:
                        window_dispatch.open_window(
                            StaffFingerprintEnrolmentWindow
                        )
                else:
                    window_dispatch.open_window(StaffFaceEnrolmentWindow)
                return True

            if event in ("cancel", "home"):
                confirm = sg.popup_yes_no(
                    "Cancel Staff registration?",
                    title="Cancel Registration",
                    keep_on_top=True,
                )
                if confirm == "Yes":
                    staff.delete()
                    window_dispatch.open_window(StaffEnrolmentWindow)
                    return True
                else:
                    return True
        return True


class StaffFaceEnrolmentWindow(FaceCameraWindow):
    """This window is used to capture face encodings for a new staff
    being enrolled."""

    @classmethod
    def process_image(cls, captured_face_encodings, window):
        if captured_face_encodings is None:
            cls.popup_auto_close_error(
                "Error. Image must have exactly one face"
            )
            return
        new_staff = app_config["new_staff"]

        try:
            staff = Staff.objects.get(staff_number=new_staff["staff_number"])
        except Exception as e:
            cls.popup_auto_close_error(e)
            return

        staff.face_encodings = face_enc_to_str(captured_face_encodings)
        staff.save()

        window_dispatch.open_window(StaffFingerprintEnrolmentWindow)
        cls.popup_auto_close_success("Biometric data saved")
        return

    @staticmethod
    def cancel_camera():
        confirm = sg.popup_yes_no(
            "Staff details will be saved with no biometric data. Continue?",
            keep_on_top=True,
        )
        if confirm == "Yes":
            app_config.remove_section("new_staff")
            window_dispatch.open_window(HomeWindow)
        return


class StudentEnrolmentWindow(ValidationMixin, BaseGUIWindow):
    """The GUI window for enrolment of student biodata."""

    @classmethod
    def window(cls):
        field_label_props = {"size": 22}
        combo_props = {"size": 22}
        input_props = {"size": 23}
        column1 = [
            [sg.Push(), sg.Text("Student Enrolment"), sg.Push()],
            [cls.message_display_field()],
            [
                sg.Text("Registration Number:", **field_label_props),
                sg.Input(
                    justification="left",
                    key="student_reg_number_input",
                    focus=True,
                    **input_props,
                ),
            ],
            [
                sg.Text("First Name:", **field_label_props),
                sg.Input(
                    justification="left",
                    key="student_first_name",
                    **input_props,
                ),
            ],
            [
                sg.Text("Last Name:", **field_label_props),
                sg.Input(
                    justification="left",
                    key="student_last_name",
                    **input_props,
                ),
            ],
            [
                sg.Text("Other Names:", **field_label_props),
                sg.Input(
                    justification="left",
                    key="student_other_names",
                    **input_props,
                ),
            ],
            [
                sg.Text("SexChoices:", **field_label_props),
                sg.Combo(
                    values=SexChoices.labels,
                    default_value=cls.COMBO_DEFAULT,
                    key="student_sex",
                    **combo_props,
                ),
            ],
            [
                sg.Text("Level of study:", **field_label_props),
                sg.Input(
                    justification="left",
                    key="student_level_of_study",
                    **input_props,
                ),
            ],
            [
                sg.Text("Possible graduation year:", **field_label_props),
                sg.Input(
                    justification="left",
                    key="student_possible_grad_yr",
                    **input_props,
                ),
            ],
            [
                sg.Text("Faculty:", **field_label_props),
                sg.Combo(
                    values=Faculty.get_all_faculties(),
                    default_value=cls.COMBO_DEFAULT,
                    enable_events=True,
                    key="student_faculty",
                    **combo_props,
                ),
            ],
            [
                sg.Text("Department:", **field_label_props),
                sg.Combo(
                    values=Department.get_departments(),
                    default_value=cls.COMBO_DEFAULT,
                    enable_events=True,
                    key="student_department",
                    **combo_props,
                ),
            ],
        ]

        layout = [
            [sg.VPush()],
            [
                sg.Push(),
                sg.Column(column1),
                sg.Push(),
            ],
            [
                sg.Button("Submit", key="submit"),
                sg.Button("Cancel", key="cancel", **cls.cancel_button_kwargs()),
            ],
            [sg.VPush()],
        ]

        scrolled_layout = [
            [
                sg.Column(
                    layout,
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
            "Student Enrolment", scrolled_layout, **cls.window_init_dict()
        )
        return window

    @classmethod
    def loop(cls, window, event, values):
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
                window.refresh()
                window["main_column"].contents_changed()
                return True

            app_config["new_student"] = {}
            app_config["new_student"] = {
                "reg_number": values["student_reg_number_input"],
                "first_name": values["student_first_name"],
                "last_name": values["student_last_name"],
                "other_names": values["student_other_names"],
                "level_of_study": values["student_level_of_study"],
                "possible_grad_yr": values["student_possible_grad_yr"],
                "sex": SexChoices.str_to_value(values["student_sex"]),
                "department": Department.get_id(values["student_department"]),
            }
            new_student_dict = app_config.section_dict("new_student")
            department = Department.objects.get(
                id=new_student_dict.pop("department")
            )

            if Student.objects.filter(
                    reg_number=new_student_dict["reg_number"]
            ).exists():
                student = Student.objects.filter(
                    reg_number=new_student_dict["reg_number"]
                )
                student.update(**new_student_dict)
            else:
                Student.objects.create(
                    department=department, **new_student_dict
                )

            if not OperationalMode.check_camera():
                cls.popup_auto_close_error("Camera not connected")
                time.sleep(1)
                if not OperationalMode.check_fingerprint():
                    cls.popup_auto_close_error(
                        "Fingerprit scanner not connected"
                    )
                    window_dispatch.open_window(HomeWindow)
                    return True
                else:
                    window_dispatch.open_window(
                        StudentFingerprintEnrolmentWindow
                    )
                    return True
            else:
                window_dispatch.open_window(StudentFaceEnrolmentWindow)
                return True
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

        # if Student.objects.filter(
        #     reg_number=values["student_reg_number_input"]
        # ).exists():
        #     cls.display_message(
        #         f"Student with registration number "
        #         f"{values['student_reg_number_input']} already exists",
        #         window,
        #     )
        #     return True
        return None


class StudentFaceEnrolmentWindow(FaceCameraWindow):
    """This window is used to capture face encodings for a new student
    being enrolled."""

    @classmethod
    def process_image(cls, captured_face_encodings, window):
        if captured_face_encodings is None:
            cls.popup_auto_close_error(
                "Error. Image must have exactly one face"
            )
            return
        new_student = app_config["new_student"]

        try:
            student = Student.objects.get(reg_number=new_student["reg_number"])
        except Exception as e:
            cls.popup_auto_close_error(e)
            return

        student.face_encodings = face_enc_to_str(captured_face_encodings)
        student.save()
        cls.popup_auto_close_success("Biometric data saved")
        window_dispatch.open_window(StudentFingerprintEnrolmentWindow)
        return

    @staticmethod
    def cancel_camera():
        confirm = sg.popup_yes_no(
            "Student details will be saved with no biometric data. Continue?",
            keep_on_top=True,
        )
        if confirm == "Yes":
            app_config.remove_section("new_student")
            window_dispatch.open_window(HomeWindow)
        return


class FingerprintGenericWindow(BaseGUIWindow):
    """Base window. Provides the layout for the fingerprint capture
    window for the application."""

    @classmethod
    def window(cls):
        layout = [
            [sg.Push(), sg.Text(cls.window_title()), sg.Push()],
            [sg.Push(), cls.message_display_field(), sg.Push()],
            [sg.VPush()],
            [
                sg.Push(),
                sg.Image(cls.get_icon("fingerprint_grey", 1.3)),
                sg.Push(),
            ],
            [sg.VPush()],
            [
                sg.Push(),
                cls.get_camera_button(),
                sg.Button(
                    image_data=cls.get_icon("cancel", 0.6),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="cancel",
                    use_ttk_buttons=True,
                ),
                sg.Push(),
            ],
        ]
        window = sg.Window(
            "Fingerprint Verification", layout, **cls.window_init_dict()
        )
        return window

    @classmethod
    def get_camera_button(cls):
        if "verification" in cls.__name__.lower():
            return sg.pin(
                sg.Button(
                    image_data=cls.get_icon("camera", 0.6),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="camera",
                    visible=True,
                    use_ttk_buttons=True,
                )
            )
        else:
            return sg.pin(
                sg.Button(
                    image_data=cls.get_icon("camera", 0.6),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="camera",
                    visible=False,
                    use_ttk_buttons=True,
                )
            )

    @classmethod
    def window_title(cls):
        return "Fingerprint Scan"


class StudentFingerprintVerificationWindow(
    StudentRegNumberInputRouterMixin, FingerprintGenericWindow
):
    """This window provides an interface for verifying student fingerprint
    during attendance logging."""

    @classmethod
    def loop(cls, window, event, values):
        if event == "cancel":
            window_dispatch.open_window(AttendanceSessionLandingWindow)
            return True
        if event == "camera":
            if not OperationalMode.check_camera():
                cls.popup_auto_close_error("Camera not connected")
            else:
                window_dispatch.open_window(StudentFaceVerificationWindow)
            return True

        tmp_student = app_config["tmp_student"]
        try:
            fp_template = eval(tmp_student.get("fingerprint_template"))
        except Exception as e:
            cls.popup_auto_close_error(
                "Invalid fingerprint data from student registration", duration=5
            )
            cls.student_reg_number_input_window()

            return True

        if fp_template in (None, ""):
            cls.popup_auto_close_error(
                "No valid fingerprint data from student registration",
                duration=5,
            )
            cls.student_reg_number_input_window()
            return True

        try:
            fp_scanner = FingerprintScanner()
        except RuntimeError as e:
            cls.popup_auto_close_error(e, duration=5)
            cls.student_reg_number_input_window()
            return True

        cls.display_message("Waiting for finger print...", window)
        try:
            fp_response = fp_scanner.fp_capture()
        except RuntimeError:
            cls.popup_auto_close_error("Connection to fingerprint scanner lost")
            cls.student_reg_number_input_window()
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
            cls.student_reg_number_input_window()
            return True

        if fp_scanner.verify_match():
            if AttendanceLogger.log_attendance(app_config):
                cls.popup_auto_close_success(AttendanceLogger.message)
                app_config.remove_section("tmp_student")

            else:
                cls.popup_auto_close_error(AttendanceLogger.message)

            cls.student_reg_number_input_window()
            return True
        elif not fp_scanner.verify_match():
            AttendanceLogger.log_failed_attempt(app_config)
            cls.popup_auto_close_error(
                f"Fingerprint did not match registration data.\n"
                f"{app_config['tmp_student']['reg_number']}."
                f"You have {4 - app_config.getint('failed_attempts', tmp_student['reg_number'])}"
            )
            return True

        return True

    @classmethod
    def window_title(cls):
        return "Student Fingerprint Verification"


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
            if app_config.has_option(
                    "current_attendance_session", "initiator_id"
            ):
                window_dispatch.open_window(ActiveEventSummaryWindow)
            else:
                app_config["new_event"] = app_config[
                    "current_attendance_session"
                ]
                window_dispatch.open_window(NewEventSummaryWindow)
            return True

        if event == "camera":
            if not OperationalMode.check_camera():
                cls.popup_auto_close_error("Camera not connected")
            else:
                window_dispatch.open_window(StaffFaceVerificationWindow)
            return True

        tmp_staff = app_config["tmp_staff"]
        try:
            fp_template = eval(tmp_staff.get("fingerprint_template"))
        except Exception as e:
            cls.popup_auto_close_error(
                "Invalid fingerprint data from staff registration", duration=5
            )
            app_config.remove_section("tmp_staff")
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
            window_dispatch.open_window(AttendanceSessionLandingWindow)
            return True

        if fp_scanner.verify_match():
            att_session = AttendanceSession.objects.get(
                id=app_config.get("current_attendance_session", "session_id")
            )
            att_session.initiator_id = tmp_staff.get("staff_number")
            att_session.save()
            app_config["current_attendance_session"][
                "initiator_id"
            ] = tmp_staff["staff_number"]
            cls.popup_auto_close_success(
                f"{tmp_staff['first_name'][0].upper()}. "
                f"{tmp_staff['last_name'].capitalize()} "
                f"authorized attendance-marking",
            )

            app_config.remove_section("tmp_staff")
            window_dispatch.open_window(AttendanceSessionLandingWindow)
            return True
        elif not fp_scanner.verify_match():
            cls.popup_auto_close_error(
                "Fingerprint did not match registration data"
            )
            return True

        cls.popup_auto_close_success(
            f"{tmp_staff['last_name']} {tmp_staff['first_name'][0]}. checked in"
        )
        window_dispatch.open_window(AttendanceSessionLandingWindow)
        return True

    @classmethod
    def window_title(cls):
        return "Staff Fingerprint Verification"


class FingerprintEnrolmentWindow(FingerprintGenericWindow):
    """
    This class provides the loop method for capturing the fingerprint
    template for both staff and student enrolment.
    """

    @classmethod
    def loop(cls, window, event, values):

        if event == "cancel":
            cls.cancel_fp_enrolment()
            return True

        try:
            fp_scanner = FingerprintScanner()
        except RuntimeError as e:
            cls.popup_auto_close_error(e, duration=5)
            cls.remove_enrolment_config()
            window_dispatch.open_window(HomeWindow)
            return True

        for fingerimg in range(1, 3):
            if fingerimg == 1:
                cls.popup_auto_close_warn(
                    "Place your right thumb on fingerprint sensor...",
                    title="Info",
                )
            else:
                cls.popup_auto_close_warn(
                    "Place same finger again...", title="Info"
                )

            time.sleep(1)

            try:
                fp_scanner.fp_continuous_capture()
            except RuntimeError as e:
                cls.popup_auto_close_error(
                    "Connection to fingerprint scanner lost"
                )
                window_dispatch.open_window(HomeWindow)
                return True

            if not fp_scanner.image_2_tz(fingerimg):
                cls.popup_auto_close_error(fp_scanner.error, duration=5)
                return True

            if fingerimg == 1:
                cls.popup_auto_close_warn("Remove finger...", title="Info")
                time.sleep(2)
                i = fp_scanner.get_image()
                while i != fp_scanner.NOFINGER:
                    i = fp_scanner.get_image()

        cls.display_message("Creating model...", window)
        if not fp_scanner.create_model():
            cls.popup_auto_close_error(fp_scanner.error)
            return True

        fingerprint_data = fp_scanner.get_fpdata(scanner_slot=1)
        cls.process_fingerprint(fingerprint_data)
        return True

    @classmethod
    def process_fingerprint(cls, fingerprint_data):
        raise NotImplementedError

    @staticmethod
    def cancel_fp_enrolment():
        raise NotImplementedError

    @staticmethod
    def remove_enrolment_config():
        raise NotImplementedError


class StudentFingerprintEnrolmentWindow(FingerprintEnrolmentWindow):
    """This class provides methods tailored to student fingerprint enrolment."""

    @classmethod
    def process_fingerprint(cls, fingerprint_data):
        new_student = app_config["new_student"]

        try:
            student = Student.objects.get(reg_number=new_student["reg_number"])
        except Exception as e:
            cls.popup_auto_close_error(e)
            return
        student.fingerprint_template = str(fingerprint_data)
        student.save()
        app_config.remove_section("new_student")
        cls.popup_auto_close_success("Student enrolment successful")
        window_dispatch.open_window(StudentEnrolmentWindow)
        return

    @staticmethod
    def cancel_fp_enrolment():
        confirm = sg.popup_yes_no(
            "Student details will be saved with no fingerprint biometric data. Continue?",
            keep_on_top=True,
        )
        if confirm == "Yes":
            app_config.remove_section("new_student")
            window_dispatch.open_window(HomeWindow)
        return

    @staticmethod
    def remove_enrolment_config():
        app_config.remove_section("new_student")
        return

    @classmethod
    def window_title(cls):
        return "Student Fingerprint Enrolment"


class StaffFingerprintEnrolmentWindow(FingerprintEnrolmentWindow):
    """This class provides methods tailored to staff fingerprint enrolement."""

    @classmethod
    def process_fingerprint(cls, fingerprint_data):
        new_staff = app_config["new_staff"]

        try:
            staff = Staff.objects.get(staff_number=new_staff["staff_number"])
        except Exception as e:
            cls.popup_auto_close_error(e)
            return

        staff.fingerprint_template = str(fingerprint_data)
        staff.save()
        app_config.remove_section("new_staff")
        cls.popup_auto_close_success("Staff enrolment successful")
        window_dispatch.open_window(StaffEnrolmentWindow)
        return

    @staticmethod
    def cancel_fp_enrolment():
        confirm = sg.popup_yes_no(
            "Staff details will be saved with no biometric data. Continue?",
            keep_on_top=True,
        )
        if confirm == "Yes":
            app_config.remove_section("new_staff")
            window_dispatch.open_window(HomeWindow)
        return

    @staticmethod
    def remove_enrolment_config():
        app_config.remove_section("new_staff")
        return

    @classmethod
    def window_title(cls):
        return "Student Fingerprint Verification"


class StudentEnrolmentUpdateWindow(StudentEnrolmentWindow):
    """A window for updating biodata of existing student."""

    @classmethod
    def window(cls):
        student = app_config["edit_student"]

        try:
            student_sex = SexChoices(int(student["sex"])).label
        except Exception:
            student_sex = None

        field_label_props = {"size": 22}
        combo_props = {"size": 22}
        input_props = {"size": 23}
        column1 = [
            [sg.Push(), sg.Text("Student Enrolment"), sg.Push()],
            [cls.message_display_field()],
            [
                sg.Text("Registration Number:", **field_label_props),
                sg.Input(
                    justification="left",
                    key="student_reg_number_input",
                    disabled=True,
                    **input_props,
                    default_text=student["reg_number"],
                ),
            ],
            [
                sg.Text("First Name:", **field_label_props),
                sg.Input(
                    justification="left",
                    key="student_first_name",
                    focus=True,
                    **input_props,
                    default_text=student["first_name"],
                ),
            ],
            [
                sg.Text("Last Name:", **field_label_props),
                sg.Input(
                    justification="left",
                    key="student_last_name",
                    **input_props,
                    default_text=student["last_name"],
                ),
            ],
            [
                sg.Text("Other Names:", **field_label_props),
                sg.Input(
                    justification="left",
                    key="student_other_names",
                    **input_props,
                    default_text=student["other_names"],
                ),
            ],
            [
                sg.Text("SexChoices:", **field_label_props),
                sg.Combo(
                    values=SexChoices.labels,
                    default_value=student_sex or cls.COMBO_DEFAULT,
                    key="student_sex",
                    **combo_props,
                ),
            ],
            [
                sg.Text("Level of study:", **field_label_props),
                sg.Input(
                    justification="left",
                    key="student_level_of_study",
                    **input_props,
                    default_text=student["level_of_study"],
                ),
            ],
            [
                sg.Text("Possible graduation year:", **field_label_props),
                sg.Input(
                    justification="left",
                    key="student_possible_grad_yr",
                    **input_props,
                    default_text=student["possible_grad_yr"],
                ),
            ],
            [
                sg.Text("Faculty:", **field_label_props),
                sg.Combo(
                    values=Faculty.get_all_faculties(),
                    default_value=student["department__faculty__name"],
                    enable_events=True,
                    key="student_faculty",
                    **combo_props,
                ),
            ],
            [
                sg.Text("Department:", **field_label_props),
                sg.Combo(
                    values=Department.get_departments(),
                    default_value=student["department__name"],
                    enable_events=True,
                    key="student_department",
                    **combo_props,
                ),
            ],
        ]

        layout = [
            [sg.VPush()],
            [
                sg.Push(),
                sg.Column(column1),
                sg.Push(),
            ],
            [
                sg.Button("Submit", key="submit"),
                sg.Button("Cancel", key="cancel", **cls.cancel_button_kwargs()),
            ],
            [sg.VPush()],
        ]

        scrolled_layout = [
            [
                sg.Column(
                    layout,
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
            "Student Enrolment", scrolled_layout, **cls.window_init_dict()
        )
        return window

    @classmethod
    def loop(cls, window, event, values):
        return super().loop(window, event, values)


class StudentEnrolmentUpdateIDSearch(StudentRegNumInputWindow):
    @classmethod
    def window(cls):
        return super().window()

    @classmethod
    def loop(cls, window, event, values):
        return super().loop(window, event, values)

    @classmethod
    def process_student(cls, student, window):
        app_config["edit_student"] = app_config.dict_vals_to_str(
            student.values(
                "reg_number",
                "first_name",
                "last_name",
                "other_names",
                "level_of_study",
                "possible_grad_yr",
                "sex",
                "department__name",
                "department__faculty__name",
                "face_encodings",
                "fingerprint_template",
            ).first()
        )
        window_dispatch.open_window(StudentEnrolmentUpdateWindow)
        return


class StaffEnrolmentUpdateIDSearch(StaffNumberInputWindow):
    @classmethod
    def window(cls):
        return super().window()

    @classmethod
    def loop(cls, window, event, values):
        return super().loop(window, event, values)

    @classmethod
    def process_staff(cls, staff):
        app_config["edit_staff"] = app_config.dict_vals_to_str(
            staff.values(
                "staff_number",
                "first_name",
                "last_name",
                "other_names",
                "sex",
                "department__name",
                "department__faculty__name",
                "face_encodings",
                "fingerprint_template",
            ).first()
        )
        window_dispatch.open_window(StaffEnrolmentUpdateWindow)
        return

    @staticmethod
    def back_nav_key_handler():
        window_dispatch.open_window(HomeWindow)
        return


class StaffEnrolmentUpdateWindow(StaffEnrolmentWindow):
    """A window for updating biodata of existing staff."""

    @classmethod
    def window(cls):
        staff = app_config["edit_staff"]

        try:
            staff_sex = SexChoices(int(staff["sex"])).label
        except Exception:
            staff_sex = None

        field_label_props = {"size": 16}
        combo_props = {"size": 28}
        input_props = {"size": 29}
        column1 = [
            [sg.Push(), sg.Text("Staff Enrolment"), sg.Push()],
            [sg.HorizontalSeparator()],
            [cls.message_display_field()],
            [
                sg.Text("Staff Number:", **field_label_props),
                sg.Input(
                    justification="left",
                    key="staff_number_input",
                    disabled=True,
                    **input_props,
                    default_text=staff["staff_number"],
                ),
            ],
            [
                sg.Text("First Name:", **field_label_props),
                sg.Input(
                    justification="left",
                    focus=True,
                    key="staff_first_name",
                    **input_props,
                    default_text=staff["first_name"],
                ),
            ],
            [
                sg.Text("Last Name:", **field_label_props),
                sg.Input(
                    justification="left",
                    default_text=staff["last_name"],
                    key="staff_last_name",
                    **input_props,
                ),
            ],
            [
                sg.Text("Other Names:", **field_label_props),
                sg.Input(
                    justification="left",
                    default_text=staff["other_names"],
                    key="staff_other_names",
                    **input_props,
                ),
            ],
            [
                sg.Text("SexChoices:", **field_label_props),
                sg.Combo(
                    values=SexChoices.labels,
                    default_value=staff_sex or cls.COMBO_DEFAULT,
                    key="staff_sex",
                    **combo_props,
                ),
            ],
            [
                sg.Text("Faculty:", **field_label_props),
                sg.Combo(
                    values=Faculty.get_all_faculties(),
                    default_value=staff["department__faculty__name"],
                    enable_events=True,
                    key="staff_faculty",
                    **combo_props,
                ),
            ],
            [
                sg.Text("Department:", **field_label_props),
                sg.Combo(
                    values=Department.get_departments(),
                    default_value=staff["department__name"],
                    enable_events=True,
                    key="staff_department",
                    **combo_props,
                ),
            ],
        ]
        layout = [
            [sg.VPush()],
            [
                sg.Push(),
                sg.Column(column1),
                sg.Push(),
            ],
            [
                sg.Button("Submit", key="submit"),
                sg.Button("Cancel", key="cancel", **cls.cancel_button_kwargs()),
            ],
            [sg.VPush()],
        ]

        scrolled_layout = [
            [
                sg.Column(
                    layout,
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
            "Staff Enrolment", scrolled_layout, **cls.window_init_dict()
        )
        return window

    @classmethod
    def loop(cls, window, event, values):
        return super().loop(window, event, values)

    @classmethod
    def next_window(cls):
        if not OperationalMode.check_camera():
            cls.popup_auto_close_warn("Camera not connected.")
            time.sleep(2)
            if not OperationalMode.check_fingerprint():
                cls.popup_auto_close_warn("Fingerprint scanner not connected")
                window_dispatch.open_window(HomeWindow)
            else:
                window_dispatch.open_window(StaffFingerprintEnrolmentWindow)
        else:
            window_dispatch.open_window(StaffFaceEnrolmentWindow)


class DeviceSetupWindow(BaseGUIWindow):
    """
    Window for setting up the node device.
    The window will handle synching data from the server."""

    @classmethod
    def window(cls):
        layout = [
            [sg.Text("Device Synch")],
            [
                sg.Image(
                    data=cls.get_icon("loading_ring_lines"),
                    enable_events=True,
                    key="loading_image",
                )
            ],
            [sg.Push(), sg.Text("Synching..."), sg.Push()],
            cls.navigation_pane(),
        ]

    @classmethod
    def loop(cls, window, event, values):
        # The synching operation could be running in another thread and
        # send a signal when done

        window["loading_image"].update_animation(
            cls.get_icon("loading_ring_lines"), time_between_frames=500
        )
        return True


class ServerConnectionDetailsWindow(ValidationMixin, BaseGUIWindow):
    """
    This window will be collect information (server address, SSID, password)
    that will enable connection to the server.
    """

    @classmethod
    def window(cls):
        field_label_props = {"size": (22, 1)}
        input_props = {"size": (23, 1)}
        combo_props = {"size": 22}
        layout = [
            [sg.Push(), sg.Text("Server Details"), sg.Push()],
            [cls.message_display_field()],
            [
                sg.Text("Server IP adress:", **field_label_props),
                sg.InputText(key="server_ip_address", default_text="127.0.0.1", **input_props),
            ],
            [
                sg.Text("Server Port:", **field_label_props),
                sg.InputText(key="server_port", default_text="8080", **input_props),
            ],
            [
                sg.Text("Connection Type:", **field_label_props),
                sg.Combo(
                    values=["WiFi", "LORA"],
                    default_value="WiFi",
                    key="connection_type",
                    enable_events=True,
                    **combo_props,
                ),
            ],
            [
                sg.Text("WLAN Name (SSID):", **field_label_props),
                sg.Combo(
                    key="ssid",
                    values=WLANInterface.available_networks() or [],
                    **combo_props),
            ],
            [
                sg.Text("WLAN Password:", **field_label_props),
                sg.InputText(key="wlan_password", password_char="*", **input_props),
            ],
            [sg.Button("Submit", key="submit")],
            cls.navigation_pane(),
        ]

        window = sg.Window(
            "Server Details Window", layout, **cls.window_init_dict()
        )
        return window

    @classmethod
    def loop(cls, window, event, values):
        if event in ("home", "back"):
            window_dispatch.open_window(HomeWindow)
            return True

        if event == "connection_type":
            if values["connection_type"] != "WiFi":
                window["ssid"].disabled = True
                window["wlan_password"].disabled = True
            else:
                window["ssid"].disabled = False
                window["wlan_password"].disabled = False

        if event in ("submit", "next"):
            required_fields = [
                (values["server_ip_address"], "Server IP address"),
                (values["server_port"], "Server port"),
            ]

            # TODO: not validating all required fields. Only validating the first field
            if (
                    cls.validate_required_fields(required_fields, window)
                    is not None
            ):
                return True

            app_config["server_details"] = {
                "server_ip_address": values["server_ip_address"],
                "server_port": values["server_port"],
                "connection_type": values["connection_type"],
                "ssid": values["ssid"],
                "wlan_password": values["wlan_password"],
            }

            server_details = app_config["server_details"]
            if values["connection_type"] == "WiFi":
                try:
                    connect_result = 0
                    # TODO: uncomment and fix the connect to wifi method
                    # connect_result = connect_to_wifi(
                    #     server_details["ssid"], server_details["wlan_password"]
                    # )
                except Exception as e:
                    cls.popup_auto_close_error(e)
                    connect_result = 0  # TODO: remove this flag  and uncomment return value when done testing
                    # return True

                if connect_result == 0:
                    cls.popup_auto_close_success(
                        "WiFi network connection established"
                    )
                    time.sleep(1)
                    NodeDataSynch.first_time_sync(server_details["server_ip_address"],
                                                  int(server_details["server_port"]))

                elif connect_result != 0:
                    cls.popup_auto_close_error(
                        "Error establishing WiFi Network connection. Check details provided."
                    )
                    return True

                # test connection to server after network has been established
        return True


def main():
    window_dispatch.open_window(HomeWindow)
    continue_loop = True
    window = None

    while continue_loop:
        window = window_dispatch.current_window
        event, values = window.read(timeout=500)
        current_window = window_dispatch.find_window_name(window)
        if current_window:
            continue_loop = eval(current_window).loop(window, event, values)
        if event == sg.WIN_CLOSED:
            break

    if window is not None:
        window.close()


# def main():
#     window = HomeWindow.window()
#     loop_exit_code = True

#     while loop_exit_code:
#         # window = window_dispatch.current_window
#         event, values = window.read(timeout=500)
#         # current_window = window_dispatch.find_window(window)
#         loop_exit_code = HomeWindow.loop(window, event, values)

#         if event == sg.WIN_CLOSED:
#             break
#     window.close()


if __name__ == "__main__":
    main()
