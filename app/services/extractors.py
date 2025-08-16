"""
Specialized extractors for different types of data
"""

import asyncio
import json
import re
from typing import List, Dict, Optional, Any
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import logging

from app.models.schemas import (
    ProductSchema, FAQSchema, SocialHandlesSchema, ContactDetailsSchema,
    ImportantLinksSchema, PolicySchema
)
from app.utils.validators import validate_email, validate_phone_number, extract_social_handle
from app.utils.http_client import HTTPClient
from app.utils.llm_processor import LLMProcessor

logger = logging.getLogger(__name__)

class ProductExtractor:
    """Extractor for product information"""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    async def extract_all_products(self, base_url: str) -> List[ProductSchema]:
        """Extract all products from the store"""
        products = []
        
        try:
            # Try Shopify products.json endpoint
            products_url = urljoin(base_url, '/products.json')
            
            page = 1
            while True:
                paginated_url = f"{products_url}?page={page}&limit=250"
                
                try:
                    content = await self.http_client.get_json(paginated_url)
                    if not content or 'products' not in content:
                        break
                    
                    page_products = content['products']
                    if not page_products:
                        break
                    
                    for product_data in page_products:
                        product = self._parse_product_json(product_data, base_url)
                        if product:
                            products.append(product)
                    
                    page += 1
                    
                    # Prevent infinite loops
                    if page > 100:
                        break
                        
                except Exception as e:
                    logger.warning(f"Error fetching products page {page}: {e}")
                    break
            
            logger.info(f"Extracted {len(products)} products from {base_url}")
            return products
            
        except Exception as e:
            logger.error(f"Error extracting products from {base_url}: {e}")
            return []
    
    async def extract_hero_products(self, soup: BeautifulSoup, base_url: str) -> List[ProductSchema]:
        """Extract hero/featured products from homepage"""
        hero_products = []
        
        try:
            # Look for common hero product selectors
            hero_selectors = [
                '.featured-product',
                '.hero-product',
                '.product-featured',
                '.homepage-product',
                '[data-product-id]',
                '.product-card',
                '.product-item'
            ]
            
            for selector in hero_selectors:
                elements = soup.select(selector)
                if elements:
                    for element in elements[:6]:  # Limit to first 6
                        product = await self._parse_product_element(element, base_url)
                        if product:
                            hero_products.append(product)
                    break
            
            # Remove duplicates based on title
            seen_titles = set()
            unique_products = []
            for product in hero_products:
                if product.title not in seen_titles:
                    seen_titles.add(product.title)
                    unique_products.append(product)
            
            logger.info(f"Extracted {len(unique_products)} hero products")
            return unique_products
            
        except Exception as e:
            logger.error(f"Error extracting hero products: {e}")
            return []
    
    def _parse_product_json(self, product_data: dict, base_url: str) -> Optional[ProductSchema]:
        """Parse product from JSON data"""
        try:
            # Extract images
            images = []
            if 'images' in product_data:
                images = [img.get('src', '') for img in product_data['images'] if img.get('src')]
            
            # Extract variants
            variants = []
            if 'variants' in product_data:
                for variant in product_data['variants']:
                    variants.append({
                        'id': variant.get('id'),
                        'title': variant.get('title'),
                        'price': variant.get('price'),
                        'available': variant.get('available', True),
                        'sku': variant.get('sku')
                    })
            
            # Get main price from first variant
            price = None
            compare_at_price = None
            if variants:
                price = variants[0].get('price')
                compare_at_price = variants[0].get('compare_at_price')
            
            product = ProductSchema(
                id=str(product_data.get('id', '')),
                title=product_data.get('title', ''),
                handle=product_data.get('handle', ''),
                description=product_data.get('body_html', ''),
                price=price,
                compare_at_price=compare_at_price,
                vendor=product_data.get('vendor', ''),
                product_type=product_data.get('product_type', ''),
                tags=product_data.get('tags', '').split(',') if product_data.get('tags') else [],
                images=images,
                variants=variants,
                available=any(v.get('available', False) for v in variants) if variants else True,
                url=urljoin(base_url, f"/products/{product_data.get('handle', '')}")
            )
            
            return product
            
        except Exception as e:
            logger.error(f"Error parsing product JSON: {e}")
            return None
    
    async def _parse_product_element(self, element: BeautifulSoup, base_url: str) -> Optional[ProductSchema]:
        """Parse product from HTML element"""
        try:
            # Extract title
            title_selectors = ['h1', 'h2', 'h3', '.product-title', '.title', '[data-product-title]']
            title = None
            for selector in title_selectors:
                title_elem = element.select_one(selector)
                if title_elem:
                    title = title_elem.get_text().strip()
                    break
            
            if not title:
                return None
            
            # Extract price
            price_selectors = ['.price', '.product-price', '[data-price]', '.money']
            price = None
            for selector in price_selectors:
                price_elem = element.select_one(selector)
                if price_elem:
                    price = price_elem.get_text().strip()
                    break
            
            # Extract image
            images = []
            img_elem = element.select_one('img')
            if img_elem and img_elem.get('src'):
                images.append(img_elem['src'])
            
            # Extract URL
            url = None
            link_elem = element.select_one('a')
            if link_elem and link_elem.get('href'):
                url = urljoin(base_url, link_elem['href'])
            
            product = ProductSchema(
                title=title,
                price=price,
                images=images,
                url=url,
                available=True
            )
            
            return product
            
        except Exception as e:
            logger.error(f"Error parsing product element: {e}")
            return None

