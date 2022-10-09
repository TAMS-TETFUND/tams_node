import os
import time
from typing import List

import serial
import adafruit_fingerprint
import numpy as np
from PIL import Image


"""
for bash script:
add the following lines to /boot/config.txt

#disable bluetooth
dtoverlay=disable-bt


then disable related services
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
    """The Fingerprint scanner class.
    
    Responsible for interfacing application to fingerprint scanners.
    Currently supports only fingerprint scanners that can work with
    the adafruit_fingerprint library. Should work when fingerprint
    scanner is connected via a serial connection and when a 
    Serial-to-USB converter is used to connect the fingerprint scanner.
    """
    SERIAL_PATH = "/dev/ttyAMA0"
    BAUD_RATE = 57600
    NOFINGER = adafruit_fingerprint.NOFINGER

    def __init__(self) -> None:
        self._error: str = ""

        if self.scanner_present():
            self.uart = serial.Serial(
                self.SERIAL_PATH, baudrate=self.BAUD_RATE, timeout=1
            )
            self.finger = adafruit_fingerprint.Adafruit_Fingerprint(self.uart)
            
        else:
            self.finger = None
            raise RuntimeError("Fingerprint scanner connection not detected")

    @property
    def error(self) -> str:
        """Property for holding scanner errors."""
        return self._error

    @error.setter
    def error(self, value: str) -> None:
        """Setter for the error property."""
        self._error = value

    def scanner_present(self) -> bool:
        """Check if fingerprint scanner is connected."""
        if os.path.exists(self.SERIAL_PATH):
            return True
        else:
            return False

    def scanner_functional(self) -> bool:
        """Confirm scanner is compatible with adafruit fingerprint library."""
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

    def verify_match(self) -> bool:
        """Interprete return value of the fp_match method."""
        i = self.fp_match()
        if i == adafruit_fingerprint.OK:
            return True
        else:
            return False

    def send_fpdata(self, fingerprint_template: List[int], slot: int, buffer: str="char") -> int:
        """Load fingerprint template into scanner buffer.
        
        Returns a code of success/failure of the send operation.
        Typically adafruit_fingerprint.OK would indicate a success."""
        return self.finger.send_fpdata(
            data=fingerprint_template, slot=slot, sensorbuffer=buffer
        )

    def fp_match(self) -> int:
        """Compare the fingerprint templates in char buffers 1 and 2.
        
        Returns a code of success/failure of the match operation.
        Stores the confidence score in self.fp_match_confidence."""
        return self.finger.compare_templates()

    def fp_match_confidence(self) -> float:
        """Return confidence level of fingerprint match operation."""
        return self.finger.confidence

    def create_model(self) -> bool:
        """Generate a fingerprint template from scanner buffer content.
        
        Returns:
            True if create operation succeeds.
            False if create operation fails.
        """
        i = self.finger.create_model()
        if i == adafruit_fingerprint.OK:
            return True
        else:
            if i == adafruit_fingerprint.ENROLLMISMATCH:
                self.error = "Prints did not match"
            else:
                self.error = "Other error"
            return False

    def fp_capture(self) -> bool:
        """Capture fingerprint placed on the scanner.
        
        Returns: 
            True if capture operation was successful.
            False if capture operation fails.
        """
        fp_scan_end_time = time.time() + 1
        while time.time() < fp_scan_end_time:
            i = self.finger.get_image()
            if i == adafruit_fingerprint.OK:
                return True

        if i == adafruit_fingerprint.NOFINGER:
            self.error = "Place finger on scanner"
        if i == adafruit_fingerprint.IMAGEFAIL:
            self.error = "Imaging error. Place finger again"
        return False

    def fp_continuous_capture(self) -> None:
        """Read the fingerprint sensor till a valid fingerprint image is obtained."""
        while True:
            i = self.finger.get_image()
            if i == adafruit_fingerprint.OK:
                break

    def store_template_in_file(self, filename: str) -> bool:
        """Store generated fingerprint template in a file.
        
        Returns:
            True if save operation is successful.
            False if save operation fails."""
        img = Image.new("L", (256, 288), "white")
        pixel_data = img.load()
        mask = 0b00001111
        result: List[int] = self.get_fpdata(sensorbuffer="image")

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

    def get_fpdata(self, sensorbuffer: str = "char", scanner_slot: int = 1) -> List[int]:
        """Read fingerprint data from the scanner buffer.
        
        Fingerprint scanners supported by the adafruit_fingerprint 
        library typically have 2 char sensor buffers and an image 
        sensor buffer. By default, this method will attempt to access
        the char sensor buffer. 
        These adafruit-compatible scanners
        typically also have 2 slots. By default, this method will attempt
        to access char buffer slot 1. 
        
        Returns a code indicating success/failure of read operation.
        adafruit_fingerprint.OK would typically indicate operation success.
        """
        if sensorbuffer == "char":
            return self.finger.get_fpdata(sensorbuffer, scanner_slot)
        else:
            return self.finger.get_fpdata(sensorbuffer)

    def image_2_tz(self, scanner_slot: int = 1) -> bool:
        """Convert image to fingerprint template."""
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

    def get_image(self) -> int:
        """Requests the scanner to take an image and store it in memory.
        
        Returns a code that indicates success/failure of operation."""
        return self.finger.get_image()