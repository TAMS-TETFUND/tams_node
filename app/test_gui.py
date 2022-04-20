import PySimpleGUI as sg

window_dispatch = {
    "home_window": None,
    "another_win": None
}

class BaseGUIWindow:
    SCREEN_SIZE = (480, 320)

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
            pass        
        return True

class HomeWindow(BaseGUIWindow):

    @classmethod
    def make_window(cls):
        layout = [
            [sg.VPush()],
            [
                sg.Push(),
                sg.Text("This is the home window:"),
                sg.Push()    
            ],
            [sg.Text("Welcome to all things good")],
            [sg.Button("New Event Button", key="new_event")],
            [sg.Button("Quit", key="quit")]
        ]

        window = sg.Window(
            "Home Window",
            layout,
            size=cls.SCREEN_SIZE,
            finalize=True,
        )
        return window
    
    @staticmethod
    def window_loop(window, event, values):
        if event == "new_event":
            global window_dispatch
            window_dispatch['another_win'] = AnotherWindow.make_window()
            window_dispatch['home_win'].close()
            window_dispatch['home_win'] = None

        if event == "quit":
            return HomeWindow.confirm_exit()
        return True


class AnotherWindow(BaseGUIWindow):
    @classmethod
    def make_window(cls):
        layout = [
            [sg.VPush()],
            [
                sg.Push(),
                sg.Text("This is another window:"),
                sg.Push()    
            ],
            [sg.Text("Classes may work out after all")],
            [sg.Button("Quit", key="quit")],
            [sg.Button("New Event Button", key="new_event")],
        ]

        window = sg.Window(
            "Another Window",
            layout,
            size=cls.SCREEN_SIZE,
            finalize=True,
        )
        return window
    
    @staticmethod
    def window_loop(window, event, values):
        print("entering another window loop")
        if event == "new_event":
            global window_dispatch
            window_dispatch['home_win'] = HomeWindow.make_window()
            window_dispatch['another_win'].close()
            window_dispatch['another_win'] = None
            
        if event == "quit":
             return AnotherWindow.confirm_exit()
        return True


def main():
    global window_dispatch
    window_dispatch['home_win'] = HomeWindow.make_window()
    while True:
        window, event, values = sg.read_all_windows()
        window_loop_exit_code = True
        if window == window_dispatch['home_win']:
            window_loop_exit_code = HomeWindow.window_loop(window, event, values)
        if window == window_dispatch['another_win']:
            window_loop_exit_code = AnotherWindow.window_loop(window, event, values)
        if not window_loop_exit_code:
            break
        if event == sg.WIN_CLOSED:
            break
    window.close()


if __name__ == "__main__":
    main()