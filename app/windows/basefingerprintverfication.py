import time
from typing import Any, Dict, List

import PySimpleGUI as sg

from app.windows.basefingerprint import FingerprintGenericWindow
from app.fingerprint import FingerprintScanner
import app.windowdispatch


window_dispatch = app.windowdispatch.WindowDispatch()


class FingerprintEnrolmentWindow(FingerprintGenericWindow):
    """
    This class provides the loop method for capturing the fingerprint
    template for both staff and student enrolment.
    """

    @classmethod
    def loop(
        cls, window: sg.Window, event: str, values: Dict[str, Any]
    ) -> bool:
        """Track user interaction with window."""

        if event == cls.key("cancel"):
            cls.cancel_fp_enrolment()
            return True

        try:
            fp_scanner = FingerprintScanner()
        except RuntimeError as e:
            cls.popup_auto_close_error(e, duration=5)
            cls.post_process_enrolment_config()
            window_dispatch.dispatch.open_window("HomeWindow")
            return True

        for fingerimg in range(1, 3):
            if fingerimg == 1:
                cls.popup_auto_close_warn(
                    "Place your right thumb on fingerprint sensor...",
                    title="Info",
                )
            else:
                cls.popup_auto_close_warn(
                    "Place same finger again...", title="Info"
                )

            time.sleep(1)

            try:
                fp_scanner.fp_continuous_capture()
            except RuntimeError as e:
                cls.popup_auto_close_error(
                    "Connection to fingerprint scanner lost"
                )
                window_dispatch.dispatch.open_window("HomeWindow")
                return True

            if not fp_scanner.image_2_tz(fingerimg):
                cls.popup_auto_close_error(fp_scanner.error, duration=5)
                return True

            if fingerimg == 1:
                cls.popup_auto_close_warn("Remove finger...", title="Info")
                time.sleep(2)
                i = fp_scanner.get_image()
                while i != fp_scanner.NOFINGER:
                    i = fp_scanner.get_image()

        cls.display_message("Creating model...", window)
        if not fp_scanner.create_model():
            cls.popup_auto_close_error(fp_scanner.error)
            return True

        fingerprint_data = fp_scanner.get_fpdata(scanner_slot=1)
        cls.process_fingerprint(fingerprint_data)
        return True

    @classmethod
    def process_fingerprint(cls, fingerprint_data: List[int]) -> None:
        raise NotImplementedError

    @staticmethod
    def cancel_fp_enrolment() -> None:
        """Next window when user presses cancel button on GUI window."""
        raise NotImplementedError

    @staticmethod
    def post_process_enrolment_config() -> None:
        """Method to call when staff registration data has been validated.

        Typically contains logic for synching collected data to the server.
        """
        raise NotImplementedError
