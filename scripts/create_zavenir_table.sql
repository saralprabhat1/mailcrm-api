-- scripts/create_zavenir_table.sql
-- Creates the zavenir_requirements table in Supabase.
--
-- HOW TO USE:
--   1. Open Supabase → SQL Editor → New Query
--   2. Paste this entire file and click Run
--   3. The table will be created (safe to re-run — uses IF NOT EXISTS)
--
-- Or print to console from terminal (Windows / Mac / Linux):
--   type scripts\create_zavenir_table.sql    (Windows cmd)
--   cat scripts/create_zavenir_table.sql     (PowerShell / bash)

CREATE TABLE IF NOT EXISTS zavenir_requirements (

    -- Primary key — auto-incremented by Supabase
    id                  BIGINT          GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Pipeline-assigned unique identifier (e.g. ZAV-20260609-A1B2C3-01)
    req_id              TEXT            UNIQUE,

    -- AI-extracted commercial fields
    customer            TEXT,
    industry_segment    TEXT,
    product_category    TEXT,
    product_brand       TEXT,
    quantity            NUMERIC,
    quantity_unit       TEXT,
    location            TEXT,
    delivery_date       TEXT,

    -- Pipeline-managed status field
    status              TEXT            DEFAULT 'New',

    -- Email metadata (set by pipeline runner, not AI)
    received_date       TEXT,
    sender_name         TEXT,
    sender_email        TEXT,
    email_subject       TEXT,

    -- AI-generated summary and action fields
    email_summary       TEXT,
    next_action         TEXT,

    -- AI confidence score (0.0 – 1.0)
    llm_confidence      NUMERIC,

    -- Phase 18 — auto-assignment + conversation timeline
    assigned_to             TEXT,
    assigned_to_confidence  TEXT,
    conversation_timeline   TEXT,

    -- Row creation timestamp (set automatically by Supabase)
    created_at          TIMESTAMPTZ     DEFAULT NOW()

);

-- Optional: add a comment to the table so it is self-documenting in Supabase
COMMENT ON TABLE zavenir_requirements IS
    'CRM records extracted from Zavenir Daubert sales enquiry emails by the MailCRM pipeline.';
