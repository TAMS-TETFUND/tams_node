from typing import Any, Dict, Optional
import PySimpleGUI as sg

from app.basegui import BaseGUIWindow
import app.appconfigparser
import app.windowdispatch
from app.gui_utils import (
    ValidationMixin,
    StudentBiometricVerificationRouterMixin,
)
from db.models import AttendanceRecord, Student, RecordTypesChoices

app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


class StudentRegNumInputWindow(
    ValidationMixin, StudentBiometricVerificationRouterMixin, BaseGUIWindow
):
    """Window provides an interface for students to enter their registration
    numbers by button clicks."""

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
    def loop(
        cls, window: sg.Window, event: str, values: Dict[str, Any]
    ) -> bool:
        """Track user interaction with window."""
        if event == "back":
            cls.back_nav_key_handler()
            return True
        if event == "home":
            window_dispatch.dispatch.open_window("HomeWindow")
            return True

        keys_pressed = None
        if event in "0123456789/":
            keys_pressed = values["reg_num_input"]
            keys_pressed += event
            window["reg_num_input"].update(keys_pressed)
            return True

        elif event == "clear":
            window["reg_num_input"].update("")
            cls.hide_message_display_field(window)
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
    def process_student(cls, student: Student, window: sg.Window) -> None:
        """Process staff info for update."""
        app_config.cp["tmp_student"] = app_config.cp.dict_vals_to_str(
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

        tmp_student = app_config.cp["tmp_student"]
        if AttendanceRecord.objects.filter(
            attendance_session_id=app_config.cp.get(
                "current_attendance_session", "session_id"
            ),
            student_id=tmp_student["reg_number"],
        ).exists():
            record = AttendanceRecord.objects.get(
                student_id=tmp_student["reg_number"],
                attendance_session_id=app_config.cp.get(
                    "current_attendance_session", "session_id"
                ),
            )
            # check if the student is signed out and prevent re-entry
            if record.record_type == RecordTypesChoices.SIGN_OUT:
                cls.display_message("Student already signed out!", window)
                cls.resize_column(window)
                return

            window_dispatch.dispatch.open_window("AttendanceSignOutWindow")
            return
        cls.student_verification_window()

    @classmethod
    def validate(
        cls, values: Dict[str, Any], window: sg.Window
    ) -> Optional[bool]:
        """Validate values supplied by user in the window input fields."""
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
    def resize_column(window: sg.Window) -> None:
        """Refresh GUI when adding/removing message display field."""
        window.refresh()
        window["main_column"].contents_changed()

    @staticmethod
    def back_nav_key_handler() -> None:
        """Handle user pressing back button in nav pane."""
        window_dispatch.dispatch.open_window("AttendanceSessionLandingWindow")
        return
