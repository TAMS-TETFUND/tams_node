from typing import Any, Dict, List

import PySimpleGUI as sg

from app.windows.staffnumberinput import StaffNumberInputWindow
import app.appconfigparser
import app.windowdispatch
from db.models import Staff

app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


class StaffEnrolmentUpdateIDSearchWindow(StaffNumberInputWindow):
    """Window for finding staff by id for bio data update."""

    @classmethod
    def window(cls) -> List[Any]:
        """Construct layout/appearance of window."""
        return super().window()
    
    @classmethod
    def loop(cls, window: sg.Window, event: str, values: Dict[str, Any]) -> bool:
        """Track user interaction with window."""
        return super().loop(window, event, values)

    @classmethod
    def process_staff(cls, staff: Staff) -> None:
        """Process staff info for update."""
        app_config.cp["edit_staff"] = app_config.cp.dict_vals_to_str(
            staff.values(
                "staff_number",
                "first_name",
                "last_name",
                "other_names",
                "sex",
                "department__name",
                "department__faculty__name",
                "face_encodings",
                "fingerprint_template",
            ).first()
        )
        window_dispatch.dispatch.open_window("StaffEnrolmentUpdateWindow")
        return

    @staticmethod
    def back_nav_key_handler() -> None:
        """Handle user pressing back button in nav pane."""
        window_dispatch.dispatch.open_window("HomeWindow")
        return

