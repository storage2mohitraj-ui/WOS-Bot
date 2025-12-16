## Problem
- On Render, local SQLite files are ephemeral; after redeploy, `/settings` behaves like first run: re-registers admin, alliances disappear, gift codes list resets, auto-redemption fails.
- Current cogs primarily read/write `db/*.sqlite`. MongoDB support exists but is not wired into settings/alliance/gift flows.

## Approach
- Use MongoDB as source of truth and hydrate SQLite only if needed. Conditionally read/write Mongo when `MONGO_URI` is set; otherwise fall back to SQLite.
- Minimal, targeted changes to existing cogs; follow current patterns and avoid broad refactors.

## Changes
1. Add Mongo adapters (extend existing file):
   - `AdminsAdapter` (collection: `admins`): store admin IDs and `is_initial` flag.
   - `AlliancesAdapter` (collection: `alliances`): store `alliance_id`, `name`, `discord_server_id`.
   - `AllianceSettingsAdapter` (collection: `alliance_settings`): map `alliance_id` → `channel_id`, `interval`, `giftcodecontrol`, `giftcode_channel`.

2. Alliance Cog (`DISCORD BOT/cogs/alliance.py`):
   - In `settings(...)`:
     - If Mongo enabled, load admin via `AdminsAdapter`; skip first-time SQLite admin insert; create admin in Mongo on first run.
     - Build menu as before.
   - In `view_alliances(...)`:
     - If Mongo enabled, list alliances via `AlliancesAdapter` and member counts via `AllianceMembersAdapter`; read interval from `AllianceSettingsAdapter`.
   - In create/edit/delete flows:
     - Mirror SQLite writes to Mongo adapters (upsert on create/edit; delete associated docs on delete).

3. Gift Operations (`DISCORD BOT/cogs/gift_operations.py`):
   - In `list_gift_codes(...)`:
     - If Mongo enabled, read codes via `GiftCodesAdapter.get_all()` and build the embed; fall back to SQLite if Mongo disabled.
     - When fetching from website, upsert into Mongo via `GiftCodesAdapter.insert(...)`.
   - Where status is updated/deleted, call `GiftCodesAdapter.update_status(...)`/`delete(...)` in addition to existing SQLite logic when Mongo is enabled.

4. Optional hydration (safety net):
   - On cog init, if `mongo_enabled()` and corresponding SQLite tables are empty, hydrate local SQLite from Mongo adapters for legacy flows that still expect SQLite.

## Validation
- Set `MONGO_URI` and `MONGO_DB_NAME` on Render.
- Open `/settings`: no re-registration; existing admins and alliances appear from Mongo.
- Add/edit/delete alliance: verify Mongo collections reflect changes and survive redeploy.
- Gift codes listing: shows validated codes pulled from Mongo; website fetch upserts to Mongo.
- Auto-redemption settings: persist `interval`, `giftcodecontrol`, `giftcode_channel` in Mongo; flows continue to work after redeploy.

## Files
- `DISCORD BOT/db/mongo_adapters.py`: add new adapters.
- `DISCORD BOT/cogs/alliance.py`: wire Mongo reads/writes in settings, alliance CRUD, view.
- `DISCORD BOT/cogs/gift_operations.py`: wire Mongo reads/writes in list and status flows.
- Keep SQLite fallbacks intact for environments without Mongo.

## Rollout
- Implement changes, restart bot, test in a staging guild on Render.
- Confirm persistence across at least one redeploy.