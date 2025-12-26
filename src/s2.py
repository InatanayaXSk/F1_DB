"""
Streamlit Dashboard for F1 Prediction System
Interactive UI to view data, predictions, and model explanations
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
from telemetry_handler import TelemetryHandler
from ml_models import F1PredictionModel


# Page configuration
st.set_page_config(
    page_title="F1 Prediction System",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark theme CSS injection
st.markdown("""
<style>
    :root {
        --primary-bg: #0a0e27;
        --secondary-bg: #1a1f3a;
        --accent-yellow: #ffd60a;
        --accent-dark: #1a1a2e;
        --text-primary: #e0e0e0;
        --text-secondary: #a0a0a0;
    }
    
    * {
        color: var(--text-primary);
    }
    
    .stApp {
        background-color: var(--primary-bg);
        background-image: 
            radial-gradient(circle at 20% 50%, rgba(255, 214, 10, 0.03) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(255, 214, 10, 0.02) 0%, transparent 50%);
    }
    
    .stMainBlockContainer {
        background-color: var(--primary-bg);
    }
    
    .stMetric {
        background-color: var(--secondary-bg);
        padding: 20px;
        border-radius: 8px;
        border-left: 4px solid var(--accent-yellow);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background-color: var(--secondary-bg);
        border-radius: 8px;
        padding: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 6px;
        color: var(--text-secondary);
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--accent-dark);
        color: var(--accent-yellow);
    }
    
    .stExpander {
        background-color: var(--secondary-bg);
        border: 1px solid rgba(255, 214, 10, 0.2);
        border-radius: 8px;
    }
    
    .stDataFrame {
        background-color: var(--secondary-bg);
    }
    
    [data-testid="stDataFrameContainer"] {
        background-color: var(--secondary-bg);
        border-radius: 8px;
        padding: 12px;
    }
    
    .stPlotlyChart {
        background-color: var(--secondary-bg);
        border-radius: 8px;
        padding: 12px;
        margin: 12px 0;
    }
    
    .stSidebar [data-testid="stSidebar"] {
        background-color: var(--secondary-bg);
    }
    
    .stSelectbox, .stMultiSelect, .stSlider, .stTextInput, .stTextArea {
        background-color: var(--accent-dark);
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: var(--accent-yellow);
    }
    
    hr {
        border-color: rgba(255, 214, 10, 0.3);
    }
    
    .info-panel {
        background-color: var(--secondary-bg);
        border-left: 4px solid var(--accent-yellow);
        padding: 16px;
        border-radius: 6px;
        margin: 16px 0;
    }
    
    .stat-card {
        background-color: var(--secondary-bg);
        border: 1px solid rgba(255, 214, 10, 0.2);
        border-radius: 8px;
        padding: 20px;
        text-align: center;
    }
    
    .driver-card {
        background-color: var(--accent-dark);
        border: 1px solid rgba(255, 214, 10, 0.2);
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main Streamlit application"""
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("## 🏎️ Formula 1 Prediction System")
    with col2:
        st.markdown("**v2.0** | Race Engineering Console")
    
    st.divider()
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 🎛️ MISSION CONTROL")
        st.divider()
        
        page = st.radio(
            "Navigation",
            ["🏠 Home", "👤 Drivers & Teams", "🏁 2026 Predictions", 
             "🗄️ Database", "📡 Telemetry", "🧠 Model Predictions", "📊 Feature Analysis"],
            label_visibility="collapsed"
        )
        
        st.divider()
        st.markdown("**System Status**")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Status", "Active")
        with col2:
            st.metric("Mode", "Offline")
    
    # Route pages
    if page == "🏠 Home":
        show_home()
    elif page == "👤 Drivers & Teams":
        show_drivers_teams()
    elif page == "🏁 2026 Predictions":
        show_2026_predictions()
    elif page == "🗄️ Database":
        show_database_explorer()
    elif page == "📡 Telemetry":
        show_telemetry_viewer()
    elif page == "🧠 Model Predictions":
        show_predictions()
    elif page == "📊 Feature Analysis":
        show_feature_importance()


def show_home():
    """Home page with system overview"""
    
    # Overview metrics
    st.markdown("### 📊 SYSTEM OVERVIEW")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🤖 ML Models", "5+", "Ensemble")
    with col2:
        st.metric("🏁 Race Predictions", "24", "2026 Season")
    with col3:
        st.metric("📈 Data Points", "100K+", "Telemetry")
    with col4:
        st.metric("⚙️ System", "Ready", "Initialized")
    
    st.divider()
    
    # Architecture sections
    st.markdown("### 🏗️ SYSTEM ARCHITECTURE")
    
    tab1, tab2, tab3 = st.tabs(["🔄 Data Pipeline", "💾 Storage Layer", "🎯 Prediction Engine"])
    
    with tab1:
        st.markdown("""
        **Data Collection & Processing**
        - 🔗 FastF1 API integration with Redis caching
        - 📊 Historical data: 2023-2025 seasons
        - 🔄 Real-time synchronization capability
        - ⚡ Offline mode support
        """)
    
    with tab2:
        st.markdown("""
        **Data Storage Architecture**
        - 🗄️ PostgreSQL: Structured race, driver, qualifying data
        - 📄 JSON: Telemetry and sensor logs
        - 🔐 Cached records: Redis (when online)
        - 📦 32+ tables normalized schema
        """)
    
    with tab3:
        st.markdown("""
        **ML Prediction Models**
        - 🌳 Gradient Boosting (XGBoost)
        - 🎲 Random Forest
        - 🧠 Neural Networks (pending)
        - 📊 Ensemble voting (production)
        """)
    
    st.divider()
    
    # Features grid
    st.markdown("### ✨ CORE FEATURES")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Data Exploration**
        - 📋 Browse drivers, teams, race history
        - 📊 Interactive SQL query explorer
        - 📈 Seasonal statistics and comparisons
        - 🏆 Historical standings
        """)
    
    with col2:
        st.markdown("""
        **Race Predictions**
        - 🎯 Position & championship forecasts
        - 📊 Confidence metrics per prediction
        - 🏁 Race-by-race breakdowns
        - 🏆 Final standings projections
        """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Telemetry Analysis**
        - 📡 Session-level diagnostics
        - 📉 Performance visualization
        - ⚙️ Technical metrics explorer
        - 🔍 Incident analysis
        """)
    
    with col2:
        st.markdown("""
        **Model Explainability**
        - 🧠 Feature importance breakdown
        - 📊 Model performance metrics
        - 🎯 Prediction confidence analysis
        - 📈 Training insights
        """)
    
    st.divider()
    
    # Quick start
    st.markdown("### 🚀 QUICK START")
    
    with st.expander("📖 Setup Instructions", expanded=False):
        st.markdown("""
        **Step 1: Initialize Database**
        ```
        python src/database.py
        ```
        
        **Step 2: Populate Data**
        ```
        python src/populate_database.py
        ```
        
        **Step 3: Train Models & Generate Predictions**
        ```
        jupyter notebooks/f1_2026_predictions.ipynb
        ```
        
        **Step 4: View Dashboard**
        ```
        streamlit run src/streamlit_app.py
        ```
        """)
    
    st.info("💡 **Navigation Tip**: Use the sidebar to explore different analysis views")


def show_drivers_teams():
    """Drivers and Teams page with comprehensive driver info"""
    
    st.markdown("### 👤 DRIVERS & TEAMS ROSTER")
    
    try:
        db = F1Database()
        
        # Year selector
        years_query = "SELECT DISTINCT year FROM drivers ORDER BY year DESC"
        years_df = db.execute_query(years_query)
        
        if len(years_df) > 0:
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                selected_year = st.selectbox(
                    "Select Season",
                    years_df['year'].tolist(),
                    index=0,
                    label_visibility="collapsed"
                )
            
            # Get drivers for selected year
            drivers_query = f"""
            SELECT 
                driver_number as 'Car Number',
                full_name as 'Driver Name',
                abbreviation as 'Code',
                team_name as 'Constructor/Team'
            FROM drivers
            WHERE year = {selected_year}
            ORDER BY team_name, driver_number
            """
            drivers_df = db.execute_query(drivers_query)
            
            if len(drivers_df) > 0:
                # Overview metrics
                st.divider()
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🏎️ Drivers", len(drivers_df))
                with col2:
                    num_teams = drivers_df['Constructor/Team'].nunique()
                    st.metric("🏁 Teams", num_teams)
                with col3:
                    st.metric("📅 Season", selected_year)
                with col4:
                    st.metric("🔢 Grid Size", len(drivers_df))
                
                st.divider()
                
                # Drivers table
                st.markdown(f"#### {selected_year} Grid - {len(drivers_df)} Competitors")
                st.dataframe(
                    drivers_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                st.divider()
                
                # Group by team
                st.markdown("#### 🏁 DRIVERS BY CONSTRUCTOR")
                
                teams_sorted = sorted(drivers_df['Constructor/Team'].unique())
                
                col_width = 2
                cols = st.columns(col_width)
                
                for idx, team in enumerate(teams_sorted):
                    team_drivers = drivers_df[drivers_df['Constructor/Team'] == team]
                    col_idx = idx % col_width
                    
                    with cols[col_idx]:
                        st.markdown(f"**{team}** ({len(team_drivers)} drivers)")
                        for _, driver in team_drivers.iterrows():
                            st.markdown(f"""
                            `#{driver['Car Number']}` **{driver['Driver Name']}** 
                            *{driver['Code']}*
                            """)
                        st.divider()
                
                st.divider()
                
                # Download option
                st.markdown("#### 📥 EXPORT DATA")
                csv = drivers_df.to_csv(index=False)
                st.download_button(
                    label=f"📋 Download {selected_year} Driver List (CSV)",
                    data=csv,
                    file_name=f"f1_drivers_{selected_year}.csv",
                    mime="text/csv"
                )
            else:
                st.warning(f"⚠️ No driver data available for {selected_year}")
        else:
            st.warning("⚠️ No driver data available. Run data fetcher to populate the database.")
    
    except Exception as e:
        st.error(f"❌ Error: {e}")
        st.info("Make sure to run `python src/database.py` to initialize the database first.")


def show_2026_predictions():
    """2026 Season Predictions page with race-by-race breakdown"""
    
    st.markdown("### 🏁 2026 CHAMPIONSHIP FORECAST")
    
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
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🎯 Total Predictions", len(predictions_df))
            with col2:
                num_races = predictions_df['race_id'].nunique()
                st.metric("🏁 Races", num_races)
            with col3:
                num_drivers = predictions_df['driver_number'].nunique()
                st.metric("👤 Drivers", num_drivers)
            with col4:
                avg_confidence = predictions_df['confidence'].mean()
                st.metric("📊 Avg Confidence", f"{avg_confidence:.2%}")
            
            st.divider()
            
            # Race selector and tabs
            race_options = predictions_df[['round_number', 'event_name', 'event_date']].drop_duplicates()
            race_options = race_options.sort_values('round_number')
            
            st.markdown("#### SELECT RACE")
            
            selected_race = st.selectbox(
                "Choose a race",
                options=race_options['event_name'].tolist(),
                format_func=lambda x: f"Round {race_options[race_options['event_name']==x]['round_number'].values[0]:2d} | {x}",
                label_visibility="collapsed"
            )
            
            # Filter for selected race
            race_predictions = predictions_df[predictions_df['event_name'] == selected_race].copy()
            race_predictions = race_predictions.sort_values('predicted_position')
            
            if len(race_predictions) > 0:
                # Race header
                race_round = int(race_predictions['round_number'].iloc[0])
                race_date = race_predictions['event_date'].iloc[0]
                
                st.divider()
                st.markdown(f"## Round {race_round:02d} • {selected_race}")
                st.markdown(f"📅 **Race Date:** {race_date}")
                
                # Main prediction tabs
                tab1, tab2, tab3 = st.tabs(["🏆 Top 10", "📊 Full Grid", "📈 Visualization"])
                
                with tab1:
                    st.markdown("### 🏆 PREDICTED PODIUM & TOP 10")
                    top10 = race_predictions.head(10).copy()
                    top10['Position'] = range(1, len(top10) + 1)
                    
                    # Display with emoji medals
                    for idx, (_, row) in enumerate(top10.iterrows()):
                        medal = "🥇" if idx == 0 else "🥈" if idx == 1 else "🥉" if idx == 2 else f"{idx+1:2d}."
                        col1, col2, col3 = st.columns([1, 3, 1])
                        
                        with col1:
                            st.markdown(f"# {medal}")
                        with col2:
                            st.markdown(f"""
                            **#{int(row['driver_number'])} {row['driver_name']}**  
                            {row['team_name']} | Confidence: {row['confidence']:.1%}
                            """)
                        with col3:
                            st.metric("Score", f"{row['confidence']:.3f}")
                
                with tab2:
                    st.markdown("### 📋 FULL GRID")
                    full_grid = race_predictions.copy()
                    full_grid['Position'] = range(1, len(full_grid) + 1)
                    full_grid_display = full_grid[['Position', 'driver_name', 'team_name', 'driver_number', 'confidence']]
                    full_grid_display.columns = ['Pos', 'Driver', 'Team', 'Car #', 'Confidence']
                    full_grid_display['Confidence'] = full_grid_display['Confidence'].apply(lambda x: f"{x:.1%}")
                    st.dataframe(full_grid_display, use_container_width=True, hide_index=True)
                
                with tab3:
                    st.markdown("### 📈 CONFIDENCE ANALYSIS")
                    
                    fig = go.Figure()
                    
                    fig.add_trace(go.Bar(
                        x=race_predictions['driver_name'].head(15),
                        y=race_predictions['confidence'].head(15),
                        marker=dict(
                            color=race_predictions['confidence'].head(15),
                            colorscale='YlOrRd',
                            showscale=True,
                            colorbar=dict(title="Confidence")
                        ),
                        hovertemplate='<b>%{x}</b><br>Confidence: %{y:.1%}<extra></extra>'
                    ))
                    
                    fig.update_layout(
                        title=f"Top 15 Prediction Confidence - {selected_race}",
                        xaxis_title="Driver",
                        yaxis_title="Confidence Score",
                        template="plotly_dark",
                        hovermode='x unified',
                        height=500
                    )
                    fig.update_xaxes(tickangle=-45)
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # Feature analysis
                st.divider()
                st.markdown("### 🔍 PREDICTION INPUTS")
                
                with st.expander("📊 Feature Analysis", expanded=False):
                    if 'features_json' in race_predictions.columns:
                        try:
                            sample_features = json.loads(race_predictions.iloc[0]['features_json'])
                            sample_driver = race_predictions.iloc[0]['driver_name']
                            
                            st.markdown(f"**Sample Features** *(First Predicted Driver: {sample_driver})*")
                            features_df = pd.DataFrame([sample_features]).T
                            features_df.columns = ['Value']
                            features_df['Feature'] = features_df.index
                            features_df = features_df[['Feature', 'Value']]
                            st.dataframe(features_df, use_container_width=True, hide_index=True)
                        except:
                            st.info("Feature data unavailable")
            
            # Championship standings projection
            st.divider()
            st.markdown("### 🏆 PROJECTED CHAMPIONSHIP STANDINGS")
            
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
            
            # Visualization
            tab1, tab2 = st.tabs(["📊 Top 10 Standings", "🏁 Full Championship"])
            
            with tab1:
                top_standings = standings.head(10)
                
                fig = px.bar(
                    top_standings,
                    x='Points',
                    y='Driver',
                    color='Team',
                    orientation='h',
                    title="Projected Top 10 - Championship Points",
                    labels={'Points': 'Championship Points', 'Driver': 'Driver'},
                )
                fig.update_layout(template="plotly_dark", height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                st.dataframe(standings, use_container_width=True, hide_index=True)
        
        else:
            st.warning("⚠️ No 2026 predictions available")
            st.markdown("""
            **To generate predictions:**
            1. Open `notebooks/f1_2026_predictions.ipynb`
            2. Run all cells to train models
            3. Refresh this page
            """)
    
    except Exception as e:
        st.error(f"❌ Error: {e}")


def show_database_explorer():
    """Database explorer page"""
    
    st.markdown("### 🗄️ DATABASE EXPLORER")
    
    try:
        db = F1Database()
        
        # Table selector
        tables = ["races", "drivers", "teams", "race_results", 
                  "qualifying_results", "sprint_results", "predictions"]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_table = st.selectbox(
                "SELECT TABLE",
                tables,
                label_visibility="collapsed"
            )
        
        with col2:
            st.markdown("")
        
        st.divider()
        
        # Execute query
        if selected_table:
            
            # Enhanced query for drivers
            if selected_table == "drivers":
                query = "SELECT driver_number, full_name, abbreviation, team_name, year FROM drivers ORDER BY year DESC, driver_number"
            else:
                query = f"SELECT * FROM {selected_table}"
            
            df = db.execute_query(query)
            
            if len(df) > 0:
                # Info row
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📊 Records", len(df))
                with col2:
                    st.metric("📋 Columns", len(df.columns))
                with col3:
                    st.metric("💾 Table", selected_table)
                
                st.divider()
                
                # Display data
                st.markdown(f"#### {selected_table.upper()} DATA")
                st.dataframe(df, use_container_width=True)
                
                st.divider()
                
                # Download option
                csv = df.to_csv(index=False)
                st.download_button(
                    label=f"📥 Download {selected_table} (CSV)",
                    data=csv,
                    file_name=f"{selected_table}.csv",
                    mime="text/csv"
                )
            else:
                st.info(f"⚠️ No data in {selected_table} table")
        
        # Custom query section
        st.divider()
        st.markdown("### 🔍 CUSTOM SQL QUERY")
        
        with st.expander("📝 Run Custom Query", expanded=False):
            custom_query = st.text_area(
                "Enter SQL Query",
                "SELECT * FROM races LIMIT 10",
                height=150,
                label_visibility="collapsed"
            )
            
            if st.button("⚡ EXECUTE", use_container_width=True):
                try:
                    result_df = db.execute_query(custom_query)
                    st.success(f"✓ Query executed - {len(result_df)} rows returned")
                    st.dataframe(result_df, use_container_width=True)
                except Exception as e:
                    st.error(f"❌ Query error: {e}")
    
    except Exception as e:
        st.error(f"❌ Database error: {e}")


def show_telemetry_viewer():
    """Telemetry viewer page"""
    
    st.markdown("### 📡 TELEMETRY DIAGNOSTICS CONSOLE")
    
    try:
        handler = TelemetryHandler()
        
        # Get telemetry summary
        summary = handler.get_telemetry_summary()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📁 Total Files", summary['total_files'])
        with col2:
            years = ", ".join(summary['by_year'].keys()) if summary['by_year'] else "None"
            st.metric("📅 Years", years if years else "No Data")
        with col3:
            st.metric("📊 Sessions", sum(summary['by_year'].values()) if summary['by_year'] else 0)
        
        st.divider()
        
        # List all telemetry files
        files = handler.list_available_telemetry()
        
        if files:
            st.markdown("#### 🔍 AVAILABLE TELEMETRY DATA")
            
            selected_file = st.selectbox(
                "Select telemetry session",
                files,
                label_visibility="collapsed"
            )
            
            if selected_file:
                # Parse file path
                parts = selected_file.split(os.sep)
                
                if len(parts) >= 3:
                    year = parts[0]
                    event = parts[1]
                    session = parts[2]
                    
                    st.divider()
                    st.markdown(f"## 📊 SESSION: {event.upper()}")
                    st.markdown(f"📅 Year: **{year}** | Session: **{session}**")
                    st.divider()
                    
                    # Load file
                    file_path = os.path.join(handler.telemetry_dir, selected_file)
                    
                    try:
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                        
                        # Tabs for different views
                        tab1, tab2 = st.tabs(["📋 Metadata", "📊 Telemetry Data"])
                        
                        with tab1:
                            st.markdown("### SESSION METADATA")
                            metadata = data.get('metadata', {})
                            if metadata:
                                st.json(metadata)
                            else:
                                st.info("No metadata available")
                        
                        with tab2:
                            # Show data
                            if 'telemetry' in data:
                                st.markdown("### TELEMETRY STREAM")
                                telemetry_df = pd.DataFrame(data['telemetry'])
                                st.dataframe(telemetry_df, use_container_width=True)
                                
                                # Plot if numeric columns exist
                                numeric_cols = telemetry_df.select_dtypes(include=['float64', 'int64']).columns
                                if len(numeric_cols) > 0:
                                    st.divider()
                                    st.markdown("#### VISUALIZATION")
                                    plot_col = st.selectbox(
                                        "Select metric to visualize",
                                        numeric_cols,
                                        label_visibility="collapsed"
                                    )
                                    
                                    fig = px.line(
                                        telemetry_df,
                                        y=plot_col,
                                        title=f"{plot_col} - Telemetry Stream",
                                        labels={plot_col: 'Value', 'index': 'Sample'}
                                    )
                                    fig.update_layout(template="plotly_dark", height=500)
                                    st.plotly_chart(fig, use_container_width=True)
                            
                            elif 'laps' in data:
                                st.markdown("### LAP DATA")
                                laps_df = pd.DataFrame(data['laps'])
                                st.dataframe(laps_df, use_container_width=True)
                    
                    except Exception as e:
                        st.error(f"❌ Error loading file: {e}")
        else:
            st.warning("⚠️ No telemetry data available")
            st.markdown("Run data fetcher to collect telemetry data.")
    
    except Exception as e:
        st.error(f"❌ Error: {e}")


def show_predictions():
    """Model predictions page"""
    
    st.markdown("### 🧠 PREDICTION ENGINE")
    
    try:
        db = F1Database()
        
        # Get predictions from database
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
            st.markdown("#### STORED PREDICTIONS INVENTORY")
            
            # Filter options
            col1, col2, col3 = st.columns(3)
            with col1:
                session_types = predictions_df['session_type'].unique()
                selected_session = st.selectbox("Session Type", ['All'] + list(session_types), label_visibility="collapsed")
            
            with col2:
                model_types = predictions_df['model_type'].unique()
                selected_model = st.selectbox("Model Type", ['All'] + list(model_types), label_visibility="collapsed")
            
            with col3:
                st.markdown("")
            
            st.divider()
            
            # Filter data
            filtered_df = predictions_df.copy()
            if selected_session != 'All':
                filtered_df = filtered_df[filtered_df['session_type'] == selected_session]
            if selected_model != 'All':
                filtered_df = filtered_df[filtered_df['model_type'] == selected_model]
            
            # Stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🎯 Predictions", len(filtered_df))
            with col2:
                if 'confidence' in filtered_df.columns:
                    avg_conf = filtered_df['confidence'].mean()
                    st.metric("📊 Avg Confidence", f"{avg_conf:.1%}")
                else:
                    st.metric("📊 Status", "No Conf")
            with col3:
                st.metric("🏎️ Drivers", filtered_df['driver_name'].nunique())
            
            st.divider()
            
            # Display predictions
            st.markdown("#### PREDICTION DATA")
            display_cols = ['driver_number', 'driver_name', 'team_name', 'event_name', 
                          'year', 'session_type', 'predicted_position', 'confidence', 'model_type']
            available_cols = [col for col in display_cols if col in filtered_df.columns]
            st.dataframe(filtered_df[available_cols], use_container_width=True)
            
            # Visualization
            st.divider()
            st.markdown("#### 📈 VISUALIZATION")
            
            if len(filtered_df) > 0 and 'driver_name' in filtered_df.columns:
                
                fig = px.scatter(
                    filtered_df.head(50),
                    x='driver_number',
                    y='predicted_position',
                    size='confidence',
                    color='team_name',
                    hover_data=['driver_name', 'team_name', 'event_name', 'confidence'],
                    title="Predictions by Driver",
                    labels={'driver_number': 'Driver Number', 'predicted_position': 'Predicted Position'}
                )
                fig.update_layout(template="plotly_dark", height=500)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ No predictions available")
            st.markdown("Train models using the Jupyter notebook.")
        
        # Model inventory
        st.divider()
        st.markdown("#### 🤖 TRAINED MODELS")
        
        model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
        if os.path.exists(model_dir):
            model_files = [f for f in os.listdir(model_dir) if f.endswith('.pkl')]
            
            if model_files:
                st.markdown("**Trained Models:**")
                for model_file in model_files:
                    st.markdown(f"✓ `{model_file}`")
            else:
                st.info("No trained models found")
        else:
            st.info("Models directory not found")
    
    except Exception as e:
        st.error(f"❌ Error: {e}")


def show_feature_importance():
    """Feature importance page"""
    
    st.markdown("### 📊 FEATURE IMPORTANCE & EXPLAINABILITY")
    
    try:
        model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
        
        # Check for metadata files
        metadata_files = []
        if os.path.exists(model_dir):
            metadata_files = [f for f in os.listdir(model_dir) if f.endswith('_metadata.json')]
        
        if metadata_files:
            st.markdown("#### SELECT MODEL")
            selected_model = st.selectbox(
                "Choose trained model",
                metadata_files,
                label_visibility="collapsed"
            )
            
            if selected_model:
                metadata_path = os.path.join(model_dir, selected_model)
                
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                st.divider()
                st.markdown("### 🔬 MODEL INFORMATION")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Model:** `{selected_model.replace('_metadata.json', '')}`")
                    st.markdown(f"**Saved:** {metadata.get('saved_at', 'N/A')}")
                
                with col2:
                    features = metadata.get('feature_names', [])
                    st.metric("🧬 Features", len(features))
                
                st.divider()
                
                # Feature importance
                feature_importance = metadata.get('feature_importance', {})
                
                if feature_importance:
                    st.markdown("### 📊 FEATURE IMPORTANCE RANKINGS")
                    
                    # Tabs for each model type
                    model_types = list(feature_importance.keys())
                    tabs = st.tabs([f"🤖 {mt.replace('_', ' ').title()}" for mt in model_types])
                    
                    for tab, model_type in zip(tabs, model_types):
                        with tab:
                            importance = feature_importance[model_type]
                            
                            # Create dataframe for plotting
                            importance_df = pd.DataFrame(
                                list(importance.items()),
                                columns=['Feature', 'Importance']
                            ).sort_values('Importance', ascending=False)
                            
                            # Bar chart
                            fig = px.bar(
                                importance_df,
                                x='Importance',
                                y='Feature',
                                orientation='h',
                                title=f"Feature Importance - {model_type.replace('_', ' ').title()}",
                                color='Importance',
                                color_continuous_scale='YlOrRd'
                            )
                            fig.update_layout(
                                template="plotly_dark",
                                height=500,
                                showlegend=False
                            )
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Table
                            st.markdown("**Top Features:**")
                            st.dataframe(
                                importance_df.head(15),
                                use_container_width=True,
                                hide_index=True
                            )
                else:
                    st.info("No feature importance data available")
        else:
            st.warning("⚠️ No trained models found")
            st.markdown("Run the ML pipeline notebook first.")
        
        # Explanation guide
        st.divider()
        st.markdown("### 📚 UNDERSTANDING FEATURE IMPORTANCE")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **What is Feature Importance?**
            
            Indicates which factors most influence model predictions.
            
            - 🔴 **High** = Critical predictor
            - 🟡 **Medium** = Moderate influence
            - 🔵 **Low** = Minimal impact
            """)
        
        with col2:
            st.markdown("""
            **Common Top Predictors**
            
            - 🏁 Qualifying position
            - 📊 Driver average performance
            - 📈 Recent form
            - 🏁 Grid position
            - 🏎️ Car balance metrics
            """)
    
    except Exception as e:
        st.error(f"❌ Error: {e}")


if __name__ == "__main__":
    main()