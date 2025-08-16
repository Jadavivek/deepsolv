"""
SQLAlchemy database models for persistence
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
Base = declarative_base()
class BrandInsights(Base):
    __tablename__ = "brand_insights"
    id = Column(Integer, primary_key=True, index=True)
    brand_name = Column(String(255), nullable=True)
    website_url = Column(String(500), nullable=False, unique=True, index=True)
    brand_context = Column(Text, nullable=True)
    extraction_timestamp = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    products = relationship("Product", back_populates="brand", cascade="all, delete-orphan")
    hero_products = relationship("HeroProduct", back_populates="brand", cascade="all, delete-orphan")
    policies = relationship("Policy", back_populates="brand", cascade="all, delete-orphan")
    faqs = relationship("FAQ", back_populates="brand", cascade="all, delete-orphan")
    social_handles = relationship("SocialHandle", back_populates="brand", uselist=False, cascade="all, delete-orphan")
    contact_details = relationship("ContactDetail", back_populates="brand", uselist=False, cascade="all, delete-orphan")
    important_links = relationship("ImportantLink", back_populates="brand", uselist=False, cascade="all, delete-orphan")
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brand_insights.id"), nullable=False)
    shopify_id = Column(String(100), nullable=True)
    title = Column(String(500), nullable=False)
    handle = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    price = Column(String(50), nullable=True)
    compare_at_price = Column(String(50), nullable=True)
    vendor = Column(String(255), nullable=True)
    product_type = Column(String(255), nullable=True)
    tags = Column(JSON, nullable=True)
    images = Column(JSON, nullable=True)
    variants = Column(JSON, nullable=True)
    available = Column(Boolean, default=True)
    url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=func.now())
    brand = relationship("BrandInsights", back_populates="products")
class HeroProduct(Base):
    __tablename__ = "hero_products"
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brand_insights.id"), nullable=False)
    shopify_id = Column(String(100), nullable=True)
    title = Column(String(500), nullable=False)
    handle = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    price = Column(String(50), nullable=True)
    compare_at_price = Column(String(50), nullable=True)
    images = Column(JSON, nullable=True)
    url = Column(String(500), nullable=True)
    position = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now())
    brand = relationship("BrandInsights", back_populates="hero_products")
class Policy(Base):
    __tablename__ = "policies"
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brand_insights.id"), nullable=False)
    policy_type = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    url = Column(String(500), nullable=True)
    last_updated = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=func.now())
    brand = relationship("BrandInsights", back_populates="policies")
class FAQ(Base):
    __tablename__ = "faqs"
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brand_insights.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String(255), nullable=True)
    position = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now())
    brand = relationship("BrandInsights", back_populates="faqs")
class SocialHandle(Base):
    __tablename__ = "social_handles"
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brand_insights.id"), nullable=False)
    instagram = Column(String(500), nullable=True)
    facebook = Column(String(500), nullable=True)
    twitter = Column(String(500), nullable=True)
    tiktok = Column(String(500), nullable=True)
    youtube = Column(String(500), nullable=True)
    linkedin = Column(String(500), nullable=True)
    pinterest = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=func.now())
    brand = relationship("BrandInsights", back_populates="social_handles")
class ContactDetail(Base):
    __tablename__ = "contact_details"
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brand_insights.id"), nullable=False)
    emails = Column(JSON, nullable=True)
    phone_numbers = Column(JSON, nullable=True)
    address = Column(Text, nullable=True)
    support_hours = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=func.now())
    brand = relationship("BrandInsights", back_populates="contact_details")
class ImportantLink(Base):
    __tablename__ = "important_links"
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brand_insights.id"), nullable=False)
    order_tracking = Column(String(500), nullable=True)
    contact_us = Column(String(500), nullable=True)
    blogs = Column(String(500), nullable=True)
    size_guide = Column(String(500), nullable=True)
    shipping_info = Column(String(500), nullable=True)
    careers = Column(String(500), nullable=True)
    about_us = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=func.now())
    brand = relationship("BrandInsights", back_populates="important_links")
class CompetitorAnalysis(Base):
    __tablename__ = "competitor_analysis"
    id = Column(Integer, primary_key=True, index=True)
    main_brand_id = Column(Integer, ForeignKey("brand_insights.id"), nullable=False)
    competitor_brand_id = Column(Integer, ForeignKey("brand_insights.id"), nullable=False)
    similarity_score = Column(Float, nullable=True)
    competitive_advantages = Column(JSON, nullable=True)
    analysis_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    main_brand = relationship("BrandInsights", foreign_keys=[main_brand_id])
    competitor_brand = relationship("BrandInsights", foreign_keys=[competitor_brand_id])
class ExtractionLog(Base):
    __tablename__ = "extraction_logs"
    id = Column(Integer, primary_key=True, index=True)
    website_url = Column(String(500), nullable=False, index=True)
    status = Column(String(50), nullable=False)
    error_message = Column(Text, nullable=True)
    extraction_time_seconds = Column(Float, nullable=True)
    data_points_extracted = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
