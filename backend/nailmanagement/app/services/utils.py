import bcrypt
import re

def hash_pin(pin: int) -> str:
    hashed = bcrypt.hashpw(pin.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    return hashed

def verify_pin(pin: int) -> bool:
    is_valid = bcrypt.checkpw(pin.encode("utf-8"), hash_pin(pin))
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