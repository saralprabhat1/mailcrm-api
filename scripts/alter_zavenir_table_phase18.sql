-- scripts/alter_zavenir_table_phase18.sql
-- Phase 18 migration — adds forwarded-sender, auto-assignment, and
-- conversation-timeline columns to the existing zavenir_requirements table.
--
-- HOW TO USE:
--   1. Open Supabase -> SQL Editor -> New Query
--   2. Paste this entire file and click Run
--   3. Safe to re-run — uses IF NOT EXISTS

ALTER TABLE zavenir_requirements
    ADD COLUMN IF NOT EXISTS sender_name             TEXT,
    ADD COLUMN IF NOT EXISTS assigned_to             TEXT,
    ADD COLUMN IF NOT EXISTS assigned_to_confidence  TEXT,
    ADD COLUMN IF NOT EXISTS conversation_timeline   TEXT;

COMMENT ON COLUMN zavenir_requirements.sender_name IS
    'Display name of the original (customer) sender, extracted from the forwarded email header.';

COMMENT ON COLUMN zavenir_requirements.assigned_to IS
    'Zavenir employee the deal appears to be assigned to, derived from the forward recipients and forwarder note.';

COMMENT ON COLUMN zavenir_requirements.assigned_to_confidence IS
    'Confidence in assigned_to: "high" (recipient + assignment language found), "low" (recipient only), or null.';

COMMENT ON COLUMN zavenir_requirements.conversation_timeline IS
    'AI-generated sequential summary of the email thread, one line per message: [Date | Sender | Company] -> summary.';
