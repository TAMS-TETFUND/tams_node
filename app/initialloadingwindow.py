import PySimpleGUI as sg

from app.basegui import BaseGUIWindow


class LoadingWindow(BaseGUIWindow):
    ring_lines = b"R0lGODlh2ADYAKIHAPj4+ODg4MnJyaysrIuLi2NjYzk5Of///yH/C05FVFNDQVBFMi4wAwEAAAAh/wtYTVAgRGF0YVhNUDw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuMC1jMDYwIDYxLjEzNDc3NywgMjAxMC8wMi8xMi0xNzozMjowMCAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENTNSBNYWNpbnRvc2giIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6Q0NFQTZFMUU5QzBDMTFFMkFFNDdDRTVDRTJCRUM3RTIiIHhtcE1NOkRvY3VtZW50SUQ9InhtcC5kaWQ6Q0NFQTZFMUY5QzBDMTFFMkFFNDdDRTVDRTJCRUM3RTIiPiA8eG1wTU06RGVyaXZlZEZyb20gc3RSZWY6aW5zdGFuY2VJRD0ieG1wLmlpZDpDQ0VBNkUxQzlDMEMxMUUyQUU0N0NFNUNFMkJFQzdFMiIgc3RSZWY6ZG9jdW1lbnRJRD0ieG1wLmRpZDpDQ0VBNkUxRDlDMEMxMUUyQUU0N0NFNUNFMkJFQzdFMiIvPiA8L3JkZjpEZXNjcmlwdGlvbj4gPC9yZGY6UkRGPiA8L3g6eG1wbWV0YT4gPD94cGFja2V0IGVuZD0iciI/PgH//v38+/r5+Pf29fTz8vHw7+7t7Ovq6ejn5uXk4+Lh4N/e3dzb2tnY19bV1NPS0dDP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"

    @classmethod
    def window(cls):
        return sg.Window(
            title="Loading window",
            no_titlebar=True,
            layout=[
                [
                    sg.Image(
                        data=cls.ring_lines,
                        enable_events=True,
                        key="loading_image",
                    )
                ],
                [sg.Push(), sg.Text("Loading..."), sg.Push()],
            ],
            margins=(0, 0),
            finalize=True,
        )

    @classmethod
    def loop(cls, window, event, values):
        pass
