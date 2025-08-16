import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app
from app.models.schemas import BrandInsightsSchema, ProductSchema
client = TestClient(app)
class TestHealthEndpoint:
    def test_health_check(self):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
class TestInsightsEndpoint:
    @patch('app.services.scraper.ShopifyStoreScraper.extract_insights')
    def test_extract_insights_success(self, mock_extract):
        mock_insights = BrandInsightsSchema(
            brand_name="Test Brand",
            website_url="https://test-store.com",
            product_catalog=[
                ProductSchema(title="Test Product", price="29.99")
            ]
        )
        mock_extract.return_value = mock_insights
        response = client.post(
            "/api/v1/insights/extract",
            json={"website_url": "https://test-store.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["brand_name"] == "Test Brand"
    def test_extract_insights_invalid_url(self):
        response = client.post(
            "/api/v1/insights/extract",
            json={"website_url": "invalid-url"}
        )
        assert response.status_code == 422
    @patch('app.services.scraper.ShopifyStoreScraper.extract_insights')
    def test_extract_insights_website_not_found(self, mock_extract):
        mock_extract.side_effect = Exception("Website not found")
        response = client.post(
            "/api/v1/insights/extract",
            json={"website_url": "https://nonexistent-store.com"}
        )
        assert response.status_code == 500
class TestCompetitorAnalysisEndpoint:
    @patch('app.services.competitor_analyzer.CompetitorAnalyzer.analyze_competitors')
    def test_competitor_analysis_success(self, mock_analyze):
        mock_analysis = {
            "main_brand": BrandInsightsSchema(
                brand_name="Main Brand",
                website_url="https://main-brand.com"
            ),
            "competitors": [],
            "analysis_summary": "Test analysis summary"
        }
        mock_analyze.return_value = mock_analysis
        response = client.post(
            "/api/v1/insights/competitors",
            json={
                "website_url": "https://main-brand.com",
                "max_competitors": 3
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True