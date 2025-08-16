import asyncio
import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import time
from app.models.schemas import (
    InsightExtractionRequest, InsightExtractionResponse, 
    CompetitorAnalysisRequest, CompetitorAnalysisResponseWrapper,
    APIResponse, ErrorResponse, HealthCheckResponse
)
from app.services.scraper import ShopifyStoreScraper
from app.services.competitor_analyzer import CompetitorAnalyzer
from app.database.connection import get_db
from app.services.database_service import DatabaseService
from app.utils.validators import validate_shopify_url
from app.models.enums import ExtractionStatus
logger = logging.getLogger(__name__)
router = APIRouter()
scraper = ShopifyStoreScraper()
competitor_analyzer = CompetitorAnalyzer()
@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    return HealthCheckResponse(
        status="healthy",
        version="1.0.0"
    )
@router.post("/insights/extract", response_model=InsightExtractionResponse)
async def extract_insights(
    request: InsightExtractionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    start_time = time.time()
    website_url = str(request.website_url)
    logger.info(f"Starting insight extraction for: {website_url}")
    try:
        if not validate_shopify_url(website_url):
            raise HTTPException(
                status_code=400,
                detail="Invalid website URL format"
            )
        db_service = DatabaseService(db)
        existing_insights = await db_service.get_recent_insights(website_url, hours=24)
        if existing_insights:
            logger.info(f"Returning cached insights for: {website_url}")
            return InsightExtractionResponse(
                success=True,
                message="Insights retrieved from cache",
                data=existing_insights
            )
        try:
            insights = await scraper.extract_insights(website_url)
        except Exception as scraping_error:
            logger.error(f"Scraping error for {website_url}: {str(scraping_error)}")
            extraction_time = time.time() - start_time
            background_tasks.add_task(
                db_service.log_extraction_attempt,
                website_url, ExtractionStatus.FAILED, str(scraping_error), extraction_time
            )
            error_message = str(scraping_error).lower()
            if any(keyword in error_message for keyword in ['not found', '404', 'does not exist']):
                raise HTTPException(
                    status_code=401,
                    detail="Website not found or not accessible"
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Internal server error occurred during extraction"
                )
        extraction_time = time.time() - start_time
        data_points_count = _count_data_points(insights)
        background_tasks.add_task(
            db_service.save_insights,
            insights
        )
        background_tasks.add_task(
            db_service.log_extraction_attempt,
            website_url, ExtractionStatus.SUCCESS, None, extraction_time, data_points_count
        )
        logger.info(f"Successfully extracted insights for: {website_url} in {extraction_time:.2f}s")
        return InsightExtractionResponse(
            success=True,
            message=f"Insights extracted successfully in {extraction_time:.2f} seconds",
            data=insights
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error extracting insights from {website_url}: {str(e)}")
        extraction_time = time.time() - start_time
        background_tasks.add_task(
            db_service.log_extraction_attempt,
            website_url, ExtractionStatus.FAILED, str(e), extraction_time
        )
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during extraction"
        )
@router.post("/insights/competitors", response_model=CompetitorAnalysisResponseWrapper)
async def analyze_competitors(
    request: CompetitorAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    start_time = time.time()
    website_url = str(request.website_url)
    logger.info(f"Starting competitor analysis for: {website_url}")
    try:
        if not validate_shopify_url(website_url):
            raise HTTPException(
                status_code=400,
                detail="Invalid website URL format"
            )
        db_service = DatabaseService(db)
        existing_analysis = await db_service.get_recent_competitor_analysis(website_url, hours=48)
        if existing_analysis:
            logger.info(f"Returning cached competitor analysis for: {website_url}")
            return CompetitorAnalysisResponseWrapper(
                success=True,
                message="Competitor analysis retrieved from cache",
                data=existing_analysis
            )
        try:
            analysis_result = await competitor_analyzer.analyze_competitors(
                website_url, 
                max_competitors=request.max_competitors
            )
        except Exception as analysis_error:
            logger.error(f"Competitor analysis error for {website_url}: {str(analysis_error)}")
            raise HTTPException(
                status_code=500,
                detail="Error occurred during competitor analysis"
            )
        analysis_time = time.time() - start_time
        background_tasks.add_task(
            db_service.save_competitor_analysis,
            analysis_result
        )
        logger.info(f"Successfully completed competitor analysis for: {website_url} in {analysis_time:.2f}s")
        return CompetitorAnalysisResponseWrapper(
            success=True,
            message=f"Competitor analysis completed successfully in {analysis_time:.2f} seconds",
            data=analysis_result
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in competitor analysis for {website_url}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during competitor analysis"
        )
@router.get("/insights/history/{website_url:path}")
async def get_extraction_history(
    website_url: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    try:
        db_service = DatabaseService(db)
        history = await db_service.get_extraction_history(website_url, limit)
        return APIResponse(
            success=True,
            message=f"Retrieved {len(history)} extraction records",
            data=history
        )
    except Exception as e:
        logger.error(f"Error retrieving extraction history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving extraction history"
        )
@router.get("/insights/stats")
async def get_extraction_stats(db: Session = Depends(get_db)):
    try:
        db_service = DatabaseService(db)
        stats = await db_service.get_extraction_stats()
        return APIResponse(
            success=True,
            message="Extraction statistics retrieved successfully",
            data=stats
        )
    except Exception as e:
        logger.error(f"Error retrieving extraction stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving extraction statistics"
        )
@router.delete("/insights/{website_url:path}")
async def delete_insights(
    website_url: str,
    db: Session = Depends(get_db)
):
    try:
        db_service = DatabaseService(db)
        deleted = await db_service.delete_insights(website_url)
        if deleted:
            return APIResponse(
                success=True,
                message=f"Insights deleted successfully for {website_url}"
            )
        else:
            raise HTTPException(
                status_code=404,
                detail="No insights found for the specified website"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting insights: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error deleting insights"
        )
@router.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            error_code=str(exc.status_code)
        ).dict()
    )
@router.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            error_code="500"
        ).dict()
    )
def _count_data_points(insights) -> int:
    count = 0
    if insights.brand_name:
        count += 1
    if insights.product_catalog:
        count += len(insights.product_catalog)
    if insights.hero_products:
        count += len(insights.hero_products)
    if insights.privacy_policy:
        count += 1
    if insights.return_policy:
        count += 1
    if insights.refund_policy:
        count += 1
    if insights.terms_of_service:
        count += 1
    if insights.faqs:
        count += len(insights.faqs)
    if insights.social_handles:
        social_dict = insights.social_handles.dict()
        count += sum(1 for v in social_dict.values() if v)
    if insights.contact_details:
        contact_dict = insights.contact_details.dict()
        count += sum(len(v) if isinstance(v, list) else (1 if v else 0) for v in contact_dict.values())
    if insights.important_links:
        links_dict = insights.important_links.dict()
        count += sum(1 for v in links_dict.values() if v)
    if insights.brand_context:
        count += 1
    return count