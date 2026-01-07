# 🎁 Gift Code System v1.4.0 Features Implementation

## 📋 Overview
This document outlines the new features from v1.4.0 that will be integrated into your Discord bot's gift code system.

## 🆕 New Features from v1.4.0

### 1. **VIP-Only Code Support** ✨
- Detect and handle codes that require VIP status
- Show warnings when attempting to redeem VIP codes without VIP
- Track VIP status of alliance members
- Skip non-VIP members when auto-redeeming VIP codes

### 2. **Minimum Furnace Level Codes** 🏭
- Support for codes requiring specific furnace levels
- Validate furnace levels before redemption attempts
- Auto-skip members below required furnace level
- Display furnace level requirements in code embeds

### 3. **Reactivated Code Handling** 🔄
- Detect when a code has been reactivated
- Clear previous redemption records for reactivated codes
- Auto-retry redemption for previously failed codes
- Track reactivation history

### 4. **Enhanced Code Validation** ✅
- API-received codes validated locally on reception
- Improved validation logic to reduce false positives
- Better error messages for validation failures
- Validation queue with priority handling

### 5. **Configurable Redemption Order** 🎯
- Prioritize specific alliances for redemption
- Custom redemption order per guild
- VIP/high-priority members get codes first
- Reduces timeout issues from sequential processing

### 6. **Improved CAPTCHA Handling** 🤖
- Better "Too Frequent" error detection
- Proper rate-limit backoff strategy
- Session pool management (multiple sessions)
- Automatic CAPTCHA solver integration

### 7. **Better Admin Notifications** 📬
- Gift channel auto-posting for API codes
- Consolidated embeds during bulk redemption
- Detailed failure reports post-redemption
- Real-time progress updates

## 🔧 Implementation Details

### Code Structure Changes

#### 1. VIP Detection System
```python
# Add to ManageGiftCode class
def is_vip_required(self, giftcode):
    """Check if code requires VIP status"""
    # Implementation details below

async def check_member_vip_status(self, fid):
    """Fetch VIP status from player data"""
    # Implementation details below
```

#### 2. Furnace Level Validator
```python
# Add to ManageGiftCode class
def get_furnace_requirement(self, giftcode):
    """Extract furnace level requirement from API response"""
    # Implementation details below

def meets_furnace_requirement(self, member_level, required_level):
    """Check if member meets furnace requirement"""
    # Implementation details below
```

#### 3. Reactivation Detector
```python
# Add to GiftOperations class
async def detect_code_reactivation(self, giftcode):
    """Detect if code was previously expired and now active"""
    # Implementation details below

async def clear_redemption_history(self, giftcode):
    """Clear redemption records for reactivated code"""
    # Implementation details below
```

#### 4. Redemption Priority Queue
```python
# Add to ManageGiftCode class
class RedemptionPriorityQueue:
    """Manage redemption order with priorities"""
    def __init__(self):
        self.high_priority = []  # VIP/whitelisted alliances
        self.normal_priority = []
        
    def add_alliance(self, alliance_id, priority='normal'):
        """Add alliance to queue with priority"""
        
    def get_next(self):
        """Get next alliance in priority order"""
```

### Database Schema Updates

#### New Tables
```sql
-- VIP tracking
CREATE TABLE IF NOT EXISTS member_vip_status (
    fid TEXT PRIMARY KEY,
    is_vip INTEGER DEFAULT 0,
    vip_level INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Code requirements
CREATE TABLE IF NOT EXISTS gift_code_requirements (
    code TEXT PRIMARY KEY,
    vip_required INTEGER DEFAULT 0,
    min_furnace_level INTEGER DEFAULT 0,
    reactivated INTEGER DEFAULT 0,
    reactivation_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Redemption priority
CREATE TABLE IF NOT EXISTS alliance_redemption_priority (
    guild_id INTEGER,
    alliance_id INTEGER,
    priority_level INTEGER DEFAULT 0,
    PRIMARY KEY (guild_id, alliance_id)
);
```

### API Response Handling

#### Enhanced Error Detection
```python
# New error codes to handle
VIP_REQUIRED_ERRORS = [
    'RECHARGE_MONEY_VIP',
    'VIP_REQUIREMENT_NOT_MET',
    'NEED_VIP_STATUS'
]

FURNACE_LEVEL_ERRORS = [
    'FURNACE_LEVEL_TOO_LOW',
    'LEVEL_REQUIREMENT_NOT_MET'
]

CODE_REACTIVATED_INDICATORS = [
    # When a previously expired code becomes valid
    'was_expired_now_active'
]
```

## 📦 Files to Modify

1. **cogs/manage_giftcode.py**
   - Add VIP validation
   - Add furnace level checking
   - Implement priority queue
   - Enhanced error handling

2. **cogs/gift_operations.py**
   - Add code reactivation detection
   - Update validation queue
   - Improve API validation

3. **giftcode_poster.py**
   - Post to gift channels on API codes
   - Better notification handling

4. **db/mongo_adapters.py** (if using MongoDB)
   - Add adapters for new tables
   - VIP status adapter
   - Code requirements adapter
   - Priority adapter

## 🧪 Testing Checklist

- [ ] VIP code rejection for non-VIP members
- [ ] Furnace level validation
- [ ] Code reactivation detection
- [ ] Priority queue ordering
- [ ] Rate limit backoff
- [ ] Gift channel posting
- [ ] Consolidated admin embeds

## 🚀 Deployment Steps

1. Backup current database
2. Apply schema updates
3. Update code files
4. Test in development
5. Deploy to production
6. Monitor logs for issues

## 📊 Expected Improvements

- **Reduced Failed Redemptions**: Auto-skip ineligible members
- **Faster Processing**: Priority queue reduces timeouts
- **Better UX**: Clear error messages about requirements
- **Smarter Retries**: Reactivation detection prevents duplicate work

## 🔗 Related Files

- `cogs/manage_giftcode.py` - Main gift code management
- `cogs/gift_operations.py` - Gift code operations and validation
- `gift_codes.py` - Code scraping and fetching
- `giftcode_poster.py` - Auto-posting new codes

## 📝 Notes

- All features maintain backward compatibility
- Existing functionality preserved
- Gradual rollout recommended
- Monitor v1.4.0 releases for updates

---

**Implementation Status**: Planning Phase
**Target Version**: v1.4.0+
**Priority**: High
