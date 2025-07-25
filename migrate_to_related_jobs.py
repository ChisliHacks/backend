"""
Database migration script to add RelatedJob model and update lesson relationships
Run this script to migrate from the old lesson-job relationship to the new lesson-related_job relationship
"""

from app.models import *  # Import all models to ensure they're registered
from app.core.database import Base
from app.core.config import settings
from sqlalchemy import create_engine, text
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def run_migration():
    """Run the database migration"""

    # Create database engine
    engine = create_engine(settings.DATABASE_URL, echo=True)

    print("Starting database migration...")

    try:
        with engine.begin() as conn:
            # Create new related_jobs table
            print("Creating related_jobs table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS related_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    position VARCHAR(255) NOT NULL,
                    company VARCHAR(255),
                    description TEXT,
                    job_type VARCHAR(100),
                    experience_level VARCHAR(100),
                    industry VARCHAR(100),
                    skills_required TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP
                );
            """))

            # Create index on position for faster lookups
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_related_jobs_position ON related_jobs(position);
            """))

            # Create new lesson_related_job_relations table
            print("Creating lesson_related_job_relations table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS lesson_related_job_relations (
                    lesson_id INTEGER NOT NULL,
                    related_job_id INTEGER NOT NULL,
                    PRIMARY KEY (lesson_id, related_job_id),
                    FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE,
                    FOREIGN KEY (related_job_id) REFERENCES related_jobs(id) ON DELETE CASCADE
                );
            """))

            # Check if old lesson_job_relations table exists and migrate data
            result = conn.execute(text("""
                SELECT name FROM sqlite_master WHERE type='table' AND name='lesson_job_relations';
            """))

            if result.fetchone():
                print("Migrating data from old lesson_job_relations...")

                # Get all existing lesson-job relationships
                old_relations = conn.execute(text("""
                    SELECT l.lesson_id, j.position, j.company 
                    FROM lesson_job_relations l
                    JOIN jobs j ON l.job_id = j.id
                """)).fetchall()

                # Migrate each relationship
                for lesson_id, position, company in old_relations:
                    # Check if related_job already exists
                    existing = conn.execute(text("""
                        SELECT id FROM related_jobs 
                        WHERE position = :position AND (company = :company OR (company IS NULL AND :company IS NULL))
                    """), {"position": position, "company": company}).fetchone()

                    if existing:
                        related_job_id = existing[0]
                    else:
                        # Create new related_job
                        result = conn.execute(text("""
                            INSERT INTO related_jobs (position, company, is_active)
                            VALUES (:position, :company, 1)
                        """), {"position": position, "company": company})
                        related_job_id = result.lastrowid

                    # Create new lesson-related_job relationship
                    conn.execute(text("""
                        INSERT OR IGNORE INTO lesson_related_job_relations (lesson_id, related_job_id)
                        VALUES (:lesson_id, :related_job_id)
                    """), {"lesson_id": lesson_id, "related_job_id": related_job_id})

                print(
                    f"Migrated {len(old_relations)} lesson-job relationships")

                # Drop old table (commented out for safety - uncomment when ready)
                # print("Dropping old lesson_job_relations table...")
                # conn.execute(text("DROP TABLE lesson_job_relations;"))

            print("Migration completed successfully!")

    except Exception as e:
        print(f"Migration failed: {str(e)}")
        raise


if __name__ == "__main__":
    run_migration()
