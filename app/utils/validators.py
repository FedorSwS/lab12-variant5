import re
from typing import Tuple

def validate_email(email: str) -> Tuple[bool, str]:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True, ""
    return False, "Invalid email format"

def validate_phone(phone: str) -> Tuple[bool, str]:
    pattern = r'^\+?[0-9]{10,15}$'
    if re.match(pattern, phone):
        return True, ""
    return False, "Phone must contain 10-15 digits, optionally starting with +"

def validate_passport(passport_number: str) -> Tuple[bool, str]:
    pattern = r'^[A-Z0-9]{5,50}$'
    if re.match(pattern, passport_number):
        return True, ""
    return False, "Passport number must contain only uppercase letters and digits, 5-50 characters"

def validate_room_number(room_number: str) -> Tuple[bool, str]:
    pattern = r'^[0-9]{1,4}[A-Z]?$'
    if re.match(pattern, room_number):
        return True, ""
    return False, "Room number format: 1-4 digits optionally followed by a letter"

def test_validators():
    test_cases = [
        ("test@example.com", True, validate_email),
        ("invalid-email", False, validate_email),
        ("+79991234567", True, validate_phone),
        ("123456", False, validate_phone),
        ("AB12345", True, validate_passport),
        ("abc123", True, validate_passport),
        ("101A", True, validate_room_number),
        ("12345", True, validate_room_number),
        ("A101", False, validate_room_number),
    ]
    
    for value, expected, validator in test_cases:
        result, _ = validator(value)
        assert result == expected, f"Failed for {value}"
    
    print("All validator tests passed!")

if __name__ == "__main__":
    test_validators()
