"""
Utility functions for Golden Wok Food Delivery Analytics Dashboard.
Contains data processing, analysis, and helper functions.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Tuple, List, Dict, Optional
import warnings

warnings.filterwarnings('ignore')


def load_and_merge_data(base_path: str) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """
    Load and merge all dataset files.
    
    Args:
        base_path: Base directory path for data files
    
    Returns:
        Tuple of (merged_dataframe, dimension_dataframes_dict)
    """
    import os
    
    # Load all datasets
    fact_orders = pd.read_csv(os.path.join(base_path, "fact_orders.csv"))
    dim_delivery_zone = pd.read_csv(os.path.join(base_path, "dim_delivery_zone.csv"))
    dim_kitchen = pd.read_csv(os.path.join(base_path, "dim_kitchen.csv"))
    dim_rider = pd.read_csv(os.path.join(base_path, "dim_rider.csv"))
    dim_time_slot = pd.read_csv(os.path.join(base_path, "dim_time_slot.csv"))
    
    # Store dimension tables
    dimensions = {
        'kitchen': dim_kitchen,
        'delivery_zone': dim_delivery_zone,
        'rider': dim_rider,
        'time_slot': dim_time_slot
    }
    
    # Merge datasets
    merged_data = fact_orders.merge(dim_kitchen, on='kitchen_id', how='left')
    merged_data = merged_data.merge(dim_delivery_zone, on='zone_id', how='left')
    merged_data = merged_data.merge(dim_rider, on='rider_id', how='left')
    merged_data = merged_data.merge(dim_time_slot, on='time_slot_id', how='left')
    
    return merged_data, dimensions


def clean_data(data: pd.DataFrame, 
                promised_cap: int = 120, 
                actual_cap: int = 180) -> pd.DataFrame:
    """
    Clean and preprocess data by handling unrealistic values.
    
    Args:
        data: Raw dataframe
        promised_cap: Maximum allowed promised delivery time (minutes)
        actual_cap: Maximum allowed actual delivery time (minutes)
    
    Returns:
        Cleaned dataframe
    """
    cleaned_data = data.copy()
    
    # Cap unrealistic delivery times
    cleaned_data['promised_delivery_min'] = cleaned_data['promised_delivery_min'].clip(upper=promised_cap)
    cleaned_data['actual_delivery_min'] = cleaned_data['actual_delivery_min'].clip(upper=actual_cap)
    
    # Handle missing values
    cleaned_data['customer_rating'] = cleaned_data['customer_rating'].fillna(
        cleaned_data['customer_rating'].mean()
    )
    cleaned_data['food_temp_on_arrival_c'] = cleaned_data['food_temp_on_arrival_c'].fillna(
        cleaned_data['food_temp_on_arrival_c'].mean()
    )
    
    return cleaned_data


def add_temporal_features(data: pd.DataFrame) -> pd.DataFrame:
    """
    Add temporal features to the dataframe.
    
    Args:
        data: Dataframe with order_date column
    
    Returns:
        Dataframe with added temporal features
    """
    data = data.copy()
    
    # Convert date column
    data['order_date'] = pd.to_datetime(data['order_date'])
    
    # Extract temporal features
    data['year'] = data['order_date'].dt.year
    data['month'] = data['order_date'].dt.month
    data['day_of_week'] = data['order_date'].dt.day_name()
    data['week_of_year'] = data['order_date'].dt.isocalendar().week
    data['quarter'] = data['order_date'].dt.quarter
    
    return data


def calculate_performance_metrics(data: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate key performance metrics.
    
    Args:
        data: Filtered dataframe
    
    Returns:
        Dictionary of performance metrics
    """
    metrics = {}
    
    if len(data) == 0:
        return metrics
    
    metrics['total_orders'] = len(data)
    metrics['avg_delivery_time'] = data['actual_delivery_min'].mean()
    metrics['avg_profit'] = data['order_profit_ngn'].mean()
    metrics['avg_customer_rating'] = data['customer_rating'].mean()
    metrics['on_time_rate'] = (data['actual_delivery_min'] <= data['promised_delivery_min']).mean() * 100
    metrics['avg_order_value'] = data['order_value_ngn'].mean()
    metrics['avg_delivery_distance'] = data['delivery_distance_km'].mean()
    metrics['total_revenue'] = data['order_value_ngn'].sum()
    metrics['total_profit'] = data['order_profit_ngn'].sum()
    
    return metrics


