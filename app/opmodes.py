from enum import Enum

from app.camera2 import Camera
from app.fingerprint import FingerprintScanner


class OpModes(Enum):
    FINGERPRINT = 1
    FACE = 2
    BIMODAL = 100

class OperationalMode:
    """"A helper class to set the available biometric 
    verification modes in the application configparser file."""
    @classmethod
    def check_all_modes(cls):
        cam_present = cls.check_camera()
        fp_present = cls.check_fingerprint()

        if cam_present and fp_present:
            return OpModes.BIMODAL.value
        elif cam_present and not fp_present:
            return OpModes.FACE.value
        elif not cam_present and fp_present:
            return OpModes.FINGERPRINT.value
        else:
            raise RuntimeError("No Biometric verification device found")

    @staticmethod
    def check_fingerprint():
        """Method to check if fingerprint scanner is available
        Returns:
            True: if available
            False if unavailable
        """
        try:
            fp = FingerprintScanner()
        except Exception:
            return False
        else:
            return True

    @staticmethod
    def check_camera():
        """Method to check if camera is available
        Returns:
            True: if available
            False: if unavailable
        """
        try:
            cam = Camera()
        
        except Exception:
            return False

        else:
            cam.stop()
            return True