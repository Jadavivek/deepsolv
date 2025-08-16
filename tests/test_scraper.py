"""
Scraper service tests
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from bs4 import BeautifulSoup

from app.services.scraper import ShopifyStoreScraper
from app.services.extractors import ProductExtractor
from app.utils.http_client import HTTPClient

class TestShopifyStoreScraper:
    """Test main scraper functionality"""
    
    @pytest.fixture
    def scraper(self):
        """Create scraper instance for testing"""
        return ShopifyStoreScraper()
    
    @pytest.fixture
    def mock_html(self):
        """Mock HTML content for testing"""
        return """
        <html>
            <head><title>Test Store</title></head>
            <body>
                <h1>Test Store</h1>
                <div class="product-card">
                    <h3>Test Product</h3>
                    <span class="price">$29.99</span>
                </div>
            </body>
        </html>
        """
    
    def test_normalize_url(self, scraper):
        """Test URL normalization"""
        assert scraper._normalize_url("example.com") == "https://example.com"
        assert scraper._normalize_url("http://example.com") == "http://example.com"
        assert scraper._normalize_url("https://example.com/") == "https://example.com"
    
    def test_extract_brand_name(self, scraper, mock_html):
        """Test brand name extraction"""
        soup = BeautifulSoup(mock_html, 'html.parser')
        brand_name = scraper._extract_brand_name(soup, "https://test-store.com")
        assert brand_name == "Test Store"

class TestProductExtractor:
    """Test product extraction functionality"""
    
    @pytest.fixture
    def extractor(self):
        """Create product extractor for testing"""
        http_client = Mock(spec=HTTPClient)
        return ProductExtractor(http_client)
    
    def test_parse_product_json(self, extractor):
        """Test parsing product from JSON data"""
        product_data = {
            "id": 12345,
            "title": "Test Product",
            "handle": "test-product",
            "price": "29.99",
            "vendor": "Test Vendor",
            "product_type": "T-Shirts",
            "tags": "cotton,comfortable",
            "images": [{"src": "https://example.com/image.jpg"}],
            "variants": [{"id": 1, "price": "29.99", "available": True}]
        }
        
        product = extractor._parse_product_json(product_data, "https://test-store.com")
        
        assert product is not None
        assert product.title == "Test Product"
        assert product.price == "29.99"
        assert product.vendor == "Test Vendor"
        assert len(product.images) == 1