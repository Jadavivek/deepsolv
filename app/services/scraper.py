import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from app.models.schemas import (
    BrandInsightsSchema, ProductSchema, FAQSchema, SocialHandlesSchema,
    ContactDetailsSchema, ImportantLinksSchema, PolicySchema
)
from app.services.extractors import (
    ProductExtractor, PolicyExtractor, FAQExtractor, SocialExtractor,
    ContactExtractor, LinkExtractor, BrandContextExtractor
)
from app.utils.http_client import HTTPClient
from app.utils.llm_processor import LLMProcessor
from app.core.config import settings
logger = logging.getLogger(__name__)
class ShopifyStoreScraper:
    def __init__(self):
        self.http_client = HTTPClient()
        self.llm_processor = LLMProcessor()
        self.product_extractor = ProductExtractor(self.http_client)
        self.policy_extractor = PolicyExtractor(self.http_client)
        self.faq_extractor = FAQExtractor(self.http_client, self.llm_processor)
        self.social_extractor = SocialExtractor(self.http_client)
        self.contact_extractor = ContactExtractor(self.http_client)
        self.link_extractor = LinkExtractor(self.http_client)
        self.brand_context_extractor = BrandContextExtractor(self.http_client, self.llm_processor)
    async def extract_insights(self, website_url: str) -> BrandInsightsSchema:
        logger.info(f"Starting insight extraction for: {website_url}")
        try:
            normalized_url = self._normalize_url(website_url)
            main_page_content = await self.http_client.get_page_content(normalized_url)
            main_soup = BeautifulSoup(main_page_content, 'html.parser')
            brand_name = self._extract_brand_name(main_soup, normalized_url)
            extraction_tasks = [
                self._extract_product_catalog(normalized_url),
                self._extract_hero_products(main_soup, normalized_url),
                self._extract_policies(normalized_url),
                self._extract_faqs(normalized_url),
                self._extract_social_handles(main_soup, normalized_url),
                self._extract_contact_details(main_soup, normalized_url),
                self._extract_important_links(main_soup, normalized_url),
                self._extract_brand_context(main_soup, normalized_url)
            ]
            results = await asyncio.gather(*extraction_tasks, return_exceptions=True)
            (product_catalog, hero_products, policies, faqs, 
             social_handles, contact_details, important_links, brand_context) = results
            product_catalog = product_catalog if not isinstance(product_catalog, Exception) else []
            hero_products = hero_products if not isinstance(hero_products, Exception) else []
            policies = policies if not isinstance(policies, Exception) else {}
            faqs = faqs if not isinstance(faqs, Exception) else []
            social_handles = social_handles if not isinstance(social_handles, Exception) else SocialHandlesSchema()
            contact_details = contact_details if not isinstance(contact_details, Exception) else ContactDetailsSchema()
            important_links = important_links if not isinstance(important_links, Exception) else ImportantLinksSchema()
            brand_context = brand_context if not isinstance(brand_context, Exception) else None
            insights = BrandInsightsSchema(
                brand_name=brand_name,
                website_url=normalized_url,
                product_catalog=product_catalog,
                hero_products=hero_products,
                privacy_policy=policies.get('privacy'),
                return_policy=policies.get('return'),
                refund_policy=policies.get('refund'),
                terms_of_service=policies.get('terms'),
                faqs=faqs,
                social_handles=social_handles,
                contact_details=contact_details,
                important_links=important_links,
                brand_context=brand_context,
                extraction_timestamp=datetime.now()
            )
            logger.info(f"Successfully extracted insights for: {website_url}")
            return insights
        except Exception as e:
            logger.error(f"Error extracting insights from {website_url}: {str(e)}")
            raise
    def _normalize_url(self, url: str) -> str:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url.rstrip('/')
    def _extract_brand_name(self, soup: BeautifulSoup, url: str) -> Optional[str]:
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
            brand_name = re.sub(r'\s*[-|–]\s*.*$', '', title)
            if brand_name and len(brand_name) < 100:
                return brand_name
        logo = soup.find('img', {'alt': re.compile(r'logo', re.I)})
        if logo and logo.get('alt'):
            return logo['alt'].strip()
        site_name = soup.find('meta', {'property': 'og:site_name'})
        if site_name and site_name.get('content'):
            return site_name['content'].strip()
        domain = urlparse(url).netloc
        if domain:
            brand = re.sub(r'^(www\.|shop\.)', '', domain)
            brand = re.sub(r'\.(com|co\.in|in|org|net).*$', '', brand)
            return brand.replace('-', ' ').replace('_', ' ').title()
        return None
    async def _extract_product_catalog(self, url: str) -> List[ProductSchema]:
        return await self.product_extractor.extract_all_products(url)
    async def _extract_hero_products(self, soup: BeautifulSoup, url: str) -> List[ProductSchema]:
        return await self.product_extractor.extract_hero_products(soup, url)
    async def _extract_policies(self, url: str) -> Dict[str, PolicySchema]:
        return await self.policy_extractor.extract_all_policies(url)
    async def _extract_faqs(self, url: str) -> List[FAQSchema]:
        return await self.faq_extractor.extract_faqs(url)
    async def _extract_social_handles(self, soup: BeautifulSoup, url: str) -> SocialHandlesSchema:
        return await self.social_extractor.extract_social_handles(soup, url)
    async def _extract_contact_details(self, soup: BeautifulSoup, url: str) -> ContactDetailsSchema:
        return await self.contact_extractor.extract_contact_details(soup, url)
    async def _extract_important_links(self, soup: BeautifulSoup, url: str) -> ImportantLinksSchema:
        return await self.link_extractor.extract_important_links(soup, url)
    async def _extract_brand_context(self, soup: BeautifulSoup, url: str) -> Optional[str]:
        return await self.brand_context_extractor.extract_brand_context(soup, url)