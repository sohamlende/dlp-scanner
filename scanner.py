import re

CARD_PATTERN = re.compile(r"\b(?:\d[ -]?){13,16}\b")


def luhn_check(number:str) -> bool:
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

if __name__ == "__main__":
    sample = "Order ref 1234 5678 9012 3456, card 4111 1111 1111 1111, phone 0871234567"
    print(find_card_numbers(sample))