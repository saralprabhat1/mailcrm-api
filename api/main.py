# api/main.py — MailCRM REST API
#
# Exposes CRM data from Supabase and triggers the email pipeline via HTTP.
# Run with: uvicorn api.main:app --reload  (from project root)
#
# Endpoints:
#   GET  /                  health check
#   GET  /records           all CRM records from Supabase
#   GET  /records/{id}      single record by email_id (REQ- format)
#   GET  /stats             totals, status breakdown, top PSLs, last-7-days count
#   POST /run-pipeline      triggers run_pipeline(max_emails=5), returns summary

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta, timezone
from collections import Counter

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# --- Path setup -----------------------------------------------------------
# api/main.py is one level below the project root, so parent.parent is NOT needed.
# __file__ = crm-automation/api/main.py  →  .parent = crm-automation/api/
#                                         →  .parent.parent = crm-automation/
PROJECT_ROOT = Path(__file__).parent.parent

# These paths let us import from run_parser (and everything it in turn imports)
for _p in [
    PROJECT_ROOT,
    PROJECT_ROOT / "04_email_parser",
    PROJECT_ROOT / "05_classifier",
    PROJECT_ROOT / "06_data_storage",
    PROJECT_ROOT / "08_advanced",
    PROJECT_ROOT / "03_outlook",
]:
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

load_dotenv(PROJECT_ROOT / ".env")

# --- Supabase client ------------------------------------------------------
from supabase import create_client  # noqa: E402 (import after path setup)

_sb_url = os.getenv("SUPABASE_URL")
_sb_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
if not _sb_url or not _sb_key:
    raise RuntimeError("SUPABASE_URL / SUPABASE_SERVICE_KEY missing from .env")
supabase = create_client(_sb_url, _sb_key)

# --- FastAPI app ----------------------------------------------------------
app = FastAPI(
    title="MailCRM API",
    description="REST API for MailCRM — reads from Supabase, triggers the email pipeline.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------------------------
# GET /
# -------------------------------------------------------------------------
@app.get("/")
def root():
    """Health check."""
    return {"status": "ok", "product": "MailCRM"}


# -------------------------------------------------------------------------
# GET /records
# -------------------------------------------------------------------------
@app.get("/records")
def get_records():
    """Return all CRM records from Supabase, newest first."""
    try:
        resp = (
            supabase.table("crm_requirements")
            .select("*")
            .order("inserted_at", desc=True)
            .execute()
        )
        return {"count": len(resp.data), "records": resp.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------------------
# GET /records/{email_id}
# -------------------------------------------------------------------------
@app.get("/records/{email_id}")
def get_record(email_id: str):
    """Return a single CRM record by its email_id (REQ-YYYYMMDD-HASH-NN format)."""
    try:
        resp = (
            supabase.table("crm_requirements")
            .select("*")
            .eq("email_id", email_id)
            .execute()
        )
        if not resp.data:
            raise HTTPException(status_code=404, detail=f"Record not found: {email_id}")
        return resp.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------------------
# GET /stats
# -------------------------------------------------------------------------
@app.get("/stats")
def get_stats():
    """
    Aggregated stats:
      - total_records
      - by_status        {New: N, In Progress: N, …}
      - top_5_psl_categories  {Drilling: N, …}
      - records_last_7_days
    """
    try:
        resp = supabase.table("crm_requirements").select("*").execute()
        rows = resp.data

        status_counts = Counter(r.get("status") or "Unknown" for r in rows)

        # PSL column may hold a single value or a comma-separated list
        psl_counts: Counter = Counter()
        for r in rows:
            raw = r.get("psl_categories") or ""
            for psl in [p.strip() for p in raw.split(",") if p.strip()]:
                psl_counts[psl] += 1
        top_psls = dict(psl_counts.most_common(5))

        cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
        recent_count = sum(
            1 for r in rows
            if (r.get("received_date") or "") >= cutoff
        )

        return {
            "total_records": len(rows),
            "by_status": dict(status_counts),
            "top_5_psl_categories": top_psls,
            "records_last_7_days": recent_count,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------------------
# POST /run-pipeline
# -------------------------------------------------------------------------
@app.post("/run-pipeline")
def trigger_pipeline():
    """
    Triggers run_pipeline(max_emails=5).
    Fetches latest emails, classifies, extracts, saves to Excel + Supabase.
    Returns a summary of what was done.
    """
    try:
        # Lazy import — avoids loading ML model etc. until endpoint is hit.
        # run_parser's module-level code sets up all sys.path it needs.
        from run_parser import run_pipeline  # noqa: PLC0415

        crm_rows = run_pipeline(max_emails=5)

        # Build a lightweight summary (crm_rows = new records only; follow-ups
        # are handled inside run_pipeline and saved directly, not returned)
        summary_rows = []
        for row in crm_rows:
            summary_rows.append({
                "req_id":      row.get("req_id", ""),
                "designation": row.get("designation", ""),
                "client_name": row.get("client_name", ""),
                "status":      row.get("status", ""),
            })

        return {
            "status":               "complete",
            "new_records_created":  len(crm_rows),
            "new_records":          summary_rows,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
