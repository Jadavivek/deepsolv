import asyncio
import logging
import sys
import os
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.core.config import settings
from app.database.connection import SessionLocal
from app.models.database import BrandInsights, ExtractionLog
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
async def cleanup_old_data(days: int = 30):
    db = SessionLocal()
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        old_logs = db.query(ExtractionLog).filter(
            ExtractionLog.created_at < cutoff_date
        ).count()
        if old_logs > 0:
            db.query(ExtractionLog).filter(
                ExtractionLog.created_at < cutoff_date
            ).delete()
            logger.info(f"Deleted {old_logs} old extraction logs")
        db.commit()
        logger.info(f"Cleanup completed for data older than {days} days")
    except Exception as e:
        db.rollback()
        logger.error(f"Error during cleanup: {str(e)}")
        raise
    finally:
        db.close()
async def get_database_stats():
    db = SessionLocal()
    try:
        stats = {}
        stats['brands'] = db.query(BrandInsights).count()
        stats['extraction_logs'] = db.query(ExtractionLog).count()
        recent_extractions = db.query(ExtractionLog).filter(
            ExtractionLog.created_at >= datetime.now() - timedelta(days=7)
        ).count()
        stats['recent_extractions'] = recent_extractions
        try:
            engine = create_engine(settings.database_url)
            with engine.connect() as conn:
                result = conn.execute(text(
                    f"SELECT ROUND(SUM(data_length + index_length) / 1024 / 1024, 1) AS 'DB Size in MB' "
                    f"FROM information_schema.tables "
                    f"WHERE table_schema='{settings.MYSQL_DATABASE}'"
                ))
                db_size = result.fetchone()
                stats['database_size_mb'] = db_size[0] if db_size else 0
            engine.dispose()
        except Exception as e:
            logger.warning(f"Could not get database size: {e}")
            stats['database_size_mb'] = 'Unknown'
        logger.info("Database Statistics:")
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")
        return stats
    except Exception as e:
        logger.error(f"Error getting database stats: {str(e)}")
        raise
    finally:
        db.close()
async def backup_database():
    try:
        import subprocess
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backup_shopify_insights_{timestamp}.sql"
        cmd = [
            "mysqldump",
            f"--host={settings.MYSQL_HOST}",
            f"--port={settings.MYSQL_PORT}",
            f"--user={settings.MYSQL_USER}",
            f"--password={settings.MYSQL_PASSWORD}",
            "--single-transaction",
            "--routines",
            "--triggers",
            settings.MYSQL_DATABASE
        ]
        logger.info(f"Creating database backup: {backup_file}")
        with open(backup_file, 'w') as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            logger.info(f"Database backup created successfully: {backup_file}")
        else:
            logger.error(f"Backup failed: {result.stderr}")
            raise Exception(f"Backup failed: {result.stderr}")
    except Exception as e:
        logger.error(f"Error creating backup: {str(e)}")
        raise
async def main():
    if len(sys.argv) < 2:
        print("Usage: python database_utils.py <command>")
        print("Commands:")
        print("  stats    - Show database statistics")
        print("  cleanup  - Clean up old data (30 days)")
        print("  backup   - Create database backup")
        return
    command = sys.argv[1].lower()
    if command == "stats":
        await get_database_stats()
    elif command == "cleanup":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        await cleanup_old_data(days)
    elif command == "backup":
        await backup_database()
    else:
        print(f"Unknown command: {command}")
if __name__ == "__main__":
    asyncio.run(main())