class PolicyExtractor:
    """Extractor for policy information"""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    async def extract_all_policies(self, base_url: str) -> Dict[str, PolicySchema]:
        """Extract all policies"""
        policies = {}
        
        policy_urls = {
            'privacy': ['/pages/privacy-policy', '/privacy-policy', '/privacy'],
            'return': ['/pages/return-policy', '/return-policy', '/returns'],
            'refund': ['/pages/refund-policy', '/refund-policy', '/refunds'],
            'terms': ['/pages/terms-of-service', '/terms-of-service', '/terms']
        }
        
        tasks = []
        for policy_type, url_patterns in policy_urls.items():
            tasks.append(self._extract_policy(base_url, policy_type, url_patterns))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, (policy_type, _) in enumerate(policy_urls.items()):
            if not isinstance(results[i], Exception) and results[i]:
                policies[policy_type] = results[i]
        
        return policies
    
    async def _extract_policy(self, base_url: str, policy_type: str, url_patterns: List[str]) -> Optional[PolicySchema]:
        """Extract a specific policy"""
        for pattern in url_patterns:
            try:
                policy_url = urljoin(base_url, pattern)
                content = await self.http_client.get_page_content(policy_url)
                
                if content:
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    # Extract main content
                    content_selectors = [
                        '.policy-content',
                        '.page-content',
                        '.main-content',
                        'main',
                        '.content',
                        'article'
                    ]
                    
                    policy_content = None
                    for selector in content_selectors:
                        content_elem = soup.select_one(selector)
                        if content_elem:
                            policy_content = content_elem.get_text().strip()
                            break
                    
                    if not policy_content:
                        policy_content = soup.get_text().strip()
                    
                    if policy_content and len(policy_content) > 100:
                        return PolicySchema(
                            content=policy_content,
                            url=policy_url
                        )
                        
            except Exception as e:
                logger.debug(f"Could not extract {policy_type} policy from {pattern}: {e}")
                continue
        
        return None

