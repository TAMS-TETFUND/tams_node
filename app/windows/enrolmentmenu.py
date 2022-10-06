import json

import PySimpleGUI as sg

from app.basegui import BaseGUIWindow
import app.appconfigparser
import app.windowdispatch
from app.nodedevicedatasynch import NodeDataSynch

window_dispatch = app.windowdispatch.WindowDispatch()


class EnrolmentMenuWindow(BaseGUIWindow):
    """This window provides links to student and staff enrolment."""

    @classmethod
    def window(cls):

        column1 = [
            [
                sg.Push(),
                sg.Button(
                    image_data=cls.get_icon("add_user", 0.5),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="staff_enrolment",
                    use_ttk_buttons=True,
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text("Staff", key="staff_enrolment_txt", enable_events=True),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text(
                    "Enrolment", key="staff_enrolment_txt_2", enable_events=True
                ),
                sg.Push(),
            ],
        ]
        column2 = [
            [
                sg.Push(),
                sg.Button(
                    image_data=cls.get_icon("add_user", 0.5),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="student_enrolment",
                    use_ttk_buttons=True,
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text(
                    "Student", key="student_enrolment_txt", enable_events=True
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text(
                    "Enrolment",
                    key="student_enrolment_txt_2",
                    enable_events=True,
                ),
                sg.Push(),
            ],
        ]
        column3 = [
            [
                sg.Push(),
                sg.Button(
                    image_data=cls.get_icon("edit_user", 0.5),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="staff_enrolment_update",
                    use_ttk_buttons=True,
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text(
                    "Staff",
                    key="staff_enrolment_update_txt",
                    enable_events=True,
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text(
                    "Enrolment",
                    key="staff_enrolment_update_txt_2",
                    enable_events=True,
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text(
                    "Update",
                    key="staff_enrolment_update_txt_3",
                    enable_events=True,
                ),
                sg.Push(),
            ],
        ]
        column4 = [
            [
                sg.Push(),
                sg.Button(
                    image_data=cls.get_icon("edit_user", 0.5),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="student_enrolment_update",
                    use_ttk_buttons=True,
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text(
                    "Student",
                    key="student_enrolment_update_txt",
                    enable_events=True,
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text(
                    "Enrolment",
                    key="student_enrolment_update_txt_2",
                    enable_events=True,
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text(
                    "Update",
                    key="student_enrolment_update_txt_2",
                    enable_events=True,
                ),
                sg.Push(),
            ],
        ]
        column5 = [
            [
                sg.Push(),
                sg.Button(
                    image_data=cls.get_icon("register_device", 0.5),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="register_device",
                    use_ttk_buttons=True,
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text(
                    "Register", key="register_device_txt", enable_events=True
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text(
                    "Device", key="register_device_txt", enable_events=True
                ),
                sg.Push(),
            ],
        ]
        column6 = [
            [
                sg.Push(),
                sg.Button(
                    image_data=cls.get_icon("synch", 0.5),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="synch_device",
                    use_ttk_buttons=True,
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text("Synch", key="synch_device_txt", enable_events=True),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text("Device", key="synch_device_txt", enable_events=True),
                sg.Push(),
            ],
        ]
        layout = [
            [sg.VPush()],
            [
                sg.Push(),
                sg.Column(column1),
                sg.Column(column2),
                sg.Column(column5),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Column(column3),
                sg.Column(column4),
                sg.Column(column6),
                sg.Push(),
            ],
            [sg.VPush()],
            cls.navigation_pane(next_icon="next_disabled"),
        ]
        window = sg.Window("Enrolment Window", layout, **cls.window_init_dict())
        return window

    @classmethod
    def loop(cls, window, event, values):
        if event in ("back", "home"):
            window_dispatch.dispatch.open_window("HomeWindow")
        if event in (
            "staff_enrolment",
            "staff_enrolment_txt",
            "staff_enrolment_txt_2",
        ):
            window_dispatch.dispatch.open_window("StaffEnrolmentWindow")
        if event in (
            "student_enrolment",
            "student_enrolment_txt",
            "student_enrolment_txt_2",
        ):
            window_dispatch.dispatch.open_window("StudentEnrolmentWindow")
        if event in (
            "staff_enrolment_update",
            "staff_enrolment_update_txt",
            "staff_enrolment_update_txt_2",
            "staff_enrolment_update_txt_3",
        ):
            window_dispatch.dispatch.open_window("StaffEnrolmentUpdateIDSearch")
        if event in (
            "student_enrolment_update",
            "student_enrolment_update_txt",
            "student_enrolment_update_txt_2",
            "student_enrolment_update_txt_3",
        ):
            window_dispatch.dispatch.open_window(
                "StudentEnrolmentUpdateIDSearch"
            )
        if event in (
            "register_device",
            "register_device_txt",
            "register_device_txt_2",
        ):
            window_dispatch.dispatch.open_window("NodeDeviceRegistrationWindow")
        if event in ("synch_device", "synch_device_txt", "synch_device_txt_2"):
            window_dispatch.dispatch.open_window(
                "ServerConnectionDetailsWindow"
            )
        if event == "sync_attendance":
            try:
                NodeDataSynch.node_attendance_sync()
                msg = "Attendance Successfully Synced!"
            except Exception as e:
                print(e)
                err_msg = f"Error: {json.loads(str(e))['detail']}"
                cls.popup_auto_close_error(message=err_msg, duration=5)
                return True
            cls.popup_auto_close_success(message=msg, duration=5)
        return True
