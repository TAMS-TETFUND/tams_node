from cgitb import enable
from datetime import datetime
import PySimpleGUI as sg

from app.appconfigparser import AppConfigParser
from app.basegui import BaseGUIWindow

# from app.camera import Camera
from app.barcode import Barcode
from app.facerec import FaceRecognition
from app.windowdispatch import WindowDispatch
from manage import init_django

init_django()

from db.models import (
    AttendanceSession,
    AcademicSession,
    Student,
    Sex,
    Staff,
    Course,
    Faculty,
    Semester,
    Department,
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
                    image_data=cls.get_icon("fingerprint"),
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
                    image_data=cls.get_icon("users"),
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
        if event == "settings":
            window_dispatch.open_window(EnrolmentWindow)
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
                    key="test",
                ),
                sg.Push(),
            ],
            [sg.Push(), sg.Text("Test"), sg.Push()],
        ]

        column4 = [
            [
                sg.Push(),
                sg.Button(
                    image_data=cls.get_icon("graduation_cap"),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="exam",
                ),
                sg.Push(),
            ],
            [sg.Push(), sg.Text("Exam"), sg.Push()],
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
        if event in ("lecture", "exam", "lab", "test"):
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
                elif recurring == "No":
                    app_config["new_event"]["recurring"] = "False"
                else:
                    pass

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
            required_fields = ["current_semester", "current_session"]
            for field in required_fields:
                if not cls.validate_required_field(values[field], field):
                    return True
            if not cls.validate(values):
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
    def validate(cls, values):
        """fields: current_session, current_semester"""
        if values["current_semester"] not in Semester.labels:
            sg.popup(
                "Invalid value in current semester",
                "Invalid semester",
                keep_on_top=True,
            )
            return False
        if not AcademicSession.is_valid_session(values["current_session"]):
            sg.popup(
                "Invlid value in current session",
                "Invalid session",
                keep_on_top=True,
            )
            return False
        return True


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
                sg.Button("Start Event", k="start_event"),
                sg.Button("Schedule Event", k="schedule_event"),
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
            if event is None:
                return True
            else:
                window["start_date"].update(
                    value=f"{event_date[1]}-{event_date[0]}-{event_date[2]}"
                )
            window.force_focus()
        if event in ("start_event", "schedule_event"):
            required_fields = [
                "selected_course",
                "start_hour",
                "start_date",
                "duration",
            ]
            for field in required_fields:
                if not cls.validate_required_field(values[field], field):
                    return True
            if not cls.validate(values):
                return True
            app_config["new_event"]["course"] = values["selected_course"]
            app_config["new_event"]["start_time"] = (
                values["start_hour"] + ":" + values["start_minute"]
            )
            app_config["new_event"]["start_date"] = values["start_date"]
            app_config["new_event"]["duration"] = values["duration"]
            app_config.save()

            if event == "start_event":
                window_dispatch.open_window(StaffNumberInputWindow)
            if event == "schedule_event":
                sg.popup(
                    "Event saved to scheduled events",
                    title="Event saved",
                    keep_on_top=True,
                )
                window_dispatch.open_window(HomeWindow)
        if event == "cancel":
            app_config["new_event"] = {}
            app_config.save()
            window_dispatch.open_window(HomeWindow)
        return True

    @classmethod
    def validate(cls, values):
        if Course.str_to_course(values["selected_course"]) is None:
            sg.popup("Invalid course selected", title="Error", keep_on_top=True)
            return False

        if None in (
            cls.get_int(values["start_hour"]),
            cls.get_int(values["start_minute"]),
        ):
            sg.popup("Invalid value in start time", keep_on_top=True)
            return False

        if (
            cls.get_int(values["duration"]) is None
            or int(values["duration"]) <= 0
        ):
            sg.popup("Invalid value in duration", keep_on_top=True)
            return False

        try:
            start_date = datetime.strptime(values["start_date"], "%d-%m-%Y")
        except ValueError:
            sg.popup("Invalid start date", keep_on_top=True)
            return False

        current_dt = datetime.now()

        if current_dt < start_date or current_dt.hour > int(
            values["start_hour"]
        ):
            sg.popup(
                "Date and time must not be earlier than current date and time",
                keep_on_top=True,
            )
            return False

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
        global window_dispatch, app_config
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
        global window_dispatch, app_config
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
            if not cls.validate_required_field(
                values["staff_number_input"], "staff_input_value"
            ):
                return True
            if not cls.validate(values):
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
    def validate(cls, values):
        """fields: staff_number_input"""
        if not Staff.is_valid_staff_number(
            "SS." + values["staff_number_input"]
        ):
            sg.popup(
                "Invalid staff number",
                title="Invalid staff number",
                keep_on_top=True,
            )
            return False
        return True


class CameraWindow(BaseGUIWindow):
    @classmethod
    def window(cls):
        layout = [
            [sg.Push(), sg.Image(filename="", key="image_display"), sg.Push()],
            [
                sg.Push(),
                sg.Button(
                    image_data=cls.get_icon("camera", 0.5),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="capture",
                ),
                sg.Push(),
            ],
        ]
        window = sg.Window("Camera", layout, **cls.window_init_dict())
        return window


class FaceCameraWindow(CameraWindow):
    @classmethod
    def loop(cls, window, event, values):
        cam_on = True
        with Camera() as cam:
            while cam_on:
                event, values = window.read(timeout=20)
                if event == "capture":
                    return False
                img = cam.feed()
                face_locations = FaceRecognition.face_locations(img)
                if len(face_locations) > 0:
                    for face_location in face_locations:
                        FaceRecognition.draw_bounding_box(face_location, img)
                window["image_display"].update(data=img)
        return True


class BarcodeCameraWindow(CameraWindow):
    @classmethod
    def loop(cls, window, event, values):
        cam_on = True
        with Camera() as cam:
            while cam_on:
                event, values = window.read(timeout=20)
                if event == "capture":
                    return False
                img = cam.feed()
                barcodes = Barcode.decode_image(img)
                if len(barcodes) > 0:
                    for barcode in barcodes:
                        Barcode.draw_bounding_box(barcode, img)
                window["image_display"].update(data=img)
        return True


class EnrolmentWindow(BaseGUIWindow):
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
        ]
        window = sg.Window("Enrolment Window", layout, **cls.window_init_dict())
        return window

    @classmethod
    def loop(cls, window, event, values):
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
            [cls.message_display()],
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
            val_check = None
            local_val_check = None
            req_fields = [
                "staff_number_input",
                "staff_first_name",
                "staff_last_name",
                "staff_sex",
                "staff_faculty",
                "staff_department",
            ]
            for field in req_fields:
                val_check = cls.validate_required_field(values[field], field)
                if val_check is not None:
                    window["message_display"].update(
                        value=val_check, visible=True
                    )
                    return True
            local_val_check = cls.validate(values)
            if local_val_check is not None:
                window["message_display"].update(
                    value=local_val_check, visible=True
                )
                return True
            else:
                window_dispatch.open_window(HomeWindow)
            window_dispatch.open_window(HomeWindow)
        if event == "cancel":
            window_dispatch.open_window(HomeWindow)
        return True

    @classmethod
    def validate(cls, values):
        for criteria in (
            cls.validate_staff_number(values["staff_number_input"]),
            cls.validate_sex(values["staff_sex"]),
            cls.validate_faculty(values["staff_faculty"]),
            cls.validate_department(values["staff_department"]),
        ):
            if criteria is not None:
                return criteria
        return None


