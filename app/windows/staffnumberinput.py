from typing import Any, Dict, Optional
import PySimpleGUI as sg

from app.basegui import BaseGUIWindow
from app.gui_utils import StaffBiometricVerificationRouterMixin, ValidationMixin
import app.appconfigparser
import app.windowdispatch
from db.models import Staff

app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


class StaffNumberInputWindow(
    ValidationMixin, StaffBiometricVerificationRouterMixin, BaseGUIWindow
):
    """This window will provide an on-screen keypad for staff to enter
    their staff id/number by button clicks."""

    @classmethod
    def window(cls) -> sg.Window:
        """Construct layout/appearance of window."""
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
    def loop(cls, window: sg.Window, event: str, values: Dict[str, Any]) -> bool:
        """Track user interaction with window."""
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
    def validate(cls, values: Dict[str, Any], window: sg.Window) -> Optional[bool]:
        """Validate values supplied by user in the window input fields."""
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
    def resize_column(window: sg.Window) -> None:
        """Refresh GUI when adding/removing message display field."""
        window.refresh()
        window["main_column"].contents_changed()

    @classmethod
    def process_staff(cls, staff: Staff) -> None:
        """Process staff info for update."""
        app_config.cp["tmp_staff"] = app_config.cp.dict_vals_to_str(
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
    def back_nav_key_handler() -> None:
        """Handle user pressing back button in nav pane."""
        window_dispatch.dispatch.open_window("HomeWindow")
        sg.popup(
            "Event details saved.",
            title="Event saved",
            keep_on_top=True,
        )
        return
