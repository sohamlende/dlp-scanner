# DLP Scanner

A Python data loss prevention (DLP) scanner that finds sensitive data in text and CSV files, validates every match to cut false positives, labels each file by sensitivity, and writes a report that never copies the sensitive values themselves.

## What it detects

| Data type | How it finds candidates | How it validates them |
|---|---|---|
| Payment card numbers | Regex: 13 to 16 digits, with optional spaces or dashes | Luhn checksum |
| Irish PPS numbers | Regex: 7 digits followed by a letter | Check letter (weighted sum, mod 23) |
| Irish IBANs | Regex: `IE`, 2 check digits, 18 letters or digits | ISO 13616 mod 97 check |
| Email addresses | Regex | Pattern only |

Regex finds candidates. The check algorithms remove false positives, so a random 16-digit number or a mistyped IBAN is not flagged.

## Features

- **Folder scanning:** reads every `.txt` and `.csv` file in a folder.
- **Classification labels:** each file is labelled using a high-water mark (the most sensitive content decides the label):
  - **Confidential:** any card number, PPS number or IBAN
  - **Internal:** email addresses only
  - **Public:** nothing found
  - **Not scanned:** the file could not be read
- **Error handling:** locked or missing files are logged with the reason and the scan carries on, so a file it couldn't read is never reported as clean.
- **CSV report:** one row per file with the label and the **counts** of each data type. It never copies card numbers, PPS numbers or IBANs into the report (data minimisation, GDPR Article 5).
- **Automated tests:** 10 pytest tests cover every validator and every label.

## How to run it

Requires Python 3.10 or later.

```
git clone https://github.com/sohamlende/dlp-scanner.git
cd dlp-scanner
python scanner.py
```

This scans the `test_files` folder (fake sample data only) and writes `report.csv`.

To run the tests:

```
python -m pip install pytest
python -m pytest -v
```

## Sample output

```
--- Folder scan ---
contacts.txt Internal
notes.txt Public
orders.txt Confidential
payroll.csv Confidential
Report saved to report.csv
```

`report.csv`:

| file | label | cards | pps | ibans | emails | error |
|---|---|---|---|---|---|---|
| test_files\contacts.txt | Internal | 0 | 0 | 0 | 2 | |
| test_files\notes.txt | Public | 0 | 0 | 0 | 0 | |
| test_files\orders.txt | Confidential | 1 | 0 | 0 | 1 | |
| test_files\payroll.csv | Confidential | 0 | 1 | 1 | 0 | |

## Project structure

```
dlp-scanner/
├── scanner.py         # detectors, validators, scanning, classification, report
├── test_scanner.py    # pytest tests
└── test_files/        # fake sample data (no real personal data)
```

## Limitations and next steps

- Only scans `.txt` and `.csv` files. Next: `.docx` and `.pdf` support.
- Only scans one folder level. Next: scan subfolders.
- PPS validation uses the simplified single-letter check. Next: support the newer two-letter format.
- Next: a command-line option to choose the folder and report name.

## What I learned

- **Pattern matching is only half of detection.** My first card regex flagged any 16-digit number. Adding the Luhn check (and mod 23 for PPS, mod 97 for IBANs) is what turned "looks like" into "is", which is the same false-positive problem SOC analysts deal with every day.
- **A silent failure is worse than a crash.** Early versions either crashed on a locked file or skipped it quietly, which would have reported an unread file as clean. Now unreadable files are logged with the reason and labelled "Not scanned", so a gap in coverage is always visible.
- **The most sensitive item decides the label.** One card number makes the whole file Confidential, no matter how many harmless emails are in it. That is the high-water mark principle used in data classification (ISO 27001 control 5.12).
- **A security tool must not create a new leak.** I designed the report to store counts only, never the card numbers or IBANs themselves, and kept report.csv out of Git. A DLP report full of the data it found would be a breach of its own.
- **Tests make changes safe.** Writing pytest tests for every validator and label meant I could refactor without guessing whether I had broken something.

## Disclaimer

All data in `test_files` is fake and for testing only. Card number 4111 1111 1111 1111 is a standard test number.
