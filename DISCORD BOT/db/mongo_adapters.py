import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from .mongo_client_wrapper import get_mongo_client_sync

logger = logging.getLogger(__name__)


def _get_db():
    uri = os.getenv('MONGO_URI')
    if not uri:
        raise ValueError('MONGO_URI not set')
    client = get_mongo_client_sync(uri)
    db_name = os.getenv('MONGO_DB_NAME', 'discord_bot')
    return client[db_name]


def mongo_enabled() -> bool:
    return bool(os.getenv('MONGO_URI'))


def get_mongo_db():
    """Public function to get MongoDB database instance"""
    return _get_db()


class UserTimezonesAdapter:
    COLL = 'user_timezones'

    @staticmethod
    def load_all() -> Dict[str, str]:
        try:
            db = _get_db()
            docs = db[UserTimezonesAdapter.COLL].find({})
            return {str(d['_id']): d.get('timezone') for d in docs}
        except Exception as e:
            logger.error(f'Failed to load user_timezones from Mongo: {e}')
            return {}

    @staticmethod
    def get(user_id: str) -> Optional[str]:
        try:
            db = _get_db()
            d = db[UserTimezonesAdapter.COLL].find_one({'_id': str(user_id)})
            return d.get('timezone') if d else None
        except Exception as e:
            logger.error(f'Failed to get timezone for {user_id}: {e}')
            return None

    @staticmethod
    def set(user_id: str, tz_abbr: str) -> bool:
        try:
            db = _get_db()
            now = datetime.utcnow().isoformat()
            db[UserTimezonesAdapter.COLL].update_one(
                {'_id': str(user_id)},
                {'$set': {'timezone': tz_abbr.lower(), 'updated_at': now}, '$setOnInsert': {'created_at': now}},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f'Failed to set timezone for {user_id}: {e}')
            return False


