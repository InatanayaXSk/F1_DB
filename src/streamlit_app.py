"""
Streamlit Dashboard for F1 Prediction System
Interactive UI to view data, predictions, and model explanations
Race Engineering Console Theme
"""

import streamlit as st
import pandas as pd
import os
import sys
import json
import plotly.express as px
import plotly.graph_objects as go

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from database import F1Database
from ml_models import F1PredictionModel


# Page configuration
st.set_page_config(
    page_title="F1 RACE CONTROL",
    page_icon="🏁",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# CUSTOM CSS - RACE ENGINEERING THEME
# ============================================
def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap');
    
    :root {
        --bg-primary: #0a0a0b;
        --bg-secondary: #111113;
        --bg-panel: #161618;
        --bg-card: #1a1a1d;
        --accent-yellow: #f5c518;
        --accent-yellow-dim: #c9a30e;
        --accent-red: #e10600;
        --text-primary: #e8e8e8;
        --text-secondary: #8a8a8a;
        --text-muted: #5a5a5a;
        --border-color: #2a2a2d;
        --success: #00d26a;
        --carbon-pattern: repeating-linear-gradient(
            45deg,
            transparent,
            transparent 2px,
            rgba(255,255,255,0.02) 2px,
            rgba(255,255,255,0.02) 4px
        );
    }
    
    .stApp {
        background: var(--bg-primary);
        background-image: var(--carbon-pattern);
        font-family: 'JetBrains Mono', monospace;
    }
    
    .stApp > header {
        background: transparent;
    }
    
    .stApp [data-testid="stSidebar"] {
        background: var(--bg-secondary);
        border-right: 1px solid var(--border-color);
    }
    
    h1, h2, h3, h4, h5, h6, p, span, div, label {
        font-family: 'JetBrains Mono', monospace !important;
        color: var(--text-primary);
    }
    
    .main-header {
        background: linear-gradient(90deg, var(--bg-panel) 0%, var(--bg-secondary) 100%);
        border-bottom: 2px solid var(--accent-yellow);
        padding: 1.5rem 2rem;
        margin: -1rem -1rem 2rem -1rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        animation: slideDown 0.4s ease-out;
    }
    
    @keyframes slideDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .main-header h1 {
        color: var(--accent-yellow);
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    
    .header-badge {
        background: var(--accent-red);
        color: white;
        padding: 0.3rem 0.8rem;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 1px;
        border-radius: 2px;
    }
    
    .nav-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        padding: 1rem 0;
        animation: fadeIn 0.5s ease-out;
    }
    
    .nav-tile {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 4px;
        padding: 1.2rem;
        cursor: pointer;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .nav-tile::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 3px;
        height: 100%;
        background: var(--accent-yellow);
        transform: scaleY(0);
        transition: transform 0.25s ease;
    }
    
    .nav-tile:hover {
        background: var(--bg-panel);
        border-color: var(--accent-yellow-dim);
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(245, 197, 24, 0.1);
    }
    
    .nav-tile:hover::before {
        transform: scaleY(1);
    }
    
    .nav-tile.active {
        border-color: var(--accent-yellow);
        background: linear-gradient(135deg, var(--bg-panel) 0%, var(--bg-card) 100%);
    }
    
    .nav-tile.active::before {
        transform: scaleY(1);
    }
    
    .nav-tile-icon {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
        color: var(--accent-yellow);
    }
    
    .nav-tile-title {
        font-size: 0.9rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.3rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .nav-tile-subtitle {
        font-size: 0.7rem;
        color: var(--text-secondary);
        line-height: 1.4;
    }
    
    .panel {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 4px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        animation: slideUp 0.4s ease-out;
    }
    
    .panel-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid var(--border-color);
    }
    
    .panel-header h3 {
        color: var(--accent-yellow);
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 0;
    }
    
    .status-indicator {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--success);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
    }
    
    .metric-card {
        background: var(--bg-panel);
        border: 1px solid var(--border-color);
        border-radius: 4px;
        padding: 1rem;
        text-align: center;
        transition: all 0.2s ease;
    }
    
    .metric-card:hover {
        border-color: var(--accent-yellow-dim);
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--accent-yellow);
        margin-bottom: 0.25rem;
    }
    
    .metric-label {
        font-size: 0.7rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .metric-delta {
        font-size: 0.65rem;
        color: var(--success);
        margin-top: 0.25rem;
    }
    
    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border-color), transparent);
        margin: 1.5rem 0;
    }
    
    .stButton > button {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-primary) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        transition: all 0.2s ease !important;
        border-radius: 4px !important;
    }
    
    .stButton > button:hover {
        border-color: var(--accent-yellow) !important;
        background: var(--bg-panel) !important;
        color: var(--accent-yellow) !important;
    }
    
    .stSelectbox > div > div {
        background: var(--bg-card) !important;
        border-color: var(--border-color) !important;
        color: var(--text-primary) !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    .stTextArea > div > div > textarea {
        background: var(--bg-card) !important;
        border-color: var(--border-color) !important;
        color: var(--text-primary) !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    .stDataFrame {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 4px !important;
    }
    
    [data-testid="stMetricValue"] {
        color: var(--accent-yellow) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
        font-family: 'JetBrains Mono', monospace !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    
    [data-testid="stMetricDelta"] {
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background: var(--bg-panel) !important;
        border-radius: 4px !important;
        padding: 0.25rem !important;
        gap: 0.25rem !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: var(--text-secondary) !important;
        font-family: 'JetBrains Mono', monospace !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        font-size: 0.75rem !important;
        border-radius: 2px !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--bg-card) !important;
        color: var(--accent-yellow) !important;
    }
    
    .stExpander {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 4px !important;
    }
    
    .stExpander > div > div > div > div {
        color: var(--text-primary) !important;
    }
    
    .stDownloadButton > button {
        background: transparent !important;
        border: 1px solid var(--accent-yellow) !important;
        color: var(--accent-yellow) !important;
    }
    
    .stDownloadButton > button:hover {
        background: var(--accent-yellow) !important;
        color: var(--bg-primary) !important;
    }
    
    .feature-item {
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        padding: 0.75rem;
        background: var(--bg-panel);
        border-radius: 4px;
        margin-bottom: 0.5rem;
        transition: all 0.2s ease;
    }
    
    .feature-item:hover {
        background: var(--bg-card);
    }
    
    .feature-icon {
        color: var(--accent-yellow);
        font-size: 1rem;
        min-width: 24px;
    }
    
    .feature-content h4 {
        font-size: 0.85rem;
        color: var(--text-primary);
        margin: 0 0 0.25rem 0;
    }
    
    .feature-content p {
        font-size: 0.75rem;
        color: var(--text-secondary);
        margin: 0;
        line-height: 1.4;
    }
    
    .code-block {
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: 4px;
        padding: 1rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        color: var(--text-primary);
        overflow-x: auto;
    }
    
    .code-block code {
        color: var(--accent-yellow);
    }
    
    .info-banner {
        background: linear-gradient(90deg, rgba(245, 197, 24, 0.1), transparent);
        border-left: 3px solid var(--accent-yellow);
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 4px 4px 0;
    }
    
    .info-banner p {
        margin: 0;
        font-size: 0.8rem;
        color: var(--text-secondary);
    }
    
    .section-title {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1.5rem;
    }
    
    .section-title h2 {
        color: var(--text-primary);
        font-size: 1.1rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin: 0;
    }
    
    .section-title .line {
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, var(--border-color), transparent);
    }
    
    .team-card {
        background: var(--bg-panel);
        border: 1px solid var(--border-color);
        border-radius: 4px;
        padding: 1rem;
        margin-bottom: 0.5rem;
    }
    
    .team-card h4 {
        color: var(--accent-yellow);
        font-size: 0.85rem;
        margin: 0 0 0.5rem 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .driver-tag {
        display: inline-block;
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        padding: 0.25rem 0.5rem;
        border-radius: 2px;
        font-size: 0.7rem;
        color: var(--text-secondary);
        margin: 0.2rem;
    }
    
    .race-header {
        background: linear-gradient(90deg, var(--bg-panel), var(--bg-card));
        border: 1px solid var(--border-color);
        border-radius: 4px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    .race-header h2 {
        color: var(--accent-yellow);
        font-size: 1.2rem;
        margin: 0 0 0.5rem 0;
    }
    
    .race-header .meta {
        font-size: 0.75rem;
        color: var(--text-secondary);
    }
    
    .position-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        border-radius: 4px;
        font-weight: 700;
        font-size: 0.8rem;
    }
    
    .position-badge.p1 { background: #ffd700; color: #000; }
    .position-badge.p2 { background: #c0c0c0; color: #000; }
    .position-badge.p3 { background: #cd7f32; color: #000; }
    .position-badge.other { background: var(--bg-panel); color: var(--text-secondary); border: 1px solid var(--border-color); }
    
    </style>
    """, unsafe_allow_html=True)


# ============================================
# NAVIGATION SYSTEM
# ============================================
PAGES = {
    "home": {
        "title": "CONTROL CENTER",
        "subtitle": "System overview and status",
        "icon": "◉"
    },
    "drivers": {
        "title": "DRIVERS & TEAMS",
        "subtitle": "Season roster and team data",
        "icon": "◈"
    },
    "predictions_2026": {
        "title": "2026 PREDICTIONS",
        "subtitle": "Race-by-race forecasts",
        "icon": "◎"
    },
    "database": {
        "title": "DATA EXPLORER",
        "subtitle": "Query and browse tables",
        "icon": "◇"
    },
    "model_predictions": {
        "title": "MODEL OUTPUT",
        "subtitle": "Prediction results",
        "icon": "◐"
    },
    "features": {
        "title": "FEATURE ANALYSIS",
        "subtitle": "Model explainability",
        "icon": "◑"
    }
}


def render_header():
    st.markdown("""
    <div class="main-header">
        <h1>F1 RACE CONTROL</h1>
        <span class="header-badge">PREDICTION SYSTEM</span>
        <div style="flex:1;"></div>
        <div class="status-indicator"></div>
        <span style="font-size:0.7rem; color:#8a8a8a; text-transform:uppercase; letter-spacing:1px;">SYSTEM ACTIVE</span>
    </div>
    """, unsafe_allow_html=True)


def render_navigation():
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    
    cols = st.columns(4)
    page_keys = list(PAGES.keys())
    
    for idx, (page_id, page_info) in enumerate(PAGES.items()):
        col_idx = idx % 4
        with cols[col_idx]:
            is_active = st.session_state.current_page == page_id
            active_class = "active" if is_active else ""
            
            if st.button(
                f"{page_info['icon']} {page_info['title']}",
                key=f"nav_{page_id}",
                use_container_width=True,
                type="secondary" if not is_active else "primary"
            ):
                st.session_state.current_page = page_id
                st.rerun()
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


def render_back_button():
    if st.button("← BACK TO CONTROL CENTER", key="back_btn"):
        st.session_state.current_page = 'home'
        st.rerun()
    st.markdown("")


def main():
    """Main Streamlit application"""
    inject_custom_css()
    render_header()
    render_navigation()
    
    page = st.session_state.get('current_page', 'home')
    
    if page == "home":
        show_home()
    elif page == "drivers":
        show_drivers_teams()
    elif page == "predictions_2026":
        show_2026_predictions()
    elif page == "database":
        show_database_explorer()
    elif page == "model_predictions":
        show_predictions()
    elif page == "features":
        show_feature_importance()


def show_home():
    """Home page with system overview"""
    
    # Status metrics
    st.markdown("""
    <div class="section-title">
        <h2>SYSTEM STATUS</h2>
        <div class="line"></div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("MODELS", "5+", "GB, RF, XGB")
    with col2:
        st.metric("PREDICTIONS", "24", "2026 RACES")
    with col3:
        st.metric("DATA YEARS", "3", "2023-2025")
    with col4:
        st.metric("STATUS", "READY", "OFFLINE OK")
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # System Features Panel
    col_left, col_right = st.columns([1.5, 1])
    
    with col_left:
        st.markdown("""
        <div class="panel">
            <div class="panel-header">
                <div class="status-indicator"></div>
                <h3>SYSTEM CAPABILITIES</h3>
            </div>
        """, unsafe_allow_html=True)
        
        features = [
            ("◉", "DATA PIPELINE", "FastF1 API integration with Redis caching for 2023-2025 seasons"),
            ("◇", "STORAGE ENGINE", "PostgreSQL database with JSON telemetry storage"),
            ("◐", "ML MODELS", "Ensemble models: Gradient Boosting, Random Forest, XGBoost"),
            ("◎", "PREDICTIONS", "Race-by-race predictions for complete 2026 season"),
            ("◈", "STANDINGS", "Projected championship standings with confidence scores"),
            ("◑", "EXPLAINABILITY", "Feature importance and SHAP-based analysis"),
            ("◆", "OFFLINE MODE", "Full functionality without internet after caching")
        ]
        
        for icon, title, desc in features:
            st.markdown(f"""
            <div class="feature-item">
                <span class="feature-icon">{icon}</span>
                <div class="feature-content">
                    <h4>{title}</h4>
                    <p>{desc}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col_right:
        st.markdown("""
        <div class="panel">
            <div class="panel-header">
                <h3>QUICK START</h3>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="code-block">
        <span style="color:#5a5a5a;"># 1. Populate database</span><br>
        <code>python src/populate_database.py</code><br><br>
        <span style="color:#5a5a5a;"># 2. Generate predictions</span><br>
        <code>jupyter notebook f1_2026_predictions.ipynb</code><br><br>
        <span style="color:#5a5a5a;"># 3. Launch dashboard</span><br>
        <code>streamlit run src/streamlit_app.py</code>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-banner">
            <p>Navigate using the tiles above to access prediction data, telemetry, and model analysis.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)


def show_drivers_teams():
    """Drivers and Teams page with comprehensive driver info"""
    render_back_button()
    
    st.markdown("""
    <div class="section-title">
        <h2>◈ DRIVERS & TEAMS</h2>
        <div class="line"></div>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        db = F1Database()
        
        # Year selector
        years_query = "SELECT DISTINCT year FROM drivers ORDER BY year DESC"
        years_df = db.execute_query(years_query)
        
        if len(years_df) > 0:
            col_filter, col_spacer = st.columns([1, 3])
            with col_filter:
                selected_year = st.selectbox("SEASON", years_df['year'].tolist(), index=0)
            
            # Get drivers for selected year
            drivers_query = f"""
            SELECT 
                driver_number as "Car Number",
                full_name as "Driver Name",
                abbreviation as "Code",
                team_name as "Constructor/Team"
            FROM drivers
            WHERE year = {selected_year}
            ORDER BY team_name, driver_number
            """
            drivers_df = db.execute_query(drivers_query)
            
            if len(drivers_df) > 0:
                st.markdown('<div class="panel">', unsafe_allow_html=True)
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("DRIVERS", len(drivers_df))
                with col2:
                    num_teams = drivers_df['Constructor/Team'].nunique()
                    st.metric("TEAMS", num_teams)
                with col3:
                    st.metric("SEASON", selected_year)
                with col4:
                    avg_per_team = len(drivers_df) / num_teams if num_teams > 0 else 0
                    st.metric("AVG/TEAM", f"{avg_per_team:.1f}")
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                
                tab_grid, tab_teams = st.tabs(["GRID VIEW", "BY CONSTRUCTOR"])
                
                with tab_grid:
                    st.markdown('<div class="panel">', unsafe_allow_html=True)
                    # Display as formatted table
                    st.dataframe(
                        drivers_df,
                        use_container_width=True,
                        hide_index=True
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with tab_teams:
                    cols = st.columns(2)
                    teams = sorted(drivers_df['Constructor/Team'].unique())
                    
                    for idx, team in enumerate(teams):
                        team_drivers = drivers_df[drivers_df['Constructor/Team'] == team]
                        col_idx = idx % 2
                        
                        with cols[col_idx]:
                            with st.expander(f"◆ {team.upper()} ({len(team_drivers)})", expanded=False):
                                for _, driver in team_drivers.iterrows():
                                    st.markdown(f"**#{driver['Car Number']}** {driver['Driver Name']} `{driver['Code']}`")
                
                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                
                # Download option
                csv = drivers_df.to_csv(index=False)
                st.download_button(
                    label=f"EXPORT {selected_year} ROSTER",
                    data=csv,
                    file_name=f"f1_drivers_{selected_year}.csv",
                    mime="text/csv"
                )
            else:
                st.markdown("""
                <div class="info-banner">
                    <p>No driver data for selected season. Execute data pipeline.</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="info-banner">
                <p>Database empty. Run: python src/data_fetcher.py</p>
            </div>
            """, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"DATABASE ERROR: {e}")
        st.markdown("""
        <div class="info-banner">
            <p>Initialize database: python src/database.py</p>
        </div>
        """, unsafe_allow_html=True)


def show_2026_predictions():
    """2026 Season Predictions page with race-by-race breakdown"""
    render_back_button()
    
    st.markdown("""
    <div class="section-title">
        <h2>◎ 2026 SEASON PREDICTIONS</h2>
        <div class="line"></div>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        db = F1Database()
        
        # Get 2026 predictions
        predictions_query = """
        SELECT 
            p.race_id,
            r.event_name,
            r.round_number,
            r.event_date,
            p.driver_number,
            d.full_name as driver_name,
            d.team_name,
            p.predicted_position,
            p.confidence,
            p.model_type,
            p.features_json
        FROM predictions p
        JOIN races r ON p.race_id = r.race_id
        LEFT JOIN drivers d ON p.driver_number = d.driver_number AND d.year = 2023
        WHERE r.year = 2026
        ORDER BY r.round_number, p.predicted_position
        """
        predictions_df = db.execute_query(predictions_query)
        
        if len(predictions_df) > 0:
            # Overview stats
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("PREDICTIONS", len(predictions_df))
            with col2:
                num_races = predictions_df['race_id'].nunique()
                st.metric("RACES", num_races)
            with col3:
                num_drivers = predictions_df['driver_number'].nunique()
                st.metric("DRIVERS", num_drivers)
            with col4:
                avg_confidence = predictions_df['confidence'].mean()
                st.metric("AVG CONF", f"{avg_confidence:.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            
            tab_race, tab_championship = st.tabs(["RACE ANALYSIS", "CHAMPIONSHIP PROJECTION"])
            
            with tab_race:
                # Race selector
                race_options = predictions_df[['round_number', 'event_name', 'event_date']].drop_duplicates()
                race_options = race_options.sort_values('round_number')
                
                col_select, col_spacer = st.columns([2, 2])
                with col_select:
                    selected_race = st.selectbox(
                        "SELECT GRAND PRIX",
                        options=race_options['event_name'].tolist(),
                        format_func=lambda x: f"R{race_options[race_options['event_name']==x]['round_number'].values[0]:02d} | {x.upper()}"
                    )
                
                # Filter for selected race
                race_predictions = predictions_df[predictions_df['event_name'] == selected_race].copy()
                race_predictions = race_predictions.sort_values('predicted_position')
                
                if len(race_predictions) > 0:
                    # Race header
                    race_round = race_predictions['round_number'].iloc[0]
                    race_date = race_predictions['event_date'].iloc[0]
                    
                    st.markdown(f"""
                    <div class="race-header">
                        <h2>ROUND {race_round:02d} | {selected_race.upper()}</h2>
                        <span class="meta">DATE: {race_date}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col_podium, col_chart = st.columns([1, 1.5])
                    
                    with col_podium:
                        st.markdown("""
                        <div class="panel">
                            <div class="panel-header">
                                <h3>PREDICTED PODIUM</h3>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        top3 = race_predictions.head(3)
                        for idx, (_, driver) in enumerate(top3.iterrows()):
                            pos = idx + 1
                            badge_class = f"p{pos}" if pos <= 3 else "other"
                            st.markdown(f"""
                            <div class="feature-item">
                                <span class="position-badge {badge_class}">P{pos}</span>
                                <div class="feature-content">
                                    <h4>{driver['driver_name'] or 'Unknown'}</h4>
                                    <p>{driver['team_name'] or 'Unknown'} | Conf: {driver['confidence']:.3f}</p>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with col_chart:
                        # Top 10 predictions
                        top10 = race_predictions.head(10).copy()
                        top10['Position'] = range(1, len(top10) + 1)
                        
                        # Bar chart of top 10
                        fig = go.Figure()
                        fig.add_trace(go.Bar(
                            x=top10['driver_name'],
                            y=top10['confidence'],
                            marker_color='#f5c518',
                            marker_line_color='#c9a30e',
                            marker_line_width=1,
                            hovertemplate='<b>%{x}</b><br>Confidence: %{y:.3f}<extra></extra>'
                        ))
                        fig.update_layout(
                            title=dict(text='TOP 10 CONFIDENCE SCORES', font=dict(color='#e8e8e8', size=14)),
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(22,22,24,1)',
                            font=dict(family='JetBrains Mono, monospace', color='#8a8a8a'),
                            xaxis=dict(tickangle=-45, gridcolor='#2a2a2d'),
                            yaxis=dict(gridcolor='#2a2a2d'),
                            margin=dict(t=40, b=80)
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Full grid
                    with st.expander("VIEW FULL PREDICTED GRID"):
                        full_grid = race_predictions.copy()
                        full_grid['Position'] = range(1, len(full_grid) + 1)
                        full_grid_display = full_grid[['Position', 'driver_name', 'team_name', 'driver_number', 'confidence']]
                        full_grid_display.columns = ['POS', 'DRIVER', 'TEAM', 'CAR#', 'CONF']
                        full_grid_display['CONF'] = full_grid_display['CONF'].apply(lambda x: f"{x:.3f}")
                        st.dataframe(full_grid_display, use_container_width=True, hide_index=True)
                    
                    # Feature importance (if available)
                    if 'features_json' in race_predictions.columns:
                        with st.expander("FEATURE ANALYSIS"):
                            try:
                                # Parse first driver's features as example
                                sample_features = json.loads(race_predictions.iloc[0]['features_json'])
                                
                                features_df = pd.DataFrame([sample_features]).T
                                features_df.columns = ['Value']
                                features_df['Feature'] = features_df.index
                                features_df = features_df[['Feature', 'Value']]
                                st.dataframe(features_df, use_container_width=True, hide_index=True)
                            except:
                                st.markdown('<div class="info-banner"><p>Feature data unavailable</p></div>', unsafe_allow_html=True)
            
            with tab_championship:
                st.markdown("""
                <div class="panel">
                    <div class="panel-header">
                        <h3>PROJECTED DRIVER STANDINGS</h3>
                    </div>
                """, unsafe_allow_html=True)
                
                # Points system
                points_system = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}
                
                # Calculate points for each driver
                driver_points = {}
                for _, pred in predictions_df.iterrows():
                    driver = pred['driver_name']
                    position = pred['predicted_position']
                    points = points_system.get(position, 0)
                    
                    if driver not in driver_points:
                        driver_points[driver] = {'points': 0, 'team': pred['team_name']}
                    driver_points[driver]['points'] += points
                
                # Create standings dataframe
                standings = pd.DataFrame([
                    {'Driver': k, 'Team': v['team'], 'Points': v['points']}
                    for k, v in driver_points.items()
                ]).sort_values('Points', ascending=False)
                
                standings['Position'] = range(1, len(standings) + 1)
                standings = standings[['Position', 'Driver', 'Team', 'Points']]
                standings.columns = ['POS', 'DRIVER', 'TEAM', 'PTS']
                
                col_table, col_viz = st.columns([1, 1.5])
                
                with col_table:
                    st.dataframe(standings.head(10), use_container_width=True, hide_index=True)
                
                with col_viz:
                    top10_standings = standings.head(10)
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        y=top10_standings['DRIVER'],
                        x=top10_standings['PTS'],
                        orientation='h',
                        marker_color='#f5c518',
                        marker_line_color='#c9a30e',
                        marker_line_width=1
                    ))
                    fig.update_layout(
                        title=dict(text='CHAMPIONSHIP POINTS', font=dict(color='#e8e8e8', size=14)),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(22,22,24,1)',
                        font=dict(family='JetBrains Mono, monospace', color='#8a8a8a'),
                        xaxis=dict(gridcolor='#2a2a2d'),
                        yaxis=dict(gridcolor='#2a2a2d', autorange='reversed'),
                        margin=dict(l=120, t=40)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
            
        else:
            st.markdown("""
            <div class="info-banner">
                <p>No 2026 predictions available. Run the predictions notebook first.</p>
            </div>
            <div class="code-block">
            <span style="color:#5a5a5a;"># Generate predictions:</span><br>
            <code>jupyter notebook notebooks/f1_2026_predictions.ipynb</code>
            </div>
            """, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"ERROR: {e}")
        st.markdown('<div class="info-banner"><p>Run 2026 predictions notebook first.</p></div>', unsafe_allow_html=True)


def show_database_explorer():
    """Database explorer page"""
    render_back_button()
    
    st.markdown("""
    <div class="section-title">
        <h2>◇ DATA EXPLORER</h2>
        <div class="line"></div>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        db = F1Database()
        
        # Table selector
        tables = ["races", "drivers", "teams", "race_results", 
                  "qualifying_results", "sprint_results", "predictions"]
        
        tab_browse, tab_query = st.tabs(["TABLE BROWSER", "SQL CONSOLE"])
        
        with tab_browse:
            col_select, col_spacer = st.columns([1, 3])
            with col_select:
                selected_table = st.selectbox("SELECT TABLE", tables)
            
            # Execute query
            if selected_table:
                # Enhanced query for drivers to show all info
                if selected_table == "drivers":
                    query = "SELECT driver_number, full_name, abbreviation, team_name, year FROM drivers ORDER BY year DESC, driver_number"
                else:
                    query = f"SELECT * FROM {selected_table}"
                df = db.execute_query(query)
                
                if len(df) > 0:
                    st.markdown('<div class="panel">', unsafe_allow_html=True)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("ROWS", len(df))
                    with col2:
                        st.metric("COLUMNS", len(df.columns))
                    with col3:
                        st.metric("TABLE", selected_table.upper())
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    # Download option
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="EXPORT CSV",
                        data=csv,
                        file_name=f"{selected_table}.csv",
                        mime="text/csv"
                    )
                else:
                    st.markdown(f'<div class="info-banner"><p>No data in {selected_table} table</p></div>', unsafe_allow_html=True)
        
        with tab_query:
            st.markdown("""
            <div class="panel">
                <div class="panel-header">
                    <h3>SQL QUERY INTERFACE</h3>
                </div>
            """, unsafe_allow_html=True)
            
            custom_query = st.text_area(
                "ENTER SQL QUERY",
                "SELECT * FROM races LIMIT 10",
                height=100
            )
            
            if st.button("EXECUTE", type="primary"):
                try:
                    result_df = db.execute_query(custom_query)
                    st.markdown(f'<div class="info-banner"><p>Returned {len(result_df)} rows</p></div>', unsafe_allow_html=True)
                    st.dataframe(result_df, use_container_width=True, hide_index=True)
                except Exception as e:
                    st.error(f"QUERY ERROR: {e}")
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"DATABASE ERROR: {e}")
        st.markdown('<div class="info-banner"><p>Initialize: python src/database.py</p></div>', unsafe_allow_html=True)


def show_predictions():
    """Model predictions page"""
    render_back_button()
    
    st.markdown("""
    <div class="section-title">
        <h2>◐ MODEL OUTPUT</h2>
        <div class="line"></div>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        db = F1Database()
        
        # Get predictions from database with driver info
        predictions_query = """
        SELECT 
            p.prediction_id,
            p.race_id,
            r.event_name,
            r.year,
            p.session_type,
            p.driver_number,
            d.full_name as driver_name,
            d.team_name,
            p.predicted_position,
            p.confidence,
            p.model_type,
            p.prediction_date
        FROM predictions p
        LEFT JOIN races r ON p.race_id = r.race_id
        LEFT JOIN drivers d ON p.driver_number = d.driver_number AND r.year = d.year
        ORDER BY p.prediction_date DESC, p.predicted_position
        """
        predictions_df = db.execute_query(predictions_query)
        
        if len(predictions_df) > 0:
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                session_types = predictions_df['session_type'].unique()
                selected_session = st.selectbox("SESSION", ['All'] + list(session_types))
            with col2:
                model_types = predictions_df['model_type'].unique()
                selected_model = st.selectbox("MODEL", ['All'] + list(model_types))
            with col3:
                st.metric("TOTAL", len(predictions_df))
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Filter data
            filtered_df = predictions_df.copy()
            if selected_session != 'All':
                filtered_df = filtered_df[filtered_df['session_type'] == selected_session]
            if selected_model != 'All':
                filtered_df = filtered_df[filtered_df['model_type'] == selected_model]
            
            tab_table, tab_viz = st.tabs(["DATA TABLE", "VISUALIZATION"])
            
            with tab_table:
                # Display predictions with formatted columns
                display_cols = ['driver_number', 'driver_name', 'team_name', 'event_name', 
                              'year', 'session_type', 'predicted_position', 'confidence', 'model_type']
                available_cols = [col for col in display_cols if col in filtered_df.columns]
                st.dataframe(filtered_df[available_cols], use_container_width=True, hide_index=True)
            
            with tab_viz:
                if len(filtered_df) > 0 and 'driver_name' in filtered_df.columns:
                    fig = go.Figure()
                    
                    for team in filtered_df['team_name'].dropna().unique():
                        team_data = filtered_df[filtered_df['team_name'] == team]
                        fig.add_trace(go.Scatter(
                            x=team_data['driver_number'],
                            y=team_data['predicted_position'],
                            mode='markers',
                            name=team,
                            marker=dict(size=team_data['confidence'] * 20 + 5),
                            hovertemplate='<b>%{text}</b><br>Position: %{y}<br>Confidence: %{marker.size:.2f}<extra></extra>',
                            text=team_data['driver_name']
                        ))
                    
                    fig.update_layout(
                        title=dict(text='PREDICTIONS BY DRIVER', font=dict(color='#e8e8e8', size=14)),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(22,22,24,1)',
                        font=dict(family='JetBrains Mono, monospace', color='#8a8a8a'),
                        xaxis=dict(gridcolor='#2a2a2d', title='DRIVER NUMBER'),
                        yaxis=dict(gridcolor='#2a2a2d', title='PREDICTED POSITION', autorange='reversed'),
                        legend=dict(font=dict(size=10))
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown('<div class="info-banner"><p>No predictions available. Train models using notebook.</p></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="panel">
            <div class="panel-header">
                <h3>AVAILABLE MODELS</h3>
            </div>
        """, unsafe_allow_html=True)
        
        model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
        if os.path.exists(model_dir):
            model_files = [f for f in os.listdir(model_dir) if f.endswith('.pkl')]
            
            if model_files:
                for model_file in model_files:
                    st.markdown(f"""
                    <div class="feature-item">
                        <span class="feature-icon">◉</span>
                        <span>{model_file}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown('<div class="info-banner"><p>No trained models found</p></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="info-banner"><p>Models directory not found</p></div>', unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"ERROR: {e}")


def show_feature_importance():
    """Feature importance page"""
    render_back_button()
    
    st.markdown("""
    <div class="section-title">
        <h2>◑ FEATURE ANALYSIS</h2>
        <div class="line"></div>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
        
        # Check for metadata files
        metadata_files = []
        if os.path.exists(model_dir):
            metadata_files = [f for f in os.listdir(model_dir) if f.endswith('_metadata.json')]
        
        if metadata_files:
            col_select, col_spacer = st.columns([1, 3])
            with col_select:
                selected_model = st.selectbox("SELECT MODEL", metadata_files)
            
            if selected_model:
                metadata_path = os.path.join(model_dir, selected_model)
                
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                tab_info, tab_importance = st.tabs(["MODEL INFO", "FEATURE IMPORTANCE"])
                
                with tab_info:
                    st.markdown("""
                    <div class="panel">
                        <div class="panel-header">
                            <h3>MODEL METADATA</h3>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**SAVED AT:**")
                        st.code(metadata.get('saved_at', 'Unknown'))
                    with col2:
                        features = metadata.get('feature_names', [])
                        st.markdown(f"**FEATURES:** {len(features)}")
                    
                    if features:
                        with st.expander("VIEW ALL FEATURES"):
                            for feat in features:
                                st.markdown(f"- `{feat}`")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with tab_importance:
                    # Feature importance
                    feature_importance = metadata.get('feature_importance', {})
                    
                    if feature_importance:
                        for model_type, importance in feature_importance.items():
                            st.markdown(f"""
                            <div class="panel">
                                <div class="panel-header">
                                    <h3>{model_type.upper().replace('_', ' ')}</h3>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            # Create dataframe for plotting
                            importance_df = pd.DataFrame(
                                list(importance.items()),
                                columns=['Feature', 'Importance']
                            ).sort_values('Importance', ascending=True)
                            
                            # Bar chart
                            fig = go.Figure()
                            fig.add_trace(go.Bar(
                                y=importance_df['Feature'],
                                x=importance_df['Importance'],
                                orientation='h',
                                marker_color='#f5c518',
                                marker_line_color='#c9a30e',
                                marker_line_width=1
                            ))
                            fig.update_layout(
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(22,22,24,1)',
                                font=dict(family='JetBrains Mono, monospace', color='#8a8a8a'),
                                xaxis=dict(gridcolor='#2a2a2d', title='IMPORTANCE'),
                                yaxis=dict(gridcolor='#2a2a2d'),
                                margin=dict(l=150, t=20),
                                height=max(300, len(importance_df) * 25)
                            )
                            st.plotly_chart(fig, use_container_width=True)
                            
                            st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="info-banner"><p>No feature importance data in metadata</p></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="info-banner"><p>No trained models found. Run ML pipeline notebook.</p></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="panel">
            <div class="panel-header">
                <h3>INTERPRETATION GUIDE</h3>
            </div>
        """, unsafe_allow_html=True)
        
        guide_items = [
            ("HIGHER VALUES", "More influential on predictions"),
            ("QUALIFYING POSITION", "Strong race outcome predictor"),
            ("DRIVER/TEAM AVG", "Historical performance factor"),
            ("RECENT FORM", "Current season momentum"),
            ("GRID POSITION", "Starting position impact"),
            ("TRACK EXPERIENCE", "Circuit familiarity bonus")
        ]
        
        for title, desc in guide_items:
            st.markdown(f"""
            <div class="feature-item">
                <span class="feature-icon">◉</span>
                <div class="feature-content">
                    <h4>{title}</h4>
                    <p>{desc}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"ERROR: {e}")


if __name__ == "__main__":
    main()
