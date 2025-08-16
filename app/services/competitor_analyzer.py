import asyncio
import logging
from typing import List, Dict, Any, Optional
import re
from urllib.parse import urlparse
from app.models.schemas import (
    CompetitorAnalysisResponse, CompetitorSchema, BrandInsightsSchema
)
from app.services.scraper import ShopifyStoreScraper
from app.utils.llm_processor import LLMProcessor
from app.utils.http_client import HTTPClient
logger = logging.getLogger(__name__)
class CompetitorAnalyzer:
    def __init__(self):
        self.scraper = ShopifyStoreScraper()
        self.llm_processor = LLMProcessor()
        self.http_client = HTTPClient()
    async def analyze_competitors(
        self, 
        main_brand_url: str, 
        max_competitors: int = 5
    ) -> CompetitorAnalysisResponse:
        logger.info(f"Starting competitor analysis for: {main_brand_url}")
        try:
            main_brand_insights = await self.scraper.extract_insights(main_brand_url)
            competitor_urls = await self._find_competitors(main_brand_url, main_brand_insights, max_competitors)
            competitor_tasks = [
                self._analyze_single_competitor(url, main_brand_insights)
                for url in competitor_urls
            ]
            competitor_results = await asyncio.gather(*competitor_tasks, return_exceptions=True)
            competitors = [
                result for result in competitor_results 
                if not isinstance(result, Exception) and result is not None
            ]
            analysis_summary = None
            if self.llm_processor.is_available() and competitors:
                try:
                    main_brand_data = main_brand_insights.dict()
                    competitor_data = [comp.insights.dict() for comp in competitors]
                    llm_analysis = await self.llm_processor.analyze_competitors(
                        main_brand_data, competitor_data
                    )
                    analysis_summary = llm_analysis.get('analysis_summary')
                    advantages = llm_analysis.get('competitive_advantages', [])
                    for i, competitor in enumerate(competitors):
                        if i < len(advantages):
                            competitor.competitive_advantages = advantages[i:i+1]
                except Exception as e:
                    logger.warning(f"LLM analysis failed: {e}")
            response = CompetitorAnalysisResponse(
                main_brand=main_brand_insights,
                competitors=competitors,
                analysis_summary=analysis_summary or self._generate_basic_summary(main_brand_insights, competitors)
            )
            logger.info(f"Completed competitor analysis with {len(competitors)} competitors")
            return response
        except Exception as e:
            logger.error(f"Error in competitor analysis: {str(e)}")
            raise
    async def _find_competitors(
        self, 
        main_brand_url: str, 
        main_brand_insights: BrandInsightsSchema, 
        max_competitors: int
    ) -> List[str]:
        competitors = []
        try:
            search_queries = self._generate_search_queries(main_brand_insights)
            for query in search_queries[:3]:
                try:
                    search_results = await self._search_for_competitors(query)
                    competitors.extend(search_results)
                    if len(competitors) >= max_competitors * 2:
                        break
                except Exception as e:
                    logger.warning(f"Search failed for query '{query}': {e}")
                    continue
            industry_competitors = await self._find_industry_competitors(main_brand_insights)
            competitors.extend(industry_competitors)
            valid_competitors = []
            main_domain = urlparse(main_brand_url).netloc
            for competitor_url in competitors:
                if len(valid_competitors) >= max_competitors:
                    break
                competitor_domain = urlparse(competitor_url).netloc
                if competitor_domain == main_domain:
                    continue
                if await self._validate_competitor_url(competitor_url):
                    valid_competitors.append(competitor_url)
            logger.info(f"Found {len(valid_competitors)} valid competitors")
            return valid_competitors
        except Exception as e:
            logger.error(f"Error finding competitors: {str(e)}")
            return []
    def _generate_search_queries(self, brand_insights: BrandInsightsSchema) -> List[str]:
        queries = []
        if brand_insights.brand_context:
            context_words = re.findall(r'\b[a-zA-Z]{4,}\b', brand_insights.brand_context.lower())
            common_words = {'brand', 'company', 'store', 'shop', 'online', 'website', 'products'}
            key_terms = [word for word in context_words if word not in common_words][:5]
            if key_terms:
                queries.append(f"{' '.join(key_terms[:3])} shopify store")
        if brand_insights.product_catalog:
            product_types = set()
            for product in brand_insights.product_catalog[:10]:
                if product.product_type:
                    product_types.add(product.product_type.lower())
            for product_type in list(product_types)[:3]:
                queries.append(f"{product_type} online store")
        if not queries:
            queries.append("shopify ecommerce store")
        return queries
    async def _search_for_competitors(self, query: str) -> List[str]:
        competitors = []
        try:
            sample_stores = [
                "https://colourpop.com",
                "https://gymshark.com",
                "https://allbirds.com",
                "https://warbyparker.com",
                "https://casper.com"
            ]
            return sample_stores[:2]
        except Exception as e:
            logger.error(f"Error searching for competitors: {str(e)}")
            return []
    async def _find_industry_competitors(self, brand_insights: BrandInsightsSchema) -> List[str]:
        industry_stores = {
            'fashion': [
                'https://fashionnova.com',
                'https://prettylittlething.com'
            ],
            'beauty': [
                'https://glossier.com',
                'https://rarebeauty.com'
            ],
            'fitness': [
                'https://lululemon.com',
                'https://alo.com'
            ]
        }
        if brand_insights.brand_context:
            context_lower = brand_insights.brand_context.lower()
            for industry, stores in industry_stores.items():
                if industry in context_lower:
                    return stores[:2]
        return []
    async def _validate_competitor_url(self, url: str) -> bool:
        try:
            if not url.startswith(('http://', 'https://')):
                return False
            content = await self.http_client.get_page_content(url)
            return content is not None and len(content) > 1000
        except Exception:
            return False
    async def _analyze_single_competitor(
        self, 
        competitor_url: str, 
        main_brand_insights: BrandInsightsSchema
    ) -> Optional[CompetitorSchema]:
        try:
            competitor_insights = await self.scraper.extract_insights(competitor_url)
            similarity_score = self._calculate_similarity(main_brand_insights, competitor_insights)
            advantages = self._identify_competitive_advantages(main_brand_insights, competitor_insights)
            return CompetitorSchema(
                competitor_name=competitor_insights.brand_name,
                website_url=competitor_url,
                insights=competitor_insights,
                similarity_score=similarity_score,
                competitive_advantages=advantages
            )
        except Exception as e:
            logger.warning(f"Failed to analyze competitor {competitor_url}: {str(e)}")
            return None
    def _calculate_similarity(
        self, 
        main_brand: BrandInsightsSchema, 
        competitor: BrandInsightsSchema
    ) -> float:
        score = 0.0
        total_factors = 0
        if main_brand.product_catalog and competitor.product_catalog:
            main_types = set(p.product_type.lower() for p in main_brand.product_catalog if p.product_type)
            comp_types = set(p.product_type.lower() for p in competitor.product_catalog if p.product_type)
            if main_types and comp_types:
                overlap = len(main_types.intersection(comp_types))
                union = len(main_types.union(comp_types))
                score += (overlap / union) if union > 0 else 0
                total_factors += 1
        main_social = main_brand.social_handles.dict() if main_brand.social_handles else {}
        comp_social = competitor.social_handles.dict() if competitor.social_handles else {}
        main_platforms = sum(1 for v in main_social.values() if v)
        comp_platforms = sum(1 for v in comp_social.values() if v)
        if main_platforms > 0 and comp_platforms > 0:
            score += min(main_platforms, comp_platforms) / max(main_platforms, comp_platforms)
            total_factors += 1
        main_product_count = len(main_brand.product_catalog) if main_brand.product_catalog else 0
        comp_product_count = len(competitor.product_catalog) if competitor.product_catalog else 0
        if main_product_count > 0 and comp_product_count > 0:
            ratio = min(main_product_count, comp_product_count) / max(main_product_count, comp_product_count)
            score += ratio
            total_factors += 1
        return (score / total_factors) if total_factors > 0 else 0.0
    def _identify_competitive_advantages(
        self, 
        main_brand: BrandInsightsSchema, 
        competitor: BrandInsightsSchema
    ) -> List[str]:
        advantages = []
        main_products = len(main_brand.product_catalog) if main_brand.product_catalog else 0
        comp_products = len(competitor.product_catalog) if competitor.product_catalog else 0
        if comp_products > main_products * 1.5:
            advantages.append("Larger product catalog")
        main_social = main_brand.social_handles.dict() if main_brand.social_handles else {}
        comp_social = competitor.social_handles.dict() if competitor.social_handles else {}
        main_platforms = sum(1 for v in main_social.values() if v)
        comp_platforms = sum(1 for v in comp_social.values() if v)
        if comp_platforms > main_platforms:
            advantages.append("Stronger social media presence")
        main_policies = sum(1 for policy in [
            main_brand.privacy_policy, main_brand.return_policy, 
            main_brand.refund_policy, main_brand.terms_of_service
        ] if policy)
        comp_policies = sum(1 for policy in [
            competitor.privacy_policy, competitor.return_policy,
            competitor.refund_policy, competitor.terms_of_service
        ] if policy)
        if comp_policies > main_policies:
            advantages.append("More comprehensive policies")
        main_faqs = len(main_brand.faqs) if main_brand.faqs else 0
        comp_faqs = len(competitor.faqs) if competitor.faqs else 0
        if comp_faqs > main_faqs * 1.5:
            advantages.append("More comprehensive FAQ section")
        return advantages[:5]
    def _generate_basic_summary(
        self, 
        main_brand: BrandInsightsSchema, 
        competitors: List[CompetitorSchema]
    ) -> str:
        if not competitors:
            return f"No competitors found for analysis of {main_brand.brand_name or 'the brand'}."
        avg_similarity = sum(c.similarity_score or 0 for c in competitors) / len(competitors)
        summary = f"Analyzed {len(competitors)} competitors for {main_brand.brand_name or 'the brand'}. "
        summary += f"Average similarity score: {avg_similarity:.2f}. "
        if competitors:
            top_competitor = max(competitors, key=lambda c: c.similarity_score or 0)
            summary += f"Most similar competitor: {top_competitor.competitor_name or 'Unknown'} "
            summary += f"with similarity score of {top_competitor.similarity_score:.2f}."