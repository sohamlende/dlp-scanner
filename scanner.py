import re
from pathlib import Path

# Card numbers: 13-16 digits, optionally separated by spaces or dashes
CARD_PATTERN = re.compile(r"\b(?:\d[ -]?){13,16}\b")

# Irish PPS numbers: 7 digits followed by a letter
PPS_PATTERN = re.compile(r"\b\d{7}[A-Z]\b", re.IGNORECASE)

# Irish IBANs: IE, 2 check digits, then 18 letters/digits (spaces allowed)
IBAN_PATTERN = re.compile(r"\bIE\d{2}(?: ?[A-Z0-9]){18}\b", re.IGNORECASE)

# Email addresses: name@domain.ending
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")

def luhn_check(number: str) -> bool:
    """Return True if the number passes the Luhn checksum used by card numbers."""
    digits = [int(d) for d in number if d.isdigit()]
    total = 0
    # Double every second digit from the right
    for i, digit in enumerate(reversed(digits)):
        if i % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


def find_card_numbers(text: str) -> list[str]:
    """Find likely card numbers: matches the pattern AND passes Luhn."""
    found = []
    for match in CARD_PATTERN.findall(text):
        if luhn_check(match):
            found.append(match.strip())
    return found


def pps_check(pps: str) -> bool:
    """Return True if the PPS number's check letter matches its digits."""
    pps = pps.upper()  # make letters capital, so "1111111l" works too
    digits = pps[:7]  # step 1: the 7 digits
    check_letter = pps[7]  # step 2: the letter at the end

    total = 0  # step 3: start the running total at 0
    weight = 8  # the first digit gets weight 8
    for digit in digits:
        total += int(digit) * weight  # multiply and add to the total
        weight -= 1  # next weight: 7, then 6, and so on

    remainder = total % 23  # step 4: remainder after dividing by 23
    expected = chr(64 + remainder)  # step 5: number to letter (12 gives L)
    return check_letter == expected  # step 6: does it match?


def find_pps_numbers(text: str) -> list[str]:
    """Find PPS numbers that match the pattern AND have a valid check letter."""
    found = []
    for match in PPS_PATTERN.findall(text):
        if pps_check(match):
            found.append(match.upper())
    return found

def find_ibans(text: str) -> list[str]:
    """Find Irish IBANs that match the pattern AND pass the mod 97 check."""
    found = []
    for match in IBAN_PATTERN.findall(text):
        if iban_check(match):
            found.append(match.replace(" ", "").upper())
    return found


def iban_check(iban: str) -> bool:
    """Return true if an Irish IBAN passes the mod 97 check"""
    iban = iban.replace(" ","").upper()  #step 0 - no spaces, capitals
    if len(iban) != 22: #irish IBANS are always 22 char
        return False
    
    rearranged = iban[4:] + iban[:4] #step 1 - first 4 to end
    
    number_text = "" #  step 2: build the long number
    for character in rearranged:
        if character.isalpha():  #a letter: A =10
            number_text += str(ord(character)-55)
        else: # a digit: keep it
            number_text += character
    
    return int(number_text) % 97 == 1   #step 3: remainder must be 1


def find_emails(text: str) -> list[str]:
    """Find email addresses in the text."""
    return EMAIL_PATTERN.findall(text)

def scan_text(text: str) -> dict:
    return{
        "cards": find_card_numbers(text),
        "pps": find_pps_numbers(text),
        "ibans": find_ibans(text),
        "emails": find_emails(text),
    }

def scan_file(path: Path) -> dict:
    with open(path, "r", encoding="utf-8", errors="ignore") as file:
        text = file.read()
    return scan_text(text)

def scan_folder(folder: str) -> dict:
    results = {}
    for path in Path(folder).glob("*"):
        if path.suffix.lower() in (".txt",".csv"):
            results[path.name] = scan_file(path)
    return results


if __name__ == "__main__":
    sample = (
        "Card 4111 1111 1111 1111. Staff 1234567T. "
        "Pay IE29 AIBK 9311 5212 3456 78 or IE64IRCE92050112345678. "
        "Typo IE29AIBK93115212345679. Ref IE12345. "
        "Contact soham.lende@primark.ie or hr@company.com. "
        "Not an email: name@nowhere."
    )
    print("Cards:", find_card_numbers(sample))
    print("PPS:", find_pps_numbers(sample))
    print("IBANs:", find_ibans(sample))
    print("Emails:", find_emails(sample))
    print("\n--- Folder scan ---")
    for name, found in scan_folder("test_files").items():
        print(name, found) 