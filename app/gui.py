from datetime import datetime
import PySimpleGUI as sg

from app.appconfigparser import AppConfigParser
from app.basegui import BaseGUIWindow
# from app.camera import Camera
from app.windowdispatch import WindowDispatch
from manage import init_django

init_django()

from db.models import (
    AttendanceSession,
    AcademicSession,
    Student,
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

    @staticmethod
    def loop(window, event, values):
        if event == "new_event":
            window_dispatch.open_window(EventMenuWindow)

        if event == "quit":
            return HomeWindow.confirm_exit()
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

    @staticmethod
    def loop(window, event, values):
        if event in (sg.WIN_CLOSED, "back"):
            window_dispatch.open_window(HomeWindow)
        if event in ("lecture", "exam", "lab", "test"):
            app_config["new_event"] = {}
            app_config["new_event"]["type"] = event
            if event in ("lecure", "lab"):
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

    @staticmethod
    def loop(window, event, values):
        if event == "next":
            app_config["DEFAULT"]["semester"] = values["current_semester"]
            app_config["DEFAULT"]["session"] = values["current_session"]
            app_config.save()
            window_dispatch.open_window(EventDetailWindow)
        elif event == "back":
            window_dispatch.open_window(EventMenuWindow)
        elif event == "cancel":
            window_dispatch.open_window(HomeWindow)
        return True


class EventDetailWindow(BaseGUIWindow):
    @classmethod
    def window(cls):
        layout = [
            [sg.Push(), sg.Text("Event Details"), sg.Push()],
            [sg.Text("_" * 80)],
            [sg.VPush()],
            [
                sg.Text("What Faculty administers the course:  "),
                sg.InputCombo(
                    Faculty.get_all_faculties(),
                    default_value="--select--",
                    enable_events=True,
                    key="course_faculty",
                    expand_y=True,
                ),
            ],
            [
                sg.Text("What Department administers the course:  "),
                sg.InputCombo(
                    Department.get_all_departments(),
                    default_value="--select--",
                    enable_events=True,
                    key="course_department",
                    expand_y=True,
                ),
            ],
            [
                sg.Text("Select Course:  "),
                sg.InputCombo(
                    Course.get_all_courses(
                        semester=app_config.get("DEFAULT", "semester")
                    ),
                    default_value="--select--",
                    enable_events=True,
                    key="selected_course",
                    expand_y=True,
                ),
            ],
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
                sg.Text("Hours"),
            ],
            [
                sg.Push(),
                sg.Button("Start Event"),
                sg.Button("Schedule Event"),
                sg.Push(),
            ],
            [sg.VPush()],
        ]

        window = sg.Window("Event Details", layout, **cls.window_init_dict())
        return window

    @staticmethod
    def loop(window, event, values):
        if event == "course_faculty":
            if values["course_faculty"] in ("--select--", None):
                window["course_department"].update(
                    values=Department.get_all_departments(), value="--select--"
                )
            else:
                window["course_department"].update(
                    values=Department.filter_departments(
                        values["course_faculty"]
                    ),
                    value="--select--",
                )
        if event == "course_department":
            if values["course_department"] in ("--select--", None):
                window["selected_course"].update(
                    values=Course.get_all_courses(), value="--select--"
                )
            else:
                window["selected_course"].update(
                    values=Course.filter_courses(
                        dept=values["course_department"]
                    ),
                    value="--select--",
                )
        if event == "pick_date":
            event_date = sg.popup_get_date()
            if event is None:
                return True
            else:
                window["start_date"].update(
                    value=f"{event_date[1]}-{event_date[0]}-{event_date[2]}"
                )
        if event in ("Start Event", "Schedule Event"):
            app_config["new_event"]["course"] = values["selected_course"]
            app_config["new_event"]["start_time"] = (
                values["start_hour"] + ":" + values["start_minute"]
            )
            app_config["new_event"]["start_date"] = values["start_date"]
            app_config["new_event"]["duration"] = values["duration"]
            app_config.save()

            if event == "Start Event":
                window_dispatch.open_window(StaffNumberInputWindow)
            if event == "Schedule Event":
                window_dispatch.open_window(HomeWindow)
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

    @staticmethod
    def loop(window, event, values):
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

    @staticmethod
    def loop(window, event, values):
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
            keys_entered = values["staff_number_input"]
            app_config["new_event"]["initiator_staff_num"] = (
                "SS." + keys_entered
            )
            app_config.save()
            window_dispatch.open_window(VerifyAttendanceInitiatorWindow)
            return True
        window["staff_number_input"].update(keys_entered)
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
                sg.Push()
            ],
        ]
        window = sg.Window("Camera", layout, **cls.window_init_dict())
        return window

    @staticmethod
    def loop(window, event, values):
        cam_on = True
        with Camera() as cam:
            while cam_on:
                event, values = window.read(timeout=20)
                if event == "capture":
                    return False
                window["image_display"].update(data=cam.feed())
        return True


class EnrolWindow(BaseGUIWindow):
    """The GUI """

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
