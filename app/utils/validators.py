"""
Custom validators for data validation
"""

import re
from typing import List, Optional
from urllib.parse import urlparse
import validators

def validate_email(email: str) -> bool:
    """Validate email address format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone_number(phone: str) -> bool:
    """Validate phone number format"""
    # Remove common separators
    cleaned = re.sub(r'[\s\-$$$$\+]', '', phone)
    # Check if it's a valid phone number (basic validation)
    return bool(re.match(r'^\d{7,15}$', cleaned))

def validate_url(url: str) -> bool:
    """Validate URL format"""
    return validators.url(url)

def validate_shopify_url(url: str) -> bool:
    """Validate if URL appears to be a Shopify store"""
    if not validate_url(url):
        return False
    
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    
    # Check for common Shopify indicators
    shopify_indicators = [
        'myshopify.com',
        '.shopify.com',
        # Many custom domains use Shopify
    ]
    
    # Basic validation - in real implementation, you might check for Shopify-specific elements
    return any(indicator in domain for indicator in shopify_indicators) or len(domain) > 0

def clean_price(price_str: str) -> Optional[str]:
    """Clean and validate price string"""
    if not price_str:
        return None
    
    # Remove currency symbols and extra spaces
    cleaned = re.sub(r'[^\d.,]', '', price_str.strip())
    
    # Basic validation
    if re.match(r'^\d+([.,]\d{1,2})?$', cleaned):
        return cleaned
    
    return price_str  # Return original if can't clean

def extract_social_handle(url: str, platform: str) -> Optional[str]:
    """Extract social media handle from URL"""
    if not validate_url(url):
        return None
    
    patterns = {
        'instagram': r'instagram\.com/([^/?]+)',
        'facebook': r'facebook\.com/([^/?]+)',
        'twitter': r'twitter\.com/([^/?]+)',
        'tiktok': r'tiktok\.com/@?([^/?]+)',
        'youtube': r'youtube\.com/(?:c/|channel/|user/)?([^/?]+)',
        'linkedin': r'linkedin\.com/(?:company/|in/)?([^/?]+)',
        'pinterest': r'pinterest\.com/([^/?]+)'
    }
    
    pattern = patterns.get(platform.lower())
    if pattern:
        match = re.search(pattern, url, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return url  # Return full URL if can't extract handle

def validate_product_data(product_data: dict) -> dict:
    """Validate and clean product data"""
    cleaned = {}
    
    # Required fields
    cleaned['title'] = product_data.get('title', '').strip()
    
    # Optional fields with cleaning
    if 'price' in product_data:
        cleaned['price'] = clean_price(product_data['price'])
    
    if 'compare_at_price' in product_data:
        cleaned['compare_at_price'] = clean_price(product_data['compare_at_price'])
    
    # Handle arrays
    for field in ['tags', 'images']:
        if field in product_data and isinstance(product_data[field], list):
            cleaned[field] = [item.strip() for item in product_data[field] if item.strip()]
    
    # Copy other fields as-is
    for field in ['id', 'handle', 'description', 'vendor', 'product_type', 'variants', 'available', 'url']:
        if field in product_data:
            cleaned[field] = product_data[field]
    
    return cleaned
