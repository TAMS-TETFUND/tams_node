import io
import json
import os
import base64
import configparser
from pathlib import Path

from PIL import Image, ImageDraw, ImageTk, ImageFont
import PySimpleGUI as sg

from app import utils

from manage import init_django

init_django()

from db.models import AttendanceSession

CURRENT_DIR = os.path.abspath(__file__)
CONFIG_FILE = os.path.join(Path(CURRENT_DIR).parent, "config.ini")
SCREEN_SIZE = (480, 320)
ICON_SIZE = {"h": 125, "w": 70}
SYMBOL_UP = "▲"
SYMBOL_DOWN = "▼"

# loading the application icons
icons_path = os.path.join(Path(CURRENT_DIR).parent, "icons.json")
with open(icons_path, "r") as data:
    icon_dict = json.loads(data.read())

# setting GUI's theme
sg.theme("LightGreen6")  # Dark, LightGreen6
ICON_BUTTON_COLOR = (sg.theme_background_color(), sg.theme_background_color())

# initializing the configparser object
app_config = configparser.ConfigParser()
app_config.read(CONFIG_FILE)


def save_config(parser_obj: configparser):
    """Function for saving the configparser object
    as changes are made in the application
    """
    with open(CONFIG_FILE, "w") as configfile:
        parser_obj.write(configfile)


def image_file_to_bytes(image64, size):
    image_file = io.BytesIO(base64.b64decode(image64))
    img = Image.open(image_file)
    img.thumbnail(size, Image.ANTIALIAS)
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    imgbytes = bio.getvalue()
    return imgbytes


