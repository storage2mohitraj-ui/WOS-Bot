"""
Cleanup Script for Auto-Redeem Members
========================================

This script removes any test users or members with invalid FIDs from the auto-redeem system.

Valid FID Requirements:
- Must be exactly 9 digits
- Must be numeric only
- No special characters or letters

Usage:
    python cleanup_invalid_fids.py

"""

import sqlite3
import sys
from datetime import datetime

def cleanup_sqlite():
    """Clean up invalid FIDs from SQLite database"""
    print("=" * 60)
    print("Auto-Redeem Members Cleanup - SQLite")
    print("=" * 60)
    
    conn = sqlite3.connect('db/giftcode.sqlite')
    cursor = conn.cursor()
    
    # Get all members
    cursor.execute('SELECT guild_id, fid, nickname FROM auto_redeem_members')
    members = cursor.fetchall()
    
    if not members:
        print("✅ No auto-redeem members found in database.")
        conn.close()
        return
    
    print(f"\n📊 Total members in database: {len(members)}\n")
    
    # Validate and find invalid FIDs
    invalid_members = []
    valid_members = []
    
    for guild_id, fid, nickname in members:
        fid_str = str(fid) if fid else ""
        
        # Check if FID is valid (must be exactly 9 digits)
        is_valid = (
            fid_str and 
            len(fid_str) == 9 and 
            fid_str.isdigit()
        )
        
        if is_valid:
            valid_members.append((guild_id, fid, nickname))
        else:
            invalid_members.append((guild_id, fid, nickname))
    
    print(f"✅ Valid members: {len(valid_members)}")
    print(f"❌ Invalid members: {len(invalid_members)}\n")
    
    if invalid_members:
        print("Invalid Members Found:")
        print("-" * 60)
        for guild_id, fid, nickname in invalid_members:
            print(f"  Guild: {guild_id}")
            print(f"  FID: '{fid}' (Length: {len(str(fid)) if fid else 0})")
            print(f"  Nickname: {nickname}")
            print("-" * 60)
        
        # Ask for confirmation
        response = input("\n⚠️  Remove these invalid members? (yes/no): ").strip().lower()
        
        if response == 'yes':
            removed_count = 0
            for guild_id, fid, nickname in invalid_members:
                try:
                    cursor.execute(
                        'DELETE FROM auto_redeem_members WHERE guild_id = ? AND fid = ?',
                        (guild_id, fid)
                    )
                    removed_count += 1
                    print(f"  ✅ Removed: {nickname} (FID: {fid})")
                except Exception as e:
                    print(f"  ❌ Error removing {nickname}: {e}")
            
            conn.commit()
            print(f"\n✅ Successfully removed {removed_count} invalid member(s) from SQLite!")
        else:
            print("\n⏭️  Cleanup cancelled. No changes made.")
    else:
        print("✅ All members have valid FIDs! No cleanup needed.")
    
    conn.close()

def cleanup_mongodb():
    """Clean up invalid FIDs from MongoDB"""
    print("\n" + "=" * 60)
    print("Auto-Redeem Members Cleanup - MongoDB")
    print("=" * 60)
    
    try:
        from db.mongo_adapters import mongo_enabled, AutoRedeemMembersAdapter, _get_db
        
        if not mongo_enabled():
            print("ℹ️  MongoDB is not enabled. Skipping MongoDB cleanup.")
            return
        
        if not AutoRedeemMembersAdapter:
            print("⚠️  AutoRedeemMembersAdapter not available. Skipping MongoDB cleanup.")
            return
        
        # Get database connection
        db = _get_db()
        if not db:
            print("❌ Could not connect to MongoDB. Skipping MongoDB cleanup.")
            return
        
        # Get all auto-redeem members
        collection = db[AutoRedeemMembersAdapter.COLL]
        all_members = list(collection.find({}))
        
        if not all_members:
            print("✅ No auto-redeem members found in MongoDB.")
            return
        
        print(f"\n📊 Total members in MongoDB: {len(all_members)}\n")
        
        # Validate and find invalid FIDs
        invalid_members = []
        valid_members = []
        
        for member in all_members:
            guild_id = member.get('guild_id')
            fid = member.get('fid', '')
            nickname = member.get('nickname', 'Unknown')
            
            fid_str = str(fid) if fid else ""
            
            # Check if FID is valid
            is_valid = (
                fid_str and 
                len(fid_str) == 9 and 
                fid_str.isdigit()
            )
            
            if is_valid:
                valid_members.append(member)
            else:
                invalid_members.append(member)
        
        print(f"✅ Valid members: {len(valid_members)}")
        print(f"❌ Invalid members: {len(invalid_members)}\n")
        
        if invalid_members:
            print("Invalid Members Found in MongoDB:")
            print("-" * 60)
            for member in invalid_members:
                print(f"  Guild: {member.get('guild_id')}")
                print(f"  FID: '{member.get('fid')}' (Length: {len(str(member.get('fid', ''))) if member.get('fid') else 0})")
                print(f"  Nickname: {member.get('nickname', 'Unknown')}")
                print("-" * 60)
            
            # Ask for confirmation
            response = input("\n⚠️  Remove these invalid members from MongoDB? (yes/no): ").strip().lower()
            
            if response == 'yes':
                removed_count = 0
                for member in invalid_members:
                    try:
                        collection.delete_one({
                            'guild_id': member.get('guild_id'),
                            'fid': member.get('fid')
                        })
                        removed_count += 1
                        print(f"  ✅ Removed: {member.get('nickname')} (FID: {member.get('fid')})")
                    except Exception as e:
                        print(f"  ❌ Error removing {member.get('nickname')}: {e}")
                
                print(f"\n✅ Successfully removed {removed_count} invalid member(s) from MongoDB!")
            else:
                print("\n⏭️  Cleanup cancelled. No changes made to MongoDB.")
        else:
            print("✅ All MongoDB members have valid FIDs! No cleanup needed.")
    
    except ImportError as e:
        print(f"⚠️  Could not import MongoDB adapters: {e}")
        print("ℹ️  Skipping MongoDB cleanup.")
    except Exception as e:
        print(f"❌ Error during MongoDB cleanup: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main cleanup function"""
    print("\n" + "=" * 60)
    print("Auto-Redeem Members - Invalid FID Cleanup")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    print("\n📋 This script will:")
    print("  1. Scan all auto-redeem members in SQLite and MongoDB")
    print("  2. Identify members with invalid FIDs (not exactly 9 digits)")
    print("  3. Ask for confirmation before removing invalid entries\n")
    
    try:
        # Clean up SQLite
        cleanup_sqlite()
        
        # Clean up MongoDB
        cleanup_mongodb()
        
        print("\n" + "=" * 60)
        print("✅ Cleanup Complete!")
        print("=" * 60)
        print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Cleanup interrupted by user. Exiting...")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during cleanup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
