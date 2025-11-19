"""
Feature Engineering Module
Advanced feature extraction from F1 telemetry and lap data
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.signal import find_peaks


class FeatureEngineer:
    """Extract and engineer features for ML models"""
    
    def __init__(self):
        self.driver_history = {}
        self.team_history = {}
        
    def calculate_tyre_degradation(self, lap_times, tyre_life):
        """
        Calculate tyre degradation slope using linear regression
        
        Args:
            lap_times: Array of lap times
            tyre_life: Array of tyre age for each lap
        
        Returns:
            degradation_slope: Seconds per lap increase
        """
        if len(lap_times) < 3:
            return 0.0
        
        # Remove outliers (slow laps due to traffic, etc.)
        times = np.array(lap_times)
        life = np.array(tyre_life)
        
        # Filter out laps that are > 3 std dev from mean
        mean_time = np.mean(times)
        std_time = np.std(times)
        mask = np.abs(times - mean_time) <= 3 * std_time
        
        filtered_times = times[mask]
        filtered_life = life[mask]
        
        if len(filtered_times) < 3:
            return 0.0
        
        # Linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(filtered_life, filtered_times)
        
        return slope
    
    def calculate_speed_percentiles(self, speed_data):
        """
        Calculate speed statistics including median and 95th percentile
        
        Args:
            speed_data: Array of speed values
        
        Returns:
            dict with median_speed, percentile_95, max_speed
        """
        if len(speed_data) == 0:
            return {'median_speed': 0, 'percentile_95': 0, 'max_speed': 0}
        
        speeds = np.array(speed_data)
        
        return {
            'median_speed': np.median(speeds),
            'percentile_95': np.percentile(speeds, 95),
            'max_speed': np.max(speeds)
        }
    
    def calculate_throttle_brake_variance(self, throttle_data, brake_data):
        """
        Calculate variance in throttle and brake application
        
        Args:
            throttle_data: Array of throttle percentages (0-100)
            brake_data: Array of brake pressure values
        
        Returns:
            dict with throttle_variance, brake_variance, smoothness_score
        """
        if len(throttle_data) == 0 or len(brake_data) == 0:
            return {'throttle_variance': 0, 'brake_variance': 0, 'smoothness_score': 0}
        
        throttle = np.array(throttle_data)
        brake = np.array(brake_data)
        
        # Calculate variance
        throttle_var = np.var(throttle)
        brake_var = np.var(brake)
        
        # Smoothness score (lower variance = smoother driving)
        # Normalize to 0-100 scale
        smoothness = 100 / (1 + (throttle_var + brake_var) / 200)
        
        return {
            'throttle_variance': throttle_var,
            'brake_variance': brake_var,
            'smoothness_score': smoothness
        }
    
    def calculate_cornering_speed_deltas(self, speed_data, distance_data, brake_data):
        """
        Calculate speed deltas in corners (entry vs apex vs exit)
        
        Args:
            speed_data: Array of speeds
            distance_data: Array of distances along track
            brake_data: Array of brake applications
        
        Returns:
            dict with corner_entry_speed, apex_speed, corner_exit_speed, delta_entry_exit
        """
        if len(speed_data) < 10:
            return {
                'corner_entry_speed': 0,
                'apex_speed': 0,
                'corner_exit_speed': 0,
                'delta_entry_exit': 0
            }
        
        speeds = np.array(speed_data)
        brakes = np.array(brake_data)
        
        # Find corners (where braking occurs)
        corner_indices = np.where(brakes > 10)[0]  # Brake pressure > 10%
        
        if len(corner_indices) == 0:
            return {
                'corner_entry_speed': np.mean(speeds),
                'apex_speed': np.mean(speeds),
                'corner_exit_speed': np.mean(speeds),
                'delta_entry_exit': 0
            }
        
        # Find local minima in speed (apex points)
        apex_indices, _ = find_peaks(-speeds, distance=5)
        
        if len(apex_indices) == 0:
            return {
                'corner_entry_speed': np.mean(speeds[corner_indices]),
                'apex_speed': np.min(speeds),
                'corner_exit_speed': np.mean(speeds[corner_indices]),
                'delta_entry_exit': 0
            }
        
        # Calculate average speeds at different corner phases
        corner_entry = np.mean([speeds[max(0, i-3)] for i in apex_indices])
        apex = np.mean(speeds[apex_indices])
        corner_exit = np.mean([speeds[min(len(speeds)-1, i+3)] for i in apex_indices])
        
        return {
            'corner_entry_speed': corner_entry,
            'apex_speed': apex,
            'corner_exit_speed': corner_exit,
            'delta_entry_exit': corner_exit - corner_entry
        }
    
    def calculate_driver_form(self, race_results, driver_number, current_race_index, window=5, decay=0.8):
        """
        Calculate time-decay weighted driver form over last N races
        
        Args:
            race_results: DataFrame with columns [race_index, driver_number, position]
            driver_number: Driver to calculate form for
            current_race_index: Index of current race
            window: Number of previous races to consider
            decay: Time decay factor (0-1, closer to 1 = less decay)
        
        Returns:
            weighted_form_score: Lower is better (like position)
        """
        # Get driver's recent results
        driver_races = race_results[
            (race_results['driver_number'] == driver_number) &
            (race_results['race_index'] < current_race_index)
        ].sort_values('race_index', ascending=False).head(window)
        
        if len(driver_races) == 0:
            return 10.0  # Neutral score
        
        # Calculate weighted average position
        positions = driver_races['position'].values
        weights = np.array([decay ** i for i in range(len(positions))])
        weights = weights / np.sum(weights)  # Normalize
        
        weighted_form = np.sum(positions * weights)
        
        return weighted_form
    
    def create_interaction_features(self, driver_stats, team_stats, track_stats):
        """
        Create interaction features (driver×track, team×track)
        
        Args:
            driver_stats: Dict with driver performance metrics
            team_stats: Dict with team performance metrics
            track_stats: Dict with track characteristics
        
        Returns:
            dict with interaction features
        """
        interactions = {}
        
        # Driver×Track interactions
        interactions['driver_track_experience'] = (
            driver_stats.get('races_at_track', 0) * driver_stats.get('avg_position', 10)
        )
        
        # Team×Track interactions
        interactions['team_track_performance'] = (
            team_stats.get('avg_position_at_track', 10) * 
            (1 - track_stats.get('overtaking_difficulty', 0.5))
        )
        
        # Driver×Team synergy
        interactions['driver_team_synergy'] = (
            driver_stats.get('avg_position', 10) * team_stats.get('avg_position', 10)
        ) ** 0.5  # Geometric mean
        
        return interactions
    
    def calculate_uncertainty_score(self, regulation_changes=0, driver_moves=0, 
                                   technical_updates=0, race_rumours=0):
        """
        Calculate uncertainty score based on regulation changes, driver moves, etc.
        
        Args:
            regulation_changes: Number of regulation changes (0-1 scale)
            driver_moves: Number of driver transfers (0-1 scale)
            technical_updates: Number of technical updates (0-1 scale)
            race_rumours: Rumour intensity (0-1 scale)
        
        Returns:
            uncertainty_score: 0-1 scale, higher = more uncertainty
        """
        # Weighted combination
        weights = {
            'regulation': 0.4,
            'drivers': 0.3,
            'technical': 0.2,
            'rumours': 0.1
        }
        
        uncertainty = (
            weights['regulation'] * regulation_changes +
            weights['drivers'] * driver_moves +
            weights['technical'] * technical_updates +
            weights['rumours'] * race_rumours
        )
        
        return min(1.0, uncertainty)
    
    def extract_telemetry_features(self, telemetry_df):
        """
        Extract all telemetry-derived features from a telemetry DataFrame
        
        Args:
            telemetry_df: DataFrame with columns [Speed, Throttle, Brake, Distance, etc.]
        
        Returns:
            dict with all telemetry features
        """
        features = {}
        
        if telemetry_df is None or len(telemetry_df) == 0:
            return features
        
        # Speed features
        if 'Speed' in telemetry_df.columns:
            speed_stats = self.calculate_speed_percentiles(telemetry_df['Speed'].values)
            features.update(speed_stats)
        
        # Throttle and brake features
        if 'Throttle' in telemetry_df.columns and 'Brake' in telemetry_df.columns:
            tb_stats = self.calculate_throttle_brake_variance(
                telemetry_df['Throttle'].values,
                telemetry_df['Brake'].values
            )
            features.update(tb_stats)
        
        # Cornering features
        if all(col in telemetry_df.columns for col in ['Speed', 'Distance', 'Brake']):
            corner_stats = self.calculate_cornering_speed_deltas(
                telemetry_df['Speed'].values,
                telemetry_df['Distance'].values,
                telemetry_df['Brake'].values
            )
            features.update(corner_stats)
        
        return features
    
    def prepare_training_features(self, lap_data, telemetry_summaries, driver_stats, 
                                  team_stats, track_stats, race_results):
        """
        Prepare complete feature set for model training
        
        Args:
            lap_data: DataFrame with lap information
            telemetry_summaries: Dict with precomputed telemetry features
            driver_stats: Dict with driver statistics
            team_stats: Dict with team statistics
            track_stats: Dict with track characteristics
            race_results: DataFrame with historical race results
        
        Returns:
            DataFrame with all features ready for training
        """
        features_list = []
        
        for idx, lap in lap_data.iterrows():
            driver_num = lap['driver_number']
            race_idx = lap.get('race_index', 0)
            
            # Base features from lap data
            feature_dict = {
                'driver_number': driver_num,
                'lap_time': lap.get('lap_time', 0),
                'sector1': lap.get('sector1_time', 0),
                'sector2': lap.get('sector2_time', 0),
                'sector3': lap.get('sector3_time', 0),
                'compound': lap.get('compound', 'UNKNOWN'),
                'tyre_life': lap.get('tyre_life', 0),
            }
            
            # Telemetry features
            if driver_num in telemetry_summaries:
                feature_dict.update(telemetry_summaries[driver_num])
            
            # Driver form
            driver_form = self.calculate_driver_form(race_results, driver_num, race_idx)
            feature_dict['driver_form'] = driver_form
            
            # Driver stats
            driver_data = driver_stats.get(driver_num, {})
            feature_dict['driver_avg_position'] = driver_data.get('avg_position', 10)
            feature_dict['driver_races'] = driver_data.get('total_races', 0)
            
            # Team stats
            team_name = driver_data.get('team_name', 'Unknown')
            team_data = team_stats.get(team_name, {})
            feature_dict['team_avg_position'] = team_data.get('avg_position', 10)
            
            # Interaction features
            interactions = self.create_interaction_features(driver_data, team_data, track_stats)
            feature_dict.update(interactions)
            
            features_list.append(feature_dict)
        
        return pd.DataFrame(features_list)


def main():
    """Demonstration of feature engineering"""
    print("\nFeature Engineering Module")
    print("=" * 50)
    
    engineer = FeatureEngineer()
    
    # Example: Tyre degradation
    lap_times = [90.5, 90.7, 90.9, 91.1, 91.4, 91.6, 91.9]
    tyre_life = [1, 2, 3, 4, 5, 6, 7]
    degradation = engineer.calculate_tyre_degradation(lap_times, tyre_life)
    print(f"\nTyre degradation slope: {degradation:.4f} sec/lap")
    
    # Example: Speed statistics
    speed_data = np.random.normal(280, 20, 1000)
    speed_stats = engineer.calculate_speed_percentiles(speed_data)
    print(f"\nSpeed statistics:")
    for key, value in speed_stats.items():
        print(f"  {key}: {value:.2f}")
    
    # Example: Driver form
    race_results = pd.DataFrame({
        'race_index': [1, 2, 3, 4, 5, 6, 7, 8],
        'driver_number': [1, 1, 1, 1, 1, 1, 1, 1],
        'position': [1, 2, 1, 3, 2, 1, 1, 2]
    })
    form = engineer.calculate_driver_form(race_results, 1, 8, window=5)
    print(f"\nDriver form score: {form:.2f}")
    
    print("\n✓ Feature engineering demonstration complete!")


if __name__ == "__main__":
    main()
