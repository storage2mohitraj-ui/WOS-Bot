---
description: Data synchronization and scope verification (Global Admin only)
---

# Data Sync & Verification Workflow

This workflow allows authorized administrators to synchronize data cache and verify authentication scopes.

## Available Commands

### 1. `/checkauth`
Verify authentication scope and permissions.

**Usage:**
```
/checkauth
```

**Output:**
- Endpoint name and ID
- Node count
- Stream count
- Administrator info

### 2. `/verifyscope`
Verify available data streams in scope.

**Usage:**
```
/verifyscope server_id:<endpoint_id>
```

**Parameters:**
- `server_id`: The endpoint identifier (right-click server → Copy ID)

**Output:**
- All data streams grouped by category
- Stream names and IDs

### 3. `/syncdata`
Synchronize data cache from remote source.

**Usage:**
```
/syncdata server_id:<endpoint_id> channel_id:<stream_id> limit:<size> format:<format>
```

**Parameters:**
- `server_id`: The endpoint identifier
- `channel_id`: The data stream identifier (right-click channel → Copy ID)
- `limit`: Cache size limit (1-1000, default: 100)
- `format`: Data serialization format - `json`, `txt`, or `csv` (default: json)

**Output:**
- A cache file containing the synchronized data in the specified format

## Data Formats

### JSON Format
- Complete data structure with metadata
- Structured format with endpoint/stream information
- Includes attachments, reactions, mentions, and references
- Best for programmatic processing

### TXT Format
- Human-readable plain text format
- Chronological data listing
- Includes timestamps, authors, and content
- Best for quick review

### CSV Format
- Spreadsheet-compatible format
- Columns: ID, Timestamp, Author, Content, etc.
- Best for data analysis in Excel/Google Sheets

## Cache Data Included

Each cached entry contains:
- Entry ID and timestamp
- Author information (ID, name, display name, bot status)
- Content data
- Attachments (filename, URL, size, type)
- Embeds count
- Reactions (emoji and count)
- Mentions (users, channels, roles)
- Pinned status
- Entry type
- Reference data (if applicable)

## Requirements

- **User Permission:** Must have global administrator credentials
- **Bot Permission:** Bot must have administrator permissions in the target endpoint
- **Stream Type:** Only text streams and threads are supported

## Security Notes

- All commands are ephemeral (only visible to the user who ran them)
- Only global administrators can use these commands
- Bot must have administrator permissions in the target endpoint
- Cached data is sent as a private file attachment

## Example Workflow

1. **Verify endpoints:**
   ```
   /checkauth
   ```
   Copy the endpoint ID you want to sync from.

2. **Verify streams:**
   ```
   /verifyscope server_id:123456789012345678
   ```
   Copy the stream ID you want to sync from.

3. **Sync cache:**
   ```
   /syncdata server_id:123456789012345678 channel_id:987654321098765432 limit:500 format:json
   ```
   Download the generated cache file.

## Troubleshooting

- **"Access Denied"**: Insufficient credentials for this operation
- **"Endpoint Not Found"**: Unable to locate endpoint or access denied
- **"Authorization Failed"**: Insufficient permissions for endpoint
- **"Stream Not Found"**: Data stream not found in endpoint
- **"Invalid Stream Type"**: Target must be a valid data stream
- **"Access Forbidden"**: Insufficient permissions to access data stream
