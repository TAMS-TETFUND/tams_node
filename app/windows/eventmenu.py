import PySimpleGUI as sg
from app.basegui import BaseGUIWindow
import app.appconfigparser
import app.windowdispatch


app_config = app.appconfigparser.AppConfigParser()
window_dispatch = app.windowdispatch.WindowDispatch()


class EventMenuWindow(BaseGUIWindow):
    """
    A window which presents options for the user to choose the
    event type for the attendance session.
    """

    @classmethod
    def window(cls):
        column1 = [
            [
                sg.Push(),
                sg.Button(
                    image_data=cls.get_icon("lecture"),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="lecture",
                    use_ttk_buttons=True,
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text("Lecture", key="lecture_txt", enable_events=True),
                sg.Push(),
            ],
        ]

        column2 = [
            [
                sg.Push(),
                sg.Button(
                    image_data=cls.get_icon("lab"),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="lab",
                    use_ttk_buttons=True,
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text("Lab", key="lab_txt", enable_events=True),
                sg.Push(),
            ],
        ]

        column3 = [
            [
                sg.Push(),
                sg.Button(
                    image_data=cls.get_icon("test_script"),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="quiz",
                    use_ttk_buttons=True,
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text("Quiz", key="quiz_txt", enable_events=True),
                sg.Push(),
            ],
        ]

        column4 = [
            [
                sg.Push(),
                sg.Button(
                    image_data=cls.get_icon("graduation_cap"),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="examination",
                    use_ttk_buttons=True,
                ),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Text(
                    "Examination", key="examination_txt", enable_events=True
                ),
                sg.Push(),
            ],
        ]

        layout = [
            [
                sg.Push(),
                sg.Text("Take Attendance for:", font="Helvetica 20"),
                sg.Push(),
            ],
            [sg.HorizontalSeparator()],
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
            [sg.HorizontalSeparator()],
            cls.navigation_pane(next_icon="next_disabled"),
        ]
        window = sg.Window("Event Menu", layout, **cls.window_init_dict())
        return window

    @classmethod
    def loop(cls, window, event, values):
        if event in (sg.WIN_CLOSED, "back", "cancel", "home"):
            window_dispatch.dispatch.open_window("HomeWindow")
        if event in (
                "lecture",
                "examination",
                "lab",
                "quiz",
                "lecture_txt",
                "examination_txt",
                "lab_txt",
                "quiz_txt",
        ):
            event = event.split("_")[0]
            app_config.cp["new_event"] = {}
            app_config.cp["new_event"]["type"] = event
            app_config.cp["new_event"]["recurring"] = "False"
            if event in ("lecture", "lab"):
                recurring = sg.popup_yes_no(
                    f"Is this {event} a weekly activity?",
                    title="Event detail",
                    keep_on_top=True,
                )
                if recurring == "Yes":
                    app_config.cp["new_event"]["recurring"] = "True"

            window_dispatch.dispatch.open_window("AcademicSessionDetailsWindow")
        return True