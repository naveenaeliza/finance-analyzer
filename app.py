import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai
from prophet import Prophet
from sklearn.ensemble import IsolationForest
import pdfplumber
import re
import mysql.connector

# -----------------------------------
# PAGE CONFIG
# -----------------------------------

st.set_page_config(
    page_title="FinSight AI",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------------
# CUSTOM CSS
# -----------------------------------

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@300;400;500&display=swap');

  html, body, [class*="css"] {
      font-family: 'DM Mono', monospace;
      background-color: #0b0c0f;
      color: #e8e4dc;
  }
  .stApp { background-color: #0b0c0f; }
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding: 2.5rem 3rem 4rem; max-width: 1400px; }

  .hero-header {
      display: flex; align-items: flex-end; gap: 1.2rem;
      border-bottom: 1px solid #2a2c32;
      padding-bottom: 1.8rem; margin-bottom: 2.5rem;
  }
  .hero-title { font-family: 'DM Serif Display', serif; font-size: 3.4rem; line-height: 1; color: #f0ebe0; letter-spacing: -0.02em; }
  .hero-title span { color: #c9a84c; font-style: italic; }
  .hero-sub { font-size: 0.72rem; letter-spacing: 0.18em; text-transform: uppercase; color: #5c5e66; margin-bottom: 0.45rem; }

  .kpi-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1px; background: #1e2026; border: 1px solid #1e2026; border-radius: 12px; overflow: hidden; margin-bottom: 2.5rem; }
  .kpi-card { background: #121418; padding: 1.6rem 1.8rem; transition: background 0.2s; }
  .kpi-card:hover { background: #16181d; }
  .kpi-label { font-size: 0.65rem; letter-spacing: 0.16em; text-transform: uppercase; color: #4a4d57; margin-bottom: 0.5rem; }
  .kpi-value { font-family: 'DM Serif Display', serif; font-size: 2rem; color: #e8e4dc; letter-spacing: -0.03em; }
  .kpi-value.accent { color: #c9a84c; }

  .section-title { font-family: 'DM Serif Display', serif; font-size: 1.5rem; color: #e8e4dc; letter-spacing: -0.01em; margin: 1.8rem 0 1rem; display: flex; align-items: center; gap: 0.6rem; }
  .section-title::after { content: ''; flex: 1; height: 1px; background: #1e2026; }

  .budget-wrap { background: #121418; border: 1px solid #1e2026; border-radius: 12px; padding: 1.4rem 1.8rem; margin-bottom: 2rem; }
  .budget-bar-bg { height: 6px; background: #1e2026; border-radius: 3px; margin-top: 0.7rem; }
  .budget-bar-fill { height: 6px; border-radius: 3px; }
  .budget-status { font-size: 0.75rem; margin-top: 0.5rem; letter-spacing: 0.04em; }

  .alert-danger  { background: rgba(224,90,90,0.08);  border: 1px solid rgba(224,90,90,0.25);  border-radius: 8px; padding: 0.9rem 1.2rem; color: #e05a5a; font-size: 0.82rem; margin: 0.5rem 0; }
  .alert-success { background: rgba(76,175,125,0.08); border: 1px solid rgba(76,175,125,0.2);  border-radius: 8px; padding: 0.9rem 1.2rem; color: #4caf7d; font-size: 0.82rem; margin: 0.5rem 0; }
  .alert-warning { background: rgba(201,168,76,0.08); border: 1px solid rgba(201,168,76,0.2);  border-radius: 8px; padding: 0.9rem 1.2rem; color: #c9a84c; font-size: 0.82rem; margin: 0.5rem 0; }

  /* ── Custom HTML table (replaces st.dataframe black-box) ── */
  .fin-table { width: 100%; border-collapse: collapse; font-size: 0.78rem; margin-bottom: 1rem; }
  .fin-table thead tr { border-bottom: 1px solid #2a2c32; }
  .fin-table thead th { text-align: left; padding: 0.6rem 1rem; font-size: 0.63rem; letter-spacing: 0.12em; text-transform: uppercase; color: #4a4d57; font-weight: 400; }
  .fin-table tbody tr { border-bottom: 1px solid #16181d; transition: background 0.15s; }
  .fin-table tbody tr:hover { background: #14161a; }
  .fin-table tbody td { padding: 0.65rem 1rem; color: #b8b4ac; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 260px; }
  .fin-table tbody td.amount { color: #e8e4dc; font-family: 'DM Serif Display', serif; font-size: 0.95rem; }
  .fin-table-wrap { background: #0f1115; border: 1px solid #1e2026; border-radius: 12px; overflow: hidden; padding: 0 0 0.5rem; }
  .fin-table-scroll { overflow-x: auto; max-height: 420px; overflow-y: auto; }

  /* category pill */
  .cat-pill { display: inline-block; padding: 0.15rem 0.55rem; border-radius: 4px; font-size: 0.65rem; letter-spacing: 0.06em; text-transform: uppercase; }
  .cat-Food          { background: rgba(201,168,76,0.12); color: #c9a84c; }
  .cat-Transport     { background: rgba(91,156,246,0.12); color: #5b9cf6; }
  .cat-Shopping      { background: rgba(179,92,255,0.12); color: #b35cff; }
  .cat-Entertainment { background: rgba(249,115,22,0.12); color: #f97316; }
  .cat-Healthcare    { background: rgba(76,175,125,0.12); color: #4caf7d; }
  .cat-Bills         { background: rgba(224,90,90,0.12);  color: #e05a5a; }
  .cat-Groceries     { background: rgba(45,212,191,0.12); color: #2dd4bf; }
  .cat-Others        { background: rgba(100,100,110,0.12); color: #6a6878; }

  /* anomaly badge */
  .anomaly-badge { display: inline-block; background: rgba(224,90,90,0.12); color: #e05a5a; border: 1px solid rgba(224,90,90,0.3); border-radius: 4px; padding: 0.12rem 0.45rem; font-size: 0.6rem; letter-spacing: 0.1em; text-transform: uppercase; margin-left: 0.4rem; }

  [data-testid="stFileUploader"] { background: #121418; border: 1px dashed #2a2c32; border-radius: 12px; padding: 1rem; }
  [data-testid="stFileUploader"]:hover { border-color: #c9a84c; }

  [data-testid="stMetric"] { background: #121418; border: 1px solid #1e2026; border-radius: 10px; padding: 1rem 1.2rem; }
  [data-testid="stMetricLabel"] { color: #5c5e66 !important; font-size: 0.7rem !important; letter-spacing: 0.12em; }
  [data-testid="stMetricValue"] { color: #e8e4dc !important; font-family: 'DM Serif Display', serif !important; font-size: 1.7rem !important; }

  .stButton > button { background: #c9a84c; color: #0b0c0f; border: none; border-radius: 6px; font-family: 'DM Mono', monospace; font-size: 0.75rem; font-weight: 500; letter-spacing: 0.1em; text-transform: uppercase; padding: 0.55rem 1.4rem; transition: background 0.2s, transform 0.1s; }
  .stButton > button:hover { background: #dbb95a; transform: translateY(-1px); }

  .stNumberInput input, .stTextInput input { background: #121418 !important; border: 1px solid #2a2c32 !important; border-radius: 6px !important; color: #e8e4dc !important; font-family: 'DM Mono', monospace !important; }

  .ai-box { background: #121418; border: 1px solid #2a2c32; border-left: 3px solid #c9a84c; border-radius: 0 10px 10px 0; padding: 1.4rem 1.6rem; font-size: 0.82rem; line-height: 1.75; color: #b8b4ac; }
  .ai-box strong { color: #e8e4dc; }
  .ai-box ol { padding-left: 1.2rem; margin: 0.5rem 0 0; }
  .ai-box li { margin-bottom: 0.4rem; }

  hr { border-color: #1e2026 !important; margin: 2rem 0 !important; }
  ::-webkit-scrollbar { width: 4px; height: 4px; }
  ::-webkit-scrollbar-track { background: #0b0c0f; }
  ::-webkit-scrollbar-thumb { background: #2a2c32; border-radius: 2px; }

  /* sidebar API key */
  .sidebar-label { font-size: 0.7rem; letter-spacing: 0.1em; text-transform: uppercase; color: #5c5e66; margin-bottom: 0.3rem; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------
# PLOTLY THEME
# -----------------------------------

PLOT_BG  = "#0f1115"
PAPER_BG = "#0f1115"
GRID_COL = "#1e2026"
FONT_COL = "#7a7880"
ACCENT   = "#c9a84c"
ACCENT2  = "#4caf7d"
ACCENT3  = "#e05a5a"

def apply_dark_theme(fig):
    fig.update_layout(
        paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
        font=dict(family="DM Mono, monospace", color=FONT_COL, size=11),
        margin=dict(l=16, r=16, t=40, b=16),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#6a6870")),
    )
    fig.update_xaxes(gridcolor=GRID_COL, zeroline=False, linecolor=GRID_COL)
    fig.update_yaxes(gridcolor=GRID_COL, zeroline=False, linecolor=GRID_COL)
    return fig

# -----------------------------------
# HELPER: render a pandas df as HTML table
# -----------------------------------

CAT_COLORS = {"Food","Transport","Shopping","Entertainment","Healthcare","Bills","Groceries","Others"}

def render_table(df_in, highlight_amount=True, anomaly_col=None):
    rows_html = ""
    for _, row in df_in.iterrows():
        cells = ""
        for col in df_in.columns:
            val = row[col]
            if col in ("Amount", "amount"):
                cells += f'<td class="amount">₹{float(val):,.2f}</td>'
            elif col in ("Category", "category"):
                cat = str(val)
                css = cat if cat in CAT_COLORS else "Others"
                cells += f'<td><span class="cat-pill cat-{css}">{cat}</span></td>'
            elif col in ("Date", "date", "transaction_date"):
                cells += f'<td style="color:#5c6070">{str(val)[:10]}</td>'
            elif col == "Description" or col == "description":
                badge = '<span class="anomaly-badge">anomaly</span>' if (anomaly_col and row.get(anomaly_col) == -1) else ""
                cells += f'<td style="max-width:280px">{str(val)[:60]}{"…" if len(str(val))>60 else ""}{badge}</td>'
            else:
                cells += f'<td>{val}</td>'
        rows_html += f"<tr>{cells}</tr>"

    headers = "".join(f"<th>{c}</th>" for c in df_in.columns)
    return f"""
    <div class="fin-table-wrap">
      <div class="fin-table-scroll">
        <table class="fin-table">
          <thead><tr>{headers}</tr></thead>
          <tbody>{rows_html}</tbody>
        </table>
      </div>
    </div>
    """

# -----------------------------------
# SIDEBAR — API KEY INPUT
# -----------------------------------

with st.sidebar:
    st.markdown('<div class="sidebar-label">Gemini API Key</div>', unsafe_allow_html=True)
    sidebar_key = st.text_input(
        "Gemini API Key",
        type="password",
        placeholder="Enter Gemini API Key",
        label_visibility="collapsed",
        help="Get your key at aistudio.google.com"
    )
    st.markdown(
        '<div style="font-size:0.65rem; color:#3a3c44; margin-top:0.3rem;">'
        'Or set <code>GEMINI_API_KEY</code> in <code>.streamlit/secrets.toml</code>'
        '</div>',
        unsafe_allow_html=True
    )

# Resolve API key: sidebar input → secrets → empty
try:
    _secrets_key = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    _secrets_key = ""

gemini_api_key = sidebar_key.strip() or _secrets_key.strip()

if gemini_api_key:
    genai.configure(api_key=gemini_api_key)

# -----------------------------------
# MYSQL CONNECTION
# -----------------------------------

@st.cache_resource
def get_db_connection():
    try:
        return mysql.connector.connect(
            host="localhost", user="root",
            password="root123", database="finance_analyzer"
        )
    except Exception:
        return None

conn   = get_db_connection()
cursor = conn.cursor() if conn else None

def load_historical_data():
    if not conn:
        return pd.DataFrame()
    query = "SELECT transaction_date, description, amount, category FROM transactions"
    return pd.read_sql(query, conn)

def save_transactions(df):
    if not conn:
        raise RuntimeError("No DB connection.")
    for _, row in df.iterrows():
        cursor.execute(
            "INSERT INTO transactions (transaction_date, description, amount, category) VALUES (%s,%s,%s,%s)",
            (row["Date"].date(), str(row["Description"]), float(row["Amount"]), str(row["Category"]))
        )
    conn.commit()

# -----------------------------------
# CATEGORY CLASSIFIER
# -----------------------------------

CATEGORY_MAP = {
    "Food":          ["swiggy","zomato","subway","dominos","pizza","culinary","restaurant","cafe","bistro"],
    "Transport":     ["uber","ola","rapido","irctc","redbus","makemytrip","flight","railway","metro"],
    "Shopping":      ["amazon","flipkart","ekart","myntra","ajio","nykaa","mall"],
    "Entertainment": ["netflix","prime","hotstar","spotify","pvr","inox","bookmyshow","youtube"],
    "Healthcare":    ["medical","hospital","pushpagiri","pharmacy","apollo","fortis","clinic"],
    "Bills":         ["electricity","bescom","kseb","jio","airtel","vi","broadband","water","gas"],
    "Groceries":     ["bigbasket","blinkit","zepto","dmart","reliance fresh","more","supermarket"],
}

def categorize(description):
    desc = str(description).lower()
    for category, keywords in CATEGORY_MAP.items():
        if any(kw in desc for kw in keywords):
            return category
    return "Others"

# -----------------------------------
# HERO HEADER
# -----------------------------------

st.markdown("""
<div class="hero-header">
  <div>
    <div class="hero-sub">Personal Finance Intelligence</div>
    <div class="hero-title">Fin<span>Sight</span> AI</div>
  </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------
# FILE UPLOAD
# -----------------------------------

st.markdown('<p class="section-title">📂 Import Transactions</p>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Drop your CSV or bank statement PDF here",
    type=["csv", "pdf"],
    help="Supports standard CSV exports and Indian bank PDF statements."
)

# -----------------------------------
# MAIN APP
# -----------------------------------

if uploaded_file is not None:

    # ── CSV ──
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)

    # ── PDF ──
    else:
        full_text = ""
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"

        transactions = []
        date_pattern = r"^\d{2}-\d{2}-\d{2}"
        lines        = full_text.split("\n")
        current_txn  = None

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            if re.match(date_pattern, line):
                if current_txn:
                    transactions.append(current_txn)
                parts = line.split()
                current_txn = {"Date": parts[0], "Description": line, "Amount": 0.0}
                if i + 1 < len(lines):
                    amounts = re.findall(r"\d[\d,]*\.\d{2}", lines[i + 1])
                    if amounts:
                        current_txn["Amount"] = float(amounts[0].replace(",", ""))
            else:
                if current_txn:
                    current_txn["Description"] += " " + line

        if current_txn:
            transactions.append(current_txn)
        df = pd.DataFrame(transactions)

    # ── Common processing ──
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])
    df["Category"] = df["Description"].apply(categorize)

    total_spending     = df["Amount"].sum()
    total_transactions = len(df)
    avg_transaction    = df["Amount"].mean() if total_transactions > 0 else 0.0

    # -----------------------------------
    # SAVE BUTTON
    # -----------------------------------

    c_save, _ = st.columns([1, 5])
    with c_save:
        if st.button("💾  Save to Database"):
            try:
                save_transactions(df)
                st.markdown('<div class="alert-success">✓ Saved to MySQL.</div>', unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f'<div class="alert-danger">✗ Save failed: {e}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # -----------------------------------
    # KPI CARDS
    # -----------------------------------

    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">Total Spending</div>
        <div class="kpi-value accent">₹{total_spending:,.0f}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Transactions</div>
        <div class="kpi-value">{total_transactions}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Avg. Transaction</div>
        <div class="kpi-value">₹{avg_transaction:,.0f}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # -----------------------------------
    # HISTORICAL ANALYTICS
    # -----------------------------------

    try:
        historical_df = load_historical_data()
        if not historical_df.empty:
            hist_spend = historical_df["amount"].sum()
            st.markdown('<p class="section-title">🗂 Historical Analytics</p>', unsafe_allow_html=True)
            h1, h2, h3 = st.columns(3)
            h1.metric("Historical Spending",     f"₹{hist_spend:,.2f}")
            h2.metric("Historical Transactions", len(historical_df))
            h3.metric("Avg. Historical Txn",     f"₹{historical_df['amount'].mean():,.2f}")
    except Exception:
        pass

    # -----------------------------------
    # BUDGET TRACKER
    # -----------------------------------

    st.markdown('<p class="section-title">🎯 Budget Tracker</p>', unsafe_allow_html=True)

    budget    = st.number_input("Monthly Budget (₹)", min_value=0, value=5000, step=500)
    pct_used  = min(total_spending / budget * 100, 100) if budget > 0 else 0
    bar_color = "#e05a5a" if total_spending > budget else "#4caf7d"
    label     = (
        f'<span style="color:#e05a5a">Over budget by ₹{total_spending - budget:,.0f}</span>'
        if total_spending > budget
        else f'<span style="color:#4caf7d">₹{budget - total_spending:,.0f} remaining</span>'
    )

    st.markdown(f"""
    <div class="budget-wrap">
      <div style="display:flex; justify-content:space-between; font-size:0.75rem;">
        <span style="color:#5c5e66; letter-spacing:0.08em;">SPENT</span>{label}
      </div>
      <div class="budget-bar-bg">
        <div class="budget-bar-fill" style="width:{pct_used:.1f}%; background:{bar_color};"></div>
      </div>
      <div class="budget-status" style="color:{bar_color}">{pct_used:.1f}% of ₹{budget:,} used</div>
    </div>
    """, unsafe_allow_html=True)

    # -----------------------------------
    # CHARTS
    # -----------------------------------

    st.markdown('<p class="section-title">📊 Spending Breakdown</p>', unsafe_allow_html=True)

    category_summary = df.groupby("Category")["Amount"].sum().reset_index()
    df["Month"]      = df["Date"].dt.strftime("%Y-%m")
    monthly_summary  = df.groupby("Month")["Amount"].sum().reset_index()

    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.pie(
            category_summary, names="Category", values="Amount", hole=0.55,
            color_discrete_sequence=["#c9a84c","#4caf7d","#5b9cf6","#e05a5a","#b35cff","#f97316","#2dd4bf"],
        )
        fig1.update_traces(textfont_size=10, textfont_color="#e8e4dc",
                           marker=dict(line=dict(color=PLOT_BG, width=2)))
        fig1.update_layout(title=dict(text="Category Split", font=dict(color="#e8e4dc", size=13)))
        apply_dark_theme(fig1)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.bar(
            monthly_summary, x="Month", y="Amount",
            color_discrete_sequence=[ACCENT],
        )
        fig2.update_traces(marker_line_width=0, opacity=0.9)
        fig2.update_layout(title=dict(text="Monthly Spending", font=dict(color="#e8e4dc", size=13)), bargap=0.35)
        apply_dark_theme(fig2)
        st.plotly_chart(fig2, use_container_width=True)

    # -----------------------------------
    # FORECASTING
    # -----------------------------------

    st.markdown('<p class="section-title">📈 30-Day Forecast</p>', unsafe_allow_html=True)

    predicted_spending = None
    fc_input = df.groupby("Date")["Amount"].sum().reset_index()
    fc_input.columns = ["ds", "y"]

    if len(fc_input) >= 5:
        try:
            m = Prophet(daily_seasonality=True)
            m.fit(fc_input)
            future = m.make_future_dataframe(periods=30)
            fc     = m.predict(future)

            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(x=fc_input["ds"], y=fc_input["y"],
                name="Actual", line=dict(color=ACCENT2, width=2)))
            fig3.add_trace(go.Scatter(x=fc["ds"], y=fc["yhat"],
                name="Forecast", line=dict(color=ACCENT, width=2, dash="dot")))
            fig3.add_trace(go.Scatter(
                x=pd.concat([fc["ds"], fc["ds"][::-1]]),
                y=pd.concat([fc["yhat_upper"], fc["yhat_lower"][::-1]]),
                fill="toself", fillcolor="rgba(201,168,76,0.07)",
                line=dict(color="rgba(0,0,0,0)"), name="Confidence Band"
            ))
            fig3.update_layout(title=dict(text="Spending Forecast", font=dict(color="#e8e4dc", size=13)))
            apply_dark_theme(fig3)
            st.plotly_chart(fig3, use_container_width=True)

            predicted_spending = fc["yhat"].tail(30).mean()
            st.markdown(f"""
            <div class="kpi-card" style="border-radius:10px; border:1px solid #1e2026; display:inline-block; padding:1rem 2rem;">
              <div class="kpi-label">Predicted Avg Daily Spend (next 30 days)</div>
              <div class="kpi-value accent">₹{predicted_spending:,.2f}</div>
            </div>""", unsafe_allow_html=True)

        except Exception as e:
            st.markdown(f'<div class="alert-warning">⚠ Forecast unavailable: {e}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-warning">⚠ Need at least 5 records to generate a forecast.</div>', unsafe_allow_html=True)

    # -----------------------------------
    # ANOMALY DETECTION
    # -----------------------------------

    st.markdown('<p class="section-title">🚨 Anomaly Detection</p>', unsafe_allow_html=True)

    try:
        anomaly_df = df.copy()
        iso = IsolationForest(contamination=0.1, random_state=42)
        anomaly_df["Anomaly"] = iso.fit_predict(anomaly_df[["Amount"]])
        anomalies = anomaly_df[anomaly_df["Anomaly"] == -1]

        if len(anomalies) > 0:
            st.markdown(f'<div class="alert-danger">⚡ {len(anomalies)} unusual transaction(s) flagged.</div>', unsafe_allow_html=True)

            fig_a = px.scatter(
                anomaly_df, x="Date", y="Amount",
                color=anomaly_df["Anomaly"].map({1: "Normal", -1: "Anomaly"}),
                color_discrete_map={"Normal": ACCENT2, "Anomaly": ACCENT3},
                hover_data=["Description","Category"],
            )
            fig_a.update_traces(marker=dict(size=7, opacity=0.85))
            fig_a.update_layout(title=dict(text="Transaction Map", font=dict(color="#e8e4dc", size=13)))
            apply_dark_theme(fig_a)
            st.plotly_chart(fig_a, use_container_width=True)

            # HTML table — no black box
            st.markdown(
                render_table(anomalies[["Date","Description","Amount","Category"]].reset_index(drop=True)),
                unsafe_allow_html=True
            )
        else:
            st.markdown('<div class="alert-success">✓ No anomalies detected.</div>', unsafe_allow_html=True)

    except Exception as e:
        st.markdown(f'<div class="alert-danger">✗ Anomaly detection error: {e}</div>', unsafe_allow_html=True)

    # -----------------------------------
    # TOP 5 EXPENSES
    # -----------------------------------

    st.markdown('<p class="section-title">💸 Top 5 Expenses</p>', unsafe_allow_html=True)

    top5 = df.sort_values("Amount", ascending=False).head(5).reset_index(drop=True)
    st.markdown(render_table(top5[["Date","Description","Amount","Category"]]), unsafe_allow_html=True)

    # -----------------------------------
    # ALL TRANSACTIONS
    # -----------------------------------

    with st.expander("📋  All Transactions", expanded=False):
        st.markdown(
            render_table(df[["Date","Description","Amount","Category"]].reset_index(drop=True)),
            unsafe_allow_html=True
        )

    # -----------------------------------
    # AI INSIGHTS
    # -----------------------------------

    st.markdown('<p class="section-title">🤖 AI Financial Advisor</p>', unsafe_allow_html=True)

    if not gemini_api_key:
        st.markdown(
            '<div class="alert-warning">⚠ Enter your Gemini API key in the sidebar (☰) to enable AI insights.</div>',
            unsafe_allow_html=True
        )
    else:
        if st.button("✦  Generate AI Insights"):
            with st.spinner("Analysing your spending…"):
                try:
                    prompt = f"""You are an expert personal finance advisor. Analyse the data below and respond concisely.

Category Summary:
{category_summary.to_string(index=False)}

Total Spending: ₹{total_spending:,.2f}
Total Transactions: {total_transactions}
Average Transaction: ₹{avg_transaction:,.2f}
Predicted Future Avg Daily Spend: ₹{predicted_spending if predicted_spending is not None else 'N/A'}

Give exactly 5 numbered insights:
1. Biggest spending category and its implications
2. Spending behaviour pattern
3. Forecast interpretation
4. Anomaly / risk observation
5. One actionable savings recommendation

Under 220 words. Direct, no fluff."""

                    model    = genai.GenerativeModel("models/gemini-2.5-flash")
                    response = model.generate_content(prompt)
                    # Convert newlines to HTML for clean rendering
                    html_text = response.text.replace("\n", "<br>")
                    st.markdown(f'<div class="ai-box">{html_text}</div>', unsafe_allow_html=True)

                except Exception as e:
                    st.markdown(f'<div class="alert-danger">✗ Gemini error: {e}</div>', unsafe_allow_html=True)

else:
    st.markdown("""
    <div style="text-align:center; padding:5rem 2rem; color:#2a2c32;">
      <div style="font-size:3.5rem; margin-bottom:1rem;">📂</div>
      <div style="font-family:'DM Serif Display',serif; font-size:1.6rem; color:#3a3c44; letter-spacing:-0.01em;">
        Upload a file to get started
      </div>
      <div style="font-size:0.75rem; margin-top:0.6rem; letter-spacing:0.1em; text-transform:uppercase; color:#2a2c32;">
        CSV or PDF bank statement
      </div>
    </div>
    """, unsafe_allow_html=True)
