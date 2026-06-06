# dashboard.py  —  Phase 8 update (55-field schema + schema-driven column names)
#
# COLUMN NAMES CHANGED IN PHASE 8:
#   client            → client_name
#   project           → project_name
#   positions         → designation
#   suggested_action  → next_action
#   sender            → sender_email
#   summary           → email_summary
#
# Column names, display labels, and date columns all come from config/fields.py.
# If a column is ever renamed, update config/fields.py — this file needs no change.

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

PROJECT_ROOT = Path(__file__).parent.parent
CRM_FILE     = PROJECT_ROOT / "data" / "crm_data.xlsx"

# Import display labels, date columns, and colour maps from the schema config
sys.path.insert(0, str(PROJECT_ROOT))
from config.fields import (
    DISPLAY_NAMES,
    DATE_COLUMNS,
    VALID_CATEGORIES,
    PSL_CATEGORIES,
    REQUIREMENT_STAGES,
    STATUS_COLOURS,
    URGENCY_BADGE_COLOURS,
)

st.set_page_config(
    page_title="CRM Pipeline Dashboard",
    page_icon="📊",
    layout="wide",
)


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

@st.cache_data(ttl=30)
def load_data():
    if not CRM_FILE.exists():
        return pd.DataFrame()
    df = pd.read_excel(CRM_FILE, engine="openpyxl", dtype=str).fillna("")
    # Parse date columns to datetime so we can do comparisons and sorting
    for col in DATE_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


df = load_data()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("CRM Pipeline Dashboard")
st.caption(
    f"Source: `{CRM_FILE.relative_to(PROJECT_ROOT)}`  |  "
    f"Records: **{len(df)}**  |  "
    f"Schema: **55 fields · 7 sections**"
)

if df.empty:
    st.warning("No data found in `data/crm_data.xlsx`. Run the email pipeline first.")
    st.stop()

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Filters")

    categories = ["All"] + sorted([c for c in df["category"].dropna().unique() if c])
    sel_category = st.selectbox("Category", categories)

    statuses = ["All"] + sorted([s for s in df["status"].dropna().unique() if s])
    sel_status = st.selectbox("Status", statuses)

    clients = ["All"] + sorted([c for c in df["client_name"].dropna().unique() if c])
    sel_client = st.selectbox("Client", clients)

    psls = ["All"] + sorted([p for p in df["psl_categories"].dropna().unique() if p])
    sel_psl = st.selectbox("PSL Category", psls)

    urgencies = ["All", "High", "Medium", "Low"]
    sel_urgency = st.selectbox("Urgency", urgencies)

    st.divider()
    if st.button("Refresh data"):
        st.cache_data.clear()
        st.rerun()

# Apply filters
fdf = df.copy()
if sel_category != "All":
    fdf = fdf[fdf["category"] == sel_category]
if sel_status != "All":
    fdf = fdf[fdf["status"] == sel_status]
if sel_client != "All":
    fdf = fdf[fdf["client_name"] == sel_client]
if sel_psl != "All":
    fdf = fdf[fdf["psl_categories"] == sel_psl]
if sel_urgency != "All":
    fdf = fdf[fdf["urgency"] == sel_urgency]

# ---------------------------------------------------------------------------
# KPI row
# ---------------------------------------------------------------------------
today = pd.Timestamp.today().normalize()

# Records matching manpower/proposal categories
active_reqs = fdf[fdf["category"].isin(["Manpower Request", "RFQ", "Proposal Request"])]

# Overdue: has a deadline in the past and isn't closed
overdue = fdf[
    fdf["deadline"].notna()
    & (fdf["deadline"] < today)
    & (~fdf["status"].isin(["Done", "Position Filled", "Requirement Cancelled"]))
]

# Due soon: deadline within the next 7 days, not closed
due_soon = fdf[
    fdf["deadline"].notna()
    & (fdf["deadline"] >= today)
    & (fdf["deadline"] <= today + pd.Timedelta(days=7))
    & (~fdf["status"].isin(["Done", "Position Filled", "Requirement Cancelled"]))
]

