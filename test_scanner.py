from scanner import luhn_check, pps_check, iban_check, classify


def test_valid_card_passes_luhn():
    assert luhn_check("4111 1111 1111 1111") == True


def test_wrong_card_fails_luhn():
    assert luhn_check("4111 1111 1111 1112") == False


def test_pps_check_pass():
    assert pps_check("1234567T") == True


def test_pps_check_fail():
    assert pps_check("1234567G") == False


def test_valid_iban_passes():
    assert iban_check("IE29 AIBK 9311 5212 3456 78") == True


def test_iban_typo_fails():
    assert iban_check("IE29 AIBK 9311 5212 3456 79") == False


def test_classify_error_is_not_scanned():
    assert classify({"error": "Permission denied"}) == "Not scanned"


def test_classify_card_and_email_is_confidential():
    findings = {"cards": ["4111 1111 1111 1111"], "pps": [], "ibans": [], "emails": ["hr@company.com"]}
    assert classify(findings) == "Confidential"


def test_classify_email_only_is_internal():
    findings = {"cards": [], "pps": [], "ibans": [], "emails": ["hr@company.com"]}
    assert classify(findings) == "Internal"


def test_classify_nothing_is_public():
    findings = {"cards": [], "pps": [], "ibans": [], "emails": []}
    assert classify(findings) == "Public"