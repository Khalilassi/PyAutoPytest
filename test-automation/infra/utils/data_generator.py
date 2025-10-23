"""
Data Generator utility using Faker library.

Provides convenient functions for generating random test data like names,
emails, addresses, etc.
"""
from typing import Optional

from faker import Faker

# Global faker instance
_faker = Faker()


def generate_email(domain: str = "example.com") -> str:
    """
    Generate random email address.
    
    Args:
        domain: Email domain (default: example.com)
        
    Returns:
        Random email address
    """
    return f"{_faker.user_name()}@{domain}"


def generate_username(length: Optional[int] = None) -> str:
    """
    Generate random username.
    
    Args:
        length: Optional max length for username
        
    Returns:
        Random username
    """
    username = _faker.user_name()
    if length:
        return username[:length]
    return username


def generate_password(length: int = 12, special_chars: bool = True) -> str:
    """
    Generate random password.
    
    Args:
        length: Password length
        special_chars: Include special characters
        
    Returns:
        Random password
    """
    return _faker.password(
        length=length,
        special_chars=special_chars,
        digits=True,
        upper_case=True,
        lower_case=True
    )


def generate_full_name() -> str:
    """
    Generate random full name.
    
    Returns:
        Random full name
    """
    return _faker.name()


def generate_first_name() -> str:
    """
    Generate random first name.
    
    Returns:
        Random first name
    """
    return _faker.first_name()


def generate_last_name() -> str:
    """
    Generate random last name.
    
    Returns:
        Random last name
    """
    return _faker.last_name()


def generate_phone_number() -> str:
    """
    Generate random phone number.
    
    Returns:
        Random phone number
    """
    return _faker.phone_number()


def generate_address() -> str:
    """
    Generate random address.
    
    Returns:
        Random address
    """
    return _faker.address()


def generate_company_name() -> str:
    """
    Generate random company name.
    
    Returns:
        Random company name
    """
    return _faker.company()


def generate_text(max_nb_chars: int = 200) -> str:
    """
    Generate random text.
    
    Args:
        max_nb_chars: Maximum number of characters
        
    Returns:
        Random text
    """
    return _faker.text(max_nb_chars=max_nb_chars)


def generate_date(pattern: str = "%Y-%m-%d") -> str:
    """
    Generate random date.
    
    Args:
        pattern: Date format pattern
        
    Returns:
        Random date string
    """
    return _faker.date(pattern=pattern)


def seed_faker(seed: int) -> None:
    """
    Seed the faker instance for reproducible data.
    
    Args:
        seed: Seed value
    """
    global _faker
    _faker = Faker()
    Faker.seed(seed)


def get_faker() -> Faker:
    """
    Get the global faker instance.
    
    Returns:
        Faker instance
    """
    return _faker
