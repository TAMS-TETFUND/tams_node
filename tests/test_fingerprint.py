from unittest.mock import Mock, patch
from app.fingerprint import FingerprintScanner

@patch('app.fingerprint.FingerprintScanner', **{'scanner_present.return_value':False})
def test_fingerprint_scanner_init(fp_scanner):
    # fp_scanner.scanner_present.return_value = False
    assert fp_scanner.finger == None