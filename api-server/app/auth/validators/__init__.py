from email_validator import validate_email, EmailNotValidError
import re


def email_validator(email: str):
    try:
        validate_email(email, check_deliverability=False)
    except EmailNotValidError as e:
        raise ValueError(e)


def secret_validator(secret: str):
    if len(secret) < 16:
        raise ValueError("Secret must be at least 16 characters long")
    if not re.match(r"^[a-zA-Z0-9]+$", secret):
        raise ValueError("Secret must contain only letters and numbers")
    return secret
