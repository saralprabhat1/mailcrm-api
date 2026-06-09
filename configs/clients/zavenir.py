# configs/clients/zavenir.py
# Configuration for the Zavenir Daubert pipeline.
# Zavenir Daubert is a specialty chemicals and lubricants company.
#
# This file is the single source of truth for all Zavenir-specific settings.
# Nothing in this file touches the GET Global pipeline.

# ---------------------------------------------------------------------------
# PIPELINE IDENTITY
# ---------------------------------------------------------------------------

PIPELINE_NAME = "zavenir_daubert"

# Only emails from this sender are processed by the Zavenir pipeline.
SENDER_FILTER = "tarora@zavenir.com"

# ---------------------------------------------------------------------------
# PRODUCT CATEGORIES
# The AI must classify each enquiry into exactly one of these categories.
# ---------------------------------------------------------------------------

PRODUCT_CATEGORIES = [
    "Specialty Greases",
    "Rust Preventive Coatings",
    "Metalworking Fluids",
    "Corrosion Inhibitor Additives (SACI)",
    "Food Grade Lubricants",
    "Oil and Gas Lubricants",
    "MIL-SPEC Defense Lubricants",
    "Adhesives and Sealants",
    "Sound Deadening NVH",
    "Process Oils",
    "Vapor Corrosion Inhibitors (VCI)",
    "Defoamers and Cleaners",
    "Other",
]

# ---------------------------------------------------------------------------
# INDUSTRY SEGMENTS
# The AI must classify each enquiry into exactly one of these segments.
# ---------------------------------------------------------------------------

INDUSTRY_SEGMENTS = [
    "Steel",
    "Automotive",
    "Oil and Gas",
    "Defense",
    "Marine",
    "Aerospace",
    "General Engineering",
    "Other",
]

# ---------------------------------------------------------------------------
# CRM SCHEMA — field names used in the Excel output and Supabase table.
#
# System-filled fields (pipeline sets these, not the AI):
#   req_id, status, received_date, sender_email, email_subject
#
# AI-extracted fields (Groq fills these from the email body):
#   customer, industry_segment, product_category, product_brand,
#   quantity, quantity_unit, location, delivery_date,
#   email_summary, next_action, llm_confidence
# ---------------------------------------------------------------------------

FIELDS = [
    "req_id",
    "customer",
    "industry_segment",
    "product_category",
    "product_brand",
    "quantity",
    "quantity_unit",
    "location",
    "delivery_date",
    "status",
    "received_date",
    "sender_email",
    "email_subject",
    "email_summary",
    "next_action",
    "llm_confidence",
]

# ---------------------------------------------------------------------------
# OUTPUT PATHS
# ---------------------------------------------------------------------------

EXCEL_OUTPUT   = "data/zavenir_crm.xlsx"
SUPABASE_TABLE = "zavenir_requirements"
