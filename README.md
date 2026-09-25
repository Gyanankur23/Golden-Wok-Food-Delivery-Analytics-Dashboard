# Golden Wok Food Delivery Analytics Dashboard

🍜 An interactive Streamlit dashboard for analyzing Golden Wok food delivery operations, performance metrics, and customer insights.

## 📊 Overview

This dashboard provides comprehensive analytics for food delivery operations, including:
- Order volume trends and patterns
- Kitchen performance comparison
- Zone-based delivery analysis
- Weather impact on delivery times
- Distance vs profitability analysis
- Food quality and customer satisfaction
- Rider performance metrics
- Rush hour analysis

## 🚀 Getting Started

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Gyanankur23/Golden-Wok-Food-Delivery-Analytics-Dashboard.git
cd Golden-Wok-Food-Delivery-Analytics-Dashboard
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Run the dashboard:
```bash
streamlit run dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

## 📁 Dataset Structure

The dashboard analyzes a comprehensive food delivery dataset with the following structure:

### Dimension Tables
- **dim_delivery_zone**: Delivery zone information (20 zones)
- **dim_kitchen**: Kitchen locations and capacities (4 kitchens)
- **dim_rider**: Rider details and performance (60 riders)
- **dim_time_slot**: Time-based dimensions (48 time slots)

### Fact Table
- **fact_orders**: Transaction-level order data (5,000 orders)

### Key Metrics Tracked
- Order value and profit margins
- Delivery distances and times
- Traffic friction scores
- Food temperature on arrival
- Customer ratings
- Weather conditions

## 🎯 Features

### Interactive Filters
- **Date Range**: Filter orders by specific time periods
- **Kitchen Selection**: Analyze performance by kitchen location
- **Zone Tier**: Compare inner, mid, and outer ring zones
- **Weather Conditions**: Analyze impact of different weather
- **Rush Hour Toggle**: Focus on peak delivery periods

### Visualizations
1. **Orders Over Time**: Daily order volume trends
2. **Kitchen Performance**: Orders and profitability by location
3. **Zone Analysis**: Geographic performance breakdown
4. **Weather Impact**: Traffic vs delivery time correlation
5. **Distance Analysis**: Distance vs profitability scatter plot
6. **Food Quality**: Temperature vs customer rating analysis
7. **Rush Hour Analysis**: Peak vs normal hour comparison
8. **Hourly Patterns**: Order distribution by hour
9. **Rider Leaderboard**: Top performers by order volume

### Automated Insights
The dashboard automatically generates insights for:
- Rush hour delivery alerts to outer zones
- Weather impact notifications
- Distance profitability warnings
- Food quality alerts

## 🎨 Design Features

- **Dark Theme Metric Cards**: Modern dark background with high contrast
- **Responsive Layout**: Works on various screen sizes
- **Interactive Charts**: Hover details and zoom capabilities
- **Color-Coded Visualizations**: Heat maps and gradient colors for patterns

## 📈 Key Insights

Based on the data analysis, the dashboard reveals:

- **Rush Hour Impact**: Orders to outer zones during rush hours (7-9 AM, 4:30-7:30 PM) often exceed 90 minutes delivery time
- **Weather Effects**: Rain conditions increase delivery times by ~28 minutes on average
- **Distance Profitability**: Orders over 8km show negative profitability due to high delivery costs
- **Food Quality**: Food temperature below 45°C correlates with customer ratings below 2.5 stars
- **Corridor Performance**: Certain kitchen-zone combinations show consistent negative profitability

## 🛠️ Technologies Used

- **Streamlit**: Interactive dashboard framework
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualizations
- **Python**: Core programming language

## 📝 Data Source

This dashboard analyzes the DataDNA Dataset Challenge - Golden Wok Food Delivery dataset (2023-2024), focusing on delivery radius optimization and urban traffic friction analysis.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available for educational and analytical purposes.

## 👤 Author

**Gyanankur Baruah**

- GitHub: [@Gyanankur23](https://github.com/Gyanankur23)

---

**Note**: This dashboard was created as part of the DataDNA Dataset Challenge for Golden Wok Food Delivery analytics.
