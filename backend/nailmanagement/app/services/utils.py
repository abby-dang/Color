import bcrypt
import re

def hash_pin(pin: int) -> str:
    hashed = bcrypt.hashpw(pin.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    return hashed

def verify_pin(pin: str, stored_hash: str) -> bool:
    is_valid = bcrypt.checkpw(pin.encode("utf-8"), stored_hash.encode("utf-8"))
    return is_valid

def valid_phone(phone: str) -> bool:
    validPhoneNum = re.match(r"^\d{10}$", phone)
    return validPhoneNum

def valid_email(email: str) -> bool:
    validEmail = re.match("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email)
    return validEmail
def valid_weekdays(days: str) -> bool:
    validSet = {"s","m","t","w","th","f","sat"}
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