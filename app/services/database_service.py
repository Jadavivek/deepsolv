import asyncio
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.models.database import (
    BrandInsights, Product, HeroProduct, Policy, FAQ, SocialHandle,
    ContactDetail, ImportantLink, CompetitorAnalysis, ExtractionLog
)
from app.models.schemas import (
    BrandInsightsSchema, CompetitorAnalysisResponse
)
from app.models.enums import ExtractionStatus, PolicyType
logger = logging.getLogger(__name__)
class DatabaseService:
    def __init__(self, db: Session):
        self.db = db
    async def save_insights(self, insights: BrandInsightsSchema) -> int:
        try:
            existing_brand = self.db.query(BrandInsights).filter(
                BrandInsights.website_url == insights.website_url
            ).first()
            if existing_brand:
                brand_record = existing_brand
                brand_record.brand_name = insights.brand_name
                brand_record.brand_context = insights.brand_context
                brand_record.updated_at = datetime.now()
                self._clear_related_data(brand_record.id)
            else:
                brand_record = BrandInsights(
                    brand_name=insights.brand_name,
                    website_url=insights.website_url,
                    brand_context=insights.brand_context
                )
                self.db.add(brand_record)
                self.db.flush()
            await self._save_products(brand_record.id, insights.product_catalog)
            await self._save_hero_products(brand_record.id, insights.hero_products)
            await self._save_policies(brand_record.id, insights)
            await self._save_faqs(brand_record.id, insights.faqs)
            await self._save_social_handles(brand_record.id, insights.social_handles)
            await self._save_contact_details(brand_record.id, insights.contact_details)
            await self._save_important_links(brand_record.id, insights.important_links)
            self.db.commit()
            logger.info(f"Successfully saved insights for brand ID: {brand_record.id}")
            return brand_record.id
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving insights: {str(e)}")
            raise
    async def get_recent_insights(self, website_url: str, hours: int = 24) -> Optional[BrandInsightsSchema]:
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            brand_record = self.db.query(BrandInsights).filter(
                BrandInsights.website_url == website_url,
                BrandInsights.updated_at >= cutoff_time
            ).first()
            if brand_record:
                return await self._convert_to_schema(brand_record)
            return None
        except Exception as e:
            logger.error(f"Error retrieving recent insights: {str(e)}")
            return None
    async def log_extraction_attempt(
        self, 
        website_url: str, 
        status: ExtractionStatus, 
        error_message: Optional[str] = None,
        extraction_time: Optional[float] = None,
        data_points_count: int = 0
    ):
        try:
            log_entry = ExtractionLog(
                website_url=website_url,
                status=status.value,
                error_message=error_message,
                extraction_time_seconds=extraction_time,
                data_points_extracted=data_points_count
            )
            self.db.add(log_entry)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error logging extraction attempt: {str(e)}")
            self.db.rollback()
    async def get_extraction_history(self, website_url: str, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            logs = self.db.query(ExtractionLog).filter(
                ExtractionLog.website_url == website_url
            ).order_by(desc(ExtractionLog.created_at)).limit(limit).all()
            return [
                {
                    "id": log.id,
                    "status": log.status,
                    "error_message": log.error_message,
                    "extraction_time_seconds": log.extraction_time_seconds,
                    "data_points_extracted": log.data_points_extracted,
                    "created_at": log.created_at.isoformat()
                }
                for log in logs
            ]
        except Exception as e:
            logger.error(f"Error retrieving extraction history: {str(e)}")
            return []
    async def get_extraction_stats(self) -> Dict[str, Any]:
        try:
            total_extractions = self.db.query(ExtractionLog).count()
            successful_extractions = self.db.query(ExtractionLog).filter(
                ExtractionLog.status == ExtractionStatus.SUCCESS.value
            ).count()
            failed_extractions = self.db.query(ExtractionLog).filter(
                ExtractionLog.status == ExtractionStatus.FAILED.value
            ).count()
            avg_extraction_time = self.db.query(func.avg(ExtractionLog.extraction_time_seconds)).filter(
                ExtractionLog.status == ExtractionStatus.SUCCESS.value
            ).scalar()
            total_brands = self.db.query(BrandInsights).count()
            total_products = self.db.query(Product).count()
            return {
                "total_extractions": total_extractions,
                "successful_extractions": successful_extractions,
                "failed_extractions": failed_extractions,
                "success_rate": (successful_extractions / total_extractions * 100) if total_extractions > 0 else 0,
                "average_extraction_time_seconds": round(avg_extraction_time, 2) if avg_extraction_time else 0,
                "total_brands_analyzed": total_brands,
                "total_products_extracted": total_products
            }
        except Exception as e:
            logger.error(f"Error retrieving extraction stats: {str(e)}")
            return {}
    async def delete_insights(self, website_url: str) -> bool:
        try:
            brand_record = self.db.query(BrandInsights).filter(
                BrandInsights.website_url == website_url
            ).first()
            if brand_record:
                self.db.delete(brand_record)
                self.db.commit()
                logger.info(f"Deleted insights for: {website_url}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting insights: {str(e)}")
            self.db.rollback()
            return False
    async def save_competitor_analysis(self, analysis: CompetitorAnalysisResponse) -> int:
        try:
            main_brand_id = await self.save_insights(analysis.main_brand)
            for competitor in analysis.competitors:
                competitor_brand_id = await self.save_insights(competitor.insights)
                comp_analysis = CompetitorAnalysis(
                    main_brand_id=main_brand_id,
                    competitor_brand_id=competitor_brand_id,
                    similarity_score=competitor.similarity_score,
                    competitive_advantages=competitor.competitive_advantages,
                    analysis_summary=analysis.analysis_summary
                )
                self.db.add(comp_analysis)
            self.db.commit()
            return main_brand_id
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving competitor analysis: {str(e)}")
            raise
    async def get_recent_competitor_analysis(self, website_url: str, hours: int = 48) -> Optional[CompetitorAnalysisResponse]:
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            main_brand = self.db.query(BrandInsights).filter(
                BrandInsights.website_url == website_url,
                BrandInsights.updated_at >= cutoff_time
            ).first()
            if not main_brand:
                return None
            comp_analyses = self.db.query(CompetitorAnalysis).filter(
                CompetitorAnalysis.main_brand_id == main_brand.id,
                CompetitorAnalysis.created_at >= cutoff_time
            ).all()
            if not comp_analyses:
                return None
            main_brand_schema = await self._convert_to_schema(main_brand)
            competitors = []
            for comp_analysis in comp_analyses:
                competitor_brand = self.db.query(BrandInsights).filter(
                    BrandInsights.id == comp_analysis.competitor_brand_id
                ).first()
                if competitor_brand:
                    competitor_schema = await self._convert_to_schema(competitor_brand)
                    competitors.append({
                        "competitor_name": competitor_brand.brand_name,
                        "website_url": competitor_brand.website_url,
                        "insights": competitor_schema,
                        "similarity_score": comp_analysis.similarity_score,
                        "competitive_advantages": comp_analysis.competitive_advantages or []
                    })
            return CompetitorAnalysisResponse(
                main_brand=main_brand_schema,
                competitors=competitors,
                analysis_summary=comp_analyses[0].analysis_summary if comp_analyses else None
            )
        except Exception as e:
            logger.error(f"Error retrieving recent competitor analysis: {str(e)}")
            return None
    def _clear_related_data(self, brand_id: int):
        self.db.query(Product).filter(Product.brand_id == brand_id).delete()
        self.db.query(HeroProduct).filter(HeroProduct.brand_id == brand_id).delete()
        self.db.query(Policy).filter(Policy.brand_id == brand_id).delete()
        self.db.query(FAQ).filter(FAQ.brand_id == brand_id).delete()
        self.db.query(SocialHandle).filter(SocialHandle.brand_id == brand_id).delete()
        self.db.query(ContactDetail).filter(ContactDetail.brand_id == brand_id).delete()
        self.db.query(ImportantLink).filter(ImportantLink.brand_id == brand_id).delete()
    async def _save_products(self, brand_id: int, products: List):
        for product in products:
            product_record = Product(
                brand_id=brand_id,
                shopify_id=product.id,
                title=product.title,
                handle=product.handle,
                description=product.description,
                price=product.price,
                compare_at_price=product.compare_at_price,
                vendor=product.vendor,
                product_type=product.product_type,
                tags=product.tags,
                images=product.images,
                variants=product.variants,
                available=product.available,
                url=product.url
            )
            self.db.add(product_record)
    async def _save_hero_products(self, brand_id: int, hero_products: List):
        for i, product in enumerate(hero_products):
            hero_record = HeroProduct(
                brand_id=brand_id,
                shopify_id=product.id,
                title=product.title,
                handle=product.handle,
                description=product.description,
                price=product.price,
                compare_at_price=product.compare_at_price,
                images=product.images,
                url=product.url,
                position=i + 1
            )
            self.db.add(hero_record)
    async def _save_policies(self, brand_id: int, insights):
        policies = [
            (PolicyType.PRIVACY, insights.privacy_policy),
            (PolicyType.RETURN, insights.return_policy),
            (PolicyType.REFUND, insights.refund_policy),
            (PolicyType.TERMS, insights.terms_of_service)
        ]
        for policy_type, policy_data in policies:
            if policy_data:
                policy_record = Policy(
                    brand_id=brand_id,
                    policy_type=policy_type.value,
                    content=policy_data.content,
                    url=policy_data.url,
                    last_updated=policy_data.last_updated
                )
                self.db.add(policy_record)
    async def _save_faqs(self, brand_id: int, faqs: List):
        for i, faq in enumerate(faqs):
            faq_record = FAQ(
                brand_id=brand_id,
                question=faq.question,
                answer=faq.answer,
                category=faq.category,
                position=i + 1
            )
            self.db.add(faq_record)
    async def _save_social_handles(self, brand_id: int, social_handles):
        if social_handles:
            social_record = SocialHandle(
                brand_id=brand_id,
                instagram=social_handles.instagram,
                facebook=social_handles.facebook,
                twitter=social_handles.twitter,
                tiktok=social_handles.tiktok,
                youtube=social_handles.youtube,
                linkedin=social_handles.linkedin,
                pinterest=social_handles.pinterest
            )
            self.db.add(social_record)
    async def _save_contact_details(self, brand_id: int, contact_details):
        if contact_details:
            contact_record = ContactDetail(
                brand_id=brand_id,
                emails=contact_details.emails,
                phone_numbers=contact_details.phone_numbers,
                address=contact_details.address,
                support_hours=contact_details.support_hours
            )
            self.db.add(contact_record)
    async def _save_important_links(self, brand_id: int, important_links):
        if important_links:
            links_record = ImportantLink(
                brand_id=brand_id,
                order_tracking=important_links.order_tracking,
                contact_us=important_links.contact_us,
                blogs=important_links.blogs,
                size_guide=important_links.size_guide,
                shipping_info=important_links.shipping_info,
                careers=important_links.careers,
                about_us=important_links.about_us
            )
            self.db.add(links_record)
    async def _convert_to_schema(self, brand_record: BrandInsights) -> BrandInsightsSchema:
        return BrandInsightsSchema(
            brand_name=brand_record.brand_name,
            website_url=brand_record.website_url,
            brand_context=brand_record.brand_context,
            extraction_timestamp=brand_record.extraction_timestamp or brand_record.created_at)