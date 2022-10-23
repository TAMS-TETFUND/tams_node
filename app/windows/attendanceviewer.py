from typing import Any, Dict, List
from app.basegui import BaseGUIWindow

import PySimpleGUI as sg

import app.appconfigparser
import app.windowdispatch
from db.models import AttendanceRecord, AttendanceSession, RecordTypesChoices

app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


class AttendanceViewerWindow(BaseGUIWindow):
    """Display Attendance Collected for active event."""
    __slots__ = ()

    @classmethod
    def window(cls) -> List[Any]:
        current_attendance_session = app_config.cp["current_attendance_session"]
        if not app_config.cp.has_option(
            "current_attendance_session", "session"
        ):
            layout = []
        else:
            try:
                att_session_obj = AttendanceSession.objects.get(
                    id=current_attendance_session.get("session_id", fallback="")
                )
            except Exception:
                table_rows = []
            else:
                att_records = list(
                    AttendanceRecord.objects.filter(
                        attendance_session=att_session_obj
                    )
                    .prefetch_related("student")
                    .values_list(
                        "student__reg_number",
                        "student__last_name",
                        "student__first_name",
                        "check_in_by",
                        "record_type",
                    )
                )

                table_rows = []
                for idx, record in enumerate(att_records, 1):
                    table_rows.append(
                        [
                            idx,
                            "".join(
                                [
                                    record[1],
                                    " ",
                                    record[2][0],
                                    ". (",
                                    record[0],
                                    ")",
                                ]
                            ),
                            record[3].strftime("%H:%M"),
                            RecordTypesChoices(record[4]).label,
                        ]
                    )
            table_headings = ["S/N", "Name/ID", "Log Time", "Type"]
            layout = [
                [
                    sg.Push(),
                    sg.Text(
                        "%s Attendance List"
                        % current_attendance_session.get(
                            "course", fallback=""
                        ).split(" : ")[0]
                    ),
                    sg.Push(),
                ],
                [sg.HorizontalSeparator()],
                [
                    sg.Push(),
                    sg.Table(
                        table_rows,
                        headings=table_headings,
                        justification="center",
                    ),
                    sg.Push(),
                ],
                [sg.VPush()],
                cls.navigation_pane(next_icon="next_disabled"),
            ]
        return layout

    @classmethod
    def loop(
        cls, window: sg.Window, event: str, values: Dict[str, Any]
    ) -> bool:
        """Track user interaction with the window."""
        if event == cls.key("home"):
            confirm = sg.popup_yes_no(
                "Leaving attendance-taking. Do you wish to continue?",
                title="Go back?",
                keep_on_top=True,
            )
            if confirm == "Yes":
                window_dispatch.dispatch.open_window("HomeWindow")
            return True
        if event == cls.key("back"):
            window_dispatch.dispatch.open_window(
                "AttendanceSessionLandingWindow"
            )
            return True
        return True
