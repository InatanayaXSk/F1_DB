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
    layout="wide"
)


def main():
    """Main Streamlit application"""
    
    st.title("🏎️ Formula 1 Prediction System")
    st.markdown("---")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select Page",
        ["Home", "Drivers & Teams", "2026 Predictions", "Database Explorer", "Telemetry Viewer", "Model Predictions", "Feature Importance"]
    )
    
    if page == "Home":
        show_home()
    elif page == "Drivers & Teams":
        show_drivers_teams()
    elif page == "2026 Predictions":
        show_2026_predictions()
    elif page == "Database Explorer":
        show_database_explorer()
    elif page == "Telemetry Viewer":
        show_telemetry_viewer()
    elif page == "Model Predictions":
        show_predictions()
    elif page == "Feature Importance":
        show_feature_importance()


def show_home():
    """Home page with system overview"""
    st.header("Welcome to F1 Prediction System")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Models", "5+", "GB, RF, XGB")
    with col2:
        st.metric("2026 Predictions", "24 Races", "Full Season")
    with col3:
        st.metric("Status", "Offline Ready", "✓")
    
    st.markdown("---")
    
    st.subheader("System Features")
    
    features = {
        "🔄 Data Collection": "FastF1 API with Redis caching (2023-2025)",
        "💾 Storage": "PostgreSQL for structured data, JSON for telemetry",
        "🤖 Machine Learning": "Multiple ensemble models with feature importance",
        "📊 2026 Predictions": "Race-by-race predictions for entire 2026 season",
        "🏁 Championship Projections": "Projected driver standings based on predictions",
        "📈 Explainability": "Feature importance and confidence scores",
        "🌐 Offline Mode": "Works without internet after Redis caching"
    }
    
    for feature, description in features.items():
        st.markdown(f"**{feature}**: {description}")
    
    st.markdown("---")
    
    st.subheader("Quick Start")
    
    st.markdown("""
    1. **Data Collection**: Run `python src/populate_database.py` to populate database (2023 data)
    2. **Generate 2026 Predictions**: Run `notebooks/f1_2026_predictions.ipynb`
    3. **View Dashboard**: Launch this Streamlit app
    4. **Explore**: Navigate to "2026 Predictions" to see race-by-race forecasts
    """)
    
    st.info("💡 Navigate using the sidebar to explore different features")


