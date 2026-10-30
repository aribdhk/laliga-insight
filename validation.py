"""
validation.py
-------------
Functions that check what the user typed in the "Add / Edit match" form.
Every function raises ValueError with a clear message if something is wrong.
The GUI catches that error and shows the message in a pop-up (no crash).
"""

from datetime import datetime
from models import VENUES


def read_text(text, name):
    """A required text field must not be empty."""
    text = text.strip()
    if text == "":
        raise ValueError(f"{name} is required.")
    return text


def read_int(text, name, low, high):
    """Turn text into a whole number between low and high."""
    text = read_text(text, name)
    try:
        number = int(text)
    except ValueError:                       # e.g. the user typed "abc" or "2.5"
        raise ValueError(f"{name} must be a whole number.")
    if number < low or number > high:
        raise ValueError(f"{name} must be between {low} and {high}.")
    return number


def read_float(text, name, low, high):
    """Turn text into a decimal number between low and high."""
    text = read_text(text, name)
    try:
        number = float(text)
    except ValueError:
        raise ValueError(f"{name} must be a number.")
    if number < low or number > high:
        raise ValueError(f"{name} must be between {low} and {high}.")
    return number


def read_date(text):
    """Date must look like 2025-08-16. Returns the date as clean text."""
    text = read_text(text, "Date")
    try:
        date = datetime.strptime(text, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Date must look like 2025-08-16 (year-month-day).")
    return date.strftime("%Y-%m-%d")


def season_from_date(date_text):
    """La Liga starts in August. Aug-Dec -> that year. Jan-Jul -> the year before."""
    date = datetime.strptime(date_text, "%Y-%m-%d")
    if date.month >= 7:
        return date.year
    return date.year - 1


def validate_match_form(values):
    """values is a dictionary of text from the form.
    Returns a dictionary of clean, correctly typed values."""
    clean = {}
    clean["date"] = read_date(values["date"])
    clean["season"] = season_from_date(clean["date"])
    clean["matchweek"] = read_int(values["matchweek"], "Matchweek", 1, 38)

    venue = read_text(values["venue"], "Venue")
    if venue not in VENUES:
        raise ValueError("Venue must be Home or Away.")
    clean["venue"] = venue

    clean["team"] = read_text(values["team"], "Team")
    clean["opponent"] = read_text(values["opponent"], "Opponent")
    if clean["team"] == clean["opponent"]:
        raise ValueError("A team cannot play against itself.")

    clean["gf"] = read_int(values["gf"], "Goals for", 0, 20)
    clean["ga"] = read_int(values["ga"], "Goals against", 0, 20)
    clean["xg"] = read_float(values["xg"], "xG", 0, 10)
    clean["xga"] = read_float(values["xga"], "xG against", 0, 10)
    clean["poss"] = read_int(values["poss"], "Possession %", 0, 100)
    clean["sh"] = read_int(values["sh"], "Shots", 0, 60)
    clean["sot"] = read_int(values["sot"], "Shots on target", 0, 60)

    if clean["sot"] > clean["sh"]:
        raise ValueError("Shots on target cannot be more than total shots.")
    return clean
