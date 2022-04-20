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
    power_icon = icon_dict["power"]
    column1 = [
        [
            sg.Push(),
            sg.Button(
                image_data=image_file_to_bytes(
                    fingerprint_icon, (ICON_SIZE["h"], ICON_SIZE["w"])
                ),
                button_color=ICON_BUTTON_COLOR,
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
                key="Schedule",
            ),
            sg.Push(),
        ],
        [sg.Push(), sg.Text("Scheduled/Recurring Events"), sg.Push()],
    ]

    layout = [
        [
            sg.Push(),
            sg.Button(
                image_data=image_file_to_bytes(
                    power_icon, (ICON_SIZE["h"] * 0.5, ICON_SIZE["w"] * 0.5)
                ),
                button_color=ICON_BUTTON_COLOR,
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
                image_data=image_file_to_bytes(
                    lab_icon, (ICON_SIZE["h"], ICON_SIZE["w"])
                ),
                button_color=ICON_BUTTON_COLOR,
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
                image_data=image_file_to_bytes(
                    test_icon, (ICON_SIZE["h"], ICON_SIZE["w"])
                ),
                button_color=ICON_BUTTON_COLOR,
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
                image_data=image_file_to_bytes(
                    exam_icon, (ICON_SIZE["h"], ICON_SIZE["w"])
                ),
                button_color=ICON_BUTTON_COLOR,
                key="exam",
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
        [
            sg.Push(),
            sg.Button("<< Back", key="back"),
            sg.Button("Next >>", key="next"),
            sg.Button("Cancel", key="cancel"),
            sg.Push(),
        ],
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
    calendar_icon = icon_dict["calendar"]
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
                key="start_hour",
            ),
            sg.Spin(
                values=[str(a).zfill(2) for a in range(0, 60)],
                initial_value="00",
                expand_x=True,
                expand_y=True,
                key="start_minute",
            ),
            sg.Input(key="start_date", size=(20, 1), expand_y=True),
            sg.Button(
                image_data=image_file_to_bytes(
                    calendar_icon,
                    (ICON_SIZE["h"] * 0.25, ICON_SIZE["w"] * 0.25),
                ),
                button_color=ICON_BUTTON_COLOR,
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
    face_scanner_icon = icon_dict["face_scanner"]
    fingerprint_icon = icon_dict["fingerprint"]
    column1 = [
        [
            sg.Push(),
            sg.Button(
                image_data=image_file_to_bytes(
                    face_scanner_icon, (ICON_SIZE["h"], ICON_SIZE["w"])
                ),
                button_color=ICON_BUTTON_COLOR,
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
                image_data=image_file_to_bytes(
                    fingerprint_icon, (ICON_SIZE["h"], ICON_SIZE["w"])
                ),
                button_color=ICON_BUTTON_COLOR,
                key="fingerprint_verification",
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


def staff_number_input_win():
    input_button_size = (10, 2)
    column1 = [
        [
            sg.Button("1", s=input_button_size),
            sg.Button("2", s=input_button_size),
            sg.Button("3", s=input_button_size),
        ],
        [
            sg.Button("4", s=input_button_size),
            sg.Button("5", s=input_button_size),
            sg.Button("6", s=input_button_size),
        ],
        [
            sg.Button("7", s=input_button_size),
            sg.Button("8", s=input_button_size),
            sg.Button("9", s=input_button_size),
        ],
        [
            sg.Button("Submit", key="submit", s=input_button_size),
            sg.Button("0", s=input_button_size),
            sg.Button("Clear", key="clear", s=input_button_size),
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
        "Staff Number Input",
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
    staff_number_input_window = None

    while True:
        window, event, values = sg.read_all_windows()

        # Home window logic
        if window == home_window:
            if event == "new_event":
                event_menu_window = event_menu_win()
                home_window.hide()
            if event == "quit":
                clicked = sg.popup_ok_cancel(
                    "System will shutdown. Do you want to continue?",
                    title="Shutdown",
                    keep_on_top=True,
                )
                if clicked == "OK":
                    print("OK pressed")
                    break
                if clicked == "Cancel":
                    print("Cancel pressed")
                if clicked == None:
                    print("Didn't start no'ing ")
                continue

        # Event menu window logic
        if window == event_menu_window:
            if event in (sg.WIN_CLOSED, "back"):
                home_window.un_hide()
                event_menu_window.close()
                event_menu_window = None
            if event in ("lecture", "exam", "lab", "test"):
                # save the selected event type in configparser object
                app_config["new_event"] = {}
                app_config["new_event"]["type"] = event
                if event in ("lecture", "lab"):
                    recurring = sg.popup_yes_no(
                        f"Is this {event} a weekly activity?",
                        title="Confirm event detail",
                        keep_on_top=True,
                    )
                    if recurring == "Yes":
                        app_config["new_event"]["recurring"] = "True"
                    elif recurring in ("No", None):
                        pass

                save_config(app_config)
                academic_session_details_window = academic_session_details_win()
                event_menu_window.close()
                event_menu_window = None

        # academic session details window logic
        if window == academic_session_details_window:
            if event == "next":
                app_config["DEFAULT"]["semester"] = values["current_semester"]
                app_config["DEFAULT"]["session"] = values["current_session"]
                save_config(app_config)

                event_details_window = event_details_win()
            elif event == "back":
                event_menu_window = event_menu_win()
            elif event == "cancel":
                home_window = home_win()
            else:
                continue
            academic_session_details_window.close()
            academic_session_details_window = None

        # event details window logic
        if window == event_details_window:
            if event == "course_faculty":
                if values["course_faculty"] in ("--select--", None):
                    window["course_department"].update(
                        values=utils.get_all_departments(), value="--select--"
                    )
                else:
                    window["course_department"].update(
                        values=utils.filter_departments(
                            values["course_faculty"]
                        ),
                        value="--select--",
                    )
            if event == "course_department":
                if values["course_department"] in ("--select--", None):
                    window["selected_course"].update(
                        values=utils.get_all_courses(), value="--select--"
                    )
                else:
                    window["selected_course"].update(
                        values=utils.filter_courses(
                            dept=values["course_department"]
                        ),
                        value="--select--",
                    )
            if event == "pick_date":
                event_date = sg.popup_get_date()
                if event is None:
                    continue
                else:
                    window["start_date"].update(
                        value=f"{event_date[1]}-{event_date[0]}-{event_date[2]}"
                    )
            if event in ("Start Event", "Schedule Event"):
                # input validation required on window elements
                app_config["new_event"]["course"] = values["selected_course"]
                app_config["new_event"]["start_time"] = ":".join(
                    [values["start_hour"], values["start_minute"]]
                )
                app_config["new_event"]["start_date"] = values["start_date"]
                app_config["new_event"]["duration"] = values["duration"]
                save_config(app_config)

                if event == "Start Event":
                    staff_number_input_window = staff_number_input_win()
                if event == "Schedule Event":
                    home_window.un_hide()
                event_details_window.close()
                event_details_window = None

        # staff number input window logic
        if window == staff_number_input_window:
            if event == "back":
                home_window = home_win()
                staff_number_input_window.close()
                staff_number_input_window = None
                sg.popup_notify(
                    "Event has been saved as a scheduled event",
                    title="Event saved",
                )
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
                save_config(app_config)
                verify_attendance_initiator_window = (
                    verify_attendance_initiator_win()
                )
                staff_number_input_window.close()
                staff_number_input_window = None
                continue
            window["staff_number_input"].update(keys_entered)

        # attendance initiator verification window logic
        if window == verify_attendance_initiator_window:
            if event in (sg.WIN_CLOSED, "back"):
                home_window = home_win()
                verify_attendance_initiator_window.close()
                verify_attendance_initiator_window = None
                sg.popup_notify(
                    "Event has been saved as a scheduled event",
                    title="Event saved",
                )
        if event == sg.WIN_CLOSED:
            break
    home_window.close()


if __name__ == "__main__":
    main()
