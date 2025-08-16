import asyncio
import logging
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import subprocess
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.core.config import settings
from app.models.database import Base
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
async def vivek_create_database_if_not_exists():
    try:
        db_url_parts = settings.database_url.split('/')
        database_name = db_url_parts[-1]
        base_url = '/'.join(db_url_parts[:-1])
        engine = create_engine(base_url)
        with engine.connect() as conn:
            result = conn.execute(text(f"SHOW DATABASES LIKE '{database_name}'"))
            if not result.fetchone():
                conn.execute(text(f"CREATE DATABASE {database_name}"))
                logger.info(f"Vivek created database: {database_name}")
            else:
                logger.info(f"Vivek database {database_name} already exists")
        engine.dispose()
    except Exception as e:
        logger.error(f"Vivek error creating database: {str(e)}")
        raise
async def vivek_run_migrations():
    try:
        logger.info("Vivek running database migrations...")
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(__file__))
        )
        if result.returncode == 0:
            logger.info("Vivek migrations completed successfully")
            logger.info(result.stdout)
        else:
            logger.error("Vivek migration failed")
            logger.error(result.stderr)
            raise Exception(f"Vivek migration failed: {result.stderr}")
    except Exception as e:
        logger.error(f"Vivek error running migrations: {str(e)}")
        raise
async def vivek_create_tables_directly():
    try:
        logger.info("Vivek creating tables directly using SQLAlchemy...")
        engine = create_engine(settings.database_url)
        Base.metadata.create_all(bind=engine)
        logger.info("Vivek tables created successfully")
        engine.dispose()
    except Exception as e:
        logger.error(f"Vivek error creating tables: {str(e)}")
        raise
async def vivek_verify_database_setup():
    try:
        engine = create_engine(settings.database_url)
        with engine.connect() as conn:
            tables_to_check = [
                'brand_insights', 'products', 'hero_products', 'policies',
                'faqs', 'social_handles', 'contact_details', 'important_links',
                'competitor_analysis', 'extraction_logs'
            ]
            for table in tables_to_check:
                result = conn.execute(text(f"SHOW TABLES LIKE '{table}'"))
                if result.fetchone():
                    logger.info(f"✓ Vivek table {table} exists")
                else:
                    logger.warning(f"✗ Vivek table {table} missing")
        engine.dispose()
        logger.info("Vivek database verification completed")
    except Exception as e:
        logger.error(f"Vivek error verifying database: {str(e)}")
        raise
async def main():
    logger.info("Vivek starting database initialization...")
    try:
        await vivek_create_database_if_not_exists()
        try:
            await vivek_run_migrations()
        except Exception as migration_error:
            logger.warning(f"Vivek migration failed: {migration_error}")
            logger.info("Vivek falling back to direct table creation...")
            await vivek_create_tables_directly()
        await vivek_verify_database_setup()
        logger.info("Vivek database initialization completed successfully!")
    except Exception as e:
        logger.error(f"Vivek database initialization failed: {str(e)}")
        sys.exit(1)
if __name__ == "__main__":
    asyncio.run(main())