def analyze_rush_hour_impact(data: pd.DataFrame) -> Dict:
    """
    Analyze the impact of rush hour on delivery performance.
    
    Args:
        data: Dataframe with rush hour information
    
    Returns:
        Dictionary with rush hour analysis results
    """
    rush_hour_data = data[data['is_rush_hour'] == True]
    normal_hour_data = data[data['is_rush_hour'] == False]
    
    analysis = {
        'rush_hour_orders': len(rush_hour_data),
        'normal_hour_orders': len(normal_hour_data),
        'rush_hour_avg_time': rush_hour_data['actual_delivery_min'].mean() if len(rush_hour_data) > 0 else 0,
        'normal_hour_avg_time': normal_hour_data['actual_delivery_min'].mean() if len(normal_hour_data) > 0 else 0,
        'rush_hour_avg_profit': rush_hour_data['order_profit_ngn'].mean() if len(rush_hour_data) > 0 else 0,
        'normal_hour_avg_profit': normal_hour_data['order_profit_ngn'].mean() if len(normal_hour_data) > 0 else 0
    }
    
    if analysis['rush_hour_avg_time'] > 0 and analysis['normal_hour_avg_time'] > 0:
        analysis['time_increase'] = analysis['rush_hour_avg_time'] - analysis['normal_hour_avg_time']
        analysis['time_increase_percent'] = (analysis['time_increase'] / analysis['normal_hour_avg_time']) * 100
    
    return analysis


def analyze_weather_impact(data: pd.DataFrame) -> Dict:
    """
    Analyze the impact of weather conditions on delivery performance.
    
    Args:
        data: Dataframe with weather information
    
    Returns:
        Dictionary with weather analysis results
    """
    weather_groups = data.groupby('weather_condition').agg({
        'actual_delivery_min': 'mean',
        'traffic_friction_score': 'mean',
        'order_profit_ngn': 'mean',
        'order_id': 'count'
    }).reset_index()
    
    weather_groups.columns = ['weather', 'avg_delivery_time', 'avg_traffic_score', 
                              'avg_profit', 'order_count']
    
    # Calculate impact compared to clear weather
    clear_weather = weather_groups[weather_groups['weather'] == 'Clear']
    
    analysis = {
        'weather_summary': weather_groups.to_dict('records')
    }
    
    if len(clear_weather) > 0:
        clear_time = clear_weather['avg_delivery_time'].values[0]
        clear_traffic = clear_traffic = clear_weather['avg_traffic_score'].values[0]
        
        for weather in weather_groups['weather']:
            if weather != 'Clear':
                weather_data = weather_groups[weather_groups['weather'] == weather]
                if len(weather_data) > 0:
                    time_impact = weather_data['avg_delivery_time'].values[0] - clear_time
                    traffic_impact = weather_data['avg_traffic_score'].values[0] - clear_traffic
                    
                    analysis[f'{weather}_time_impact'] = time_impact
                    analysis[f'{weather}_traffic_impact'] = traffic_impact
    
    return analysis


