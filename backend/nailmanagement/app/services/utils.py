import bcrypt
import re
from datetime import datetime, timezone

def hash_pin(pin: int) -> str:
    hashed = bcrypt.hashpw(pin.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    return hashed

def verify_pin(pin: str, stored_hash: str) -> bool:
    is_valid = bcrypt.checkpw(pin.encode("utf-8"), stored_hash.encode("utf-8"))
    return is_valid

def valid_phone(phone: str) -> bool:
    cleaned = re.sub(r"\D", "", phone)  # remove non-digits
    return bool(re.match(r"^\d{10}$", cleaned))

def valid_email(email: str) -> bool:
    validEmail = re.match("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email)
    return validEmail
def valid_weekdays(days: str) -> bool:
    validSet = {"s","m","t","w","th","f","sat", ""}
    cleaned = days.replace(" ", "")
    splitDays = cleaned.split(",")

    for d in splitDays:
        if not (d in validSet):
            return False

    return True

def valid_password(password: str) -> bool:
    """
    Checks if password meets the minimum requirements

    Returns:
        bool: True if password meets requirement, false otherwise
    
    """
    #PASSWORD CHECK
    hasValidLength = len(password) >= 8
    hasAtLeastOneUpperCase = re.search(r"[A-Z]", password)
    hasAtLeastOneLowerCase = re.search(r"[a-z]", password)
    hasAtLeastOneNum = re.search(r"\d", password)
    hasAtLeastOneSpecialChar = re.search(r"[^a-zA-Z0-9]", password)

    if not (hasValidLength and hasAtLeastOneLowerCase and hasAtLeastOneNum and hasAtLeastOneSpecialChar and hasAtLeastOneUpperCase):
        return False
    
    return True

def verify_date_format(date_str: str) -> bool:
    """
    Verifies that the date string is in the format YYYY-MM-DD

    Args:
        date_str (str): The date string to verify

    Returns:
        bool: True if the date string is in the correct format, False otherwise
    """
    pattern = r"^\d{4}-\d{2}-\d{2}$"
    return re.match(pattern, date_str) is not None

def generate_tech_pin() -> str:
    """
    Generates a random 4-digit pin for a tech user

    Returns:
        str: A random 4-digit pin
    """
    import random
    return str(random.randint(1000, 9999))

def convert_date_time(date: str, time: str) -> datetime:
    """
    Converts date and time strings to a datetime object

    Args:
        date (str): date string in any supported format (e.g. "2026-09-20", "09/20/2026")
        time (str): time string in any supported format (e.g. "14:00:00", "14:00")

    Returns:
        datetime: a datetime object in %Y-%m-%d %H:%M format

    Raises:
        ValueError: if date or time format is invalid
    """
    time = convert_time(time)
    date = convert_date(date)
    return datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")

def convert_time(time: str) -> str:
    """
    Converts a time string to %H:%M format

    Args:
        time (str): time string to convert

    Returns:
        str: time in %H:%M format
    
    Raises:
        ValueError: if time format is invalid
    """
    try:
        converted = datetime.strptime(time, "%H:%M:%S").strftime("%H:%M")
        return converted
    except ValueError:
        try:
            converted = datetime.strptime(time, "%H:%M").strftime("%H:%M")
            return converted
        except ValueError:
            raise ValueError(f"Invalid time format: {time}")

def convert_date(date: str) -> str:
    """
    Converts a date string to %Y-%m-%d format

    Args:
        date (str): date string to convert

    Returns:
        str: date in %Y-%m-%d format
    
    Raises:
        ValueError: if date format is invalid
    """
    formats = [
        "%Y-%m-%d",     # 2026-09-20
        "%m/%d/%Y",     # 09/20/2026
        "%d/%m/%Y",     # 20/09/2026
        "%B %d, %Y",    # September 20, 2026
        "%b %d, %Y",    # Sep 20, 2026
        "%m-%d-%Y",     # 09-20-2026
    ]

    for fmt in formats:
        try:
            converted = datetime.strptime(date, fmt).strftime("%Y-%m-%d")
            return converted
        except ValueError:
            continue
    
    raise ValueError(f"Invalid date format: {date}")