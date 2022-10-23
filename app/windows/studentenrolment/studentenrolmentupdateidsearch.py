from typing import Any, Dict, List

import PySimpleGUI as sg

from app.windows.studentregnuminput import StudentRegNumInputWindow
import app.appconfigparser
import app.windowdispatch
from db.models import Student


app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


class StudentEnrolmentUpdateIDSearchWindow(StudentRegNumInputWindow):
    """Window for finding student by reg number for bio data update."""
    __slots__ = ()

    @classmethod
    def window(cls) -> List[Any]:
        """Construct layout/appearance of window."""
        return super().window()

    @classmethod
    def loop(
        cls, window: sg.Window, event: str, values: Dict[str, Any]
    ) -> bool:
        """Track user interaction with window."""
        return super().loop(window, event, values)

    @classmethod
    def process_student(cls, student: Student, window: sg.Window) -> None:
        """Process staff info for update."""
        app_config.cp["new_student"] = app_config.cp.dict_vals_to_str(
            student.values(
                "reg_number",
                "first_name",
                "last_name",
                "other_names",
                "level_of_study",
                "possible_grad_yr",
                "sex",
                "department__name",
                "department__faculty__name",
                "face_encodings",
                "fingerprint_template",
            ).first()
        )
        window_dispatch.dispatch.open_window("StudentEnrolmentUpdateWindow")
        return

    @staticmethod
    def back_nav_key_handler() -> None:
        """Handle user pressing back button in nav pane."""
        window_dispatch.dispatch.open_window("HomeWindow")
        return
