"""Initial migration - Create all tables

Revision ID: 0001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create brand_insights table
    op.create_table('brand_insights',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('brand_name', sa.String(length=255), nullable=True),
        sa.Column('website_url', sa.String(length=500), nullable=False),
        sa.Column('brand_context', sa.Text(), nullable=True),
        sa.Column('extraction_timestamp', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_brand_insights_id'), 'brand_insights', ['id'], unique=False)
    op.create_index(op.f('ix_brand_insights_website_url'), 'brand_insights', ['website_url'], unique=True)

    # Create products table
    op.create_table('products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('brand_id', sa.Integer(), nullable=False),
        sa.Column('shopify_id', sa.String(length=100), nullable=True),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('handle', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.String(length=50), nullable=True),
        sa.Column('compare_at_price', sa.String(length=50), nullable=True),
        sa.Column('vendor', sa.String(length=255), nullable=True),
        sa.Column('product_type', sa.String(length=255), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('images', sa.JSON(), nullable=True),
        sa.Column('variants', sa.JSON(), nullable=True),
        sa.Column('available', sa.Boolean(), nullable=True),
        sa.Column('url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['brand_id'], ['brand_insights.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_products_id'), 'products', ['id'], unique=False)

    # Create hero_products table
    op.create_table('hero_products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('brand_id', sa.Integer(), nullable=False),
        sa.Column('shopify_id', sa.String(length=100), nullable=True),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('handle', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.String(length=50), nullable=True),
        sa.Column('compare_at_price', sa.String(length=50), nullable=True),
        sa.Column('images', sa.JSON(), nullable=True),
        sa.Column('url', sa.String(length=500), nullable=True),
        sa.Column('position', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['brand_id'], ['brand_insights.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hero_products_id'), 'hero_products', ['id'], unique=False)

    # Create policies table
    op.create_table('policies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('brand_id', sa.Integer(), nullable=False),
        sa.Column('policy_type', sa.String(length=100), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=True),
        sa.Column('last_updated', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['brand_id'], ['brand_insights.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_policies_id'), 'policies', ['id'], unique=False)

    # Create faqs table
    op.create_table('faqs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('brand_id', sa.Integer(), nullable=False),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('answer', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=255), nullable=True),
        sa.Column('position', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['brand_id'], ['brand_insights.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_faqs_id'), 'faqs', ['id'], unique=False)

    # Create social_handles table
    op.create_table('social_handles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('brand_id', sa.Integer(), nullable=False),
        sa.Column('instagram', sa.String(length=500), nullable=True),
        sa.Column('facebook', sa.String(length=500), nullable=True),
        sa.Column('twitter', sa.String(length=500), nullable=True),
        sa.Column('tiktok', sa.String(length=500), nullable=True),
        sa.Column('youtube', sa.String(length=500), nullable=True),
        sa.Column('linkedin', sa.String(length=500), nullable=True),
        sa.Column('pinterest', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['brand_id'], ['brand_insights.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_social_handles_id'), 'social_handles', ['id'], unique=False)

    # Create contact_details table
    op.create_table('contact_details',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('brand_id', sa.Integer(), nullable=False),
        sa.Column('emails', sa.JSON(), nullable=True),
        sa.Column('phone_numbers', sa.JSON(), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('support_hours', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['brand_id'], ['brand_insights.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contact_details_id'), 'contact_details', ['id'], unique=False)

    # Create important_links table
    op.create_table('important_links',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('brand_id', sa.Integer(), nullable=False),
        sa.Column('order_tracking', sa.String(length=500), nullable=True),
        sa.Column('contact_us', sa.String(length=500), nullable=True),
        sa.Column('blogs', sa.String(length=500), nullable=True),
        sa.Column('size_guide', sa.String(length=500), nullable=True),
        sa.Column('shipping_info', sa.String(length=500), nullable=True),
        sa.Column('careers', sa.String(length=500), nullable=True),
        sa.Column('about_us', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['brand_id'], ['brand_insights.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_important_links_id'), 'important_links', ['id'], unique=False)

    # Create competitor_analysis table
    op.create_table('competitor_analysis',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('main_brand_id', sa.Integer(), nullable=False),
        sa.Column('competitor_brand_id', sa.Integer(), nullable=False),
        sa.Column('similarity_score', sa.Float(), nullable=True),
        sa.Column('competitive_advantages', sa.JSON(), nullable=True),
        sa.Column('analysis_summary', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['competitor_brand_id'], ['brand_insights.id'], ),
        sa.ForeignKeyConstraint(['main_brand_id'], ['brand_insights.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_competitor_analysis_id'), 'competitor_analysis', ['id'], unique=False)

    # Create extraction_logs table
    op.create_table('extraction_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('website_url', sa.String(length=500), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('extraction_time_seconds', sa.Float(), nullable=True),
        sa.Column('data_points_extracted', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_extraction_logs_id'), 'extraction_logs', ['id'], unique=False)
    op.create_index(op.f('ix_extraction_logs_website_url'), 'extraction_logs', ['website_url'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_extraction_logs_website_url'), table_name='extraction_logs')
    op.drop_index(op.f('ix_extraction_logs_id'), table_name='extraction_logs')
    op.drop_table('extraction_logs')
    
    op.drop_index(op.f('ix_competitor_analysis_id'), table_name='competitor_analysis')
    op.drop_table('competitor_analysis')
    
    op.drop_index(op.f('ix_important_links_id'), table_name='important_links')
    op.drop_table('important_links')
    
    op.drop_index(op.f('ix_contact_details_id'), table_name='contact_details')
    op.drop_table('contact_details')
    
    op.drop_index(op.f('ix_social_handles_id'), table_name='social_handles')
    op.drop_table('social_handles')
    
    op.drop_index(op.f('ix_faqs_id'), table_name='faqs')
    op.drop_table('faqs')
    
    op.drop_index(op.f('ix_policies_id'), table_name='policies')
    op.drop_table('policies')
    
    op.drop_index(op.f('ix_hero_products_id'), table_name='hero_products')
    op.drop_table('hero_products')
    
    op.drop_index(op.f('ix_products_id'), table_name='products')
    op.drop_table('products')
    
    op.drop_index(op.f('ix_brand_insights_website_url'), table_name='brand_insights')
    op.drop_index(op.f('ix_brand_insights_id'), table_name='brand_insights')
    op.drop_table('brand_insights')