class FAQExtractor:
    """Extractor for FAQ information"""
    
    def __init__(self, http_client: HTTPClient, llm_processor: LLMProcessor):
        self.http_client = http_client
        self.llm_processor = llm_processor
    
    async def extract_faqs(self, base_url: str) -> List[FAQSchema]:
        """Extract FAQs from the store"""
        faqs = []
        
        # Common FAQ URL patterns
        faq_urls = [
            '/pages/faq',
            '/pages/frequently-asked-questions',
            '/faq',
            '/help',
            '/support'
        ]
        
        for url_pattern in faq_urls:
            try:
                faq_url = urljoin(base_url, url_pattern)
                content = await self.http_client.get_page_content(faq_url)
                
                if content:
                    soup = BeautifulSoup(content, 'html.parser')
                    page_faqs = await self._parse_faq_page(soup)
                    faqs.extend(page_faqs)
                    
                    if faqs:  # If we found FAQs, stop looking
                        break
                        
            except Exception as e:
                logger.debug(f"Could not extract FAQs from {url_pattern}: {e}")
                continue
        
        # Use LLM to improve FAQ structure if available
        if faqs and self.llm_processor.is_available():
            faqs = await self.llm_processor.structure_faqs(faqs)
        
        return faqs[:20]  # Limit to 20 FAQs
    
    async def _parse_faq_page(self, soup: BeautifulSoup) -> List[FAQSchema]:
        """Parse FAQs from a page"""
        faqs = []
        
        # Method 1: Look for structured FAQ elements
        faq_containers = soup.select('.faq, .question, .accordion-item, .faq-item')
        
        for container in faq_containers:
            question_elem = container.select_one('.question, .faq-question, h3, h4, .title')
            answer_elem = container.select_one('.answer, .faq-answer, .content, p')
            
            if question_elem and answer_elem:
                question = question_elem.get_text().strip()
                answer = answer_elem.get_text().strip()
                
                if question and answer:
                    faqs.append(FAQSchema(question=question, answer=answer))
        
        # Method 2: Look for alternating h3/p or h4/p patterns
        if not faqs:
            headers = soup.select('h3, h4')
            for header in headers:
                question = header.get_text().strip()
                if '?' in question:  # Likely a question
                    # Look for the next paragraph or div
                    next_elem = header.find_next_sibling(['p', 'div'])
                    if next_elem:
                        answer = next_elem.get_text().strip()
                        if answer and len(answer) > 10:
                            faqs.append(FAQSchema(question=question, answer=answer))
        
        return faqs

class SocialExtractor:
    """Extractor for social media handles"""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    async def extract_social_handles(self, soup: BeautifulSoup, base_url: str) -> SocialHandlesSchema:
        """Extract social media handles"""
        social_handles = SocialHandlesSchema()
        
        # Look for social media links
        social_patterns = {
            'instagram': r'instagram\.com/([^/?]+)',
            'facebook': r'facebook\.com/([^/?]+)',
            'twitter': r'twitter\.com/([^/?]+)',
            'tiktok': r'tiktok\.com/@?([^/?]+)',
            'youtube': r'youtube\.com/(?:c/|channel/|user/)?([^/?]+)',
            'linkedin': r'linkedin\.com/(?:company/|in/)?([^/?]+)',
            'pinterest': r'pinterest\.com/([^/?]+)'
        }
        
        # Find all links
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link['href']
            
            for platform, pattern in social_patterns.items():
                if platform.lower() in href.lower():
                    handle = extract_social_handle(href, platform)
                    if handle:
                        setattr(social_handles, platform, handle)
                        break
        
        return social_handles