class PlayerTimezonesAdapter:
    """Adapter for storing player (FID) timezones"""
    COLL = 'player_timezones'

    @staticmethod
    def get(fid: str) -> Optional[str]:
        """Get timezone for a player by FID"""
        try:
            db = _get_db()
            d = db[PlayerTimezonesAdapter.COLL].find_one({'_id': str(fid)})
            return d.get('timezone') if d else None
        except Exception as e:
            logger.error(f'Failed to get timezone for FID {fid}: {e}')
            return None

    @staticmethod
    def set(fid: str, timezone: str, set_by_user_id: int) -> bool:
        """Set timezone for a player by FID"""
        try:
            db = _get_db()
            now = datetime.utcnow().isoformat()
            db[PlayerTimezonesAdapter.COLL].update_one(
                {'_id': str(fid)},
                {
                    '$set': {
                        'timezone': str(timezone),
                        'set_by': int(set_by_user_id),
                        'updated_at': now
                    },
                    '$setOnInsert': {'created_at': now}
                },
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f'Failed to set timezone for FID {fid}: {e}')
            return False

    @staticmethod
    def get_all() -> Dict[str, str]:
        """Get all player timezones as dict {fid: timezone}"""
        try:
            db = _get_db()
            docs = db[PlayerTimezonesAdapter.COLL].find({})
            return {str(d['_id']): d.get('timezone') for d in docs}
        except Exception as e:
            logger.error(f'Failed to load player_timezones from Mongo: {e}')
            return {}

    @staticmethod
    def delete(fid: str) -> bool:
        """Delete timezone for a player"""
        try:
            db = _get_db()
            result = db[PlayerTimezonesAdapter.COLL].delete_one({'_id': str(fid)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f'Failed to delete timezone for FID {fid}: {e}')
            return False


class BirthdaysAdapter:
    COLL = 'birthdays'

    @staticmethod
    def load_all() -> Dict[str, Any]:
        try:
            db = _get_db()
            docs = db[BirthdaysAdapter.COLL].find({})
            return {str(d['_id']): {'day': int(d.get('day')), 'month': int(d.get('month'))} for d in docs}
        except Exception as e:
            logger.error(f'Failed to load birthdays from Mongo: {e}')
            return {}

    @staticmethod
    def get(user_id: str):
        try:
            db = _get_db()
            d = db[BirthdaysAdapter.COLL].find_one({'_id': str(user_id)})
            if not d:
                return None
            return {'day': int(d['day']), 'month': int(d['month'])}
        except Exception as e:
            logger.error(f'Failed to get birthday for {user_id}: {e}')
            return None

    @staticmethod
    def set(user_id: str, day: int, month: int) -> bool:
        try:
            db = _get_db()
            db[BirthdaysAdapter.COLL].update_one(
                {'_id': str(user_id)},
                {'$set': {'day': int(day), 'month': int(month), 'updated_at': datetime.utcnow().isoformat()},
                 '$setOnInsert': {'created_at': datetime.utcnow().isoformat()}},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f'Failed to set birthday for {user_id}: {e}')
            return False

    @staticmethod
    def remove(user_id: str) -> bool:
        try:
            db = _get_db()
            res = db[BirthdaysAdapter.COLL].delete_one({'_id': str(user_id)})
            return res.deleted_count > 0
        except Exception as e:
            logger.error(f'Failed to remove birthday for {user_id}: {e}')
            return False



class BirthdayChannelAdapter:
    """Adapter for per-guild birthday channel configuration"""
    COLL = 'birthday_channels'
    
    @staticmethod
    def get(guild_id: int) -> Optional[int]:
        """Get birthday channel ID for a guild"""
        try:
            db = _get_db()
            doc = db[BirthdayChannelAdapter.COLL].find_one({'_id': int(guild_id)})
            if doc:
                return int(doc.get('channel_id'))
            return None
        except Exception as e:
            logger.error(f'Failed to get birthday channel for guild {guild_id}: {e}')
            return None
    
    @staticmethod
    def set(guild_id: int, channel_id: int) -> bool:
        """Set birthday channel ID for a guild"""
        try:
            db = _get_db()
            db[BirthdayChannelAdapter.COLL].update_one(
                {'_id': int(guild_id)},
                {'$set': {
                    'channel_id': int(channel_id),
                    'updated_at': datetime.utcnow().isoformat()
                }},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f'Failed to set birthday channel for guild {guild_id}: {e}')
            return False
    
    @staticmethod
    def remove(guild_id: int) -> bool:
        """Remove birthday channel configuration for a guild"""
        try:
            db = _get_db()
            res = db[BirthdayChannelAdapter.COLL].delete_one({'_id': int(guild_id)})
            return res.deleted_count > 0
        except Exception as e:
            logger.error(f'Failed to remove birthday channel for guild {guild_id}: {e}')
            return False

class UserProfilesAdapter:
    COLL = 'user_profiles'

    @staticmethod
    def load_all() -> Dict[str, Any]:
        try:
            db = _get_db()
            docs = db[UserProfilesAdapter.COLL].find({})
            result = {}
            for d in docs:
                data = d.copy()
                data.pop('_id', None)
                result[str(d['_id'])] = data
            return result
        except Exception as e:
            logger.error(f'Failed to load user profiles from Mongo: {e}')
            return {}

    @staticmethod
    def get(user_id: str) -> Optional[Dict[str, Any]]:
        try:
            db = _get_db()
            d = db[UserProfilesAdapter.COLL].find_one({'_id': str(user_id)})
            if not d:
                return None
            d.pop('_id', None)
            return d
        except Exception as e:
            logger.error(f'Failed to get profile for {user_id}: {e}')
            return None

    @staticmethod
    def set(user_id: str, data: Dict[str, Any]) -> bool:
        try:
            db = _get_db()
            now = datetime.utcnow().isoformat()
            payload = data.copy()
            # Avoid conflicts where payload already contains 'created_at' which
            # would clash with our $setOnInsert created_at below.
            payload.pop('created_at', None)
            payload['updated_at'] = now
            db[UserProfilesAdapter.COLL].update_one({'_id': str(user_id)}, {'$set': payload, '$setOnInsert': {'created_at': now}}, upsert=True)
            return True
        except Exception as e:
            logger.error(f'Failed to set profile for {user_id}: {e}')
            return False


class GiftcodeStateAdapter:
    COLL = 'giftcode_state'

    @staticmethod
    def get_state() -> Dict[str, Any]:
        try:
            db = _get_db()
            d = db[GiftcodeStateAdapter.COLL].find_one({'_id': 'giftcode_state'})
            if not d:
                return {}
            d.pop('_id', None)
            return d
        except Exception as e:
            logger.error(f'Failed to get giftcode state from Mongo: {e}')
            return {}

    @staticmethod
    def set_state(state: Dict[str, Any]) -> bool:
        try:
            db = _get_db()
            now = datetime.utcnow().isoformat()
            payload = state.copy()
            # Remove created_at from payload to avoid $set vs $setOnInsert conflict
            payload.pop('created_at', None)
            payload['updated_at'] = now
            db[GiftcodeStateAdapter.COLL].update_one({'_id': 'giftcode_state'}, {'$set': payload, '$setOnInsert': {'created_at': now}}, upsert=True)
            return True
        except Exception as e:
            logger.error(f'Failed to set giftcode state in Mongo: {e}')
            return False


# ============================================================================
# ALLIANCE DATA ADAPTERS - For storing all alliance member info
# ============================================================================

class AllianceMembersAdapter:
    """Stores alliance members with all their data (player IDs, levels, etc.)"""
    COLL = 'alliance_members'

    @staticmethod
    def upsert_member(fid: str, data: Dict[str, Any]) -> bool:
        """Insert or update a single alliance member"""
        try:
            db = _get_db()
            now = datetime.utcnow().isoformat()
            
            # Ensure _id is string fid
            data_copy = data.copy()
            data_copy['updated_at'] = now
            data_copy.pop('created_at', None)
            
            db[AllianceMembersAdapter.COLL].update_one(
                {'_id': str(fid)},
                {'$set': data_copy, '$setOnInsert': {'created_at': now}},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f'Failed to upsert alliance member {fid} in Mongo: {e}')
            return False

    @staticmethod
    def get_member(fid: str) -> Optional[Dict[str, Any]]:
        """Get a single alliance member"""
        try:
            db = _get_db()
            doc = db[AllianceMembersAdapter.COLL].find_one({'_id': str(fid)})
            if doc:
                doc.pop('_id', None)  # Remove MongoDB _id
            return doc
        except Exception as e:
            logger.error(f'Failed to get alliance member {fid} from Mongo: {e}')
            return None

    @staticmethod
    def get_all_members() -> list:
        """Get all alliance members"""
        try:
            db = _get_db()
            docs = list(db[AllianceMembersAdapter.COLL].find({}))
            for doc in docs:
                doc.pop('_id', None)  # Remove MongoDB _id
            return docs
        except Exception as e:
            logger.error(f'Failed to get all alliance members from Mongo: {e}')
            return []

    @staticmethod
    def delete_member(fid: str) -> bool:
        """Delete a single alliance member"""
        try:
            db = _get_db()
            result = db[AllianceMembersAdapter.COLL].delete_one({'_id': str(fid)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f'Failed to delete alliance member {fid} from Mongo: {e}')
            return False

    @staticmethod
    def clear_all() -> bool:
        """Clear all alliance members"""
        try:
            db = _get_db()
            db[AllianceMembersAdapter.COLL].delete_many({})
            logger.info('[Mongo] Cleared all alliance members')
            return True
        except Exception as e:
            logger.error(f'Failed to clear alliance members from Mongo: {e}')
            return False


class AllianceMetadataAdapter:
    """Stores alliance metadata (settings, config, etc.)"""
    COLL = 'alliance_metadata'

    @staticmethod
    def set_metadata(key: str, value: Any) -> bool:
        """Set alliance metadata"""
        try:
            db = _get_db()
            now = datetime.utcnow().isoformat()
            
            db[AllianceMetadataAdapter.COLL].update_one(
                {'_id': str(key)},
                {'$set': {'value': value, 'updated_at': now}, '$setOnInsert': {'created_at': now}},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f'Failed to set alliance metadata {key}: {e}')
            return False

    @staticmethod
    def get_metadata(key: str) -> Optional[Any]:
        """Get alliance metadata"""
        try:
            db = _get_db()
            doc = db[AllianceMetadataAdapter.COLL].find_one({'_id': str(key)})
            return doc.get('value') if doc else None
        except Exception as e:
            logger.error(f'Failed to get alliance metadata {key}: {e}')
            return None


class GiftCodesAdapter:
    """Adapter for managing gift codes in MongoDB (for gift_operationsapi cog)"""
    COLL = 'gift_codes'

    @staticmethod
    def get_all():
        """Get all gift codes as list of tuples: (code, date, validation_status)"""
        try:
            db = _get_db()
            docs = db[GiftCodesAdapter.COLL].find({})
            return [(d.get('_id'), d.get('date'), d.get('validation_status')) for d in docs]
        except Exception as e:
            logger.error(f'Failed to get all gift codes from Mongo: {e}')
            return []

    @staticmethod
    def insert(code: str, date: str, validation_status: str = 'pending') -> bool:
        """Insert a new gift code (ignores if already exists)"""
        try:
            db = _get_db()
            db[GiftCodesAdapter.COLL].update_one(
                {'_id': code},
                {'$set': {'date': date, 'validation_status': validation_status, 'created_at': datetime.utcnow().isoformat()}},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f'Failed to insert gift code {code}: {e}')
            return False

    @staticmethod
    def update_status(code: str, validation_status: str) -> bool:
        """Update validation status of a gift code"""
        try:
            db = _get_db()
            db[GiftCodesAdapter.COLL].update_one(
                {'_id': code},
                {'$set': {'validation_status': validation_status, 'updated_at': datetime.utcnow().isoformat()}}
            )
            return True
        except Exception as e:
            logger.error(f'Failed to update status for {code}: {e}')
            return False

    @staticmethod
    def delete(code: str) -> bool:
        """Delete a gift code"""
        try:
            db = _get_db()
            result = db[GiftCodesAdapter.COLL].delete_one({'_id': code})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f'Failed to delete gift code {code}: {e}')
            return False

    @staticmethod
    def clear_all() -> bool:
        """Clear all gift codes (use with caution)"""
        try:
            db = _get_db()
            db[GiftCodesAdapter.COLL].delete_many({})
            return True
        except Exception as e:
            logger.error(f'Failed to clear all gift codes: {e}')
            return False


class AutoRedeemSettingsAdapter:
    """Adapter for managing auto redeem settings in MongoDB"""
    COLL = 'auto_redeem_settings'

    @staticmethod
    def get_settings(guild_id: int) -> Optional[Dict[str, Any]]:
        """Get auto redeem settings for a guild"""
        try:
            db = _get_db()
            doc = db[AutoRedeemSettingsAdapter.COLL].find_one({'_id': str(guild_id)})
            if not doc:
                return None
            return {
                'enabled': bool(doc.get('enabled', False)),
                'updated_by': int(doc.get('updated_by', 0)),
                'updated_at': doc.get('updated_at')
            }
        except Exception as e:
            logger.error(f'Failed to get auto redeem settings for guild {guild_id}: {e}')
            return None

    @staticmethod
    def set_enabled(guild_id: int, enabled: bool, updated_by: int) -> bool:
        """Set auto redeem enabled/disabled state for a guild"""
        try:
            db = _get_db()
            now = datetime.utcnow().isoformat()
            db[AutoRedeemSettingsAdapter.COLL].update_one(
                {'_id': str(guild_id)},
                {
                    '$set': {
                        'guild_id': int(guild_id),
                        'enabled': bool(enabled),
                        'updated_by': int(updated_by),
                        'updated_at': now
                    },
                    '$setOnInsert': {'created_at': now}
                },
                upsert=True
            )
            logger.info(f'Set auto redeem enabled={enabled} for guild {guild_id}')
            return True
        except Exception as e:
            logger.error(f'Failed to set auto redeem settings for guild {guild_id}: {e}')
            return False


class AutoRedeemChannelsAdapter:
    """Adapter for managing auto redeem channel configuration in MongoDB"""
    COLL = 'auto_redeem_channels'

    @staticmethod
    def get_channel(guild_id: int) -> Optional[Dict[str, Any]]:
        """Get auto redeem channel configuration for a guild"""
        try:
            db = _get_db()
            doc = db[AutoRedeemChannelsAdapter.COLL].find_one({'_id': str(guild_id)})
            if not doc:
                return None
            return {
                'channel_id': int(doc.get('channel_id')),
                'added_by': int(doc.get('added_by', 0)),
                'added_at': doc.get('added_at')
            }
        except Exception as e:
            logger.error(f'Failed to get auto redeem channel for guild {guild_id}: {e}')
            return None

    @staticmethod
    def set_channel(guild_id: int, channel_id: int, added_by: int) -> bool:
        """Set auto redeem channel for a guild"""
        try:
            db = _get_db()
            now = datetime.utcnow().isoformat()
            db[AutoRedeemChannelsAdapter.COLL].update_one(
                {'_id': str(guild_id)},
                {
                    '$set': {
                        'guild_id': int(guild_id),
                        'channel_id': int(channel_id),
                        'added_by': int(added_by),
                        'added_at': now,
                        'updated_at': now
                    },
                    '$setOnInsert': {'created_at': now}
                },
                upsert=True
            )
            logger.info(f'Set auto redeem channel {channel_id} for guild {guild_id}')
            return True
        except Exception as e:
            logger.error(f'Failed to set auto redeem channel for guild {guild_id}: {e}')
            return False


class AutoRedeemMembersAdapter:
    """Adapter for managing auto-redeem members in MongoDB"""
    COLL = 'auto_redeem_members'

    @staticmethod
    def get_members(guild_id: int) -> list:
        """Get all auto-redeem members for a guild"""
        try:
            db = _get_db()
            docs = list(db[AutoRedeemMembersAdapter.COLL].find({'guild_id': int(guild_id)}))
            members = []
            for doc in docs:
                member = {
                    'fid': str(doc.get('fid')),
                    'nickname': doc.get('nickname', 'Unknown'),
                    'furnace_lv': int(doc.get('furnace_lv', 0)),
                    'avatar_image': doc.get('avatar_image', ''),
                    'added_by': int(doc.get('added_by', 0)),
                    'added_at': doc.get('added_at')
                }
                members.append(member)
            # Sort by furnace level descending
            members.sort(key=lambda x: x['furnace_lv'], reverse=True)
            return members
        except Exception as e:
            logger.error(f'Failed to get auto-redeem members for guild {guild_id}: {e}')
            return []

    @staticmethod
    def add_member(guild_id: int, fid: str, member_data: Dict[str, Any]) -> bool:
        """Add a member to auto-redeem list"""
        try:
            db = _get_db()
            now = datetime.utcnow().isoformat()
            
            # Prepare member document
            doc = {
                'guild_id': int(guild_id),
                'fid': str(fid),
                'nickname': member_data.get('nickname', 'Unknown'),
                'furnace_lv': int(member_data.get('furnace_lv', 0)),
                'avatar_image': member_data.get('avatar_image', ''),
                'added_by': int(member_data.get('added_by', 0)),
                'added_at': member_data.get('added_at', now),
                'updated_at': now
            }
            
            # Use composite key: guild_id + fid
            db[AutoRedeemMembersAdapter.COLL].update_one(
                {'guild_id': int(guild_id), 'fid': str(fid)},
                {'$set': doc, '$setOnInsert': {'created_at': now}},
                upsert=True
            )
            logger.info(f'Added auto-redeem member {fid} to guild {guild_id}')
            return True
        except Exception as e:
            logger.error(f'Failed to add auto-redeem member {fid} to guild {guild_id}: {e}')
            return False

    @staticmethod
    def remove_member(guild_id: int, fid: str) -> bool:
        """Remove a member from auto-redeem list"""
        try:
            db = _get_db()
            result = db[AutoRedeemMembersAdapter.COLL].delete_one(
                {'guild_id': int(guild_id), 'fid': str(fid)}
            )
            if result.deleted_count > 0:
                logger.info(f'Removed auto-redeem member {fid} from guild {guild_id}')
                return True
            return False
        except Exception as e:
            logger.error(f'Failed to remove auto-redeem member {fid} from guild {guild_id}: {e}')
            return False

    @staticmethod
    def member_exists(guild_id: int, fid: str) -> bool:
        """Check if member exists in auto-redeem list"""
        try:
            db = _get_db()
            doc = db[AutoRedeemMembersAdapter.COLL].find_one(
                {'guild_id': int(guild_id), 'fid': str(fid)}
            )
            return doc is not None
        except Exception as e:
            logger.error(f'Failed to check auto-redeem member {fid} in guild {guild_id}: {e}')
            return False

    @staticmethod
    def batch_member_exists(guild_id: int, fids: list) -> dict:
        """Check if multiple members exist in auto-redeem list (batch operation)
        
        Args:
            guild_id: Discord guild ID
            fids: List of FID strings to check
        
        Returns:
            Dictionary mapping FID -> bool (True if exists, False otherwise)
        """
        try:
            db = _get_db()
            # Single query to check all FIDs at once
            docs = db[AutoRedeemMembersAdapter.COLL].find(
                {'guild_id': int(guild_id), 'fid': {'$in': [str(fid) for fid in fids]}}
            )
            
            # Create set of existing FIDs
            existing_fids = {doc['fid'] for doc in docs}
            
            # Return dict with all FIDs
            return {str(fid): (str(fid) in existing_fids) for fid in fids}
        except Exception as e:
            logger.error(f'Failed to batch check auto-redeem members in guild {guild_id}: {e}')
            # Return all False on error
            return {str(fid): False for fid in fids}

    @staticmethod
    def remove_all_members(guild_id: int) -> bool:
        """Remove all members from auto-redeem list for a guild"""
        try:
            db = _get_db()
            result = db[AutoRedeemMembersAdapter.COLL].delete_many({'guild_id': int(guild_id)})
            logger.info(f'Removed {result.deleted_count} auto-redeem members from guild {guild_id}')
            return True
        except Exception as e:
            logger.error(f'Failed to remove all auto-redeem members from guild {guild_id}: {e}')
            return False


class WelcomeChannelAdapter:
    """Adapter for managing welcome channel settings in MongoDB"""
    COLL = 'welcome_channels'

    @staticmethod
    def get(guild_id: int) -> Optional[Dict[str, Any]]:
        """Get welcome channel settings for a guild"""
        try:
            db = _get_db()
            doc = db[WelcomeChannelAdapter.COLL].find_one({'_id': str(guild_id)})
            if not doc:
                return None
            return {
                'channel_id': int(doc.get('channel_id')),
                'enabled': bool(doc.get('enabled', True)),
                'bg_image_url': doc.get('bg_image_url')
            }
        except Exception as e:
            logger.error(f'Failed to get welcome channel for guild {guild_id}: {e}')
            return None

    @staticmethod
    def set(guild_id: int, channel_id: int, enabled: bool = True) -> bool:
        """Set/update welcome channel for a guild"""
        try:
            db = _get_db()
            now = datetime.utcnow().isoformat()
            db[WelcomeChannelAdapter.COLL].update_one(
                {'_id': str(guild_id)},
                {
                    '$set': {
                        'channel_id': int(channel_id),
                        'enabled': bool(enabled),
                        'updated_at': now
                    },
                    '$setOnInsert': {'created_at': now}
                },
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f'Failed to set welcome channel for guild {guild_id}: {e}')
            return False
    
    @staticmethod
    def set_bg_image(guild_id: int, bg_image_url: str) -> bool:
        """Set/update background image URL for a guild"""
        try:
            db = _get_db()
            now = datetime.utcnow().isoformat()
            db[WelcomeChannelAdapter.COLL].update_one(
                {'_id': str(guild_id)},
                {
                    '$set': {
                        'bg_image_url': str(bg_image_url),
                        'updated_at': now
                    },
                    '$setOnInsert': {'created_at': now}
                },
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f'Failed to set background image for guild {guild_id}: {e}')
            return False

    @staticmethod
    def delete(guild_id: int) -> bool:
        """Delete welcome channel configuration for a guild"""
        try:
            db = _get_db()
            result = db[WelcomeChannelAdapter.COLL].delete_one({'_id': str(guild_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f'Failed to delete welcome channel for guild {guild_id}: {e}')
            return False

    @staticmethod
    def get_all() -> list:
        """Get all configured welcome channels"""
        try:
            db = _get_db()
            docs = list(db[WelcomeChannelAdapter.COLL].find({'enabled': True}))
            return [{
                'guild_id': int(d.get('_id')),
                'channel_id': int(d.get('channel_id')),
                'enabled': bool(d.get('enabled', True))
            } for d in docs]
        except Exception as e:
            logger.error(f'Failed to get all welcome channels: {e}')
            return []

class AdminsAdapter:
    COLL = 'admins'

    @staticmethod
    def count() -> int:
        try:
            db = _get_db()
            return db[AdminsAdapter.COLL].count_documents({})
        except Exception:
            return 0

    @staticmethod
    def get(user_id: int) -> Optional[Dict[str, Any]]:
        try:
            db = _get_db()
            d = db[AdminsAdapter.COLL].find_one({'_id': str(user_id)})
            return d
        except Exception:
            return None

    @staticmethod
    def upsert(user_id: int, is_initial: int) -> bool:
        try:
            db = _get_db()
            now = datetime.utcnow().isoformat()
            db[AdminsAdapter.COLL].update_one(
                {'_id': str(user_id)},
                {'$set': {'is_initial': int(is_initial), 'updated_at': now}, '$setOnInsert': {'created_at': now}},
                upsert=True
            )
            return True
        except Exception:
            return False

class AlliancesAdapter:
    COLL = 'alliances'

    @staticmethod
    def get_all() -> list:
        try:
            db = _get_db()
            docs = list(db[AlliancesAdapter.COLL].find({}))
            return [{'alliance_id': int(d.get('alliance_id')), 'name': d.get('name'), 'discord_server_id': int(d.get('discord_server_id', 0))} for d in docs]
        except Exception:
            return []

    @staticmethod
    def find_by_name(name: str) -> Optional[Dict[str, Any]]:
        try:
            db = _get_db()
            d = db[AlliancesAdapter.COLL].find_one({'name': name})
            return d
        except Exception:
            return None

    @staticmethod
    def upsert(alliance_id: int, name: str, discord_server_id: int) -> bool:
        try:
            db = _get_db()
            now = datetime.utcnow().isoformat()
            db[AlliancesAdapter.COLL].update_one(
                {'_id': str(alliance_id)},
                {'$set': {'alliance_id': int(alliance_id), 'name': name, 'discord_server_id': int(discord_server_id), 'updated_at': now}, '$setOnInsert': {'created_at': now}},
                upsert=True
            )
            return True
        except Exception:
            return False

    @staticmethod
    def delete(alliance_id: int) -> bool:
        try:
            db = _get_db()
            res = db[AlliancesAdapter.COLL].delete_one({'_id': str(alliance_id)})
            return res.deleted_count > 0
        except Exception:
            return False

class AllianceSettingsAdapter:
    COLL = 'alliance_settings'

    @staticmethod
    def get(alliance_id: int) -> Optional[Dict[str, Any]]:
        try:
            db = _get_db()
            d = db[AllianceSettingsAdapter.COLL].find_one({'_id': str(alliance_id)})
            return d
        except Exception:
            return None

    @staticmethod
    def get_all() -> list:
        try:
            db = _get_db()
            docs = list(db[AllianceSettingsAdapter.COLL].find({}))
            return [{'alliance_id': int(d.get('_id')), 'channel_id': int(d.get('channel_id')), 'interval': int(d.get('interval'))} for d in docs]
        except Exception:
            return []

    @staticmethod
    def upsert(alliance_id: int, channel_id: int, interval: int, giftcodecontrol: int | None = None, giftcode_channel: int | None = None) -> bool:
        try:
            db = _get_db()
            now = datetime.utcnow().isoformat()
            payload = {'channel_id': int(channel_id), 'interval': int(interval)}
            if giftcodecontrol is not None:
                payload['giftcodecontrol'] = int(giftcodecontrol)
            if giftcode_channel is not None:
                payload['giftcode_channel'] = int(giftcode_channel)
            db[AllianceSettingsAdapter.COLL].update_one(
                {'_id': str(alliance_id)},
                {'$set': payload | {'updated_at': now}, '$setOnInsert': {'created_at': now}},
                upsert=True
            )
            return True
        except Exception:
            return False

    @staticmethod
    def delete(alliance_id: int) -> bool:
        try:
            db = _get_db()
            res = db[AllianceSettingsAdapter.COLL].delete_one({'_id': str(alliance_id)})
            return res.deleted_count > 0
        except Exception:
            return False


class FurnaceHistoryAdapter:
    COLLECTION = 'furnace_history'

    @staticmethod
    def insert(data: Dict[str, Any]) -> bool:
        try:
            db = _get_db()
            if db is None:
                return False
            
            if "change_date" not in data:
                data["change_date"] = datetime.utcnow()
                
            db[FurnaceHistoryAdapter.COLLECTION].insert_one(data)
            return True
        except Exception as e:
            logging.error(f"Error inserting furnace history: {e}")
            return False

    @staticmethod
    def get_recent_changes(days: int = 7, alliance_id: Optional[int] = None) -> list:
        try:
            db = _get_db()
            if db is None:
                return []
            
            match_stage = {
                "change_date": {
                    "$gte": datetime.utcnow() - timedelta(days=days)
                }
            }
            
            if alliance_id is not None:
                match_stage["alliance_id"] = int(alliance_id)
            
            pipeline = [
                {
                    "$match": match_stage
                },
                {
                    "$group": {
                        "_id": "$fid",
                        "nickname": {"$first": "$nickname"},
                        "total_growth": {"$sum": {"$subtract": ["$new_level", "$old_level"]}}
                    }
                },
                {
                    "$match": {
                        "total_growth": {"$gt": 0}
                    }
                },
                {
                    "$sort": {"total_growth": -1}
                }
            ]
            
            return list(db[FurnaceHistoryAdapter.COLLECTION].aggregate(pipeline))
        except Exception as e:
            logging.error(f"Error fetching furnace history: {e}")
            return []


class AllianceMonitoringAdapter:
    COLL = 'alliance_monitoring'

    @staticmethod
    def get_all_monitors() -> list:
        try:
            db = _get_db()
            docs = list(db[AllianceMonitoringAdapter.COLL].find({'enabled': 1}))
            return [{
                'guild_id': int(d.get('guild_id')),
                'alliance_id': int(d.get('alliance_id')),
                'channel_id': int(d.get('channel_id')),
                'enabled': int(d.get('enabled', 1)),
                'check_interval': int(d.get('check_interval', 240))
            } for d in docs]
        except Exception as e:
            logger.error(f"Error getting alliance monitors from Mongo: {e}")
            return []

    @staticmethod
    def upsert_monitor(guild_id: int, alliance_id: int, channel_id: int, enabled: int = 1, check_interval: int = 240) -> bool:
        try:
            db = _get_db()
            now = datetime.utcnow().isoformat()
            db[AllianceMonitoringAdapter.COLL].update_one(
                {'guild_id': int(guild_id), 'alliance_id': int(alliance_id)},
                {
                    '$set': {
                        'guild_id': int(guild_id),
                        'alliance_id': int(alliance_id),
                        'channel_id': int(channel_id),
                        'enabled': int(enabled),
                        'check_interval': int(check_interval),
                        'updated_at': now
                    },
                    '$setOnInsert': {'created_at': now}
                },
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error upserting alliance monitor: {e}")
            return False

    @staticmethod
    def delete_monitor(guild_id: int, alliance_id: int) -> bool:
        try:
            db = _get_db()
            res = db[AllianceMonitoringAdapter.COLL].delete_one({'guild_id': int(guild_id), 'alliance_id': int(alliance_id)})
            return res.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting alliance monitor: {e}")
            return False


class ServerAllianceAdapter:
    """Adapter for managing server-alliance assignments in MongoDB"""
    COLL = 'server_alliances'

    @staticmethod
    def set_alliance(guild_id: int, alliance_id: int, assigned_by: int) -> bool:
        """Assign an alliance to a Discord server"""
        try:
            db = _get_db()
            now = datetime.utcnow().isoformat()
            db[ServerAllianceAdapter.COLL].update_one(
                {'_id': str(guild_id)},
                {
                    '$set': {
                        'guild_id': int(guild_id),
                        'alliance_id': int(alliance_id),
                        'assigned_by': int(assigned_by),
                        'assigned_at': now,
                        'updated_at': now
                    },
                    '$setOnInsert': {'created_at': now}
                },
                upsert=True
            )
            logger.info(f'Assigned alliance {alliance_id} to server {guild_id}')
            return True
        except Exception as e:
            logger.error(f'Failed to assign alliance to server {guild_id}: {e}')
            return False

    @staticmethod
    def get_alliance(guild_id: int) -> Optional[int]:
        """Get the assigned alliance ID for a Discord server"""
        try:
            db = _get_db()
            doc = db[ServerAllianceAdapter.COLL].find_one({'_id': str(guild_id)})
            if doc:
                return int(doc.get('alliance_id'))
            return None
        except Exception as e:
            logger.error(f'Failed to get alliance for server {guild_id}: {e}')
            return None

    @staticmethod
    def remove_alliance(guild_id: int) -> bool:
        """Remove alliance assignment from a Discord server"""
        try:
            db = _get_db()
            result = db[ServerAllianceAdapter.COLL].delete_one({'_id': str(guild_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f'Failed to remove alliance from server {guild_id}: {e}')
            return False

    @staticmethod
    def get_all() -> list:
        """Get all server-alliance mappings"""
        try:
            db = _get_db()
            docs = list(db[ServerAllianceAdapter.COLL].find({}))
            return [{
                'guild_id': int(d.get('guild_id')),
                'alliance_id': int(d.get('alliance_id')),
                'assigned_by': int(d.get('assigned_by')),
                'assigned_at': d.get('assigned_at')
            } for d in docs]
        except Exception as e:
            logger.error(f'Failed to get all server-alliance mappings: {e}')
            return []

    @staticmethod
    def set_password(guild_id: int, password: str, set_by: int) -> bool:
        """Set member list password for a Discord server"""
        try:
            db = _get_db()
            now = datetime.utcnow().isoformat()
            db[ServerAllianceAdapter.COLL].update_one(
                {'_id': str(guild_id)},
                {
                    '$set': {
                        'member_list_password': str(password),
                        'password_set_by': int(set_by),
                        'password_set_at': now,
                        'updated_at': now
                    },
                    '$setOnInsert': {'created_at': now, 'guild_id': int(guild_id)}
                },
                upsert=True
            )
            logger.info(f'Set member list password for server {guild_id}')
            
            # Invalidate all existing auth sessions when password changes
            try:
                from db.mongo_adapters import AuthSessionsAdapter
                AuthSessionsAdapter.invalidate_all_sessions(guild_id)
            except Exception as session_error:
                logger.warning(f'Failed to invalidate auth sessions for guild {guild_id}: {session_error}')
            
            return True
        except Exception as e:
            logger.error(f'Failed to set password for server {guild_id}: {e}')
            return False

    @staticmethod
    def get_password(guild_id: int) -> Optional[str]:
        """Get member list password for a Discord server"""
        try:
            db = _get_db()
            doc = db[ServerAllianceAdapter.COLL].find_one({'_id': str(guild_id)})
            if doc:
                return doc.get('member_list_password')
            return None
        except Exception as e:
            logger.error(f'Failed to get password for server {guild_id}: {e}')
            return None

    @staticmethod
    def verify_password(guild_id: int, password: str) -> bool:
        """Verify member list password for a Discord server"""
        try:
            stored_password = ServerAllianceAdapter.get_password(guild_id)
            if stored_password is None:
                return False
            return str(password) == str(stored_password)
        except Exception as e:
            logger.error(f'Failed to verify password for server {guild_id}: {e}')
            return False


class AuthSessionsAdapter:
    """Adapter for managing authentication sessions for /manage command"""
    COLL = 'auth_sessions'
    SESSION_DURATION_DAYS = 7

    @staticmethod
    def create_session(guild_id: int, user_id: int, password_hash: str) -> bool:
        """Create or update an authentication session for a user"""
        try:
            db = _get_db()
            now = datetime.utcnow()
            expires_at = now + timedelta(days=AuthSessionsAdapter.SESSION_DURATION_DAYS)
            
            db[AuthSessionsAdapter.COLL].update_one(
                {'_id': f"{guild_id}:{user_id}"},
                {
                    '$set': {
                        'guild_id': int(guild_id),
                        'user_id': int(user_id),
                        'password_hash': str(password_hash),
                        'created_at': now.isoformat(),
                        'expires_at': expires_at.isoformat(),
                        'updated_at': now.isoformat()
                    }
                },
                upsert=True
            )
            logger.info(f'Created auth session for user {user_id} in guild {guild_id}')
            return True
        except Exception as e:
            logger.error(f'Failed to create auth session for user {user_id} in guild {guild_id}: {e}')
            return False

    @staticmethod
    def get_session(guild_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Get authentication session for a user"""
        try:
            db = _get_db()
            doc = db[AuthSessionsAdapter.COLL].find_one({'_id': f"{guild_id}:{user_id}"})
            if doc:
                doc.pop('_id', None)
            return doc
        except Exception as e:
            logger.error(f'Failed to get auth session for user {user_id} in guild {guild_id}: {e}')
            return None

    @staticmethod
    def is_session_valid(guild_id: int, user_id: int, current_password: str) -> bool:
        """Check if user has a valid authentication session"""
        try:
            session = AuthSessionsAdapter.get_session(guild_id, user_id)
            if not session:
                return False
            
            # Check if session has expired
            expires_at = datetime.fromisoformat(session.get('expires_at'))
            if datetime.utcnow() > expires_at:
                logger.info(f'Auth session expired for user {user_id} in guild {guild_id}')
                return False
            
            # Check if password has changed (compare with current password)
            stored_password_hash = session.get('password_hash')
            if str(current_password) != str(stored_password_hash):
                logger.info(f'Password changed, invalidating session for user {user_id} in guild {guild_id}')
                return False
            
            return True
        except Exception as e:
            logger.error(f'Failed to validate auth session for user {user_id} in guild {guild_id}: {e}')
            return False

    @staticmethod
    def invalidate_all_sessions(guild_id: int) -> bool:
        """Invalidate all authentication sessions for a guild (called when password changes)"""
        try:
            db = _get_db()
            result = db[AuthSessionsAdapter.COLL].delete_many({'guild_id': int(guild_id)})
            logger.info(f'Invalidated {result.deleted_count} auth sessions for guild {guild_id}')
            return True
        except Exception as e:
            logger.error(f'Failed to invalidate auth sessions for guild {guild_id}: {e}')
            return False

    @staticmethod
    def cleanup_expired_sessions() -> int:
        """Remove all expired sessions from the database"""
        try:
            db = _get_db()
            now = datetime.utcnow().isoformat()
            result = db[AuthSessionsAdapter.COLL].delete_many({
                'expires_at': {'$lt': now}
            })
            logger.info(f'Cleaned up {result.deleted_count} expired auth sessions')
            return result.deleted_count
        except Exception as e:
            logger.error(f'Failed to cleanup expired auth sessions: {e}')
            return 0


class RecordsAdapter:
    """Adapter for managing custom player records in MongoDB"""
    COLL = 'custom_records'

    @staticmethod
    def create_record(guild_id: int, record_name: str, created_by: int) -> bool:
        """Create a new custom record"""
        try:
            db = _get_db()
            now = datetime.utcnow().isoformat()
            
            # Check if record already exists
            existing = db[RecordsAdapter.COLL].find_one({
                '_id': f"{guild_id}:{record_name}"
            })
            
            if existing:
                logger.warning(f'Record {record_name} already exists for guild {guild_id}')
                return False
            
            db[RecordsAdapter.COLL].insert_one({
                '_id': f"{guild_id}:{record_name}",
                'guild_id': int(guild_id),
                'record_name': str(record_name),
                'created_by': int(created_by),
                'created_at': now,
                'updated_at': now,
                'members': []
            })
            logger.info(f'Created record {record_name} for guild {guild_id}')
            return True
        except Exception as e:
            logger.error(f'Failed to create record {record_name} for guild {guild_id}: {e}')
            return False

    @staticmethod
    def delete_record(guild_id: int, record_name: str) -> bool:
        """Delete a custom record"""
        try:
            db = _get_db()
            result = db[RecordsAdapter.COLL].delete_one({
                '_id': f"{guild_id}:{record_name}"
            })
            if result.deleted_count > 0:
                logger.info(f'Deleted record {record_name} from guild {guild_id}')
                return True
            return False
        except Exception as e:
            logger.error(f'Failed to delete record {record_name} from guild {guild_id}: {e}')
            return False

    @staticmethod
    def get_record(guild_id: int, record_name: str) -> Optional[dict]:
        """Get a specific record"""
        try:
            db = _get_db()
            doc = db[RecordsAdapter.COLL].find_one({
                '_id': f"{guild_id}:{record_name}"
            })
            return doc
        except Exception as e:
            logger.error(f'Failed to get record {record_name} for guild {guild_id}: {e}')
            return None

    @staticmethod
    def get_all_records(guild_id: int) -> list:
        """Get all records for a guild"""
        try:
            db = _get_db()
            docs = list(db[RecordsAdapter.COLL].find({'guild_id': int(guild_id)}))
            return [{
                'record_name': d.get('record_name'),
                'created_by': d.get('created_by'),
                'created_at': d.get('created_at'),
                'member_count': len(d.get('members', []))
            } for d in docs]
        except Exception as e:
            logger.error(f'Failed to get all records for guild {guild_id}: {e}')
            return []

    @staticmethod
    def add_member_to_record(guild_id: int, record_name: str, fid: str, member_data: dict) -> bool:
        """Add a member to a record"""
        try:
            db = _get_db()
            now = datetime.utcnow().isoformat()
            
            # Check if member already exists in record
            record = db[RecordsAdapter.COLL].find_one({
                '_id': f"{guild_id}:{record_name}"
            })
            
            if not record:
                logger.warning(f'Record {record_name} not found for guild {guild_id}')
                return False
            
            # Remove existing member if present
            members = [m for m in record.get('members', []) if m.get('fid') != str(fid)]
            
            # Add new member data
            member_entry = {
                'fid': str(fid),
                'nickname': member_data.get('nickname', 'Unknown'),
                'furnace_lv': int(member_data.get('furnace_lv', 0)),
                'avatar_image': member_data.get('avatar_image', ''),
                'added_at': now,
                'added_by': member_data.get('added_by', 0)
            }
            members.append(member_entry)
            
            # Update record
            db[RecordsAdapter.COLL].update_one(
                {'_id': f"{guild_id}:{record_name}"},
                {
                    '$set': {
                        'members': members,
                        'updated_at': now
                    }
                }
            )
            logger.info(f'Added member {fid} to record {record_name} in guild {guild_id}')
            return True
        except Exception as e:
            logger.error(f'Failed to add member {fid} to record {record_name}: {e}')
            return False

    @staticmethod
    def remove_member_from_record(guild_id: int, record_name: str, fid: str) -> bool:
        """Remove a member from a record"""
        try:
            db = _get_db()
            now = datetime.utcnow().isoformat()
            
            record = db[RecordsAdapter.COLL].find_one({
                '_id': f"{guild_id}:{record_name}"
            })
            
            if not record:
                return False
            
            # Remove member
            members = [m for m in record.get('members', []) if m.get('fid') != str(fid)]
            
            # Update record
            db[RecordsAdapter.COLL].update_one(
                {'_id': f"{guild_id}:{record_name}"},
                {
                    '$set': {
                        'members': members,
                        'updated_at': now
                    }
                }
            )
            logger.info(f'Removed member {fid} from record {record_name} in guild {guild_id}')
            return True
        except Exception as e:
            logger.error(f'Failed to remove member {fid} from record {record_name}: {e}')
            return False

    @staticmethod
    def get_record_members(guild_id: int, record_name: str) -> list:
        """Get all members in a record"""
        try:
            record = RecordsAdapter.get_record(guild_id, record_name)
            if record:
                return record.get('members', [])
            return []
        except Exception as e:
            logger.error(f'Failed to get members for record {record_name}: {e}')
            return []

    @staticmethod
    def rename_record(guild_id: int, old_name: str, new_name: str) -> bool:
        """Rename a record"""
        try:
            db = _get_db()
            
            # Check if new name already exists
            existing = db[RecordsAdapter.COLL].find_one({
                '_id': f"{guild_id}:{new_name}"
            })
            
            if existing:
                logger.warning(f'Record {new_name} already exists for guild {guild_id}')
                return False
            
            # Get old record
            old_record = db[RecordsAdapter.COLL].find_one({
                '_id': f"{guild_id}:{old_name}"
            })
            
            if not old_record:
                return False
            
            # Create new record with new name
            old_record['_id'] = f"{guild_id}:{new_name}"
            old_record['record_name'] = new_name
            old_record['updated_at'] = datetime.utcnow().isoformat()
            
            db[RecordsAdapter.COLL].insert_one(old_record)
            
            # Delete old record
            db[RecordsAdapter.COLL].delete_one({
                '_id': f"{guild_id}:{old_name}"
            })
            
            logger.info(f'Renamed record {old_name} to {new_name} in guild {guild_id}')
            return True
        except Exception as e:
            logger.error(f'Failed to rename record {old_name} to {new_name}: {e}')
            return False


class GiftCodeRedemptionAdapter:
    """Adapter for tracking gift code redemptions per server"""
    COLL = 'giftcode_redemptions'
    
    @staticmethod
    def track_redemption(guild_id: int, code: str, fid: str, status: str) -> bool:
        """
        Track a gift code redemption attempt
        
        Args:
            guild_id: Discord server ID
            code: Gift code that was redeemed
            fid: Player FID
            status: Redemption status ('success' or 'failed')
        """
        try:
            db = _get_db()
            now = datetime.utcnow().isoformat()
            
            # Create unique document ID per guild+code
            doc_id = f"{guild_id}:{code}"
            
            # Add redemption to array and update stats
            db[GiftCodeRedemptionAdapter.COLL].update_one(
                {'_id': doc_id},
                {
                    '$push': {
                        'redemptions': {
                            'fid': str(fid),
                            'redeemed_at': now,
                            'status': status
                        }
                    },
                    '$inc': {
                        f'stats.{status}': 1,
                        'stats.total_attempts': 1
                    },
                    '$set': {
                        'guild_id': int(guild_id),
                        'code': str(code),
                        'last_redeemed_at': now,
                        'updated_at': now
                    },
                    '$setOnInsert': {'created_at': now}
                },
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f'Failed to track redemption for {code} in guild {guild_id}: {e}')
            return False
    
    @staticmethod
    def get_code_stats(guild_id: int, code: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics for a specific code in a server
        
        Returns:
            {
                'total_attempts': int,
                'success': int,
                'failed': int,
                'unique_users': int,
                'last_redeemed_at': str
            }
        """
        try:
            db = _get_db()
            doc_id = f"{guild_id}:{code}"
            doc = db[GiftCodeRedemptionAdapter.COLL].find_one({'_id': doc_id})
            
            if not doc:
                return None
            
            # Count unique users
            redemptions = doc.get('redemptions', [])
            unique_fids = set(r['fid'] for r in redemptions if r.get('status') == 'success')
            
            stats = doc.get('stats', {})
            return {
                'total_attempts': stats.get('total_attempts', 0),
                'success': stats.get('success', 0),
                'failed': stats.get('failed', 0),
                'unique_users': len(unique_fids),
                'last_redeemed_at': doc.get('last_redeemed_at')
            }
        except Exception as e:
            logger.error(f'Failed to get stats for {code} in guild {guild_id}: {e}')
            return None
    
    @staticmethod
    def get_all_stats(guild_id: int) -> list:
        """
        Get statistics for all codes in a server
        
        Returns list of:
            {
                'code': str,
                'total_attempts': int,
                'success': int,
                'failed': int,
                'unique_users': int,
                'last_redeemed_at': str
            }
        """
        try:
            db = _get_db()
            docs = list(db[GiftCodeRedemptionAdapter.COLL].find({'guild_id': int(guild_id)}))
            
            results = []
            for doc in docs:
                redemptions = doc.get('redemptions', [])
                unique_fids = set(r['fid'] for r in redemptions if r.get('status') == 'success')
                stats = doc.get('stats', {})
                
                results.append({
                    'code': doc.get('code'),
                    'total_attempts': stats.get('total_attempts', 0),
                    'success': stats.get('success', 0),
                    'failed': stats.get('failed', 0),
                    'unique_users': len(unique_fids),
                    'last_redeemed_at': doc.get('last_redeemed_at')
                })
            
            # Sort by most used
            results.sort(key=lambda x: x['unique_users'], reverse=True)
            return results
        except Exception as e:
            logger.error(f'Failed to get all stats for guild {guild_id}: {e}')
            return []
    
    @staticmethod
    def get_top_codes(guild_id: int, limit: int = 10) -> list:
        """Get most-used gift codes in a server"""
        try:
            all_stats = GiftCodeRedemptionAdapter.get_all_stats(guild_id)
            return all_stats[:limit]
        except Exception as e:
            logger.error(f'Failed to get top codes for guild {guild_id}: {e}')
            return []


class BirthdayChannelAdapter:
    """Adapter for storing birthday wishes channel configuration per guild"""
    COLL = 'birthday_channels'
    
    @staticmethod
    def get(guild_id: int) -> Optional[int]:
        """Get birthday channel ID for a guild"""
        try:
            db = _get_db()
            doc = db[BirthdayChannelAdapter.COLL].find_one({'_id': int(guild_id)})
            return doc.get('channel_id') if doc else None
        except Exception as e:
            logger.error(f'Failed to get birthday channel for guild {guild_id}: {e}')
            return None
    
    @staticmethod
    def set(guild_id: int, channel_id: int) -> bool:
        """Set birthday channel ID for a guild"""
        try:
            db = _get_db()
            db[BirthdayChannelAdapter.COLL].update_one(
                {'_id': int(guild_id)},
                {'$set': {'channel_id': int(channel_id), 'updated_at': datetime.utcnow().isoformat()}},
                upsert=True
            )
            logger.info(f'Set birthday channel for guild {guild_id} to {channel_id}')
            return True
        except Exception as e:
            logger.error(f'Failed to set birthday channel for guild {guild_id}: {e}')
            return False
    
    @staticmethod
    def remove(guild_id: int) -> bool:
        """Remove birthday channel configuration for a guild"""
        try:
            db = _get_db()
            db[BirthdayChannelAdapter.COLL].delete_one({'_id': int(guild_id)})
            logger.info(f'Removed birthday channel for guild {guild_id}')
            return True
        except Exception as e:
            logger.error(f'Failed to remove birthday channel for guild {guild_id}: {e}')
            return False


class PersistentViewsAdapter:
    """Adapter for managing persistent Discord view registrations in MongoDB"""
    COLL = 'persistent_views'
    
    @staticmethod
    def register_view(guild_id: int, channel_id: int, message_id: int, view_type: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Register a persistent view for a message
        
        Args:
            guild_id: Discord guild ID
            channel_id: Discord channel ID
            message_id: Discord message ID
            view_type: Type of view (memberlist, giftcode, birthday, birthdaywish, help)
            metadata: Optional metadata (e.g., alliance_id for memberlist, birthday_user_ids for birthdaywish)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            db = _get_db()
            now = datetime.utcnow().isoformat()
            
            doc = {
                'guild_id': int(guild_id),
                'channel_id': int(channel_id),
                'message_id': int(message_id),
                'view_type': str(view_type),
                'metadata': metadata or {},
                'updated_at': now
            }
            
            db[PersistentViewsAdapter.COLL].update_one(
                {'_id': str(message_id)},
                {'$set': doc, '$setOnInsert': {'created_at': now}},
                upsert=True
            )
            logger.info(f'Registered {view_type} view for message {message_id} in guild {guild_id}')
            return True
        except Exception as e:
            logger.error(f'Failed to register view for message {message_id}: {e}')
            return False
    
    @staticmethod
    def get_all_views() -> list:
        """Get all registered persistent views
        
        Returns:
            List of view registration documents
        """
        try:
            db = _get_db()
            docs = list(db[PersistentViewsAdapter.COLL].find({}))
            
            results = []
            for doc in docs:
                results.append({
                    'guild_id': int(doc.get('guild_id')),
                    'channel_id': int(doc.get('channel_id')),
                    'message_id': int(doc.get('message_id')),
                    'view_type': doc.get('view_type'),
                    'metadata': doc.get('metadata', {}),
                    'created_at': doc.get('created_at'),
                    'updated_at': doc.get('updated_at')
                })
            
            return results
        except Exception as e:
            logger.error(f'Failed to get all persistent views: {e}')
            return []
    
    @staticmethod
    def get_views_by_guild(guild_id: int) -> list:
        """Get all registered persistent views for a specific guild
        
        Args:
            guild_id: Discord guild ID
        
        Returns:
            List of view registration documents for the guild
        """
        try:
            db = _get_db()
            docs = list(db[PersistentViewsAdapter.COLL].find({'guild_id': int(guild_id)}))
            
            results = []
            for doc in docs:
                results.append({
                    'guild_id': int(doc.get('guild_id')),
                    'channel_id': int(doc.get('channel_id')),
                    'message_id': int(doc.get('message_id')),
                    'view_type': doc.get('view_type'),
                    'metadata': doc.get('metadata', {}),
                    'created_at': doc.get('created_at'),
                    'updated_at': doc.get('updated_at')
                })
            
            return results
        except Exception as e:
            logger.error(f'Failed to get persistent views for guild {guild_id}: {e}')
            return []
    
    @staticmethod
    def unregister_view(message_id: int) -> bool:
        """Unregister a persistent view
        
        Args:
            message_id: Discord message ID
        
        Returns:
            True if view was removed, False otherwise
        """
        try:
            db = _get_db()
            result = db[PersistentViewsAdapter.COLL].delete_one({'_id': str(message_id)})
            
            if result.deleted_count > 0:
                logger.info(f'Unregistered view for message {message_id}')
                return True
            return False
        except Exception as e:
            logger.error(f'Failed to unregister view for message {message_id}: {e}')
            return False
    
    @staticmethod
    def view_exists(message_id: int) -> bool:
        """Check if a view is registered for a message
        
        Args:
            message_id: Discord message ID
        
        Returns:
            True if view exists, False otherwise
        """
        try:
            db = _get_db()
            doc = db[PersistentViewsAdapter.COLL].find_one({'_id': str(message_id)})
            return doc is not None
        except Exception as e:
            logger.error(f'Failed to check if view exists for message {message_id}: {e}')
            return False
    
    @staticmethod
    def get_view(message_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific view registration
        
        Args:
            message_id: Discord message ID
        
        Returns:
            View registration document or None
        """
        try:
            db = _get_db()
            doc = db[PersistentViewsAdapter.COLL].find_one({'_id': str(message_id)})
            
            if not doc:
                return None
            
            return {
                'guild_id': int(doc.get('guild_id')),
                'channel_id': int(doc.get('channel_id')),
                'message_id': int(doc.get('message_id')),
                'view_type': doc.get('view_type'),
                'metadata': doc.get('metadata', {}),
                'created_at': doc.get('created_at'),
                'updated_at': doc.get('updated_at')
            }
        except Exception as e:
            logger.error(f'Failed to get view for message {message_id}: {e}')
            return None



class AutoTranslateAdapter:
    """MongoDB adapter for auto-translate configurations"""
    COLL = 'auto_translate_configs'
    
    @staticmethod
    def create_config(guild_id: int, config: dict) -> Optional[str]:
        """Create a new translation configuration
        
        Args:
            guild_id: Discord guild ID
            config: Configuration dictionary with all settings
            
        Returns:
            Configuration ID as string, or None if failed
        """
        try:
            db = _get_db()
            if db is None:
                return None
            
            config['guild_id'] = int(guild_id)
            config['enabled'] = True
            config['created_at'] = datetime.utcnow().isoformat()
            
            result = db[AutoTranslateAdapter.COLL].insert_one(config)
            logger.info(f'Created auto-translate config for guild {guild_id}')
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f'Failed to create auto-translate config: {e}')
            return None
    
    @staticmethod
    def get_config(config_id: str) -> Optional[dict]:
        """Get a specific configuration by ID"""
        try:
            db = _get_db()
            if db is None:
                return None
            
            from bson.objectid import ObjectId
            doc = db[AutoTranslateAdapter.COLL].find_one({'_id': ObjectId(config_id)})
            if doc:
                doc['config_id'] = str(doc.pop('_id'))
            return doc
        except Exception as e:
            logger.error(f'Failed to get auto-translate config {config_id}: {e}')
            return None
    
    @staticmethod
    def get_guild_configs(guild_id: int) -> list:
        """Get all configurations for a guild"""
        try:
            db = _get_db()
            if db is None:
                return []
            
            docs = list(db[AutoTranslateAdapter.COLL].find({'guild_id': int(guild_id)}))
            for doc in docs:
                doc['config_id'] = str(doc.pop('_id'))
            return docs
        except Exception as e:
            logger.error(f'Failed to get auto-translate configs for guild {guild_id}: {e}')
            return []
    
    @staticmethod
    def get_configs_for_channel(channel_id: int) -> list:
        """Get all active configurations monitoring a specific channel"""
        try:
            db = _get_db()
            if db is None:
                return []
            
            docs = list(db[AutoTranslateAdapter.COLL].find({
                'source_channel_id': int(channel_id),
                'enabled': True
            }))
            for doc in docs:
                doc['config_id'] = str(doc.pop('_id'))
            return docs
        except Exception as e:
            logger.error(f'Failed to get auto-translate configs for channel {channel_id}: {e}')
            return []
    
    @staticmethod
    def update_config(config_id: str, updates: dict) -> bool:
        """Update a configuration"""
        try:
            db = _get_db()
            if db is None:
                return False
            
            from bson.objectid import ObjectId
            updates['updated_at'] = datetime.utcnow().isoformat()
            result = db[AutoTranslateAdapter.COLL].update_one(
                {'_id': ObjectId(config_id)},
                {'$set': updates}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f'Failed to update auto-translate config {config_id}: {e}')
            return False
    
    @staticmethod
    def delete_config(config_id: str) -> bool:
        """Delete a configuration"""
        try:
            db = _get_db()
            if db is None:
                return False
            
            from bson.objectid import ObjectId
            result = db[AutoTranslateAdapter.COLL].delete_one({'_id': ObjectId(config_id)})
            logger.info(f'Deleted auto-translate config {config_id}')
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f'Failed to delete auto-translate config {config_id}: {e}')
            return False
    
    @staticmethod
    def toggle_config(config_id: str, enabled: bool) -> bool:
        """Enable/disable a configuration"""
        return AutoTranslateAdapter.update_config(config_id, {'enabled': enabled})
