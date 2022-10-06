from datetime import datetime, timedelta

import PySimpleGUI as sg
from django.utils import timezone
from app.basegui import BaseGUIWindow
import app.appconfigparser
import app.windowdispatch
from app.nodedeviceinit import DeviceRegistration

from db.models import AttendanceSession, AttendanceSessionStatusChoices

app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


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

        window = sg.Window(
            "Home Window",
            layout,
            return_keyboard_events=True,
            **cls.window_init_dict(),
        )
        return window

    @classmethod
    def loop(cls, window, event, values):
        if event in ("new_event", "new_event_txt"):
            if not DeviceRegistration.is_registered():
                cls.popup_auto_close_warn(
                    "Device setup incomplete. Contact admin"
                )
                return True
            window_dispatch.dispatch.open_window("EventMenuWindow")
        if event in (
                "continue_attendance",
                "continue_attendance_txt",
                "continue_attendance_txt_2",
        ):
            if app_config.cp.has_section("current_attendance_session"):
                current_att_session = app_config.cp["current_attendance_session"]
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
                        cls.popup_auto_close_error(
                            "Invalid session. Create new session."
                        )
                        app_config.cp.remove_section("current_attendance_session")
                        app_config.cp.remove_section("failed_attempts")
                        app_config.cp.remove_section("tmp_student")
                        app_config.cp.remove_section("tmp_staff")
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
                    app_config.cp.remove_section("current_attendance_session")
                    app_config.cp.remove_section("failed_attempts")
                    app_config.cp.remove_section("tmp_student")
                    app_config.cp.remove_section("tmp_staff")
                    return True

                if app_config.cp.has_option(
                        "current_attendance_session", "initiator_id"
                ):
                    window_dispatch.dispatch.open_window("ActiveEventSummaryWindow")
                else:
                    app_config.cp["new_event"] = app_config.cp[
                        "current_attendance_session"
                    ]
                    window_dispatch.dispatch.open_window("NewEventSummaryWindow")
            else:
                sg.popup(
                    "No active attendance-taking session found.",
                    title="No Event",
                    keep_on_top=True,
                )
        if event == "settings":
            window_dispatch.dispatch.open_window("EnrolmentMenuWindow")
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