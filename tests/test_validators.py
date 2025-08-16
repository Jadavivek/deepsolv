import pytest
from app.utils.validators import (
    validate_email, validate_phone_number, validate_url,
    validate_shopify_url, clean_price, extract_social_handle
)
class VivekTestValidators:
    def test_vivek_validate_email(self):
        assert validate_email("test@example.com") is True
        assert validate_email("user.name+tag@domain.co.uk") is True
        assert validate_email("invalid-email") is False
        assert validate_email("@domain.com") is False
        assert validate_email("user@") is False
    def test_vivek_validate_phone_number(self):
        assert validate_phone_number("+1-555-123-4567") is True
        assert validate_phone_number("555-123-4567") is True
        assert validate_phone_number("5551234567") is True
        assert validate_phone_number("123") is False
        assert validate_phone_number("abc-def-ghij") is False
    def test_vivek_validate_url(self):
        assert validate_url("https://example.com") is True
        assert validate_url("http://test.co.uk") is True
        assert validate_url("ftp://files.example.com") is True
        assert validate_url("not-a-url") is False
        assert validate_url("") is False
    def test_vivek_clean_price(self):
        assert clean_price("$29.99") == "29.99"
        assert clean_price("€45,50") == "45,50"
        assert clean_price("₹1,299.00") == "1,299.00"
        assert clean_price("") is None
        assert clean_price("Free") == "Free"
    def test_vivek_extract_social_handle(self):
        assert extract_social_handle("https://instagram.com/testuser", "instagram") == "testuser"
        assert extract_social_handle("https://twitter.com/testuser", "twitter") == "testuser"
        assert extract_social_handle("https://tiktok.com/@testuser", "tiktok") == "testuser"
        assert extract_social_handle("invalid-url", "instagram") == "invalid-url"