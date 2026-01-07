# Message Extractor Feature

## Overview
The Message Extractor is a powerful tool for global administrators to extract messages from any Discord server where the bot has administrator permissions. This feature is restricted to users with `is_initial = 1` in the admin table.

## Commands

### 1. `/listservers`
**Description:** Lists all servers where the bot has administrator permissions.

**Permission Required:** Global Administrator

**Usage:**
```
/listservers
```

**Output:**
- Server name and ID
- Member count
- Number of text channels
- Server owner information

---

### 2. `/listchannels`
**Description:** Lists all text channels in a specific server.

**Permission Required:** Global Administrator

**Usage:**
```
/listchannels server_id:<server_id>
```

**Parameters:**
- `server_id` (required): The Discord server ID

**How to get Server ID:**
1. Enable Developer Mode in Discord (User Settings → Advanced → Developer Mode)
2. Right-click on the server icon
3. Click "Copy ID"

**Output:**
- All text channels grouped by category
- Channel names and IDs

---

### 3. `/extractmessages`
**Description:** Extracts messages from a specific channel in any server where the bot is administrator.

**Permission Required:** Global Administrator

**Usage:**
```
/extractmessages server_id:<server_id> channel_id:<channel_id> limit:<number> format:<format>
```

**Parameters:**
- `server_id` (required): The Discord server ID
- `channel_id` (required): The Discord channel ID
- `limit` (optional): Number of messages to extract (1-1000, default: 100)
- `format` (optional): Output format - `json`, `txt`, or `csv` (default: json)

**How to get Channel ID:**
1. Enable Developer Mode in Discord
2. Right-click on the channel
3. Click "Copy ID"

**Output:**
- A downloadable file containing the extracted messages in the specified format

---

## Output Formats

### JSON Format
- **Best for:** Programmatic processing, data analysis, archival
- **Contains:** Complete message data with full metadata
- **Structure:**
  ```json
  {
    "metadata": {
      "server_id": "...",
      "server_name": "...",
      "channel_id": "...",
      "channel_name": "...",
      "extraction_time": "...",
      "requested_limit": 100,
      "actual_count": 95
    },
    "messages": [...]
  }
  ```

### TXT Format
- **Best for:** Quick review, human readability
- **Contains:** Chronological message listing with timestamps
- **Structure:**
  ```
  [2024-12-16 12:00:00] Username (123456789)
    Message content here
    📎 Attachments: 1
      - image.png (https://...)
    👍 Reactions: 👍 (5), ❤️ (3)
  ```

### CSV Format
- **Best for:** Spreadsheet analysis (Excel, Google Sheets)
- **Contains:** Tabular data with key message information
- **Columns:**
  - Message ID
  - Timestamp
  - Author ID
  - Author Name
  - Author Display Name
  - Is Bot
  - Content
  - Attachments Count
  - Embeds Count
  - Reactions Count
  - Pinned
  - Type
  - Reply To

---

## Message Data Included

Each extracted message contains:

- **Message ID:** Unique identifier for the message
- **Timestamp:** When the message was created (ISO 8601 format)
- **Edited Timestamp:** When the message was last edited (if applicable)
- **Author Information:**
  - User ID
  - Username
  - Display name
  - Bot status
- **Content:** The message text
- **Attachments:**
  - Filename
  - URL
  - Size (bytes)
  - Content type (MIME type)
- **Embeds:** Count of embedded content
- **Reactions:**
  - Emoji
  - Count
- **Mentions:**
  - User mentions
  - Channel mentions
  - Role mentions
- **Pinned Status:** Whether the message is pinned
- **Message Type:** Type of message (default, reply, etc.)
- **Reply Reference:** If the message is a reply, includes the original message ID and channel ID

---

## Security & Permissions

### User Requirements
- Must be a **Global Administrator** (`is_initial = 1` in the admin table)
- Regular administrators cannot use these commands

### Bot Requirements
- Bot must have **Administrator** permissions in the target server
- Bot must have access to the target channel

### Privacy & Security
- All commands are **ephemeral** (only visible to the user who ran them)
- Extracted data is sent as a **private file attachment**
- No data is stored on the bot's servers
- Only global administrators can access this feature

---

## Example Workflow

### Step 1: Find Available Servers
```
/listservers
```
This will show you all servers where the bot has administrator permissions. Copy the server ID you want to extract from.

### Step 2: Find Channels in the Server
```
/listchannels server_id:123456789012345678
```
This will show you all text channels in that server. Copy the channel ID you want to extract from.

### Step 3: Extract Messages
```
/extractmessages server_id:123456789012345678 channel_id:987654321098765432 limit:500 format:json
```
This will extract up to 500 messages from the specified channel in JSON format.

### Step 4: Download and Process
The bot will send you a file attachment containing the extracted messages. Download it and process as needed.

---

## Error Messages & Troubleshooting

### "❌ Access Denied"
**Cause:** You are not a global administrator.

**Solution:** Contact the bot owner to grant you global administrator permissions.

---

### "❌ Server Not Found"
**Cause:** The bot is not in the specified server, or the server ID is incorrect.

**Solution:** 
- Verify the server ID is correct
- Use `/listservers` to see available servers
- Ensure the bot is still in the server

---

### "❌ Insufficient Permissions"
**Cause:** The bot doesn't have administrator permissions in the target server.

**Solution:** 
- Grant the bot administrator permissions in the server
- Contact the server owner to update bot permissions

---

### "❌ Channel Not Found"
**Cause:** The channel ID is incorrect or the channel doesn't exist.

**Solution:**
- Verify the channel ID is correct
- Use `/listchannels` to see available channels
- Ensure the channel hasn't been deleted

---

### "❌ Invalid Channel Type"
**Cause:** The specified channel is not a text channel or thread.

**Solution:** 
- Only text channels and threads are supported
- Voice channels, categories, and other channel types cannot be used

---

### "❌ Access Forbidden"
**Cause:** The bot can't read messages in that channel.

**Solution:**
- Check channel-specific permissions
- Ensure the bot has "Read Message History" permission in that channel

---

## Use Cases

### 1. Server Migration
Extract all messages from channels before migrating to a new server or platform.

### 2. Data Analysis
Analyze message patterns, user engagement, or content trends.

### 3. Archival
Create backups of important conversations or announcements.

### 4. Compliance & Moderation
Review message history for compliance or moderation purposes.

### 5. Content Recovery
Recover messages from channels that may be deleted or archived.

---

## Limitations

- **Maximum messages per extraction:** 1,000
- **Rate limits:** Subject to Discord API rate limits
- **Channel types:** Only text channels and threads are supported
- **Permissions:** Requires bot administrator permissions in the target server
- **User access:** Restricted to global administrators only

---

## Technical Details

### File Naming Convention
```
messages_<server_id>_<channel_id>_<timestamp>.json
messages_<server_id>_<channel_id>_<timestamp>.txt
messages_<server_id>_<channel_id>_<timestamp>.csv
```

Example: `messages_123456789_987654321_20241216_120000.json`

### Timestamp Format
All timestamps use ISO 8601 format: `YYYY-MM-DDTHH:MM:SS.mmmmmm+00:00`

Example: `2024-12-16T12:00:00.123456+00:00`

### Character Encoding
All files use UTF-8 encoding to support international characters and emojis.

---

## Support

For issues or questions about this feature, contact the bot owner or a global administrator.

## Version
- **Feature Version:** 1.0.0
- **Created:** December 2024
- **Last Updated:** December 2024
