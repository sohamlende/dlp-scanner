import re

# Card numbers: 13-16 digits, optionally separated by spaces or dashes
CARD_PATTERN = re.compile(r"\b(?:\d[ -]?){13,16}\b")

# Irish PPS numbers: 7 digits followed by a letter
PPS_PATTERN = re.compile(r"\b\d{7}[A-Z]\b", re.IGNORECASE)


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


if __name__ == "__main__":
    sample = (
        "Update staff 1234567T and 1111111l. Typo 1234567A. "
        "Ref 7654321. Card 4111 1111 1111 1111."
    )
    print("Cards:", find_card_numbers(sample))
    print("PPS:", find_pps_numbers(sample))