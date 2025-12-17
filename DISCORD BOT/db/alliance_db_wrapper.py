"""
Alliance Database Wrapper - Uses MongoDB if available, falls back to SQLite

This wrapper ensures alliance data is ALWAYS saved to MongoDB on Render,
preventing data loss on container restarts.
"""

import os
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


def use_mongodb():
    """Check if MongoDB is configured"""
    return bool(os.getenv('MONGO_URI'))


class AllianceDatabase:
    """
    Unified interface for alliance data storage.
    Automatically uses MongoDB for Render (persistent) or SQLite for local dev (ephemeral).
    """

    def __init__(self, sqlite_conn=None, sqlite_cursor=None):
        """Initialize database wrapper
        
        Args:
            sqlite_conn: SQLite connection (used only if MongoDB not available)
            sqlite_cursor: SQLite cursor (used only if MongoDB not available)
        """
        self.use_mongo = use_mongodb()
        self.sqlite_conn = sqlite_conn
        self.sqlite_cursor = sqlite_cursor
        
        if self.use_mongo:
            logger.info("[Alliance DB] ✅ Using MongoDB for persistent storage")
            from .mongo_adapters import AllianceMembersAdapter
            self.mongo_adapter = AllianceMembersAdapter
        else:
            logger.warning("[Alliance DB] ⚠️  Using SQLite (NOT persistent on Render) - Set MONGO_URI to enable MongoDB")
            self.mongo_adapter = None

    def add_member(self, fid: str, data: Dict[str, Any]) -> bool:
        """Add or update an alliance member"""
        try:
            if self.use_mongo:
                # MongoDB: automatic persistence
                result = self.mongo_adapter.upsert_member(str(fid), data)
                logger.info(f"[Alliance DB] ✅ Saved member {fid} to MongoDB")
                return result
            else:
                # SQLite: temporary storage only
                if not self.sqlite_cursor:
                    return False
                
                # Prepare data for SQLite
                columns = ', '.join(data.keys())
                placeholders = ', '.join(['?' for _ in data.keys()])
                values = tuple(data.values())
                
                query = f"INSERT OR REPLACE INTO users ({columns}) VALUES ({placeholders})"
                self.sqlite_cursor.execute(query, values)
                self.sqlite_conn.commit()
                logger.debug(f"[Alliance DB] Saved member {fid} to SQLite (temporary)")
                return True
        except Exception as e:
            logger.error(f"[Alliance DB] Failed to add member {fid}: {e}")
            return False

    def get_member(self, fid: str) -> Optional[Dict[str, Any]]:
        """Get a single alliance member"""
        try:
            if self.use_mongo:
                return self.mongo_adapter.get_member(str(fid))
            else:
                if not self.sqlite_cursor:
                    return None
                self.sqlite_cursor.execute("SELECT * FROM users WHERE fid = ?", (fid,))
                row = self.sqlite_cursor.fetchone()
                return row
        except Exception as e:
            logger.error(f"[Alliance DB] Failed to get member {fid}: {e}")
            return None

    def get_all_members(self) -> List[Dict[str, Any]]:
        """Get all alliance members"""
        try:
            if self.use_mongo:
                return self.mongo_adapter.get_all_members()
            else:
                if not self.sqlite_cursor:
                    return []
                self.sqlite_cursor.execute("SELECT * FROM users")
                return self.sqlite_cursor.fetchall()
        except Exception as e:
            logger.error(f"[Alliance DB] Failed to get all members: {e}")
            return []

    def delete_member(self, fid: str) -> bool:
        """Delete an alliance member"""
        try:
            if self.use_mongo:
                result = self.mongo_adapter.delete_member(str(fid))
                logger.info(f"[Alliance DB] ✅ Deleted member {fid} from MongoDB")
                return result
            else:
                if not self.sqlite_cursor:
                    return False
                self.sqlite_cursor.execute("DELETE FROM users WHERE fid = ?", (fid,))
                self.sqlite_conn.commit()
                logger.debug(f"[Alliance DB] Deleted member {fid} from SQLite")
                return True
        except Exception as e:
            logger.error(f"[Alliance DB] Failed to delete member {fid}: {e}")
            return False

    def clear_all(self) -> bool:
        """Clear all alliance members"""
        try:
            if self.use_mongo:
                result = self.mongo_adapter.clear_all()
                logger.warning("[Alliance DB] ✅ Cleared all members from MongoDB")
                return result
            else:
                if not self.sqlite_cursor:
                    return False
                self.sqlite_cursor.execute("DELETE FROM users")
                self.sqlite_conn.commit()
                logger.warning("[Alliance DB] Cleared all members from SQLite")
                return True
        except Exception as e:
            logger.error(f"[Alliance DB] Failed to clear all members: {e}")
            return False

    def get_db_type(self) -> str:
        """Get current database backend"""
        return "MongoDB (Persistent ✅)" if self.use_mongo else "SQLite (Ephemeral ⚠️)"
