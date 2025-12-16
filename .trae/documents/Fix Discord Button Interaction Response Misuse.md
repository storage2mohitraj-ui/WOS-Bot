## Root Cause
- After `interaction.response.defer(...)`, callbacks must use `interaction.followup.send(...)` (or `edit_original_response(...)`). Several callbacks call `interaction.response.send_message(...)` after deferring, which raises `InteractionResponded` and is logged as “Ignoring exception in view … for item <Button … label='List Gift Codes'>”.
- Concrete example: `DISCORD BOT\cogs\gift_operations.py:2242` defers, then `response.send_message(...)` at `DISCORD BOT\cogs\gift_operations.py:2274`.

## Targeted Fixes
- Replace every `interaction.response.send_message(...)` that occurs after a prior `interaction.response.defer(...)` in the same callback with `interaction.followup.send(...)` and preserve `ephemeral=True`.
- Where an edit is intended post-defer, use `interaction.edit_original_response(...)` or `interaction.followup.send(...)` consistently instead of `interaction.response.*`.
- Keep existing try/except structure and ephemeral behavior; do not add comments.

## Files To Update
- Primary: `f:\STARK-whiteout survival bot\DISCORD BOT\cogs\gift_operations.py` (fix `list_gift_codes` fallback) — refs `2190–2354`, especially `2242` and `2274`.
- Mirror: `f:\STARK-whiteout survival bot\BOT 2\cogs\gift_operations.py` if similar patterns exist.
- Additional cogs with the same pattern (sample anchors):
  - `f:\STARK-whiteout survival bot\DISCORD BOT\cogs\alliance_member_operations.py` (~1638 defer, ~1644 send_message)
  - `f:\STARK-whiteout survival bot\DISCORD BOT\cogs\changes.py` (multiple: ~685–690, ~703–708, ~761–766, ~845–850, ~863–868, ~934–938, ~987–992, ~1071–1076, ~1089–1094, ~1160–1164, ~1205–1209, ~1353–1357)
  - Potentially: `attendance.py`, `attendance_report.py`, `backup_operations.py`, `bear_trap_editor.py`, `bear_trap.py`, `minister_menu.py`, `minister_schedule.py`, `olddb.py`

## Implementation Steps
1. Update `list_gift_codes(...)` to use `interaction.followup.send(...)` in the “no codes found” branch.
2. Sweep all cogs for `response.defer` followed by `response.send_message` and replace with `followup.send`.
3. Ensure any response edits post-defer use `edit_original_response(...)` or `followup.send(...)` consistently.

## Validation
- Reproduce by clicking “📋 List Gift Codes” in the gift menu; expect an ephemeral embed rather than an exception.
- Manually test other affected buttons (delete, alliance usage, settings) for both success and error branches.
- Confirm logs show no “Ignoring exception in view …” entries for these interactions.

## Rollout
- Make changes in both `DISCORD BOT` and `BOT 2` trees where applicable.
- Restart the bot(s) and validate in a staging guild before production.