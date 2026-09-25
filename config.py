"""
Configuration module for Golden Wok Food Delivery Analytics Dashboard.
Contains all configurable parameters, constants, and settings.
"""

# Dashboard Configuration
DASHBOARD_CONFIG = {
    'title': 'Golden Wok Food Delivery Analytics',
    'icon': '🍜',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# Data Configuration
DATA_CONFIG = {
    'data_directory': 'data',
    'files': {
        'fact_orders': 'fact_orders.csv',
        'dim_delivery_zone': 'dim_delivery_zone.csv',
        'dim_kitchen': 'dim_kitchen.csv',
        'dim_rider': 'dim_rider.csv',
        'dim_time_slot': 'dim_time_slot.csv'
    },
    'date_range': {
        'start': '2023-01-01',
        'end': '2024-12-31'
    },
    'currency': 'NGN'
}

# Data Cleaning Configuration
DATA_CLEANING = {
    'delivery_time_caps': {
        'promised_delivery_min': 120,  # 2 hours max
        'actual_delivery_min': 180      # 3 hours max
    },
    'distance_thresholds': {
        'long_distance': 8.0,  # km
        'very_long_distance': 12.0  # km
    },
    'temperature_thresholds': {
        'cold_food': 45.0,  # Celsius
        'optimal_temp': 55.0  # Celsius
    },
    'rating_thresholds': {
        'poor_rating': 2.5,
        'excellent_rating': 4.5
    }
}

# Styling Configuration
STYLING_CONFIG = {
    'colors': {
        'primary': '#FF6B35',
        'secondary': '#667eea',
        'background_dark': '#1a1a2e',
        'background_light': '#f8f9fa',
        'text_dark': '#212529',
        'text_light': '#ffffff',
        'text_muted': '#cccccc',
        'border': '#4a4a6a',
        'border_light': '#e9ecef'
    },
    'fonts': {
        'title_size': '2.5rem',
        'subtitle_size': '1.5rem',
        'metric_value_size': '2rem',
        'metric_label_size': '1.1rem',
        'body_size': '1rem'
    },
    'spacing': {
        'card_padding': '1.5rem',
        'card_margin': '0.5rem',
        'section_margin': '2rem'
    },
    'border_radius': {
        'card': '10px',
        'button': '8px'
    }
}

# Visualization Configuration
VISUALIZATION_CONFIG = {
    'plotly': {
        'default_height': 400,
        'default_width': None,
        'color_scales': {
            'profit': 'RdYlGn',
            'performance': 'Viridis',
            'temperature': 'Plasma',
            'delivery': 'RdYlGn_r'
        },
        'sample_size': 5000  # For large datasets
    },
    'metrics': {
        'decimal_places': {
            'time': 1,
            'money': 0,
            'rating': 2,
            'percentage': 1
        }
    }
}

# Filter Configuration
FILTER_CONFIG = {
    'default_filters': {
        'date_range': 'full',
        'kitchen': 'All',
        'zone_tier': 'All',
        'weather': 'All',
        'rush_hour_only': False
    },
    'rush_hour_periods': [
        ('07:00', '09:00'),   # Morning rush
        ('16:30', '19:30')    # Evening rush
    ]
}

# Analysis Configuration
ANALYSIS_CONFIG = {
    'insights': {
        'rush_hour_threshold': 90,  # minutes
        'weather_impact_threshold': 28,  # minutes
        'profitability_threshold': -500,  # NGN
        'quality_threshold': 2.5  # rating stars
    },
    'alerts': {
        'late_delivery': 90,  # minutes
        'low_profit': -500,  # NGN
        'cold_food': 45,  # Celsius
        'poor_rating': 2.5  # stars
    }
}

# Performance Configuration
PERFORMANCE_CONFIG = {
    'caching': {
        'enabled': True,
        'ttl': 3600  # 1 hour
    },
    'sampling': {
        'enabled': True,
        'max_points': 5000
    },
    'lazy_loading': {
        'enabled': False
    }
}

# Export Configuration
EXPORT_CONFIG = {
    'formats': ['csv', 'json'],
    'default_format': 'csv',
    'max_rows': 10000
}

# API Configuration (for future extensions)
API_CONFIG = {
    'version': '1.0.0',
    'base_url': None,
    'authentication': None,
    'rate_limiting': {
        'enabled': False,
        'requests_per_minute': 60
    }
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': None  # Set to filename to enable file logging
}

# Validation Configuration
VALIDATION_CONFIG = {
    'required_columns': {
        'fact_orders': [
            'order_id', 'kitchen_id', 'zone_id', 'rider_id', 'time_slot_id',
            'order_date', 'order_value_ngn', 'delivery_distance_km',
            'promised_delivery_min', 'actual_delivery_min', 'order_profit_ngn'
        ],
        'dim_kitchen': ['kitchen_id', 'kitchen_name', 'lga'],
        'dim_delivery_zone': ['zone_id', 'zone_name', 'zone_tier'],
        'dim_rider': ['rider_id', 'rider_name', 'assigned_kitchen_id'],
        'dim_time_slot': ['time_slot_id', 'slot_label', 'hour_of_day']
    },
    'data_types': {
        'order_id': 'int64',
        'order_value_ngn': 'float64',
        'delivery_distance_km': 'float64',
        'actual_delivery_min': 'int64'
    }
}

# Feature Flags (for gradual rollout)
FEATURE_FLAGS = {
    'advanced_analytics': True,
    'predictive_models': False,
    'real_time_updates': False,
    'export_functionality': False,
    'user_authentication': False,
    'multi_language': False
}


def get_config(section=None, key=None):
    """
    Get configuration value by section and key.
    
    Args:
        section: Configuration section name (e.g., 'DASHBOARD_CONFIG')
        key: Specific key within section
    
    Returns:
        Configuration value or entire section if key is None
    """
    config_sections = {
        'dashboard': DASHBOARD_CONFIG,
        'data': DATA_CONFIG,
        'cleaning': DATA_CLEANING,
        'styling': STYLING_CONFIG,
        'visualization': VISUALIZATION_CONFIG,
        'filter': FILTER_CONFIG,
        'analysis': ANALYSIS_CONFIG,
        'performance': PERFORMANCE_CONFIG,
        'export': EXPORT_CONFIG,
        'api': API_CONFIG,
        'logging': LOGGING_CONFIG,
        'validation': VALIDATION_CONFIG,
        'features': FEATURE_FLAGS
    }
    
    if section is None:
        return config_sections
    
    section_config = config_sections.get(section.lower())
    if section_config is None:
        raise ValueError(f"Unknown configuration section: {section}")
    
    if key is None:
        return section_config
    
    return section_config.get(key)


def update_config(section, key, value):
    """
    Update configuration value.
    
    Args:
        section: Configuration section name
        key: Key to update
        value: New value
    """
    config_sections = {
        'dashboard': DASHBOARD_CONFIG,
        'data': DATA_CONFIG,
        'cleaning': DATA_CLEANING,
        'styling': STYLING_CONFIG,
        'visualization': VISUALIZATION_CONFIG,
        'filter': FILTER_CONFIG,
        'analysis': ANALYSIS_CONFIG,
        'performance': PERFORMANCE_CONFIG,
        'export': EXPORT_CONFIG,
        'api': API_CONFIG,
        'logging': LOGGING_CONFIG,
        'validation': VALIDATION_CONFIG,
        'features': FEATURE_FLAGS
    }
    
    section_config = config_sections.get(section.lower())
    if section_config is None:
        raise ValueError(f"Unknown configuration section: {section}")
    
    section_config[key] = value
