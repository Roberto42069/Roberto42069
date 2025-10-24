"""
Security Database Migration Script
Creates security tables and updates existing tables with security fields
"""

from app import app, db
import logging

def create_security_tables():
    """Create security-related tables in the database"""
    
    with app.app_context():
        try:
            # Import models to ensure tables are registered
            
            # Create all tables (will only create missing ones)
            db.create_all()
            
            # Add security columns to existing users table if they don't exist
            from sqlalchemy import text
            
            security_columns = [
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER DEFAULT 0;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS account_locked_until TIMESTAMP;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS password_changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS two_factor_secret VARCHAR(32);",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS two_factor_enabled BOOLEAN DEFAULT FALSE;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS data_retention_consent BOOLEAN DEFAULT FALSE;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS privacy_policy_accepted TIMESTAMP;"
            ]
            
            for column_sql in security_columns:
                try:
                    db.session.execute(text(column_sql))
                    db.session.commit()
                    logging.info("Successfully added security column")
                except Exception as e:
                    db.session.rollback()
                    if "already exists" not in str(e).lower():
                        logging.warning(f"Error adding column: {e}")
            
            logging.info("Security database migration completed successfully")
            return True
            
        except Exception as e:
            logging.error(f"Security migration failed: {e}")
            return False

if __name__ == "__main__":
    create_security_tables()