# High urgency records
high_urgency = fdf[fdf["urgency"] == "High"]

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Records", len(fdf))
k2.metric("Active Requirements", len(active_reqs))
k3.metric("High Urgency", len(high_urgency))
k4.metric(
    "Overdue",
    len(overdue),
    delta=f"-{len(overdue)}" if len(overdue) else None,
    delta_color="inverse",
)
k5.metric("Due <= 7 days", len(due_soon))

st.divider()

# ---------------------------------------------------------------------------
# Charts row
# ---------------------------------------------------------------------------
col_left, col_mid, col_right = st.columns([1.2, 1.2, 1.6])

with col_left:
    st.subheader("By Category")
    cat_counts = df["category"].value_counts().reset_index()
    cat_counts.columns = ["category", "count"]
    fig_cat = px.pie(
        cat_counts, names="category", values="count",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        hole=0.4,
    )
    fig_cat.update_traces(textposition="inside", textinfo="percent+label")
    fig_cat.update_layout(showlegend=False, margin=dict(t=20, b=10, l=10, r=10), height=280)
    st.plotly_chart(fig_cat, use_container_width=True)

with col_mid:
    st.subheader("By PSL Category")
    psl_counts = df[df["psl_categories"] != ""].copy()
    if not psl_counts.empty:
        psl_counts = psl_counts["psl_categories"].value_counts().reset_index()
        psl_counts.columns = ["psl", "count"]
        fig_psl = px.bar(
            psl_counts.head(10), x="count", y="psl",
            orientation="h", text="count",
            color_discrete_sequence=["#4a9ede"],
        )
        fig_psl.update_traces(textposition="outside")
        fig_psl.update_layout(
            showlegend=False, xaxis_title="", yaxis_title="",
            margin=dict(t=20, b=10, l=10, r=10), height=280,
            yaxis={"categoryorder": "total ascending"},
        )
        st.plotly_chart(fig_psl, use_container_width=True)
    else:
        st.info("No PSL category data yet.")

with col_right:
    st.subheader("Records Over Time")
    timeline = (
        df[df["received_date"].notna()]
        .groupby(df["received_date"].dt.date)
        .size()
        .reset_index(name="count")
    )
    timeline.columns = ["date", "count"]
    if not timeline.empty:
        fig_time = px.area(
            timeline, x="date", y="count",
            color_discrete_sequence=["#4a9ede"],
        )
        fig_time.update_layout(
            xaxis_title="", yaxis_title="Records",
            margin=dict(t=20, b=10, l=10, r=10), height=280,
        )
        st.plotly_chart(fig_time, use_container_width=True)
    else:
        st.info("No date data available.")

st.divider()

# ---------------------------------------------------------------------------
# Requirement Stage funnel
# ---------------------------------------------------------------------------
st.subheader("Requirement Stages")

stage_counts = df[df["requirement_stage"] != ""]["requirement_stage"].value_counts()
if not stage_counts.empty:
    stage_df = stage_counts.reset_index()
    stage_df.columns = ["stage", "count"]
    fig_stage = px.bar(
        stage_df, x="stage", y="count", text="count",
        color_discrete_sequence=["#1F4E79"],
    )
    fig_stage.update_traces(textposition="outside")
    fig_stage.update_layout(
        showlegend=False, xaxis_title="", yaxis_title="Records",
        xaxis_tickangle=-30,
        margin=dict(t=20, b=80, l=10, r=10), height=300,
    )
    st.plotly_chart(fig_stage, use_container_width=True)
else:
    st.info("No requirement stage data yet.")

st.divider()

# ---------------------------------------------------------------------------
# Active Requirements table
# ---------------------------------------------------------------------------
st.subheader("Active Requirements")

req_view = fdf[fdf["category"].isin(["Manpower Request", "RFQ", "Proposal Request"])].copy()

if req_view.empty:
    st.info("No active requirements match the current filters.")
