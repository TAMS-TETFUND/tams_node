import json
from typing import Any, Dict

import PySimpleGUI as sg

from app.basegui import BaseGUIWindow
import app.appconfigparser
import app.windowdispatch
from app.serverconnection import ServerConnection
from app.nodedevicedatasynch import NodeDataSynch

window_dispatch = app.windowdispatch.WindowDispatch()
app_config = app.appconfigparser.AppConfigParser()


class EnrolmentMenuWindow(BaseGUIWindow):
    """This window provides links to student and staff enrolment."""

    @classmethod
    def window(cls) -> sg.Window:
        """Construct layout/appearance of window."""

        column1 = [
            [
                sg.Push(),
                sg.Button(
                    image_data=cls.get_icon("add_user", 0.5),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key=cls.key("staff_enrolment"),
                    use_ttk_buttons=True,
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text("Staff", key=cls.key("staff_enrolment_txt"), enable_events=True),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text(
                    "Enrolment", key=cls.key("staff_enrolment_txt_2"), enable_events=True
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
                    key=cls.key("student_enrolment"),
                    use_ttk_buttons=True,
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text(
                    "Student", key=cls.key("student_enrolment_txt"), enable_events=True
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text(
                    "Enrolment",
                    key=cls.key("student_enrolment_txt_2"),
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
                    key=cls.key("staff_enrolment_update"),
                    use_ttk_buttons=True,
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text(
                    "Staff",
                    key=cls.key("staff_enrolment_update_txt"),
                    enable_events=True,
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text(
                    "Enrolment",
                    key=cls.key("staff_enrolment_update_txt_2"),
                    enable_events=True,
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text(
                    "Update",
                    key=cls.key("staff_enrolment_update_txt_3"),
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
                    key=cls.key("student_enrolment_update"),
                    use_ttk_buttons=True,
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text(
                    "Student",
                    key=cls.key("student_enrolment_update_txt"),
                    enable_events=True,
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text(
                    "Enrolment",
                    key=cls.key("student_enrolment_update_txt_2"),
                    enable_events=True,
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text(
                    "Update",
                    key=cls.key("student_enrolment_update_txt_2"),
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
                    key=cls.key("register_device"),
                    use_ttk_buttons=True,
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text(
                    "Register", key=cls.key("register_device_txt"), enable_events=True
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text(
                    "Device", key=cls.key("register_device_txt"), enable_events=True
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
                    key=cls.key("synch_device"),
                    use_ttk_buttons=True,
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text("Synch", key=cls.key("synch_device_txt"), enable_events=True),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text("Device", key=cls.key("synch_device_txt"), enable_events=True),
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
        return layout

    @classmethod
    def loop(
        cls, window: sg.Window, event: str, values: Dict[str, Any], loop_count = []
    ) -> bool:
        """Track user interaction with window."""
        
        if loop_count == []:
            conn = ServerConnection()
            try:
                conn_test = conn.test_connection()
            except Exception:
                app_config.cp["server_connection"] = {
                    "next_window": "EnrolmentMenuWindow"
                }
                window_dispatch.dispatch.open_window(
                    "ServerConnectionDetailsWindow"
                )
                return True
            if not conn_test:
                app_config.cp["server_connection"] = {
                    "next_window": "EnrolmentMenuWindow"
                }
                window_dispatch.dispatch.open_window("ServerConnectionDetailsWindow")
                return True
            loop_count.append("Done")

        if event in (cls.key("back"), cls.key("home")):
            window_dispatch.dispatch.open_window("HomeWindow")
            return True
        if event in (
            cls.key("staff_enrolment"),
            cls.key("staff_enrolment_txt"),
            cls.key("staff_enrolment_txt_2"),
        ):
            window_dispatch.dispatch.open_window("StaffEnrolmentWindow")
            return True
        if event in (
            cls.key("student_enrolment"),
            cls.key("student_enrolment_txt"),
            cls.key("student_enrolment_txt_2"),
        ):
            window_dispatch.dispatch.open_window("StudentEnrolmentWindow")
            return True
        if event in (
            cls.key("staff_enrolment_update"),
            cls.key("staff_enrolment_update_txt"),
            cls.key("staff_enrolment_update_txt_2"),
            cls.key("staff_enrolment_update_txt_3"),
        ):
            window_dispatch.dispatch.open_window("StaffEnrolmentUpdateIDSearchWindow")
            return True
        if event in (
            cls.key("student_enrolment_update"),
            cls.key("student_enrolment_update_txt"),
            cls.key("student_enrolment_update_txt_2"),
            cls.key("student_enrolment_update_txt_3"),
        ):
            window_dispatch.dispatch.open_window(
                "StudentEnrolmentUpdateIDSearchWindow"
            )
            return True
        if event in (
            cls.key("register_device"),
            cls.key("register_device_txt"),
            cls.key("register_device_txt_2"),
        ):
            window_dispatch.dispatch.open_window("NodeDeviceRegistrationWindow")
            return True
        if event in (cls.key("synch_device"), cls.key("synch_device_txt"), cls.key("synch_device_txt_2")):
            window_dispatch.dispatch.open_window("NodeDeviceSynchWindow")
            return True
        return True