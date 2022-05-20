import os
import time

import serial
import adafruit_fingerprint
from PIL import Image


class FingerprintScanner:
    SERIAL_PATH = "/dev/ttyAMA0"
    BAUD_RATE = 57600

    def __init__(self):
        self._error: str = None

        if self.scanner_present():
            self.uart = serial.Serial(
                self.SERIAL_PATH, baudrate=self.BAUD_RATE, timeout=1
            )
            self.finger = adafruit_fingerprint.Adafruit_Fingerprint(self.uart)
            if not self.scanner_functional():
                self.finger = None
                raise RuntimeError("Fingerprint Scanner is not functional")

        else:
            self.finger = None
            raise RuntimeError("Fingerprint scanner connection not detected")

    @property
    def error(self):
        return self._error

    @error.setter
    def error(self, value):
        self._error = value

    def scanner_present(self):
        if os.path.exists(self.SERIAL_PATH):
            return True
        else:
            return False

    def scanner_functional(self):
        if self.finger.read_templates() != adafruit_fingerprint.OK:
            self.error = "Failed to read templates"
            return False
        elif self.finger.count_templates() != adafruit_fingerprint.OK:
            self.error = "Failed to read templates"
            return False
        elif self.finger.read_sysparam() != adafruit_fingerprint.OK:
            self.error = "Failed to get system parameters"
            return False
        else:
            return True

    def verify(self, known_fingerprint_template):
        if not self.capture_fingerprint_image():
            return False
        self.finger.send_fpdata(known_fingerprint_template, "char", 2)

        i = self.finger.compare_templates()
        if i == adafruit_fingerprint.OK:
            return True
        else:
            return False

    def capture_fingerprint_image(self, scanner_slot=1):
        self.fp_capture()
        i = self.finger.image_2_tz(scanner_slot)
        if i == adafruit_fingerprint.OK:
            return True
        else:
            if i == adafruit_fingerprint.IMAGEMESS:
                self.error = "Image too messy"
            elif i == adafruit_fingerprint.FEATUREFAIL:
                self.error = "Could not identify features"
            elif i == adafruit_fingerprint.INVALIDIMAGE:
                self.error = "Image invalid"
            else:
                self.error = "Other error"
            return False

    def create_model(self):
        i = self.finger.create_model()
        if i == adafruit_fingerprint.OK:
            return True
        else:
            if i == adafruit_fingerprint.ENROLLMISMATCH:
                self.error = "Prints did not match"
            else:
                self.error = "Other error"
            return False

    def fp_capture(self):
        while self.finger.get_image() != adafruit_fingerprint.OK:
            pass

    def store_template_in_file(self, filename):
        img = Image.new("L", (256, 288), "white")
        pixel_data = img.load()
        mask = 0b00001111
        result = self.get_fpdata(sensorbuffer="image")

        x = 0
        y = 0

        for i in range(len(result)):
            pixel_data[x, y] = (int(result[i]) >> 4) * 17
            x += 1
            pixel_data[x, y] = (int(result[i]) & mask) * 17
            if x == 255:
                x = 0
                y += 1
            else:
                x += 1

        try:
            img.save(f"{filename}/{filename}.png")
        except Exception:
            self.error = "Problem saving image"
            return False
        else:
            return True

    def get_fpdata(self, sensorbuffer="char", scanner_slot=1):
        if sensorbuffer == "char":
            return self.get_fpdata(sensorbuffer, scanner_slot)
        else:
            return self.get_fpdata(sensorbuffer)

    def image_2_tz(self, scanner_slot):
        return self.finger.image_2_tz(scanner_slot)

    def finger_detected(self, scanner_slot):
        if (
            self.finger.image_2_tz(scanner_slot)
            == adafruit_fingerprint.NOFINGER
        ):
            return False
        else:
            return True

    def get_image(self):
        return self.finger.get_image()

    def enrol(self, scanner_slot):
        pass
