"""
Add summary column to lessons table

This migration adds a 'summary' column to the lessons table
Run this script to update your database schema
"""

from sqlalchemy import text
from app.core.database import engine


def add_summary_column():
    """Add summary column to lessons table if it doesn't exist"""

    try:
        with engine.connect() as connection:
            # Check if summary column exists
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='lessons' AND column_name='summary'
            """))

            if result.fetchone() is None:
                # Add summary column
                connection.execute(text("""
                    ALTER TABLE lessons ADD COLUMN summary TEXT NULL
                """))
                connection.commit()
                print("✅ Successfully added 'summary' column to lessons table")
            else:
                print("ℹ️  Summary column already exists in lessons table")

    except Exception as e:
        print(f"❌ Error adding summary column: {e}")


if __name__ == "__main__":
    add_summary_column()
