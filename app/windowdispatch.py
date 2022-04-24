from collections import UserDict


class WindowDispatch(UserDict):

    def __init__(self, *args, **kwargs):
        super(WindowDispatch, self).__init__(*args, **kwargs)

    def open_window(self, window_class, on_seperate_window=False):
        self.update({window_class.__name__: window_class.window()})

        if not on_seperate_window:
            open_windows = self.copy()
            for key in open_windows.keys():
                if key != window_class.__name__:
                    self.close_window(key)
    
    def close_window(self, window_name):
        return self.pop(window_name).close()

    def find_window(self, window_object):
        return next((k for k, v in self.items() if v == window_object), None)

    @staticmethod
    def window_loop(window_name, window, event, values):
        return eval(f"{window_name}.loop(window, event, values)")