def show_drivers_teams():
    """Drivers and Teams page with comprehensive driver info"""
    st.header("🏎️ Drivers & Teams")
    
    try:
        db = F1Database()
        
        # Year selector
        years_query = "SELECT DISTINCT year FROM drivers ORDER BY year DESC"
        years_df = db.execute_query(years_query)
        
        if len(years_df) > 0:
            selected_year = st.selectbox("Select Season", years_df['year'].tolist(), index=0)
            
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
                st.subheader(f"{selected_year} Season - Drivers & Teams")
                
                # Display as formatted table
                st.dataframe(
                    drivers_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Statistics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Drivers", len(drivers_df))
                with col2:
                    num_teams = drivers_df['Constructor/Team'].nunique()
                    st.metric("Teams", num_teams)
                with col3:
                    st.metric("Season", selected_year)
                
                st.markdown("---")
                
                # Group by team
                st.subheader("Drivers by Team")
                for team in sorted(drivers_df['Constructor/Team'].unique()):
                    team_drivers = drivers_df[drivers_df['Constructor/Team'] == team]
                    
                    with st.expander(f"🏁 {team} ({len(team_drivers)} drivers)"):
                        for _, driver in team_drivers.iterrows():
                            st.markdown(f"""
                            **#{driver['Car Number']} - {driver['Driver Name']}** ({driver['Code']})
                            """)
                
                # Download option
                st.markdown("---")
                csv = drivers_df.to_csv(index=False)
                st.download_button(
                    label=f"Download {selected_year} Driver List (CSV)",
                    data=csv,
                    file_name=f"f1_drivers_{selected_year}.csv",
                    mime="text/csv"
                )
            else:
                st.info(f"No driver data available for {selected_year}. Run data fetcher to populate the database.")
        else:
            st.info("No driver data available. Run `python src/data_fetcher.py` and `python src/database.py` to populate the database.")
    
    except Exception as e:
        st.error(f"Error: {e}")
        st.info("Make sure to run `python src/database.py` to initialize the database first.")


def show_2026_predictions():
    """2026 Season Predictions page with race-by-race breakdown"""
    st.header("🏁 2026 Season Predictions")
    
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
                st.metric("Total Predictions", len(predictions_df))
            with col2:
                num_races = predictions_df['race_id'].nunique()
                st.metric("Races", num_races)
            with col3:
                num_drivers = predictions_df['driver_number'].nunique()
                st.metric("Drivers", num_drivers)
            with col4:
                avg_confidence = predictions_df['confidence'].mean()
                st.metric("Avg Confidence", f"{avg_confidence:.2f}")
            
            st.markdown("---")
            
            # Race selector
            st.subheader("Select Race")
            race_options = predictions_df[['round_number', 'event_name', 'event_date']].drop_duplicates()
            race_options = race_options.sort_values('round_number')
            
            selected_race = st.selectbox(
                "Choose a race",
                options=race_options['event_name'].tolist(),
                format_func=lambda x: f"Round {race_options[race_options['event_name']==x]['round_number'].values[0]} - {x}"
            )
            
            # Filter for selected race
            race_predictions = predictions_df[predictions_df['event_name'] == selected_race].copy()
            race_predictions = race_predictions.sort_values('predicted_position')
            
            if len(race_predictions) > 0:
                # Race header
                race_round = race_predictions['round_number'].iloc[0]
                race_date = race_predictions['event_date'].iloc[0]
                
                st.markdown(f"### Round {race_round}: {selected_race}")
                st.markdown(f"**Date:** {race_date}")
                
                # Top 10 predictions
                st.subheader("🏆 Predicted Top 10")
                top10 = race_predictions.head(10).copy()
                top10['Position'] = range(1, len(top10) + 1)
                
                display_cols = ['Position', 'driver_name', 'team_name', 'confidence']
                display_df = top10[display_cols].copy()
                display_df.columns = ['Pos', 'Driver', 'Team', 'Confidence']
                display_df['Confidence'] = display_df['Confidence'].apply(lambda x: f"{x:.3f}")
                
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                # Full grid
                st.markdown("---")
                with st.expander("📊 View Full Predicted Grid"):
                    full_grid = race_predictions.copy()
                    full_grid['Position'] = range(1, len(full_grid) + 1)
                    full_grid_display = full_grid[['Position', 'driver_name', 'team_name', 'driver_number', 'confidence']]
                    full_grid_display.columns = ['Pos', 'Driver', 'Team', 'Car #', 'Confidence']
                    full_grid_display['Confidence'] = full_grid_display['Confidence'].apply(lambda x: f"{x:.3f}")
                    st.dataframe(full_grid_display, use_container_width=True, hide_index=True)
                
                # Visualization
                st.markdown("---")
                st.subheader("📈 Prediction Visualization")
                
                # Bar chart of top 10
                fig = px.bar(
                    top10,
                    x='driver_name',
                    y='confidence',
                    color='team_name',
                    title=f"Top 10 Prediction Confidence - {selected_race}",
                    labels={'driver_name': 'Driver', 'confidence': 'Confidence Score', 'team_name': 'Team'}
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
                
                # Feature importance (if available)
                if 'features_json' in race_predictions.columns:
                    with st.expander("🔍 Feature Analysis"):
                        try:
                            # Parse first driver's features as example
                            sample_features = json.loads(race_predictions.iloc[0]['features_json'])
                            
                            st.markdown("**Sample Feature Values (First Predicted Driver):**")
                            features_df = pd.DataFrame([sample_features]).T
                            features_df.columns = ['Value']
                            features_df['Feature'] = features_df.index
                            features_df = features_df[['Feature', 'Value']]
                            st.dataframe(features_df, use_container_width=True, hide_index=True)
                        except:
                            st.info("Feature data not available")
            
            # Championship standings projection
            st.markdown("---")
            st.subheader("🏆 Projected Championship Standings")
            
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
            
            st.dataframe(standings.head(10), use_container_width=True, hide_index=True)
            
        else:
            st.info("No 2026 predictions available. Run the '2026 Predictions' notebook to generate predictions.")
            st.markdown("""
            **To generate 2026 predictions:**
            1. Open `notebooks/f1_2026_predictions.ipynb`
            2. Run all cells to train models and generate predictions
            3. Refresh this page to view predictions
            """)
    
    except Exception as e:
        st.error(f"Error: {e}")
        st.info("Make sure to run the 2026 predictions notebook first.")


def show_database_explorer():
    """Database explorer page"""
    st.header("Database Explorer")
    
    try:
        db = F1Database()
        
        # Table selector
        tables = ["races", "drivers", "teams", "race_results", 
                  "qualifying_results", "sprint_results", "predictions"]
        
        selected_table = st.selectbox("Select Table", tables)
        
        # Execute query
        if selected_table:
            st.subheader(f"Table: {selected_table}")
            
            # Enhanced query for drivers to show all info
            if selected_table == "drivers":
                query = "SELECT driver_number, full_name, abbreviation, team_name, year FROM drivers ORDER BY year DESC, driver_number"
            else:
                query = f"SELECT * FROM {selected_table}"
            df = db.execute_query(query)
            
            if len(df) > 0:
                st.dataframe(df, use_container_width=True)
                
                # Show statistics
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Rows", len(df))
                with col2:
                    st.metric("Columns", len(df.columns))
                
                # Download option
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download as CSV",
                    data=csv,
                    file_name=f"{selected_table}.csv",
                    mime="text/csv"
                )
            else:
                st.info(f"No data in {selected_table} table yet")
        
        # Custom query section
        st.markdown("---")
        st.subheader("Custom SQL Query")
        
        custom_query = st.text_area(
            "Enter SQL Query",
            "SELECT * FROM races LIMIT 10"
        )
        
        if st.button("Execute Query"):
            try:
                result_df = db.execute_query(custom_query)
                st.dataframe(result_df, use_container_width=True)
            except Exception as e:
                st.error(f"Query error: {e}")
    
    except Exception as e:
        st.error(f"Database error: {e}")
        st.info("Run `python src/database.py` to initialize the database")


def show_telemetry_viewer():
    """Telemetry viewer page"""
    st.header("Telemetry Viewer")
    
    try:
        handler = TelemetryHandler()
        
        # Get telemetry summary
        summary = handler.get_telemetry_summary()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Files", summary['total_files'])
        with col2:
            years = ", ".join(summary['by_year'].keys()) if summary['by_year'] else "None"
            st.metric("Years", years)
        
        st.markdown("---")
        
        # List all telemetry files
        files = handler.list_available_telemetry()
        
        if files:
            st.subheader("Available Telemetry Files")
            
            selected_file = st.selectbox("Select File", files)
            
            if selected_file:
                # Parse file path
                parts = selected_file.split(os.sep)
                
                if len(parts) >= 3:
                    year = parts[0]
                    event = parts[1]
                    session = parts[2]
                    
                    # Load file
                    file_path = os.path.join(handler.telemetry_dir, selected_file)
                    
                    try:
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                        
                        # Show metadata
                        st.subheader("Metadata")
                        st.json(data.get('metadata', {}))
                        
                        # Show data
                        if 'telemetry' in data:
                            st.subheader("Telemetry Data")
                            telemetry_df = pd.DataFrame(data['telemetry'])
                            st.dataframe(telemetry_df, use_container_width=True)
                            
                            # Plot if numeric columns exist
                            numeric_cols = telemetry_df.select_dtypes(include=['float64', 'int64']).columns
                            if len(numeric_cols) > 0:
                                st.subheader("Visualization")
                                plot_col = st.selectbox("Select column to plot", numeric_cols)
                                
                                fig = px.line(telemetry_df, y=plot_col, title=f"{plot_col} over time")
                                st.plotly_chart(fig, use_container_width=True)
                        
                        elif 'laps' in data:
                            st.subheader("Lap Data")
                            laps_df = pd.DataFrame(data['laps'])
                            st.dataframe(laps_df, use_container_width=True)
                    
                    except Exception as e:
                        st.error(f"Error loading file: {e}")
        else:
            st.info("No telemetry data available. Run data fetcher to collect data.")
    
    except Exception as e:
        st.error(f"Error: {e}")


def show_predictions():
    """Model predictions page"""
    st.header("Model Predictions")
    
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
            st.subheader("Stored Predictions")
            
            # Filter options
            col1, col2 = st.columns(2)
            with col1:
                session_types = predictions_df['session_type'].unique()
                selected_session = st.selectbox("Session Type", ['All'] + list(session_types))
            
            with col2:
                model_types = predictions_df['model_type'].unique()
                selected_model = st.selectbox("Model Type", ['All'] + list(model_types))
            
            # Filter data
            filtered_df = predictions_df.copy()
            if selected_session != 'All':
                filtered_df = filtered_df[filtered_df['session_type'] == selected_session]
            if selected_model != 'All':
                filtered_df = filtered_df[filtered_df['model_type'] == selected_model]
            
            # Display predictions with formatted columns
            display_cols = ['driver_number', 'driver_name', 'team_name', 'event_name', 
                          'year', 'session_type', 'predicted_position', 'confidence', 'model_type']
            available_cols = [col for col in display_cols if col in filtered_df.columns]
            st.dataframe(filtered_df[available_cols], use_container_width=True)
            
            # Visualization
            if len(filtered_df) > 0 and 'driver_name' in filtered_df.columns:
                st.subheader("Prediction Visualization")
                
                # Create hover text with driver info
                filtered_df['hover_text'] = (
                    'Driver: ' + filtered_df['driver_name'].fillna('Unknown') + '<br>' +
                    'Team: ' + filtered_df['team_name'].fillna('Unknown') + '<br>' +
                    'Car #: ' + filtered_df['driver_number'].astype(str)
                )
                
                fig = px.scatter(
                    filtered_df,
                    x='driver_number',
                    y='predicted_position',
                    size='confidence',
                    color='team_name',
                    hover_data=['driver_name', 'team_name', 'confidence'],
                    title="Predictions by Driver",
                    labels={'driver_number': 'Driver Number', 'predicted_position': 'Predicted Position'}
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No predictions available. Train models using the Jupyter notebook.")
        
        # Model information
        st.markdown("---")
        st.subheader("Available Models")
        
        model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
        if os.path.exists(model_dir):
            model_files = [f for f in os.listdir(model_dir) if f.endswith('.pkl')]
            
            if model_files:
                for model_file in model_files:
                    st.text(f"✓ {model_file}")
            else:
                st.info("No trained models found. Run the ML pipeline notebook.")
        else:
            st.info("Models directory not found.")
    
    except Exception as e:
        st.error(f"Error: {e}")


def show_feature_importance():
    """Feature importance page"""
    st.header("Feature Importance & Model Explainability")
    
    try:
        model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
        
        # Check for metadata files
        metadata_files = []
        if os.path.exists(model_dir):
            metadata_files = [f for f in os.listdir(model_dir) if f.endswith('_metadata.json')]
        
        if metadata_files:
            selected_model = st.selectbox("Select Model", metadata_files)
            
            if selected_model:
                metadata_path = os.path.join(model_dir, selected_model)
                
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                st.subheader("Model Information")
                st.json({
                    'saved_at': metadata.get('saved_at'),
                    'features': metadata.get('feature_names', [])
                })
                
                # Feature importance
                feature_importance = metadata.get('feature_importance', {})
                
                if feature_importance:
                    st.markdown("---")
                    st.subheader("Feature Importance")
                    
                    # Display for each model type
                    for model_type, importance in feature_importance.items():
                        st.write(f"**{model_type.replace('_', ' ').title()}**")
                        
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
                            title=f"Feature Importance - {model_type.replace('_', ' ').title()}"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Table
                        st.dataframe(importance_df, use_container_width=True)
                        st.markdown("---")
                else:
                    st.info("No feature importance data available in metadata")
        else:
            st.info("No trained models found. Run the ML pipeline notebook first.")
        
        # Explanation
        st.markdown("---")
        st.subheader("Understanding Feature Importance")
        
        st.markdown("""
        Feature importance indicates which factors most influence the model's predictions:
        
        - **Higher values** = More influential features
        - **Lower values** = Less influential features
        
        Common important features:
        - **Qualifying Position**: Strong predictor of race performance
        - **Driver/Team Average**: Historical performance matters
        - **Recent Form**: Current season performance trends
        - **Grid Position**: Starting position impact
        - **Track Experience**: Familiarity with circuit
        """)
    
    except Exception as e:
        st.error(f"Error: {e}")


if __name__ == "__main__":
    main()