def analyze_distance_profitability(data: pd.DataFrame, 
                                   threshold: float = 8.0) -> Dict:
    """
    Analyze profitability by delivery distance.
    
    Args:
        data: Dataframe with distance and profit information
        threshold: Distance threshold in km
    
    Returns:
        Dictionary with distance profitability analysis
    """
    short_distance = data[data['delivery_distance_km'] <= threshold]
    long_distance = data[data['delivery_distance_km'] > threshold]
    
    analysis = {
        'short_distance_orders': len(short_distance),
        'long_distance_orders': len(long_distance),
        'short_distance_avg_profit': short_distance['order_profit_ngn'].mean() if len(short_distance) > 0 else 0,
        'long_distance_avg_profit': long_distance['order_profit_ngn'].mean() if len(long_distance) > 0 else 0,
        'short_distance_avg_time': short_distance['actual_delivery_min'].mean() if len(short_distance) > 0 else 0,
        'long_distance_avg_time': long_distance['actual_delivery_min'].mean() if len(long_distance) > 0 else 0
    }
    
    if analysis['long_distance_avg_profit'] < 0:
        analysis['long_distance_profitable'] = False
        analysis['long_distance_loss_per_order'] = abs(analysis['long_distance_avg_profit'])
    else:
        analysis['long_distance_profitable'] = True
    
    return analysis


def analyze_food_quality(data: pd.DataFrame, 
                        temp_threshold: float = 45.0) -> Dict:
    """
    Analyze food quality impact on customer satisfaction.
    
    Args:
        data: Dataframe with temperature and rating information
        temp_threshold: Temperature threshold in Celsius
    
    Returns:
        Dictionary with food quality analysis
    """
    # Filter out missing values
    quality_data = data.dropna(subset=['food_temp_on_arrival_c', 'customer_rating'])
    
    cold_food = quality_data[quality_data['food_temp_on_arrival_c'] < temp_threshold]
    warm_food = quality_data[quality_data['food_temp_on_arrival_c'] >= temp_threshold]
    
    analysis = {
        'cold_food_orders': len(cold_food),
        'warm_food_orders': len(warm_food),
        'cold_food_avg_rating': cold_food['customer_rating'].mean() if len(cold_food) > 0 else 0,
        'warm_food_avg_rating': warm_food['customer_rating'].mean() if len(warm_food) > 0 else 0,
        'cold_food_avg_temp': cold_food['food_temp_on_arrival_c'].mean() if len(cold_food) > 0 else 0,
        'warm_food_avg_temp': warm_food['food_temp_on_arrival_c'].mean() if len(warm_food) > 0 else 0
    }
    
    # Correlation analysis
    if len(quality_data) > 0:
        correlation = quality_data['food_temp_on_arrival_c'].corr(quality_data['customer_rating'])
        analysis['temp_rating_correlation'] = correlation
    
    return analysis


def identify_issues(data: pd.DataFrame, 
                   thresholds: Dict = None) -> List[Dict]:
    """
    Identify potential issues in the data based on thresholds.
    
    Args:
        data: Dataframe to analyze
        thresholds: Dictionary of threshold values
    
    Returns:
        List of identified issues
    """
    if thresholds is None:
        thresholds = {
            'late_delivery': 90,
            'low_profit': -500,
            'cold_food': 45,
            'poor_rating': 2.5
        }
    
    issues = []
    
    # Late deliveries
    late_deliveries = data[data['actual_delivery_min'] > thresholds['late_delivery']]
    if len(late_deliveries) > 0:
        issues.append({
            'type': 'late_delivery',
            'count': len(late_deliveries),
            'severity': 'high' if len(late_deliveries) > 100 else 'medium',
            'description': f'{len(late_deliveries)} orders exceeded {thresholds["late_delivery"]} minutes'
        })
    
    # Low profit orders
    low_profit = data[data['order_profit_ngn'] < thresholds['low_profit']]
    if len(low_profit) > 0:
        issues.append({
            'type': 'low_profit',
            'count': len(low_profit),
            'severity': 'high' if len(low_profit) > 500 else 'medium',
            'description': f'{len(low_profit)} orders had profit below ₦{thresholds["low_profit"]}'
        })
    
    # Cold food
    cold_food = data[data['food_temp_on_arrival_c'] < thresholds['cold_food']]
    if len(cold_food) > 0:
        cold_food_poor_rating = cold_food[cold_food['customer_rating'] < thresholds['poor_rating']]
        if len(cold_food_poor_rating) > 0:
            issues.append({
                'type': 'cold_food_poor_rating',
                'count': len(cold_food_poor_rating),
                'severity': 'medium',
                'description': f'{len(cold_food_poor_rating)} cold food orders received poor ratings'
            })
    
    return issues


