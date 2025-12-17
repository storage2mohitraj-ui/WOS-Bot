import os
import logging
from datetime import datetime
from typing import List, Dict, Optional, Union
from pymongo import MongoClient, ASCENDING, DESCENDING
from bson import ObjectId

logger = logging.getLogger(__name__)

class ReminderStorageMongo:
    """MongoDB implementation of reminder storage"""
    
    def __init__(self):
        self.mongo_uri = os.getenv('MONGO_URI')
        if not self.mongo_uri:
            raise ValueError("MONGO_URI environment variable not set")
            
        self.client = MongoClient(self.mongo_uri)
        try:
            self.db = self.client.get_database() # Uses database from URI if available
        except Exception:
            self.db = self.client.get_database('whiteout_survival_bot') # Fallback default
        self.reminders = self.db.reminders
        
        # Create indexes
        self.reminders.create_index([("reminder_time", ASCENDING)])
        self.reminders.create_index([("user_id", ASCENDING)])
        self.reminders.create_index([("is_active", ASCENDING), ("is_sent", ASCENDING)])
        
        logger.info("✅ Connected to MongoDB for reminders")

    def add_reminder(self, user_id: str, channel_id: str, guild_id: str, message: str, reminder_time: datetime,
                    body: str = None, is_recurring: bool = False, recurrence_type: str = None, recurrence_interval: int = None,
                    original_pattern: str = None, mention: str = 'everyone', image_url: str = None,
                    thumbnail_url: str = None, footer_text: str = None, footer_icon_url: str = None, author_url: str = None) -> str:
        """Add a new reminder to MongoDB"""
        try:
            # Deduplicate
            existing = self.reminders.find_one({
                "user_id": user_id,
                "channel_id": channel_id,
                "reminder_time": reminder_time,
                "message": message,
                "is_active": 1,
                "is_sent": 0
            })
            
            if existing:
                # Update existing
                updates = {
                    'image_url': image_url,
                    'thumbnail_url': thumbnail_url,
                    'footer_text': footer_text,
                    'footer_icon_url': footer_icon_url,
                    'mention': mention,
                    'author_url': author_url
                }
                # Remove None values
                updates = {k: v for k, v in updates.items() if v is not None}
                
                if updates:
                    self.reminders.update_one({"_id": existing["_id"]}, {"$set": updates})
                    logger.info(f"✅ Updated existing Mongo reminder {existing['_id']}")
                return str(existing["_id"])

            # Insert new
            reminder_doc = {
                "user_id": user_id,
                "channel_id": channel_id,
                "guild_id": guild_id,
                "message": message,
                "body": body,
                "reminder_time": reminder_time,
                "created_at": datetime.utcnow(),
                "is_active": 1,
                "is_sent": 0,
                "is_recurring": 1 if is_recurring else 0,
                "recurrence_type": recurrence_type,
                "recurrence_interval": recurrence_interval,
                "original_time_pattern": original_pattern,
                "mention": mention,
                "image_url": image_url,
                "thumbnail_url": thumbnail_url,
                "footer_text": footer_text,
                "footer_icon_url": footer_icon_url,
                "author_url": author_url
            }
            
            result = self.reminders.insert_one(reminder_doc)
            logger.info(f"✅ Added Mongo reminder {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"❌ Failed to add Mongo reminder: {e}")
            return None

    def get_due_reminders(self) -> List[Dict]:
        """Get all active reminders that are due"""
        try:
            now = datetime.utcnow()
            cursor = self.reminders.find({
                "is_active": 1,
                "is_sent": 0,
                "reminder_time": {"$lte": now}
            }).sort("reminder_time", ASCENDING)
            
            results = []
            for doc in cursor:
                doc['id'] = str(doc.pop('_id'))
                results.append(doc)
            return results
        except Exception as e:
            logger.error(f"❌ Failed to get due Mongo reminders: {e}")
            return []

    def mark_reminder_sent(self, reminder_id: str) -> bool:
        """Mark a reminder as sent"""
        try:
            # Handle both string ID and ObjectId
            try:
                oid = ObjectId(reminder_id)
            except:
                oid = reminder_id
                
            result = self.reminders.update_one(
                {"_id": oid, "is_sent": 0},
                {"$set": {"is_sent": 1}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"❌ Failed to mark Mongo reminder sent: {e}")
            return False

    def update_reminder_fields(self, reminder_id: str, fields: dict) -> bool:
        """Update arbitrary fields"""
        if not fields:
            return False
            
        allowed = {'image_url', 'thumbnail_url', 'body', 'footer_text', 'footer_icon_url', 'mention', 'reminder_time'}
        to_update = {k: v for k, v in fields.items() if k in allowed}
        if not to_update:
            return False
            
        try:
            try:
                oid = ObjectId(reminder_id)
            except:
                oid = reminder_id
                
            result = self.reminders.update_one(
                {"_id": oid},
                {"$set": to_update}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"❌ Failed to update Mongo reminder: {e}")
            return False

    def get_user_reminders(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get active reminders for a user"""
        try:
            cursor = self.reminders.find({
                "user_id": user_id,
                "is_active": 1,
                "is_sent": 0
            }).sort("reminder_time", ASCENDING).limit(limit)
            
            results = []
            for doc in cursor:
                doc['id'] = str(doc.pop('_id'))
                results.append(doc)
            return results
        except Exception as e:
            logger.error(f"❌ Failed to get user Mongo reminders: {e}")
            return []

    def delete_reminder(self, reminder_id: str, user_id: str) -> bool:
        """Delete (deactivate) a reminder"""
        try:
            try:
                oid = ObjectId(reminder_id)
            except:
                oid = reminder_id
                
            result = self.reminders.update_one(
                {"_id": oid, "user_id": user_id, "is_active": 1},
                {"$set": {"is_active": 0}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"❌ Failed to delete Mongo reminder: {e}")
            return False

    def get_all_active_reminders(self) -> List[Dict]:
        """Get ALL active reminders"""
        try:
            cursor = self.reminders.find({
                "is_active": 1,
                "is_sent": 0
            }).sort("reminder_time", ASCENDING)
            
            results = []
            for doc in cursor:
                doc['id'] = str(doc.pop('_id'))
                results.append(doc)
            return results
        except Exception as e:
            logger.error(f"❌ Failed to get all active Mongo reminders: {e}")
            return []

    def update_reminder_time(self, reminder_id: str, new_time: datetime) -> bool:
        """Update the time of a reminder (for recurring)"""
        try:
            try:
                oid = ObjectId(reminder_id)
            except:
                oid = reminder_id
                
            result = self.reminders.update_one(
                {"_id": oid},
                {"$set": {"reminder_time": new_time, "is_sent": 0}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"❌ Failed to update Mongo reminder time: {e}")
            return False