class StudentEnrolmentWindow(BaseGUIWindow):
    @classmethod
    def window(cls):
        column1 = [
            [sg.Push(), sg.Text("Student Enrolment"), sg.Push()],
            [cls.message_display()],
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
            val_check = None
            local_val_check = None
            req_fields = [
                "student_reg_number_input",
                "student_first_name",
                "student_last_name",
                "student_sex",
                "student_level_of_study",
                "student_faculty",
                "student_department",
            ]
            for field in req_fields:
                val_check = cls.validate_required_field(values[field], field)
                if val_check is not None:
                    window["message_display"].update(
                        value=val_check, visible=True
                    )
                    return True
            local_val_check = cls.validate(values)
            if local_val_check is not None:
                window["message_display"].update(
                    value=local_val_check, visible=True
                )
                return True
            else:
                window_dispatch.open_window(HomeWindow)
        if event == "cancel":
            window_dispatch.open_window(HomeWindow)
        return True

    @classmethod
    def validate(cls, values):
        for criteria in (
            cls.validate_student_reg_number(values["student_reg_number_input"]),
            cls.validate_sex(values["student_sex"]),
            cls.validate_faculty(values["student_faculty"]),
            cls.validate_department(values["student_department"]),
            cls.validate_int_field(
                values["student_level_of_study"], "level of study"
            ),
        ):
            if criteria is not None:
                return criteria
        return None


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

    while True:
        window, event, values = sg.read_all_windows()
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