def filter_data(data: pd.DataFrame, 
                filters: Dict) -> pd.DataFrame:
    """
    Apply multiple filters to the dataframe.
    
    Args:
        data: Original dataframe
        filters: Dictionary of filter conditions
    
    Returns:
        Filtered dataframe
    """
    filtered_data = data.copy()
    
    # Date range filter
    if 'date_range' in filters and len(filters['date_range']) == 2:
        start_date, end_date = filters['date_range']
        filtered_data = filtered_data[
            (filtered_data['order_date'] >= pd.to_datetime(start_date)) & 
            (filtered_data['order_date'] <= pd.to_datetime(end_date))
        ]
    
    # Kitchen filter
    if 'kitchen' in filters and filters['kitchen'] != 'All':
        filtered_data = filtered_data[filtered_data['kitchen_name'] == filters['kitchen']]
    
    # Zone tier filter
    if 'zone_tier' in filters and filters['zone_tier'] != 'All':
        filtered_data = filtered_data[filtered_data['zone_tier'] == filters['zone_tier']]
    
    # Weather filter
    if 'weather' in filters and filters['weather'] != 'All':
        filtered_data = filtered_data[filtered_data['weather_condition'] == filters['weather']]
    
    # Rush hour filter
    if 'rush_hour_only' in filters and filters['rush_hour_only']:
        filtered_data = filtered_data[filtered_data['is_rush_hour'] == True]
    
    return filtered_data


def generate_summary_report(data: pd.DataFrame) -> str:
    """
    Generate a text summary of the data analysis.
    
    Args:
        data: Dataframe to analyze
    
    Returns:
        Formatted summary report
    """
    metrics = calculate_performance_metrics(data)
    
    report = f"""
    Golden Wok Food Delivery Analytics Summary
    ==========================================
    
    Total Orders: {metrics.get('total_orders', 0):,}
    Average Delivery Time: {metrics.get('avg_delivery_time', 0):.1f} minutes
    Average Profit per Order: ₦{metrics.get('avg_profit', 0):,.0f}
    Average Customer Rating: {metrics.get('avg_customer_rating', 0):.2f} ⭐
    On-Time Delivery Rate: {metrics.get('on_time_rate', 0):.1f}%
    
    Total Revenue: ₦{metrics.get('total_revenue', 0):,.0f}
    Total Profit: ₦{metrics.get('total_profit', 0):,.0f}
    Average Order Value: ₦{metrics.get('avg_order_value', 0):,.0f}
    Average Delivery Distance: {metrics.get('avg_delivery_distance', 0):.1f} km
    """
    
    return report.strip()


def export_data(data: pd.DataFrame, 
                filename: str, 
                format: str = 'csv') -> bool:
    """
    Export filtered data to file.
    
    Args:
        data: Dataframe to export
        filename: Output filename
        format: Export format ('csv' or 'json')
    
    Returns:
        True if export successful, False otherwise
    """
    try:
        if format == 'csv':
            data.to_csv(filename, index=False)
        elif format == 'json':
            data.to_json(filename, orient='records', indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
        return True
    except Exception as e:
        print(f"Export failed: {e}")
        return False


def validate_data(data: pd.DataFrame, 
                 required_columns: List[str]) -> Tuple[bool, List[str]]:
    """
    Validate that dataframe contains required columns.
    
    Args:
        data: Dataframe to validate
        required_columns: List of required column names
    
    Returns:
        Tuple of (is_valid, missing_columns)
    """
    missing_columns = [col for col in required_columns if col not in data.columns]
    is_valid = len(missing_columns) == 0
    
    return is_valid, missing_columns
