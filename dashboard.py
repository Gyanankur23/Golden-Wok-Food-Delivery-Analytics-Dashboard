import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# Set page configuration
st.set_page_config(
    page_title="Golden Wok Food Delivery Analytics",
    page_icon="🍜",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        color: #FF6B35;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
    }
    div[data-testid="stMetric"] {
        background-color: #1a1a2e;
        border: 1px solid #4a4a6a;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        margin: 0.5rem;
    }
    div[data-testid="stMetric"] > div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: bold;
        color: #ffffff;
    }
    div[data-testid="stMetric"] > div[data-testid="stMetricLabel"] {
        font-size: 1.1rem;
        color: #cccccc;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    /* Ensure label is visible */
    .stMetricLabel {
        color: #cccccc !important;
        font-weight: bold !important;
        font-size: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.join(script_dir, "data")
    
    # Load all datasets
    fact_orders = pd.read_csv(os.path.join(base_path, "fact_orders.csv"))
    dim_delivery_zone = pd.read_csv(os.path.join(base_path, "dim_delivery_zone.csv"))
    dim_kitchen = pd.read_csv(os.path.join(base_path, "dim_kitchen.csv"))
    dim_rider = pd.read_csv(os.path.join(base_path, "dim_rider.csv"))
    dim_time_slot = pd.read_csv(os.path.join(base_path, "dim_time_slot.csv"))
    
    # Merge datasets
    merged_data = fact_orders.merge(dim_kitchen, on='kitchen_id', how='left')
    merged_data = merged_data.merge(dim_delivery_zone, on='zone_id', how='left')
    merged_data = merged_data.merge(dim_rider, on='rider_id', how='left')
    merged_data = merged_data.merge(dim_time_slot, on='time_slot_id', how='left')
    
    # Convert date column
    merged_data['order_date'] = pd.to_datetime(merged_data['order_date'])
    merged_data['year'] = merged_data['order_date'].dt.year
    merged_data['month'] = merged_data['order_date'].dt.month
    merged_data['day_of_week'] = merged_data['order_date'].dt.day_name()
    
    # Clean unrealistic data - cap delivery times at realistic values
    merged_data['promised_delivery_min'] = merged_data['promised_delivery_min'].clip(upper=120)  # Max 2 hours
    merged_data['actual_delivery_min'] = merged_data['actual_delivery_min'].clip(upper=180)  # Max 3 hours
    
    return merged_data, dim_kitchen, dim_delivery_zone, dim_rider, dim_time_slot

# Load data
data, kitchens, zones, riders, time_slots = load_data()

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Date range filter
min_date = data['order_date'].min()
max_date = data['order_date'].max()
date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Kitchen filter
kitchen_options = ['All'] + list(kitchens['kitchen_name'].unique())
selected_kitchen = st.sidebar.selectbox("Kitchen", kitchen_options)

# Zone tier filter
zone_tier_options = ['All'] + list(zones['zone_tier'].unique())
selected_zone_tier = st.sidebar.selectbox("Zone Tier", zone_tier_options)

# Weather condition filter
weather_options = ['All'] + list(data['weather_condition'].unique())
selected_weather = st.sidebar.selectbox("Weather Condition", weather_options)

# Rush hour filter
rush_hour_filter = st.sidebar.checkbox("Show Rush Hour Only", False)

# Apply filters
filtered_data = data.copy()

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_data = filtered_data[
        (filtered_data['order_date'] >= pd.to_datetime(start_date)) & 
        (filtered_data['order_date'] <= pd.to_datetime(end_date))
    ]

if selected_kitchen != 'All':
    filtered_data = filtered_data[filtered_data['kitchen_name'] == selected_kitchen]

if selected_zone_tier != 'All':
    filtered_data = filtered_data[filtered_data['zone_tier'] == selected_zone_tier]

if selected_weather != 'All':
    filtered_data = filtered_data[filtered_data['weather_condition'] == selected_weather]

if rush_hour_filter:
    filtered_data = filtered_data[filtered_data['is_rush_hour'] == True]

# Main content
st.markdown('<h1 class="main-title">🍜 Golden Wok Food Delivery Analytics</h1>', unsafe_allow_html=True)
st.markdown("---")

# Key Metrics
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_orders = len(filtered_data)
    st.metric("Total Orders", f"{total_orders:,}")

with col2:
    avg_delivery_time = filtered_data['actual_delivery_min'].mean()
    st.metric("Avg Delivery Time", f"{avg_delivery_time:.1f} min")

with col3:
    avg_profit = filtered_data['order_profit_ngn'].mean()
    st.metric("Avg Profit/Order", f"₦{avg_profit:,.0f}")

with col4:
    avg_customer_rating = filtered_data['customer_rating'].mean()
    st.metric("Avg Customer Rating", f"{avg_customer_rating:.2f} ⭐")

with col5:
    on_time_rate = (filtered_data['actual_delivery_min'] <= filtered_data['promised_delivery_min']).mean() * 100
    st.metric("On-Time Rate", f"{on_time_rate:.1f}%")

st.markdown("---")

# Row 1: Time Analysis and Kitchen Performance
col1, col2 = st.columns(2)

with col1:
    st.subheader("📅 Orders Over Time")
    daily_orders = filtered_data.groupby('order_date').size().reset_index(name='count')
    fig_orders = px.line(daily_orders, x='order_date', y='count', 
                         title='Daily Order Volume',
                         labels={'order_date': 'Date', 'count': 'Orders'})
    fig_orders.update_layout(height=400)
    st.plotly_chart(fig_orders, use_container_width=True)

with col2:
    st.subheader("🏪 Kitchen Performance")
    kitchen_performance = filtered_data.groupby('kitchen_name').agg({
        'order_id': 'count',
        'order_profit_ngn': 'mean',
        'actual_delivery_min': 'mean',
        'customer_rating': 'mean'
    }).reset_index()
    kitchen_performance.columns = ['Kitchen', 'Orders', 'Avg Profit', 'Avg Delivery Time', 'Avg Rating']
    
    fig_kitchen = px.bar(kitchen_performance, x='Kitchen', y='Orders',
                         title='Orders by Kitchen',
                         color='Avg Profit',
                         color_continuous_scale='Viridis')
    fig_kitchen.update_layout(height=400)
    st.plotly_chart(fig_kitchen, use_container_width=True)

# Row 2: Zone Analysis and Weather Impact
col1, col2 = st.columns(2)

with col1:
    st.subheader("📍 Zone Performance by Tier")
    zone_performance = filtered_data.groupby('zone_tier').agg({
        'order_id': 'count',
        'order_profit_ngn': 'mean',
        'actual_delivery_min': 'mean',
        'delivery_distance_km': 'mean'
    }).reset_index()
    zone_performance.columns = ['Zone Tier', 'Orders', 'Avg Profit', 'Avg Delivery Time', 'Avg Distance']
    
    fig_zone = px.bar(zone_performance, x='Zone Tier', y='Orders',
                      title='Orders by Zone Tier',
                      color='Avg Profit',
                      color_continuous_scale='RdYlGn')
    fig_zone.update_layout(height=400)
    st.plotly_chart(fig_zone, use_container_width=True)

with col2:
    st.subheader("🌤️ Weather Impact on Delivery")
    weather_impact = filtered_data.groupby('weather_condition').agg({
        'actual_delivery_min': 'mean',
        'traffic_friction_score': 'mean',
        'order_profit_ngn': 'mean',
        'order_id': 'count'
    }).reset_index()
    weather_impact.columns = ['Weather', 'Avg Delivery Time', 'Traffic Score', 'Avg Profit', 'Orders']
    
    fig_weather = px.scatter(weather_impact, x='Traffic Score', y='Avg Delivery Time',
                            size='Orders', color='Weather',
                            title='Weather Impact: Traffic vs Delivery Time',
                            hover_data=['Avg Profit'])
    fig_weather.update_layout(height=400)
    st.plotly_chart(fig_weather, use_container_width=True)

# Row 3: Distance Analysis and Food Quality
col1, col2 = st.columns(2)

with col1:
    st.subheader("📏 Distance vs Profitability")
    fig_distance = px.scatter(filtered_data.sample(min(5000, len(filtered_data))), 
                             x='delivery_distance_km', y='order_profit_ngn',
                             color='actual_delivery_min',
                             title='Distance vs Profit Analysis',
                             labels={'delivery_distance_km': 'Distance (km)', 
                                    'order_profit_ngn': 'Profit (NGN)',
                                    'actual_delivery_min': 'Delivery Time (min)'},
                             color_continuous_scale='RdYlGn_r')
    fig_distance.update_layout(height=400)
    st.plotly_chart(fig_distance, use_container_width=True)

with col2:
    st.subheader("🌡️ Food Temperature vs Customer Rating")
    temp_rating = filtered_data.dropna(subset=['food_temp_on_arrival_c', 'customer_rating'])
    fig_temp = px.scatter(temp_rating.sample(min(3000, len(temp_rating))),
                         x='food_temp_on_arrival_c', y='customer_rating',
                         color='actual_delivery_min',
                         title='Food Temperature vs Customer Satisfaction',
                         labels={'food_temp_on_arrival_c': 'Temperature (°C)',
                                'customer_rating': 'Customer Rating',
                                'actual_delivery_min': 'Delivery Time (min)'},
                         color_continuous_scale='Plasma')
    fig_temp.update_layout(height=400)
    st.plotly_chart(fig_temp, use_container_width=True)

# Row 4: Rush Hour Analysis
st.subheader("🚗 Rush Hour Analysis")
col1, col2 = st.columns(2)

with col1:
    rush_hour_data = filtered_data.groupby('is_rush_hour').agg({
        'order_id': 'count',
        'actual_delivery_min': 'mean',
        'order_profit_ngn': 'mean',
        'customer_rating': 'mean'
    }).reset_index()
    rush_hour_data['is_rush_hour'] = rush_hour_data['is_rush_hour'].map({True: 'Rush Hour', False: 'Normal'})
    rush_hour_data.columns = ['Period', 'Orders', 'Avg Delivery Time', 'Avg Profit', 'Avg Rating']
    
    fig_rush = px.bar(rush_hour_data, x='Period', y='Orders',
                      title='Rush Hour vs Normal Hours Comparison',
                      barmode='group')
    fig_rush.update_layout(height=350)
    st.plotly_chart(fig_rush, use_container_width=True)

with col2:
    hour_performance = filtered_data.groupby('hour_of_day').agg({
        'order_id': 'count',
        'actual_delivery_min': 'mean',
        'order_profit_ngn': 'mean'
    }).reset_index()
    hour_performance.columns = ['Hour', 'Orders', 'Avg Delivery Time', 'Avg Profit']
    
    fig_hour = px.line(hour_performance, x='Hour', y='Orders',
                       title='Orders by Hour of Day',
                       markers=True)
    fig_hour.update_layout(height=350)
    st.plotly_chart(fig_hour, use_container_width=True)

# Row 5: Rider Performance
st.subheader("🏍️ Top Riders Performance")
top_riders = filtered_data.groupby(['rider_name', 'vehicle_type']).agg({
    'order_id': 'count',
    'order_profit_ngn': 'mean',
    'actual_delivery_min': 'mean',
    'customer_rating': 'mean'
}).reset_index()
top_riders.columns = ['Rider', 'Vehicle', 'Orders', 'Avg Profit', 'Avg Delivery Time', 'Avg Rating']
top_riders = top_riders.sort_values('Orders', ascending=False).head(10)

fig_riders = px.bar(top_riders, x='Rider', y='Orders',
                   color='Avg Rating',
                   title='Top 10 Riders by Order Volume',
                   hover_data=['Vehicle', 'Avg Profit', 'Avg Delivery Time'],
                   color_continuous_scale='Viridis')
fig_riders.update_layout(height=400, xaxis_tickangle=-45)
st.plotly_chart(fig_riders, use_container_width=True)

# Key Insights Section
st.markdown("---")
st.subheader("💡 Key Insights")

# Calculate some key insights
rush_hour_outer_zone = filtered_data[
    (filtered_data['is_rush_hour'] == True) & 
    (filtered_data['zone_tier'].str.contains('Outer|Extended', case=False, na=False))
]

if len(rush_hour_outer_zone) > 0:
    late_deliveries = rush_hour_outer_zone[rush_hour_outer_zone['actual_delivery_min'] > 90]
    if len(late_deliveries) > 0:
        st.warning(f"⚠️ **Rush Hour Alert:** {len(late_deliveries)} orders to outer zones during rush hour exceeded 90 minutes delivery time")

# Weather impact
rain_data = filtered_data[filtered_data['weather_condition'].str.contains('Rain', case=False, na=False)]
clear_data = filtered_data[filtered_data['weather_condition'] == 'Clear']

if len(rain_data) > 0 and len(clear_data) > 0:
    rain_avg_time = rain_data['actual_delivery_min'].mean()
    clear_avg_time = clear_data['actual_delivery_min'].mean()
    time_diff = rain_avg_time - clear_avg_time
    
    if time_diff > 0:
        st.info(f"🌧️ **Weather Impact:** Rain increases average delivery time by {time_diff:.1f} minutes compared to clear weather")

# Distance profitability
long_distance = filtered_data[filtered_data['delivery_distance_km'] > 8]
if len(long_distance) > 0:
    long_distance_profit = long_distance['order_profit_ngn'].mean()
    if long_distance_profit < 0:
        st.error(f"📏 **Distance Issue:** Orders over 8km have average profit of ₦{long_distance_profit:,.0f} (negative profitability)")

# Food quality
cold_food = filtered_data[filtered_data['food_temp_on_arrival_c'] < 45]
if len(cold_food) > 0:
    cold_food_rating = cold_food['customer_rating'].mean()
    if cold_food_rating < 2.5:
        st.warning(f"🌡️ **Quality Alert:** Food arriving below 45°C has average rating of {cold_food_rating:.2f} stars")

# Data table
st.markdown("---")
st.subheader("📊 Detailed Data View")

# Show sample of filtered data
show_data = st.checkbox("Show detailed data table", False)
if show_data:
    display_columns = ['order_date', 'kitchen_name', 'zone_name', 'rider_name', 
                     'order_value_ngn', 'delivery_distance_km', 'actual_delivery_min',
                     'promised_delivery_min', 'customer_rating', 'order_profit_ngn',
                     'weather_condition']
    st.dataframe(filtered_data[display_columns].head(100))

# Footer
st.markdown("---")
st.markdown("📊 **Golden Wok Food Delivery Analytics Dashboard** | Data: 2023-2024 | Currency: NGN")
