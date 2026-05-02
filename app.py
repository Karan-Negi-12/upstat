# ============================================================
# app.py
# Main entry point — Uptime Status Page
# Phase 1: Skeleton UI + Layout + Session State
# Run with: streamlit run app.py
# ============================================================

import streamlit as st
from streamlit_autorefresh import st_autorefresh

# ── Internal imports ────────────────────────────────────────
from core       import monitor, storage
from components import summary_banner, status_card, incident_log
from utils      import time_helper

# ============================================================
# PAGE CONFIG — Must be FIRST Streamlit call
# ============================================================
st.set_page_config(
    page_title        = "Uptime Status Page",
    page_icon         = "🟢",
    layout            = "wide",
    initial_sidebar_state = "expanded"
)

# ============================================================
# CUSTOM CSS — Full Dark Theme
# ============================================================
st.markdown(
    """
    <style>

    /* ── Google Font ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* ── Global ── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── App Background ── */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }

    /* ── Hide Streamlit Defaults ── */
    #MainMenu  { visibility: hidden; }
    footer     { visibility: hidden; }
    header     { visibility: hidden; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background-color : #161b22;
        border-right     : 1px solid #2e3440;
    }
    [data-testid="stSidebar"] * {
        color: #e6edf3 !important;
    }

    /* ── App Header ── */
    .app-header {
        display         : flex;
        align-items     : center;
        justify-content : space-between;
        padding         : 10px 0 20px 0;
        border-bottom   : 1px solid #2e3440;
        margin-bottom   : 24px;
    }
    .app-title {
        font-size   : 28px;
        font-weight : 700;
        color       : #ffffff;
        margin      : 0;
    }
    .app-subtitle {
        font-size : 14px;
        color     : #8b949e;
        margin    : 4px 0 0 0;
    }
    .app-timestamp {
        font-size        : 12px;
        color            : #8b949e;
        background-color : #1c2128;
        padding          : 6px 12px;
        border-radius    : 20px;
        border           : 1px solid #2e3440;
    }

    /* ── Summary Banner ── */
    .summary-banner-pending {
        background    : linear-gradient(135deg, #1c2128, #161b22);
        border        : 1px solid #2e3440;
        border-left   : 4px solid #4488ff;
        border-radius : 10px;
        padding       : 16px 20px;
        margin-bottom : 24px;
        display       : flex;
        align-items   : center;
        gap           : 12px;
    }
    .banner-icon { font-size: 20px; }
    .banner-text {
        font-size   : 15px;
        font-weight : 600;
        color       : #4488ff;
    }

    /* ── Status Card ── */
    .status-card {
        background-color : #161b22;
        border           : 1px solid #2e3440;
        border-radius    : 12px;
        padding          : 20px;
        margin-bottom    : 16px;
        transition       : all 0.2s ease;
        position         : relative;
        overflow         : hidden;
    }
    .status-card:hover {
        border-color : #58a6ff;
        transform    : translateY(-2px);
        box-shadow   : 0 8px 24px rgba(0, 0, 0, 0.4);
    }
    .status-card-up     { border-left: 4px solid #00ff88; }
    .status-card-down   { border-left: 4px solid #ff4444; }
    .status-card-pending{ border-left: 4px solid #4488ff; }

    /* ── Card Header ── */
    .card-header {
        display         : flex;
        justify-content : space-between;
        align-items     : center;
        margin-bottom   : 6px;
    }
    .card-label {
        font-size   : 16px;
        font-weight : 700;
        color       : #e6edf3;
    }
    .card-url {
        font-size     : 12px;
        color         : #8b949e;
        margin-bottom : 12px;
        word-break    : break-all;
    }

    /* ── Status Badges ── */
    .status-badge {
        font-size     : 12px;
        font-weight   : 700;
        padding       : 4px 10px;
        border-radius : 20px;
    }

    /* ── Card Divider ── */
    .card-divider {
        border     : none;
        border-top : 1px solid #2e3440;
        margin     : 12px 0;
    }

    /* ── Card Stats ── */
    .card-stats {
        display   : flex;
        gap       : 16px;
        flex-wrap : wrap;
    }
    .stat-item {
        display        : flex;
        flex-direction : column;
        gap            : 2px;
    }
    .stat-label {
        font-size : 11px;
        color     : #8b949e;
    }
    .stat-value {
        font-size   : 14px;
        font-weight : 600;
        color       : #e6edf3;
    }

    /* ── Empty State ── */
    .empty-state {
        text-align    : center;
        padding       : 60px 20px;
        background    : #161b22;
        border        : 1px dashed #2e3440;
        border-radius : 12px;
        margin        : 20px 0;
    }
    .empty-icon     { font-size: 48px; margin-bottom: 16px; }
    .empty-title    { font-size: 20px; font-weight: 700; color: #e6edf3; margin-bottom: 8px; }
    .empty-subtitle { font-size: 14px; color: #8b949e; }

    /* ── Sidebar Form ── */
    .sidebar-section {
        background    : #1c2128;
        border        : 1px solid #2e3440;
        border-radius : 10px;
        padding       : 16px;
        margin-bottom : 16px;
    }
    .sidebar-section-title {
        font-size     : 13px;
        font-weight   : 700;
        color         : #8b949e;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom : 12px;
    }

    /* ── Streamlit Input Override ── */
    .stTextInput > div > div > input {
        background-color : #1c2128 !important;
        border           : 1px solid #2e3440 !important;
        color            : #e6edf3 !important;
        border-radius    : 8px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color : #58a6ff !important;
        box-shadow   : 0 0 0 2px rgba(88,166,255,0.2) !important;
    }
    .stButton > button {
        background-color : #238636 !important;
        color            : #ffffff !important;
        border           : none !important;
        border-radius    : 8px !important;
        font-weight      : 600 !important;
        width            : 100% !important;
        padding          : 10px !important;
        transition       : all 0.2s ease !important;
    }
    .stButton > button:hover {
        background-color : #2ea043 !important;
        transform        : translateY(-1px) !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background-color : #161b22;
        border-bottom    : 1px solid #2e3440;
        gap              : 4px;
    }
    .stTabs [data-baseweb="tab"] {
        color            : #8b949e;
        background-color : transparent;
        border-radius    : 8px 8px 0 0;
        padding          : 10px 20px;
        font-weight      : 600;
    }
    .stTabs [aria-selected="true"] {
        color            : #ffffff !important;
        background-color : #1c2128 !important;
        border-bottom    : 2px solid #58a6ff !important;
    }

    /* ── Refresh Button ── */
    .refresh-btn > button {
        background-color : #1c2128 !important;
        border           : 1px solid #2e3440 !important;
        color            : #8b949e !important;
        width            : auto !important;
        padding          : 6px 14px !important;
        font-size        : 13px !important;
    }
    .refresh-btn > button:hover {
        border-color     : #58a6ff !important;
        color            : #58a6ff !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# SESSION STATE — Initialize all keys once
# ============================================================
if "urls"              not in st.session_state:
    st.session_state.urls = []

if "interval"          not in st.session_state:
    st.session_state.interval = 30

if "monitor_started"   not in st.session_state:
    st.session_state.monitor_started = False

if "notifications"     not in st.session_state:
    st.session_state.notifications = []

if "unread_count"      not in st.session_state:
    st.session_state.unread_count = 0

if "confirm_clear"     not in st.session_state:
    st.session_state.confirm_clear = False

# ============================================================
# AUTO REFRESH — Every 10 seconds
# ============================================================
st_autorefresh(interval=10_000, key="uptime_autorefresh")

# ============================================================
# MOCK DATA — Phase 1 placeholder cards
# ============================================================
MOCK_URLS = [
    {
        "id":             "mock_001",
        "label":          "Google",
        "url":            "https://google.com",
        "current_status": "UP",
        "last_latency":   120,
        "last_checked":   None,
        "uptime_percent": None,
        "history":        []
    },
    {
        "id":             "mock_002",
        "label":          "My API",
        "url":            "https://myapi.example.com",
        "current_status": "DOWN",
        "last_latency":   None,
        "last_checked":   None,
        "uptime_percent": None,
        "history":        []
    },
    {
        "id":             "mock_003",
        "label":          "GitHub",
        "url":            "https://github.com",
        "current_status": "PENDING",
        "last_latency":   None,
        "last_checked":   None,
        "uptime_percent": None,
        "history":        []
    }
]

# ============================================================
# HELPER — Responsive column count
# ============================================================
def get_column_count(url_count: int) -> int:
    if url_count == 1:
        return 1
    elif url_count == 2:
        return 2
    else:
        return 3

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:

    # ── Logo / App Name ──────────────────────────────────────
    st.markdown(
        """
        <div style="text-align:center; padding: 16px 0 24px 0;">
            <div style="font-size:36px;">🟢</div>
            <div style="font-size:18px; font-weight:700;
                        color:#e6edf3; margin-top:6px;">
                Uptime Monitor
            </div>
            <div style="font-size:12px; color:#8b949e; margin-top:2px;">
                Real-time URL monitoring
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # ── Add New URL Form ──────────────────────────────────────
    st.markdown(
        '<div class="sidebar-section-title">➕ Add New URL</div>',
        unsafe_allow_html=True
    )

    with st.form(key="add_url_form", clear_on_submit=True):
        input_label = st.text_input(
            "Label (optional)",
            placeholder="e.g. My Portfolio",
            help="A friendly name for this URL"
        )
        input_url = st.text_input(
            "URL *",
            placeholder="https://example.com",
            help="Must start with http:// or https://"
        )
        submitted = st.form_submit_button(
            "➕ Add URL",
            use_container_width=True
        )

        if submitted:
            # Phase 2 will wire up real logic here
            if not input_url.strip():
                st.error("⚠️ Please enter a URL.")
            elif not (input_url.startswith("http://") or
                      input_url.startswith("https://")):
                st.error("⚠️ URL must start with http:// or https://")
            else:
                st.success(f"✅ '{input_url}' added! (Phase 2 will persist this)")

    st.divider()

    # ── Settings ─────────────────────────────────────────────
    st.markdown(
        '<div class="sidebar-section-title">⚙️ Settings</div>',
        unsafe_allow_html=True
    )

    interval_options = {
        "Every 10 seconds": 10,
        "Every 30 seconds": 30,
        "Every 60 seconds": 60
    }

    selected_label = st.radio(
        "Check Interval",
        options    = list(interval_options.keys()),
        index      = 1,
        help       = "How often to ping each URL"
    )
    st.session_state.interval = interval_options[selected_label]

    st.divider()

    # ── Quick Stats (Phase 4 will populate with real data) ────
    st.markdown(
        '<div class="sidebar-section-title">📊 Quick Stats</div>',
        unsafe_allow_html=True
    )

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.metric("Total URLs",  "0", help="Total URLs being monitored")
        st.metric("🟢 UP",       "0")
    with col_s2:
        st.metric("🔴 DOWN",     "0")
        st.metric("Incidents",   "0")

    st.divider()

    # ── Monitor Status ────────────────────────────────────────
    st.markdown(
        '<div class="sidebar-section-title">🔧 Monitor Status</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <div style="font-size:13px; color:#8b949e;">
            🔵 Monitor: <span style="color:#4488ff;">Not started</span><br/>
            ⏱️ Interval: <span style="color:#e6edf3;">30s</span><br/>
            🕐 Last run: <span style="color:#e6edf3;">Never</span>
        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# MAIN CONTENT — Header
# ============================================================
header_col1, header_col2 = st.columns([3, 1])

with header_col1:
    st.markdown(
        f"""
        <div class="app-header">
            <div>
                <p class="app-title">🟢 Uptime Status Page</p>
                <p class="app-subtitle">
                    Real-time monitoring for your URLs
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with header_col2:
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown('<div class="refresh-btn">', unsafe_allow_html=True)
    if st.button("🔄 Refresh Now"):
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="text-align:right; font-size:11px;
                    color:#8b949e; margin-top:4px;">
            Last refreshed:<br/>
            {time_helper.get_current_timestamp()}
        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# TABS
# ============================================================
tab1, tab2 = st.tabs(["📡 Dashboard", "📋 Incident Log"])

# ============================================================
# TAB 1 — DASHBOARD
# ============================================================
with tab1:

    # ── Summary Banner ────────────────────────────────────────
    summary_banner.render_summary_banner([])

    st.markdown("<br/>", unsafe_allow_html=True)

    # ── Phase 1 Notice ───────────────────────────────────────
    st.markdown(
        """
        <div style="background:#1c2128; border:1px solid #2e3440;
                    border-left:4px solid #ffcc00; border-radius:10px;
                    padding:14px 18px; margin-bottom:20px;">
            <span style="color:#ffcc00; font-weight:700;">
                ⚠️ Phase 1 — Skeleton UI
            </span>
            <span style="color:#8b949e; font-size:13px; margin-left:8px;">
                Showing mock data. Real monitoring starts in Phase 3.
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ── Status Cards Grid ─────────────────────────────────────
    st.markdown("### 🌐 Monitored Services")

    urls_to_display = MOCK_URLS
    col_count       = get_column_count(len(urls_to_display))
    cols            = st.columns(col_count)

    for i, url_data in enumerate(urls_to_display):
        with cols[i % col_count]:
            status_card.render_status_card(url_data)

    # ── Empty State (shown when no URLs added) ────────────────
    # In Phase 2, this will show when urls list is empty
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="empty-state" style="opacity:0.5;">
            <div class="empty-icon">💡</div>
            <div class="empty-title">Add Your First URL</div>
            <div class="empty-subtitle">
                Use the sidebar to add URLs you want to monitor.<br/>
                They will appear as cards above.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# TAB 2 — INCIDENT LOG
# ============================================================
with tab2:
    incident_log.render_incident_log([])

# ============================================================
# FOOTER
# ============================================================
st.markdown("<br/><br/>", unsafe_allow_html=True)
st.markdown(
    f"""
    <div style="
        border-top       : 1px solid #2e3440;
        padding          : 12px 0;
        display          : flex;
        justify-content  : space-between;
        align-items      : center;
        font-size        : 12px;
        color            : #8b949e;
    ">
        <div>
            🟢 <strong style="color:#e6edf3;">Uptime Status Page</strong>
            &nbsp;|&nbsp; Built with Python + Streamlit
        </div>
        <div>
            🕐 {time_helper.get_current_timestamp()}
            &nbsp;|&nbsp; ⏱️ Auto-refresh: 10s
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