else:
    # Add a deadline badge column (named dl_badge to avoid clash with the real urgency field)
    def _dl_badge(row):
        dl = row.get("deadline")
        if pd.isna(dl) or dl == "":
            return ""
        if dl < today:
            return "OVERDUE"
        if dl <= today + pd.Timedelta(days=7):
            return "DUE SOON"
        return ""

    req_view["dl_badge"]     = req_view.apply(_dl_badge, axis=1)
    req_view["deadline_str"] = req_view["deadline"].dt.strftime("%Y-%m-%d").fillna("")

    display_cols = [
        "urgency", "dl_badge", "client_name", "project_name", "designation",
        "headcount", "psl_categories", "location", "deadline_str", "status",
    ]
    col_labels = {
        "urgency":       "Urgency",
        "dl_badge":      "Deadline Alert",
        "client_name":   "Client",
        "project_name":  "Project",
        "designation":   "Role",
        "headcount":     "HC",
        "psl_categories":"PSL",
        "location":      "Location",
        "deadline_str":  "Deadline",
        "status":        "Status",
    }

    st.dataframe(
        req_view[display_cols].rename(columns=col_labels),
        use_container_width=True,
        hide_index=True,
    )

st.divider()

# ---------------------------------------------------------------------------
# Next Actions
# ---------------------------------------------------------------------------
st.subheader("Next Actions Required")

action_view = fdf[fdf["next_action"].str.strip() != ""][
    ["received_date", "category", "client_name", "designation",
     "next_action", "status", "deadline"]
].copy()
action_view["received_date"] = action_view["received_date"].dt.strftime("%Y-%m-%d").fillna("")
action_view["deadline"]      = action_view["deadline"].dt.strftime("%Y-%m-%d").fillna("")
action_view = action_view.rename(columns={
    "received_date": "Received",
    "category":      "Category",
    "client_name":   "Client",
    "designation":   "Role",
    "next_action":   "Next Action",
    "status":        "Status",
    "deadline":      "Deadline",
})

if action_view.empty:
    st.info("No pending actions match the current filters.")
else:
    st.dataframe(action_view, use_container_width=True, hide_index=True)

st.divider()

# ---------------------------------------------------------------------------
# Recent Records
# ---------------------------------------------------------------------------
st.subheader("Recent Records")

recent = (
    fdf[fdf["received_date"].notna()]
    .sort_values("received_date", ascending=False)
    .head(20)
)

recent_display = recent[
    ["received_date", "sender_email", "category", "client_name",
     "designation", "urgency", "email_summary", "status"]
].copy()
recent_display["received_date"] = (
    recent_display["received_date"].dt.strftime("%Y-%m-%d %H:%M").fillna("")
)
recent_display = recent_display.rename(columns={
    "received_date": "Received",
    "sender_email":  "Sender",
    "category":      "Category",
    "client_name":   "Client",
    "designation":   "Role",
    "urgency":       "Urgency",
    "email_summary": "Summary",
    "status":        "Status",
})

st.dataframe(
    recent_display,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Summary": st.column_config.TextColumn("Summary", width="large"),
    },
)

# ---------------------------------------------------------------------------
# Full Record Viewer
# ---------------------------------------------------------------------------
with st.expander("Full Record Viewer"):
    if fdf.empty:
        st.info("No records.")
    else:
        # Build readable option labels: "Client — Role — Date"
        options = []
        for i, row in fdf.iterrows():
            client = row.get("client_name") or row.get("sender_email", "")
            role   = row.get("designation", "")
            date   = str(row.get("received_date", ""))[:10]
            options.append(f"{i}: {client} — {role} — {date}")

        sel = st.selectbox("Select record", options)
        idx = int(sel.split(":")[0])
        record = fdf.loc[idx]

        # Display fields in two columns, using display names from the schema
        col_a, col_b = st.columns(2)
        items = list(record.items())
        half  = len(items) // 2

        for j, (field_name, value) in enumerate(items):
            label  = DISPLAY_NAMES.get(field_name, field_name)
            target = col_a if j < half else col_b
            target.text_input(
                label,
                value=str(value) if pd.notna(value) else "",
                disabled=True,
            )