def home_win():

    fingerprint_icon = icon_dict["fingerprint"]
    users_icon = icon_dict["users"]
    schedule_icon = icon_dict["schedule"]
    column1 = [
        [
            sg.Push(),
            sg.Button(
                image_data=image_file_to_bytes(
                    fingerprint_icon, (ICON_SIZE["h"], ICON_SIZE["w"])
                ),
                button_color=ICON_BUTTON_COLOR,
                font="Any 15",
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
                image_data=image_file_to_bytes(
                    users_icon, (ICON_SIZE["h"], ICON_SIZE["w"])
                ),
                button_color=ICON_BUTTON_COLOR,
                font="Any 15",
                pad=(0, 0),
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
                image_data=image_file_to_bytes(
                    schedule_icon, (ICON_SIZE["h"], ICON_SIZE["w"])
                ),
                button_color=ICON_BUTTON_COLOR,
                font="Any 15",
                key="Schedule",
            ),
            sg.Push(),
        ],
        [sg.Push(), sg.Text("Scheduled/Regular Events"), sg.Push()],
    ]

    layout = [
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

    window = sg.Window(
        "Home Window",
        layout,
        size=SCREEN_SIZE,
        no_titlebar=True,
        keep_on_top=True,
        grab_anywhere=True,
        finalize=True,
    )
    return window


def event_menu_win():
    exam_icon = icon_dict["graduation_cap"]
    test_icon = icon_dict["test_script"]
    lab_icon = icon_dict["lab"]
    lecture_icon = icon_dict["lecture"]

    column1 = [
        [
            sg.Push(),
            sg.Button(
                image_data=image_file_to_bytes(
                    lecture_icon, (ICON_SIZE["h"], ICON_SIZE["w"])
                ),
                button_color=ICON_BUTTON_COLOR,
                font="Any 15",
                key="Lecture",
            ),
            sg.Push(),
        ],
        [sg.Push(), sg.Text("Lecture"), sg.Push()],
    ]

    column2 = [
        [
            sg.Push(),
            sg.Button(
                image_data=image_file_to_bytes(
                    lab_icon, (ICON_SIZE["h"], ICON_SIZE["w"])
                ),
                button_color=ICON_BUTTON_COLOR,
                font="Any 15",
            ),
            sg.Push(),
        ],
        [sg.Push(), sg.Text("Lab"), sg.Push()],
    ]

    column3 = [
        [
            sg.Push(),
            sg.Button(
                image_data=image_file_to_bytes(
                    test_icon, (ICON_SIZE["h"], ICON_SIZE["w"])
                ),
                button_color=ICON_BUTTON_COLOR,
                font="Any 15",
            ),
            sg.Push(),
        ],
        [sg.Push(), sg.Text("Test"), sg.Push()],
    ]

    column4 = [
        [
            sg.Push(),
            sg.Button(
                image_data=image_file_to_bytes(
                    exam_icon, (ICON_SIZE["h"], ICON_SIZE["w"])
                ),
                button_color=ICON_BUTTON_COLOR,
                font="Any 15",
            ),
            sg.Push(),
        ],
        [sg.Push(), sg.Text("Exam"), sg.Push()],
    ]

    layout = [
        [sg.Push(), sg.Text("Take Attendance for:", font="Any 20"), sg.Push()],
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

    window = sg.Window(
        "Event Menu",
        layout,
        size=SCREEN_SIZE,
        no_titlebar=True,
        keep_on_top=True,
        grab_anywhere=True,
        finalize=True,
    )
    return window


def academic_session_details_win():
    """Window for setting academic session details"""
    layout = [
        [sg.Push(), sg.Text("Academic Session Details"), sg.Push()],
        [sg.Text("_" * 80)],
        [sg.VPush()],
        [
            sg.Text("Select Current Session:  "),
            sg.Combo(
                utils.get_all_academic_sessions(),
                default_value=utils.get_all_academic_sessions()[0],
                enable_events=True,
                key="current_session",
                expand_y=True,
            ),
        ],
        [
            sg.Text("Select Current Semester: "),
            sg.Combo(
                utils.get_semesters(),
                default_value=utils.get_semesters()[0],
                enable_events=True,
                key="current_semester",
                expand_y=True,
            ),
        ],
        [sg.VPush()],
        [sg.Push(), sg.Button("Next >>", key="next"), sg.Push()],
    ]

    window = sg.Window(
        "Academic Session Details",
        layout,
        size=SCREEN_SIZE,
        no_titlebar=True,
        keep_on_top=True,
        grab_anywhere=True,
        finalize=True,
    )
    return window


def event_details_win():
    """Window for users to specify the details of the event to
    be created
    """
    layout = [
        [sg.Push(), sg.Text("Event Details"), sg.Push()],
        [sg.Text("_" * 80)],
        [sg.VPush()],
        [
            sg.Text("What Faculty administers the course:  "),
            sg.InputCombo(
                utils.get_all_faculties(),
                default_value="--select--",
                enable_events=True,
                key="course_faculty",
                expand_y=True,
            ),
        ],
        [
            sg.Text("What Department administers the course:  "),
            sg.InputCombo(
                utils.get_all_departments(),
                default_value="--select--",
                enable_events=True,
                key="course_department",
                expand_y=True,
            ),
        ],
        [
            sg.Text("Select Course:  "),
            sg.InputCombo(
                utils.get_all_courses(
                    semester=app_config.get(
                        "DEFAULT", "semester", fallback=utils.get_semesters()[0]
                    )
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
            ),
            sg.Spin(
                values=[str(a).zfill(2) for a in range(0, 60)],
                initial_value="00",
                expand_x=True,
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

    window = sg.Window(
        "Event Details",
        layout,
        size=SCREEN_SIZE,
        no_titlebar=True,
        keep_on_top=True,
        grab_anywhere=True,
        finalize=True,
    )
    return window


def verify_attendance_initiator_win():
    """Here the initiator of the attendance session"""
    verify_user_icon = icon_dict["verify_user"]
    fingerprint_icon = icon_dict["fingerprint"]
    column1 = [
        [
            sg.Push(),
            sg.Button(
                image_data=image_file_to_bytes(
                    verify_user_icon, (ICON_SIZE["h"], ICON_SIZE["w"])
                ),
                button_color=ICON_BUTTON_COLOR,
                font="Any 15",
            ),
            sg.Push(),
        ],
        [sg.Push(), sg.Text("Face ID"), sg.Push()],
    ]

    column2 = [
        [
            sg.Push(),
            sg.Button(
                image_data=image_file_to_bytes(
                    fingerprint_icon, (ICON_SIZE["h"], ICON_SIZE["w"])
                ),
                button_color=ICON_BUTTON_COLOR,
                font="Any 15",
            ),
            sg.Push(),
        ],
        [sg.Push(), sg.Text("Fingerprint"), sg.Push()],
    ]

    layout = [
        [
            sg.Text("Only registered staff can initiate attendance taking."),
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
        "Verify Attendance Initiator",
        layout,
        size=SCREEN_SIZE,
        no_titlebar=True,
        keep_on_top=True,
        grab_anywhere=True,
        finalize=True,
    )
    return window


def main():
    home_window = home_win()
    event_menu_window = None
    verify_attendance_initiator_window = None
    event_details_window = None
    academic_session_details_window = None

    while True:
        window, event, values = sg.read_all_windows()

        # Home window logic
        if window == home_window:
            if event == "new_event":
                event_menu_window = event_menu_win()
                home_window.hide()
            if event == "continue_attendance":
                break

        # Event menu window logic
        if window == event_menu_window:
            if event in (sg.WIN_CLOSED, "back"):
                home_window.un_hide()
                event_menu_window.close()
                event_menu_window = None
            if event in ("Lecture", "Exam", "Lab", "Test"):
                academic_session_details_window = academic_session_details_win()
                event_menu_window.close()
                event_menu_window = None

        # academic session details window logic
        if window == academic_session_details_window:
            if event == "next":
                event_details_window = event_details_win()
                academic_session_details_window.close()
                academic_session_details_window = None

        # event details window logic
        if window == event_details_window:
            if event == "course_faculty":
                if window["course_faculty"].get() in ("--select--", None):
                    window["course_department"].update(
                        values=utils.get_all_departments(), value="--select--"
                    )
                else:
                    window["course_department"].update(
                        values=utils.filter_departments(
                            window["course_faculty"].get()
                        ),
                        value="--select--",
                    )
            if event == "course_department":
                if window["course_department"].get() in ("--select--", None):
                    window["selected_course"].update(
                        values=utils.get_all_courses(), value="--select--"
                    )
                else:
                    window["selected_course"].update(
                        values=utils.filter_courses(
                            dept=window["course_department"].get()
                        ),
                        value="--select--",
                    )
            if event == "Start Event":
                home_window.un_hide()
                event_details_window.close()
                event_details_window = None

        # attendance initiator verification window logic
        if window == verify_attendance_initiator_window:
            if event in (sg.WIN_CLOSED, "back"):
                event_menu_window = event_menu_win()
                verify_attendance_initiator_window.close()
                verify_attendance_initiator_window = None

        if event == sg.WIN_CLOSED:
            break
    home_window.close()


if __name__ == "__main__":
    main()
