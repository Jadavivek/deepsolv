import asyncio
import logging
import sys
import os
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.database.connection import SessionLocal
from app.models.database import (
    BrandInsights, Product, HeroProduct, Policy, FAQ, SocialHandle,
    ContactDetail, ImportantLink, ExtractionLog
)
from app.models.enums import ExtractionStatus, PolicyType
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
async def vivek_seed_sample_data():
    db = SessionLocal()
    try:
        logger.info("Vivek seeding sample data...")
        sample_brand = BrandInsights(
            brand_name="Sample Fashion Store",
            website_url="https://sample-fashion.com",
            brand_context="A modern fashion brand focused on sustainable clothing and accessories for young professionals."
        )
        db.add(sample_brand)
        db.flush()
        sample_products = [
            Product(
                brand_id=sample_brand.id,
                shopify_id="12345",
                title="Organic Cotton T-Shirt",
                handle="organic-cotton-tshirt",
                description="Comfortable organic cotton t-shirt in various colors",
                price="29.99",
                vendor="Sample Fashion Store",
                product_type="T-Shirts",
                tags=["organic", "cotton", "sustainable"],
                images=["https://example.com/tshirt1.jpg"],
                available=True,
                url="https://sample-fashion.com/products/organic-cotton-tshirt"
            ),
            Product(
                brand_id=sample_brand.id,
                shopify_id="12346",
                title="Recycled Denim Jeans",
                handle="recycled-denim-jeans",
                description="Stylish jeans made from recycled denim",
                price="79.99",
                compare_at_price="99.99",
                vendor="Sample Fashion Store",
                product_type="Jeans",
                tags=["recycled", "denim", "sustainable"],
                images=["https://example.com/jeans1.jpg"],
                available=True,
                url="https://sample-fashion.com/products/recycled-denim-jeans"
            )
        ]
        for product in sample_products:
            db.add(product)
        hero_product = HeroProduct(
            brand_id=sample_brand.id,
            shopify_id="12345",
            title="Organic Cotton T-Shirt",
            handle="organic-cotton-tshirt",
            description="Featured organic cotton t-shirt",
            price="29.99",
            images=["https://example.com/tshirt1.jpg"],
            url="https://sample-fashion.com/products/organic-cotton-tshirt",
            position=1
        )
        db.add(hero_product)
        privacy_policy = Policy(
            brand_id=sample_brand.id,
            policy_type=PolicyType.PRIVACY.value,
            content="We respect your privacy and protect your personal information...",
            url="https://sample-fashion.com/pages/privacy-policy"
        )
        return_policy = Policy(
            brand_id=sample_brand.id,
            policy_type=PolicyType.RETURN.value,
            content="We offer 30-day returns on all items...",
            url="https://sample-fashion.com/pages/return-policy"
        )
        db.add(privacy_policy)
        db.add(return_policy)
        sample_faqs = [
            FAQ(
                brand_id=sample_brand.id,
                question="Do you offer international shipping?",
                answer="Yes, we ship worldwide with standard rates.",
                category="Shipping",
                position=1
            ),
            FAQ(
                brand_id=sample_brand.id,
                question="What materials do you use?",
                answer="We use organic and recycled materials whenever possible.",
                category="Products",
                position=2
            )
        ]
        for faq in sample_faqs:
            db.add(faq)
        social_handles = SocialHandle(
            brand_id=sample_brand.id,
            instagram="@samplefashion",
            facebook="samplefashionstore",
            twitter="@samplefashion"
        )
        db.add(social_handles)
        contact_details = ContactDetail(
            brand_id=sample_brand.id,
            emails=["info@sample-fashion.com", "support@sample-fashion.com"],
            phone_numbers=["+1-555-0123"],
            address="123 Fashion Street, Style City, SC 12345"
        )
        db.add(contact_details)
        important_links = ImportantLink(
            brand_id=sample_brand.id,
            order_tracking="https://sample-fashion.com/pages/track-order",
            contact_us="https://sample-fashion.com/pages/contact",
            blogs="https://sample-fashion.com/blogs/news",
            size_guide="https://sample-fashion.com/pages/size-guide"
        )
        db.add(important_links)
        extraction_log = ExtractionLog(
            website_url="https://sample-fashion.com",
            status=ExtractionStatus.SUCCESS.value,
            extraction_time_seconds=15.5,
            data_points_extracted=25
        )
        db.add(extraction_log)
        db.commit()
        logger.info("Vivek sample data seeded successfully!")
        logger.info(f"Vivek created brand: {sample_brand.brand_name}")
        logger.info(f"Vivek added {len(sample_products)} products")
        logger.info(f"Vivek added {len(sample_faqs)} FAQs")
        logger.info("Vivek added policies, social handles, contact details, and links")
    except Exception as e:
        db.rollback()
        logger.error(f"Vivek error seeding data: {str(e)}")
        raise
    finally:
        db.close()
async def vivek_clear_sample_data():
    db = SessionLocal()
    try:
        logger.info("Vivek clearing sample data...")
        sample_brand = db.query(BrandInsights).filter(
            BrandInsights.website_url == "https://sample-fashion.com"
        ).first()
        if sample_brand:
            db.delete(sample_brand)
            db.commit()
            logger.info("Vivek sample data cleared successfully!")
        else:
            logger.info("Vivek no sample data found to clear")
    except Exception as e:
        db.rollback()
        logger.error(f"Vivek error clearing sample data: {str(e)}")
        raise
    finally:
        db.close()
async def main():
    if len(sys.argv) > 1 and sys.argv[1] == "clear":
        await vivek_clear_sample_data()
    else:
        await vivek_seed_sample_data()
if __name__ == "__main__":
    asyncio.run(main())