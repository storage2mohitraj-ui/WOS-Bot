# Stop Alliance Monitor Feature

## Overview
Added a new button in the Remote Access feature that allows bot owners to remotely stop alliance monitors that are currently active for any server.

## Changes Made

### 1. Added "Stop Monitor" Button
**File**: `cogs/remote_access.py`
- Added a new "Stop Monitor" button (🛑) in the `show_server_management` method
- Positioned on row 2, next to the "Alliance Monitor" button
- Button style: `ButtonStyle.danger` (red)
- Custom ID: `remote_stop_alliance_monitor_{guild.id}`

### 2. Added Button Callback
- Added callback handler in the button loop to trigger `stop_alliance_monitor` when clicked
- Maps `remote_stop_alliance_monitor_` prefix to the new method

### 3. Implemented `stop_alliance_monitor` Method
**Location**: `cogs/remote_access.py` (line ~1730)

**Features**:
- Checks for active alliance monitors for the selected server
- Queries the `alliance_monitoring` table to find monitors with `enabled = 1`
- Displays a dropdown menu with all active monitors showing:
  - Alliance name
  - Channel name
  - Alliance ID
- Provides confirmation dialog before stopping
- Updates both SQLite and MongoDB databases
- Sets `enabled = 0` in the database to disable monitoring
- Sends confirmation notifications to both:
  - The user (ephemeral message)
  - The monitoring channel (public notification)

### 4. User Flow
1. User clicks "Stop Monitor" button from server management
2. System displays all active monitors for that server
3. User selects a monitor from the dropdown
4. Confirmation dialog appears with monitor details
5. User confirms or cancels
6. If confirmed:
   - Database updated (`enabled = 0`)
   - Success message sent to user
   - Notification posted in monitoring channel
   - Monitoring stops immediately

### 5. Database Operations
**SQLite** (`settings.sqlite`):
```sql
UPDATE alliance_monitoring 
SET enabled = 0, updated_at = CURRENT_TIMESTAMP
WHERE guild_id = ? AND alliance_id = ? AND channel_id = ?
```

**MongoDB** (if enabled):
- Calls `AllianceMonitoringAdapter.upsert_monitor(guild_id, alliance_id, channel_id, enabled=0)`

### 6. Error Handling
- Handles missing alliance system
- Handles database connection errors
- Validates that monitors exist before showing dropdown
- Gracefully handles missing channels
- Provides clear error messages for all failure scenarios

### 7. Benefits
- **Remote Control**: Bot owners can manage monitors from anywhere
- **Quick Access**: No need to navigate through multiple commands
- **Confirmation**: Prevents accidental stops with confirmation dialog
- **Transparency**: Sends notifications to the channel when monitoring stops
- **Persistence**: Can restart monitoring anytime using the "Alliance Monitor" button

## Testing Checklist
- [ ] Verify button appears in remote access server management
- [ ] Test with no active monitors (should show error message)
- [ ] Test with single active monitor
- [ ] Test with multiple active monitors
- [ ] Test confirmation flow (both confirm and cancel)
- [ ] Verify database updates (both SQLite and MongoDB)
- [ ] Test channel notification posting
- [ ] Verify monitoring actually stops after button press

## Future Enhancements
- Add "Stop All Monitors" button for bulk operations
- Add statistics showing when monitoring was stopped
- Add ability to pause/resume monitoring without losing configuration
