from enum import Enum

from app.camera2 import Camera
from app.fingerprint import FingerprintScanner


class OpModes(Enum):
    """Enum of available biometric verification modes.
    
    Values:
        Opmodes.FINGERPRINT: Only a fingerprint scanner is present
        Opmodes.FACE: Only a camera is present
        Opmodes.BIMODAL: Both camera and fingerprint scanner present.
    """
    FINGERPRINT = 1
    FACE = 2
    BIMODAL = 100


class OperationalMode:
    """A helper class to set the available biometric
    verification modes in the application configparser file.
    
    If only a camera connection is detected, the app's operational mode
    would be FACE mode. If only a fingerprint scanner connection is 
    detected, the app's operational mode would be FINGERPRINT mode. If 
    both fingerprint scanner and camera is detected, the operational mode
    would be BIMODAL.
    """

    @classmethod
    def check_all_modes(cls) -> int:
        """Check for a usable Camera and fingerprint scanner on device.
        
        Returns a value fron the OpModes (app.opmodes.OpModes) enum 
        corresponding to the biometric verification devices found
        on the node device (computer).
        """
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
    def check_fingerprint() -> bool:
        """Check if a fingerprint scanner is available.
        
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
    def check_camera() -> bool:
        """Check if a camera is available.

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