class ContactExtractor:
    """Extractor for contact information"""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    async def extract_contact_details(self, soup: BeautifulSoup, base_url: str) -> ContactDetailsSchema:
        """Extract contact details"""
        contact_details = ContactDetailsSchema()
        
        # Extract from main page first
        page_text = soup.get_text()
        
        # Find emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, page_text)
        contact_details.emails = [email for email in emails if validate_email(email)][:5]
        
        # Find phone numbers
        phone_pattern = r'[\+]?[1-9]?[\d\s\-$$$$]{7,15}'
        phones = re.findall(phone_pattern, page_text)
        contact_details.phone_numbers = [phone.strip() for phone in phones if validate_phone_number(phone)][:3]
        
        # Try to get more details from contact page
        try:
            contact_url = urljoin(base_url, '/pages/contact')
            contact_content = await self.http_client.get_page_content(contact_url)
            
            if contact_content:
                contact_soup = BeautifulSoup(contact_content, 'html.parser')
                contact_text = contact_soup.get_text()
                
                # Extract additional emails and phones
                additional_emails = re.findall(email_pattern, contact_text)
                additional_phones = re.findall(phone_pattern, contact_text)
                
                contact_details.emails.extend([email for email in additional_emails if validate_email(email) and email not in contact_details.emails])
                contact_details.phone_numbers.extend([phone.strip() for phone in additional_phones if validate_phone_number(phone) and phone not in contact_details.phone_numbers])
                
                # Limit results
                contact_details.emails = contact_details.emails[:5]
                contact_details.phone_numbers = contact_details.phone_numbers[:3]
                
        except Exception as e:
            logger.debug(f"Could not extract from contact page: {e}")
        
        return contact_details

class LinkExtractor:
    """Extractor for important links"""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    async def extract_important_links(self, soup: BeautifulSoup, base_url: str) -> ImportantLinksSchema:
        """Extract important links"""
        links = ImportantLinksSchema()
        
        # Define link patterns to look for
        link_patterns = {
            'order_tracking': ['track', 'order', 'tracking'],
            'contact_us': ['contact', 'support', 'help'],
            'blogs': ['blog', 'news', 'articles'],
            'size_guide': ['size', 'guide', 'sizing'],
            'shipping_info': ['shipping', 'delivery'],
            'careers': ['career', 'job', 'work'],
            'about_us': ['about', 'story', 'company']
        }
        
        # Find all links
        all_links = soup.find_all('a', href=True)
        
        for link in all_links:
            href = link['href']
            text = link.get_text().strip().lower()
            
            # Make relative URLs absolute
            if href.startswith('/'):
                href = urljoin(base_url, href)
            
            # Match against patterns
            for link_type, keywords in link_patterns.items():
                if any(keyword in text or keyword in href.lower() for keyword in keywords):
                    if not getattr(links, link_type):  # Only set if not already set
                        setattr(links, link_type, href)
                        break
        
        return links

class BrandContextExtractor:
    """Extractor for brand context/about information"""
    
    def __init__(self, http_client: HTTPClient, llm_processor: LLMProcessor):
        self.http_client = http_client
        self.llm_processor = llm_processor
    
    async def extract_brand_context(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Extract brand context information"""
        
        # Try to get from about page first
        about_urls = ['/pages/about', '/pages/about-us', '/about', '/story']
        
        for about_url in about_urls:
            try:
                full_url = urljoin(base_url, about_url)
                content = await self.http_client.get_page_content(full_url)
                
                if content:
                    about_soup = BeautifulSoup(content, 'html.parser')
                    
                    # Remove unwanted elements
                    for element in about_soup(['script', 'style', 'nav', 'header', 'footer']):
                        element.decompose()
                    
                    # Extract main content
                    content_selectors = ['.about-content', '.page-content', 'main', '.content', 'article']
                    
                    for selector in content_selectors:
                        content_elem = about_soup.select_one(selector)
                        if content_elem:
                            text = content_elem.get_text().strip()
                            if len(text) > 100:
                                # Use LLM to clean and structure if available
                                if self.llm_processor.is_available():
                                    return await self.llm_processor.extract_brand_context(text)
                                return text[:1000]  # Limit length
                    
            except Exception as e:
                logger.debug(f"Could not extract from {about_url}: {e}")
                continue
        
        # Fallback: extract from homepage
        try:
            # Look for hero sections or main content
            hero_selectors = ['.hero', '.banner', '.intro', '.description']
            
            for selector in hero_selectors:
                hero_elem = soup.select_one(selector)
                if hero_elem:
                    text = hero_elem.get_text().strip()
                    if len(text) > 50:
                        return text[:500]  # Shorter for homepage content
                        
        except Exception as e:
            logger.debug(f"Could not extract brand context from homepage: {e}")
        
        return None
