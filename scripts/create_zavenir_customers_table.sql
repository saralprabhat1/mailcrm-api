-- scripts/create_zavenir_customers_table.sql
-- Creates the zavenir_customers table in Supabase — the seed/reference
-- customer master for the Zavenir Daubert pipeline (633 customers from
-- data/zavenir_customers_base.xlsx).
--
-- PURPOSE:
--   1. Match incoming enquiry sender domains (Phase 18 sender_email) against
--      known customers for de-dup / linking.
--   2. Base table for the Customer Domain Enrichment script
--      (scripts/enrich_customer_domains.py).
--
-- HOW TO USE:
--   1. Open Supabase -> SQL Editor -> New Query
--   2. Paste this entire file and click Run
--   3. Safe to re-run — uses IF NOT EXISTS
--
-- NOTE: scripts/upload_zavenir_customers.py normalizes whatever columns the
-- xlsx actually has into this schema (it maps common header variants like
-- "Company Name" / "Customer" -> customer_name). If the xlsx has extra
-- columns not listed here, the upload script prints them so this DDL can be
-- extended with ALTER TABLE ... ADD COLUMN.

CREATE TABLE IF NOT EXISTS zavenir_customers (

    -- Primary key — auto-incremented by Supabase
    id                  BIGINT          GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Customer company name — the upsert/conflict key for the upload script
    customer_name       TEXT            UNIQUE NOT NULL,

    -- Company website domain (e.g. "elematic.com") — filled by the xlsx if
    -- present, otherwise by scripts/enrich_customer_domains.py
    domain              TEXT,

    -- Where the domain came from: 'xlsx' | 'email' | 'clearbit' | NULL
    domain_source       TEXT,

    -- Location fields
    city                TEXT,
    state               TEXT,
    country             TEXT,
    address             TEXT,

    -- Business classification (matches the 8 industry segments in
    -- configs/clients/zavenir.py where possible)
    industry_segment    TEXT,

    -- Contact details
    contact_person      TEXT,
    contact_email       TEXT,
    contact_phone       TEXT,

    -- Free-text notes / remarks from the master list
    notes               TEXT,

    -- Provenance of the row (e.g. 'master_xlsx')
    source              TEXT            DEFAULT 'master_xlsx',

    -- Row timestamps (set automatically by Supabase)
    created_at          TIMESTAMPTZ     DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     DEFAULT NOW()

);

-- Index on domain — the main lookup path when matching an incoming enquiry's
-- sender email domain to a known customer.
CREATE INDEX IF NOT EXISTS idx_zavenir_customers_domain
    ON zavenir_customers (domain);

COMMENT ON TABLE zavenir_customers IS
    'Zavenir Daubert customer master (633 customers) — seed list for matching incoming enquiries to known customers.';
