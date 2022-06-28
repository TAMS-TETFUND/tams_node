import os
import time
import serial
import adafruit_fingerprint
from PIL import Image


"""
for bash script:
add the following lines to /boot/config.txt

#disable bluetooth
dtoverlay=disable-bt


then disavle related services
sudo systemctl disable bluetooth.service

then reboot
sudo reboot

There may be need to enable serial interface (even if it seems to be enabled)
sudo raspi-config>interfaces>serial interface>enable
then reboot again

for the particular fprint scanner used in testing:
    red wire > 3.3V
    black wire > gnd
    blue wire > pin 8
    yellow wire > pin 10




The fingerprint scanner appears to have one (1) image buffer slot,
2 char buffer  slots. THe number of available memory locations is variable
across different fingerprint scanners.
"""


class FingerprintScanner:
    SERIAL_PATH = "/dev/ttyAMA0"
    BAUD_RATE = 57600
    NOFINGER = adafruit_fingerprint.NOFINGER

    def __init__(self):
        self._error: str = None

        if self.scanner_present():
            self.uart = serial.Serial(
                self.SERIAL_PATH, baudrate=self.BAUD_RATE, timeout=1
            )
            self.finger = adafruit_fingerprint.Adafruit_Fingerprint(self.uart)
            # if not self.scanner_functional():
            #     self.finger = None
            #     raise RuntimeError("Fingerprint Scanner is not functional")

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
        if self.finger.count_templates() != adafruit_fingerprint.OK:
            self.error = "Failed to read templates"
            return False
        if self.finger.read_sysparam() != adafruit_fingerprint.OK:
            self.error = "Failed to get system parameters"
            return False
        return True

    def verify_match(self):
        i = self.fp_match()
        if i == adafruit_fingerprint.OK:
            return True
        else:
            return False

    def send_fpdata(self, fingerprint_template, slot, buffer="char"):
        return self.finger.send_fpdata(
            data=fingerprint_template, slot=slot, sensorbuffer=buffer
        )

    def fp_match(self):
        return self.finger.compare_templates()

    def fp_match_confidence(self):
        return self.finger.confidence

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
        # while True:
        i = self.finger.get_image()
        if i == adafruit_fingerprint.OK:
            return True
        if i == adafruit_fingerprint.NOFINGER:
            self.error = "Place finger on scanner"
            return False
        if i == adafruit_fingerprint.IMAGEFAIL:
            self.error = "Imaging error. Place finger again"
            return False

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
            return self.finger.get_fpdata(sensorbuffer, scanner_slot)
        else:
            return self.finger.get_fpdata(sensorbuffer)

    def image_2_tz(self, scanner_slot=1):
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
