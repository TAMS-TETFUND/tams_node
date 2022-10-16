import time
from typing import Any, Dict

import PySimpleGUI as sg

from app.basegui import BaseGUIWindow
import app.appconfigparser
import app.windowdispatch
from app.opmodes import OperationalMode
from .utils import send_staff_data

app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


class StaffPasswordSettingWindow(BaseGUIWindow):
    """This window is used for setting password for the new staff being
    enrolled."""

    @classmethod
    def window(cls) -> sg.Window:
        """Construct layout/appearance of window."""
        field_label_props = {"size": 25}
        layout = [
            [sg.Text("Set Password")],
            [sg.HorizontalSeparator()],
            [cls.message_display_field()],
            [
                sg.Text("Password:", **field_label_props),
                sg.Input(
                    key=cls.key("staff_password"),
                    expand_x=True,
                    enable_events=True,
                    password_char="*",
                    focus=True,
                ),
            ],
            [
                sg.Text("Confirm Password:", **field_label_props),
                sg.Input(
                    key=cls.key("staff_password_confirm"),
                    expand_x=True,
                    password_char="*",
                ),
            ],
            [
                sg.Button("Submit", key=cls.key("submit")),
                sg.Button("Cancel", key=cls.key("cancel"), **cls.cancel_button_kwargs()),
            ],
            cls.navigation_pane(
                next_icon="next_disabled", back_icon="back_disabled"
            ),
        ]
        return layout

    @classmethod
    def loop(
        cls, window: sg.Window, event: str, values: Dict[str, Any]
    ) -> bool:
        """Track user interaction with window"""
        if event in (cls.key("staff_password"), cls.key("staff_password_confirm")):
            if values[cls.key("staff_password")] != values[cls.key("staff_password_confirm")]:
                cls.display_message(
                    "Re-enter the same password in the 'Confirm Password' field",
                    window,
                )
            else:
                cls.display_message("", window)

        if event in (cls.key("cancel"), cls.key("submit")):
            new_staff = app_config.cp["new_staff"]

            if event == cls.key("submit"):
                password_fields = (
                    values[cls.key("staff_password")],
                    values[cls.key("staff_password_confirm")],
                )
                for field in password_fields:
                    if field in (None, ""):
                        cls.display_message(
                            "Enter password and confirmation", window
                        )
                        return True

                new_staff["password"] = values[cls.key("staff_password")]

                cls.next_window()
                return True

            if event in (cls.key("cancel"), cls.key("home")):
                confirm = sg.popup_yes_no(
                    "Cancel Staff registration?",
                    title="Cancel Registration",
                    keep_on_top=True,
                )
                if confirm == "Yes":
                    app_config.cp.remove_section("new_staff")
                    window_dispatch.dispatch.open_window("StaffEnrolmentWindow")
                    return True
                else:
                    return True
        return True

    @classmethod
    def next_window(cls):
        if not OperationalMode.check_camera():
            cls.popup_auto_close_warn("Camera not connected.")
            time.sleep(2)
            if not OperationalMode.check_fingerprint():
                cls.popup_auto_close_warn(
                    "Fingerprint scanner not connected"
                )
                send_staff_data()
                BaseGUIWindow.popup_auto_close_success(
                    "Staff enrolment saved with no biometric data."
                    "Staff will not be able to initiate attendance "
                    "until atleast biometric data is updated.",
                    duration=5)
                window_dispatch.dispatch.open_window("HomeWindow")
            else:
                window_dispatch.dispatch.open_window(
                    "StaffFingerprintEnrolmentWindow"
                )
        else:
            window_dispatch.dispatch.open_window(
                "StaffFaceEnrolmentWindow"
            )
        return

