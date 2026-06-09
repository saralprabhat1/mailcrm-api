# configs/clients/client_template.py
# ============================================================================
# CLIENT PIPELINE CONFIGURATION TEMPLATE
# ============================================================================
# Copy this file, rename it to your client slug (e.g. acme_lubricants.py),
# and fill in the values below. Each setting is documented.
#
# Once filled in, you will also need:
#   1. A Supabase table — copy scripts/create_zavenir_table.sql and adapt it.
#   2. A Groq extractor  — copy utils/zavenir_extractor.py and adapt the prompt.
#   3. A pipeline runner — copy run_zavenir_parser.py and adapt SENDER_FILTER.
# ============================================================================

# ---------------------------------------------------------------------------
# PIPELINE IDENTITY
# ---------------------------------------------------------------------------

# PIPELINE_NAME — short slug used in logs and reports.
# Use lowercase letters and underscores only.
# Example: "acme_lubricants"
# PIPELINE_NAME = ""

# SENDER_FILTER — the email address whose emails this pipeline monitors.
# Only emails sent FROM (or forwarding messages from) this address are processed.
# Example: "sales@acmelubricants.com"
# SENDER_FILTER = ""

# ---------------------------------------------------------------------------
# PRODUCT CATEGORIES
# The AI picks exactly ONE category per enquiry from this list.
#
# Guidelines:
#   - Be specific. "Industrial Greases" is better than "Greases".
#   - Keep the list short (10–20 items). Longer lists confuse the AI.
#   - Always end with "Other" so the AI has a fallback for unusual products.
#
# Example:
#   PRODUCT_CATEGORIES = [
#       "Industrial Greases",
#       "Hydraulic Fluids",
#       "Gear Oils",
#       "Rust Preventives",
#       "Metalworking Fluids",
#       "Other",
#   ]
# ---------------------------------------------------------------------------
# PRODUCT_CATEGORIES = []

# ---------------------------------------------------------------------------
# INDUSTRY SEGMENTS
# The AI picks exactly ONE segment per enquiry from this list.
#
# Guidelines:
#   - Match the segments your sales team already uses.
#   - Always end with "Other".
#
# Example:
#   INDUSTRY_SEGMENTS = [
#       "Steel",
#       "Automotive",
#       "Oil and Gas",
#       "Aerospace",
#       "General Engineering",
#       "Other",
#   ]
# ---------------------------------------------------------------------------
# INDUSTRY_SEGMENTS = []

# ---------------------------------------------------------------------------
# CRM SCHEMA — column names in Excel and Supabase.
#
# System-filled fields (the pipeline sets these automatically — do not remove):
#   req_id          auto-generated unique ID (REQ-YYYYMMDD-XXXXXX-NN)
#   status          pipeline sets to "New" on first extraction
#   received_date   date the email was received (YYYY-MM-DD)
#   sender_email    email address of the sender (the client contact)
#   email_subject   original subject line of the email
#
# AI-extracted fields (Groq fills these from the email body):
#   customer        company name of the buyer
#   industry_segment one value from INDUSTRY_SEGMENTS
#   product_category one value from PRODUCT_CATEGORIES
#   product_brand   brand or product name exactly as stated in the email
#   quantity        number only — unit goes in quantity_unit
#   quantity_unit   kg, litres, drums, MT, units, etc.
#   location        delivery plant, city, or country
#   delivery_date   requested delivery date (YYYY-MM-DD)
#   email_summary   one-sentence summary of what is being requested
#   next_action     suggested next step for the sales team
#   llm_confidence  0.0–1.0 score: how complete is the extracted data?
#
# To add a custom field: add it here AND add the column to your Supabase
# table AND handle it in your Groq extractor prompt.
# ---------------------------------------------------------------------------
# FIELDS = [
#     "req_id",
#     "customer",
#     "industry_segment",
#     "product_category",
#     "product_brand",
#     "quantity",
#     "quantity_unit",
#     "location",
#     "delivery_date",
#     "status",
#     "received_date",
#     "sender_email",
#     "email_subject",
#     "email_summary",
#     "next_action",
#     "llm_confidence",
# ]

# ---------------------------------------------------------------------------
# OUTPUT PATHS
# ---------------------------------------------------------------------------

# EXCEL_OUTPUT — path relative to the project root where the Excel file is saved.
# Example: "data/acme_lubricants_crm.xlsx"
# EXCEL_OUTPUT = ""

# SUPABASE_TABLE — name of the Supabase table where records are upserted.
# Must match the table you created (see scripts/ for DDL examples).
# Example: "acme_requirements"
# SUPABASE_TABLE = ""
