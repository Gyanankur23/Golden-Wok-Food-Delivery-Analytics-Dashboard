# API Documentation

## Dashboard API Reference

This document provides detailed API documentation for the Golden Wok Food Delivery Analytics Dashboard, including data loading functions, processing utilities, and configuration options.

## Table of Contents

- [Data Loading Functions](#data-loading-functions)
- [Data Processing Utilities](#data-processing-utilities)
- [Dashboard Configuration](#dashboard-configuration)
- [Filter Functions](#filter-functions)
- [Visualization Functions](#visualization-functions)
- [Data Models](#data-models)

---

## Data Loading Functions

### `load_data()`

Loads and merges all dataset files into a unified dataframe.

**Returns:**
- `merged_data` (pd.DataFrame): Combined dataset with all dimensions and facts
- `dim_kitchen` (pd.DataFrame): Kitchen dimension table
- `dim_delivery_zone` (pd.DataFrame): Delivery zone dimension table  
- `dim_rider` (pd.DataFrame): Rider dimension table
- `dim_time_slot` (pd.DataFrame): Time slot dimension table

**Data Processing:**
- Merges fact_orders with all dimension tables
- Converts order_date to datetime format
- Extracts year, month, and day_of_week features
- Cleans unrealistic delivery times (caps at 180 minutes)

**Example Usage:**
```python
data, kitchens, zones, riders, time_slots = load_data()
```

---

## Data Processing Utilities

### Data Cleaning Functions

#### `clean_delivery_times()`
Applied internally during data loading to handle unrealistic values:
- `promised_delivery_min`: Capped at 120 minutes (2 hours)
- `actual_delivery_min`: Capped at 180 minutes (3 hours)

### Feature Engineering

#### Date Features
- `year`: Extracted from order_date
- `month`: Extracted from order_date  
- `day_of_week`: Extracted from order_date

#### Merged Features
After joining dimension tables, the following features are available:
- Kitchen information (name, location, capacity)
- Zone information (name, tier, traffic index, population density)
- Rider information (name, vehicle type, experience, rating)
- Time slot information (hour, day, weather, rush hour status)

---

## Dashboard Configuration

### Page Configuration

```python
st.set_page_config(
    page_title="Golden Wok Food Delivery Analytics",
    page_icon="🍜",
    layout="wide",
    initial_sidebar_state="expanded"
)
```

### Custom CSS Styling

The dashboard uses custom CSS for enhanced styling:

#### Metric Cards
- Background: Dark navy (#1a1a2e)
- Border: Dark purple-gray (#4a4a6a)
- Value color: White (#ffffff)
- Label color: Light gray (#cccccc)
- Border radius: 10px
- Box shadow: Enhanced for depth

#### Main Title
- Font size: 2.5rem
- Color: Orange (#FF6B35)
- Font weight: Bold
- Text alignment: Center

---

## Filter Functions

### Sidebar Filters

#### Date Range Filter
```python
date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)
```
**Parameters:**
- Default: Full date range of dataset
- Min: Dataset start date (2023-01-01)
- Max: Dataset end date (2024-12-31)

#### Kitchen Filter
```python
selected_kitchen = st.sidebar.selectbox("Kitchen", kitchen_options)
```
**Options:** All kitchens + "All" option

#### Zone Tier Filter
```python
selected_zone_tier = st.sidebar.selectbox("Zone Tier", zone_tier_options)
```
**Options:** All zone tiers + "All" option

#### Weather Condition Filter
```python
selected_weather = st.sidebar.selectbox("Weather Condition", weather_options)
```
**Options:** All weather conditions + "All" option

#### Rush Hour Filter
```python
rush_hour_filter = st.sidebar.checkbox("Show Rush Hour Only", False)
```
**Default:** False (shows all orders)

### Filter Application Logic

Filters are applied sequentially:
1. Date range filtering
2. Kitchen selection
3. Zone tier selection
4. Weather condition selection
5. Rush hour toggle

```python
if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_data = filtered_data[
        (filtered_data['order_date'] >= pd.to_datetime(start_date)) & 
        (filtered_data['order_date'] <= pd.to_datetime(end_date))
    ]

if selected_kitchen != 'All':
    filtered_data = filtered_data[filtered_data['kitchen_name'] == selected_kitchen]

# ... additional filters
```

---

## Visualization Functions

### Key Metrics Display

#### Total Orders
```python
total_orders = len(filtered_data)
st.metric("Total Orders", f"{total_orders:,}")
```

#### Average Delivery Time
```python
avg_delivery_time = filtered_data['actual_delivery_min'].mean()
st.metric("Avg Delivery Time", f"{avg_delivery_time:.1f} min")
```

#### Average Profit per Order
```python
avg_profit = filtered_data['order_profit_ngn'].mean()
st.metric("Avg Profit/Order", f"₦{avg_profit:,.0f}")
```

#### Average Customer Rating
```python
avg_customer_rating = filtered_data['customer_rating'].mean()
st.metric("Avg Customer Rating", f"{avg_customer_rating:.2f} ⭐")
```

#### On-Time Delivery Rate
```python
on_time_rate = (filtered_data['actual_delivery_min'] <= filtered_data['promised_delivery_min']).mean() * 100
st.metric("On-Time Rate", f"{on_time_rate:.1f}%")
```

### Chart Visualizations

#### Orders Over Time (Line Chart)
```python
daily_orders = filtered_data.groupby('order_date').size().reset_index(name='count')
fig_orders = px.line(daily_orders, x='order_date', y='count', 
                     title='Daily Order Volume',
                     labels={'order_date': 'Date', 'count': 'Orders'})
```

#### Kitchen Performance (Bar Chart)
```python
kitchen_performance = filtered_data.groupby('kitchen_name').agg({
    'order_id': 'count',
    'order_profit_ngn': 'mean',
    'actual_delivery_min': 'mean',
    'customer_rating': 'mean'
}).reset_index()
```

#### Zone Performance (Bar Chart)
```python
zone_performance = filtered_data.groupby('zone_tier').agg({
    'order_id': 'count',
    'order_profit_ngn': 'mean',
    'actual_delivery_min': 'mean',
    'delivery_distance_km': 'mean'
}).reset_index()
```

#### Weather Impact (Scatter Plot)
```python
weather_impact = filtered_data.groupby('weather_condition').agg({
    'actual_delivery_min': 'mean',
    'traffic_friction_score': 'mean',
    'order_profit_ngn': 'mean',
    'order_id': 'count'
}).reset_index()
```

#### Distance vs Profitability (Scatter Plot)
```python
fig_distance = px.scatter(filtered_data.sample(min(5000, len(filtered_data))), 
                         x='delivery_distance_km', y='order_profit_ngn',
                         color='actual_delivery_min',
                         title='Distance vs Profit Analysis')
```

#### Food Temperature vs Rating (Scatter Plot)
```python
temp_rating = filtered_data.dropna(subset=['food_temp_on_arrival_c', 'customer_rating'])
fig_temp = px.scatter(temp_rating.sample(min(3000, len(temp_rating))),
                     x='food_temp_on_arrival_c', y='customer_rating',
                     color='actual_delivery_min')
```

---

## Data Models

### Fact Orders Schema

| Column | Type | Description |
|--------|------|-------------|
| order_id | integer | Unique order identifier |
| kitchen_id | integer | Source kitchen foreign key |
| zone_id | integer | Delivery zone foreign key |
| rider_id | integer | Assigned rider foreign key |
| time_slot_id | integer | Time slot foreign key |
| order_date | date | Order placement date |
| order_value_ngn | float | Gross order revenue (NGN) |
| delivery_distance_km | float | Kitchen to door distance |
| promised_delivery_min | integer | Quoted delivery time |
| actual_delivery_min | integer | Actual delivery time |
| traffic_friction_score | float | Congestion severity (0-10) |
| food_temp_on_arrival_c | float | Temperature at doorstep (°C) |
| customer_rating | float | Customer rating (1-5 stars) |
| delivery_cost_ngn | float | Delivery cost (NGN) |
| order_profit_ngn | float | Profit after delivery cost (NGN) |

### Dimension Tables

#### Kitchen Dimension
- kitchen_id, kitchen_name, lga, latitude, longitude
- kitchen_capacity_orders_hr, date_opened, is_active

#### Delivery Zone Dimension  
- zone_id, zone_name, zone_lga, zone_tier
- avg_zone_traffic_index, zone_population_density
- baseline_delivery_min, is_restricted_zone

#### Rider Dimension
- rider_id, rider_name, assigned_kitchen_id
- vehicle_type, experience_months, avg_speed_kmh
- avg_rider_rating, is_active

#### Time Slot Dimension
- time_slot_id, slot_label, hour_of_day, day_of_week
- is_weekend, is_rush_hour, meal_period, weather_condition

---

## Automated Insights

### Rush Hour Analysis
```python
rush_hour_outer_zone = filtered_data[
    (filtered_data['is_rush_hour'] == True) & 
    (filtered_data['zone_tier'].str.contains('Outer|Extended', case=False, na=False))
]
late_deliveries = rush_hour_outer_zone[rush_hour_outer_zone['actual_delivery_min'] > 90]
```

### Weather Impact Analysis
```python
rain_data = filtered_data[filtered_data['weather_condition'].str.contains('Rain', case=False, na=False)]
clear_data = filtered_data[filtered_data['weather_condition'] == 'Clear']
time_diff = rain_data['actual_delivery_min'].mean() - clear_data['actual_delivery_min'].mean()
```

### Distance Profitability Check
```python
long_distance = filtered_data[filtered_data['delivery_distance_km'] > 8]
long_distance_profit = long_distance['order_profit_ngn'].mean()
```

### Food Quality Analysis
```python
cold_food = filtered_data[filtered_data['food_temp_on_arrival_c'] < 45]
cold_food_rating = cold_food['customer_rating'].mean()
```

---

## Configuration Files

### requirements.txt
```
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.14.0
```

### Environment Setup
```bash
pip install -r requirements.txt
streamlit run dashboard.py
```

---

## Error Handling

### Data Loading Errors
- FileNotFoundError: Check data directory structure
- KeyError: Verify column names in CSV files match schema

### Data Quality Issues
- Missing values: Handled by pandas merge (left join)
- Outliers: Capped during data cleaning phase
- Date parsing: Converted to datetime with error handling

### Visualization Errors
- Empty datasets: Filter logic prevents empty results
- Large datasets: Sampling applied for scatter plots (max 5000 points)

---

## Performance Optimization

### Caching
```python
@st.cache_data
def load_data():
    # Data loading logic
```

### Sampling
For large datasets, visualizations use sampling:
- Scatter plots: max 5000 points
- Performance charts: Aggregated data
- Time series: Daily aggregation

---

## Extension Points

### Adding New Filters
1. Add filter widget in sidebar
2. Apply filter logic to filtered_data
3. Update filter application section

### Adding New Visualizations
1. Create aggregation logic
2. Configure Plotly figure
3. Add to appropriate section layout
4. Update automated insights if relevant

### Adding New Metrics
1. Calculate metric from filtered_data
2. Add to metrics section
3. Update CSS styling if needed

---

## Support and Maintenance

### Version Compatibility
- Python: 3.7+
- Streamlit: 1.28.0+
- Pandas: 2.0.0+

### Data Updates
To update with new data:
1. Replace CSV files in data/ directory
2. Clear Streamlit cache (automatic on file change)
3. Restart dashboard

### Troubleshooting
- Dashboard not loading: Check Python version and dependencies
- Data not displaying: Verify CSV file paths and format
- Visualizations not rendering: Check browser console for errors

---

*Last Updated: September 25, 2026*
