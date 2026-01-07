# Fix for id_channel.py

## Issue
The `_upsert_member_from_api` function is broken with undefined variables (guild_id, user_id, log_file, details).
The `log_action` method is also missing, causing exceptions.

## Solution
Replace the broken `_upsert_member_from_api` function (lines 75-100) with:

```python
    def _upsert_member_from_api(self, fid: int, nickname: str, furnace_lv: int, kid, stove_lv_content, alliance_id: int, avatar_image=None) -> bool:
        """
        Insert or update member data from API response
        Returns True if successful, False otherwise
        """
        try:
            # Prepare member document
            member_doc = {
                'fid': str(fid),
                'nickname': nickname,
                'furnace_lv': int(furnace_lv) if furnace_lv is not None else 0,
                'stove_lv': int(furnace_lv) if furnace_lv is not None else 0,
                'stove_lv_content': stove_lv_content,
                'kid': kid,
                'alliance': int(alliance_id),
                'alliance_id': int(alliance_id),
                'avatar_image': avatar_image,
            }
            
            # Try MongoDB first
            try:
                if mongo_enabled() and AllianceMembersAdapter is not None:
                    result = AllianceMembersAdapter.upsert_member(str(fid), member_doc)
                    if result:
                        return True
            except Exception:
                pass
            
            # Fallback to SQLite
            try:
                with sqlite3.connect('db/users.sqlite') as users_db:
                    cursor = users_db.cursor()
                    
                    # Create table if not exists
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS users (
                            fid TEXT PRIMARY KEY,
                            nickname TEXT,
                            furnace_lv INTEGER,
                            stove_lv_content TEXT,
                            kid TEXT,
                            alliance INTEGER,
                            avatar_image TEXT
                        )
                    """)
                    
                    # Upsert member
                    cursor.execute("""
                        INSERT OR REPLACE INTO users 
                        (fid, nickname, furnace_lv, stove_lv_content, kid, alliance, avatar_image)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        str(fid),
                        nickname,
                        furnace_lv,
                        stove_lv_content,
                        kid,
                        alliance_id,
                        avatar_image
                    ))
                    users_db.commit()
                    return True
            except Exception as e:
                print(f"[ID_CHANNEL] Failed to save member {fid}: {e}")
                return False
                
        except Exception as e:
            print(f"[ID_CHANNEL] Error in _upsert_member_from_api: {e}")
            return False
```

## Add log_action method
Add this method after the `_upsert_member_from_api` function:

```python
    async def log_action(self, action_type: str, user_id: int, guild_id: int, details: dict):
        """Log ID channel actions to file"""
        try:
            log_file_path = os.path.join(self.log_directory, 'id_channel_log.txt')
            with open(log_file_path, 'a', encoding='utf-8') as log_file:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                log_file.write(f"\n[{timestamp}] {action_type}\n")
                log_file.write(f"User ID: {user_id}\n")
                log_file.write(f"Guild ID: {guild_id}\n")
                log_file.write("Details:\n")
                for key, value in details.items():
                    log_file.write(f"  {key}: {value}\n")
                log_file.write(f"{'='*50}\n")
        except Exception as e:
            print(f"[ID_CHANNEL] Failed to log action: {e}")
```

## Remove duplicate error message
In the outer exception handler (line 330-332), change to:

```python
        except Exception as e:
            # Log error silently - inner handler already sent user message
            pass
```
