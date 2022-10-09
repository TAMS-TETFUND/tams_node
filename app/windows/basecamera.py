from typing import Any, List, Dict, Optional
import PySimpleGUI as sg

import app.windowdispatch
from app.barcode import Barcode
from app.basegui import BaseGUIWindow
from app.camera2 import Camera
from app.camerafacerec import CamFaceRec
from app.opmodes import OperationalMode


window_dispatch = app.windowdispatch.WindowDispatch()


class CameraWindow(BaseGUIWindow):
    """A base class. This window provides the general camera window
    layout."""

    @classmethod
    def window(cls) -> sg.Window:
        """Construct layout/appearance of window."""
        layout = [
            [sg.Push(), sg.Column(cls.window_title()), sg.Push()],
            [
                sg.Push(),
                sg.Image(filename="", key="image_display", enable_events=True),
                sg.Push(),
            ],
            [
                sg.Push(),
                sg.Button(
                    image_data=cls.get_icon("camera", 0.6),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="capture",
                    use_ttk_buttons=True,
                ),
                cls.get_fingerprint_button(),
                cls.get_keyboard_button(),
                sg.Button(
                    image_data=cls.get_icon("cancel", 0.6),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="cancel",
                    use_ttk_buttons=True,
                ),
                sg.Push(),
            ],
        ]
        window = sg.Window("Camera", layout, **cls.window_init_dict())
        return window

    @classmethod
    def get_keyboard_button(cls) -> Any:
        """Return keyboard button for GUI window layout.
        
        Will be hidden when a keyboard window is open. Will be
        visible if a barcode window is open."""
        if issubclass(cls, BarcodeCameraWindow):
            return sg.pin(
                sg.Button(
                    image_data=cls.get_icon("keyboard", 0.6),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="keyboard",
                    visible=True,
                    use_ttk_buttons=True,
                )
            )
        else:
            return sg.pin(
                sg.Button(
                    image_data=cls.get_icon("keyboard", 0.6),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="keyboard",
                    visible=False,
                    use_ttk_buttons=True,
                )
            )

    @classmethod
    def get_fingerprint_button(cls) -> Any:
        """Return fingerprint button for GUI window layout.
        
        Will be visible if a verification window is open."""
        if "verification" in cls.__name__.lower():
            return sg.pin(
                sg.Button(
                    image_data=cls.get_icon("fingerprint", 0.6),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="fingerprint",
                    visible=True,
                    use_ttk_buttons=True,
                )
            )
        else:
            return sg.pin(
                sg.Button(
                    image_data=cls.get_icon("fingerprint", 0.6),
                    button_color=cls.ICON_BUTTON_COLOR,
                    key="fingerprint",
                    visible=False,
                    disabled=True,
                    use_ttk_buttons=True,
                )
            )

    @classmethod
    def window_title(cls) -> Optional[List[Any]]:
        """Add title to GUI window."""
        raise NotImplementedError


class FaceCameraWindow(CameraWindow):
    """This is a base class. Implements facial recognition with camera."""

    @classmethod
    def loop(cls, window: sg.Window, event: str, values: Dict[str, Any]) -> bool:
        """Track user interaction with window."""
        with CamFaceRec() as cam_facerec:
            while True:
                event, values = window.read(timeout=20)

                if event == "cancel":
                    cls.cancel_camera()
                    return True

                if event == "fingerprint":
                    if not OperationalMode.check_fingerprint():
                        cls.popup_auto_close_error(
                            "Fingerprint scanner not connected"
                        )
                    else:
                        cls.open_fingerprint()
                    return True

                if (
                    event in ("capture", "image_display")
                    and cam_facerec.deque_not_empty()
                ):
                    cam_facerec.load_facerec_attrs()
                    if cam_facerec.face_count > 1:
                        cls.popup_auto_close_error(
                            "Multiple faces detected",
                        )
                    elif cam_facerec.face_count == 0:
                        cls.popup_auto_close_error(
                            "Bring face closer to camera"
                        )

                    if cam_facerec.face_count == 1:
                        captured_encodings = cam_facerec.face_encodings()
                        cls.process_image(captured_encodings, window)
                        return True

                window["image_display"].update(
                    data=Camera.feed_to_bytes(cam_facerec.img_bbox)
                )

    @classmethod
    def process_image(cls, captured_face_encodings: Any, window: sg.Window) -> None:
        """Process detected face."""
        raise NotImplementedError

    @staticmethod
    def cancel_camera() -> None:
        """"Logic for when cancel button is pressed in camera window."""
        raise NotImplementedError

    @staticmethod
    def open_fingerprint() -> None:
        """Open window when fingerprint button is pressed in camera window."""
        raise NotImplementedError

    @classmethod
    def window_title(cls) -> List[Any]:
        """Title of GUI window."""
        return [
            [
                sg.Push(),
                sg.Image(data=cls.get_icon("face_scanner", 0.4)),
                sg.Text("Position Face", font=("Helvetica", 14)),
                sg.Push(),
            ]
        ]


class BarcodeCameraWindow(CameraWindow):
    """Base class. This implements Barcode decoding with camera."""

    @classmethod
    def loop(cls, window: sg.Window, event: str, values: Dict[str, Any]) -> bool:
        """Track user interaction with window"""
        with Camera() as cam:
            while True:
                img = cam.feed()
                barcodes = Barcode.decode_image(img)
                event, values = window.read(timeout=20)
                if event in ("capture", "image_display"):
                    if len(barcodes) == 0:
                        cls.popup_auto_close_error("No ID detected")
                    else:
                        cls.process_barcode(
                            Barcode.decode_barcode(barcodes[0]), window
                        )
                        return True

                if event == "keyboard":
                    cls.launch_keypad()
                    return True

                if event == "cancel":
                    cls.cancel_camera()
                    return True

                if len(barcodes) > 0:
                    cls.process_barcode(
                        Barcode.decode_barcode(barcodes[0]), window
                    )
                    return True
                img_bnw = cam.image_to_grayscale(img)
                window["image_display"].update(data=cam.feed_to_bytes(img_bnw))
        return True

    @classmethod
    def process_barcode(cls, identification_num: str, window: sg.Window) -> None:
        """Process a decoded identification number."""
        raise NotImplementedError

    @classmethod
    def launch_keypad(cls) -> None:
        """Window to open when the keyboard icon is pressed in GUI window."""
        raise NotImplementedError

    @staticmethod
    def cancel_camera() -> None:
        """Window to open when the cancel icon is pressed in GUI window."""
        window_dispatch.dispatch.open_window("HomeWindow")

    @classmethod
    def window_title(cls) -> List[Any]:
        """Title of GUI window."""
        return [
            [
                sg.Push(),
                sg.Image(data=cls.get_icon("qr_code", 0.3)),
                sg.Text("Present ID Card", font=("Helvetica", 14)),
                sg.Push(),
            ],
        ]
