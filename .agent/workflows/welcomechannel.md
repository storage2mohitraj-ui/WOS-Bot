---
description: Set up welcome channel for new member greetings
---

# Welcome Channel Setup Workflow

This workflow guides you through setting up the welcome channel feature that automatically sends personalized welcome messages with custom images when new members join your Discord server.

## Prerequisites

- Bot must have MongoDB configured (MONGO_URI environment variable)
- You need Administrator permissions in the Discord server
- Bot must have permissions to send messages and upload files in the welcome channel

## Setup Steps

1. **Choose a Welcome Channel**
   - Decide which channel should receive welcome messages
   - Ensure the bot has permissions to send messages in that channel

2. **Set the Welcome Channel**
   - Run the slash command: `/setwelcomechannel`
   - Select the channel from the dropdown
   - You should see a confirmation message

3. **Test the Welcome System**
   - Have a test user join the server (or use an alt account)
   - Check that a welcome message appears in the configured channel
   - Verify the welcome image shows:
     - User's profile picture in a circle
     - Welcome message with username and server name
     - Member count

4. **Remove Welcome Channel (Optional)**
   - To disable welcome messages: `/removewelcomechannel`
   - This will stop sending welcome messages for new members

## Welcome Message Format

When a member joins, they will receive:
- **Image**: Custom-generated image with their profile picture
- **Message**: "Hi @username Welcome to the {server name}🥳"
- **Member Count**: "you are the {count}th member!"

## Troubleshooting

- **No welcome message sent**: Check that MongoDB is configured and the channel still exists
- **Image not loading**: Ensure the bot has permission to upload files
- **Command not visible**: Make sure you have Administrator permissions
