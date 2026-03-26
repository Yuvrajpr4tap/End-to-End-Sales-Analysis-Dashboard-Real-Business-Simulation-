"""
Synthetic Sales Dataset Generator
Generates realistic 10,000+ row sales dataset for Business Intelligence analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_synthetic_sales_data(n_records=10000):
    """
    Generate realistic synthetic sales data
    
    Parameters:
    -----------
    n_records : int
        Number of sales records to generate (default: 10,000)
    
    Returns:
    --------
    pd.DataFrame : Sales dataset with all required columns
    """
    
    # Define business parameters
    regions = ['North', 'South', 'East', 'West']
    states = {
        'North': ['NY', 'MA', 'PA', 'OH'],
        'South': ['TX', 'FL', 'GA', 'NC'],
        'East': ['NJ', 'CT', 'DE', 'MD'],
        'West': ['CA', 'WA', 'OR', 'CO']
    }
    cities = {
        'NY': ['New York', 'Buffalo', 'Albany'],
        'TX': ['Houston', 'Dallas', 'Austin'],
        'CA': ['Los Angeles', 'San Francisco', 'San Diego'],
        'MA': ['Boston', 'Worcester', 'Springfield'],
        'FL': ['Miami', 'Tampa', 'Orlando'],
        'WA': ['Seattle', 'Tacoma', 'Vancouver'],
        'PA': ['Philadelphia', 'Pittsburgh', 'Allentown'],
        'OH': ['Columbus', 'Cleveland', 'Cincinnati'],
        'CT': ['Bridgeport', 'New Haven', 'Hartford'],
        'NJ': ['Newark', 'Jersey City', 'Paterson'],
        'DE': ['Wilmington', 'Dover', 'Milford'],
        'MD': ['Baltimore', 'Frederick', 'Gaithersburg'],
        'GA': ['Atlanta', 'Columbus', 'Savannah'],
        'NC': ['Charlotte', 'Raleigh', 'Greensboro'],
        'OR': ['Portland', 'Eugene', 'Salem'],
        'CO': ['Denver', 'Colorado Springs', 'Fort Collins']
    }
    
    product_categories = {
        'Technology': ['Laptop', 'Desktop', 'Monitor', 'Keyboard', 'Mouse', 'Printer'],
        'Furniture': ['Chair', 'Desk', 'Table', 'Cabinet', 'Bookshelf'],
        'Office Supplies': ['Paper', 'Pen', 'Clipboard', 'Notebook', 'Binder']
    }
    
    customer_segments = ['Consumer', 'Corporate', 'One-time Buyer', 'VIP']
    
    # Create base date range (2022-2024)
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    data = {
        'Order_ID': [f'ORD{str(i+1000).zfill(6)}' for i in range(n_records)],
        'Order_Date': [start_date + timedelta(days=int(np.random.random() * (end_date - start_date).days)) 
                      for _ in range(n_records)],
        'Region': np.random.choice(regions, n_records),
        'Customer_Segment': np.random.choice(customer_segments, n_records, p=[0.35, 0.40, 0.15, 0.10]),
    }
    
    # Assign states based on regions
    data['State'] = [states[r][np.random.randint(0, len(states[r]))] for r in data['Region']]
    
    # Assign cities based on states
    data['City'] = [random.choice(cities[s]) for s in data['State']]
    
    # Handle ship date (3-7 days after order date)
    data['Ship_Date'] = [order_date + timedelta(days=np.random.randint(3, 8)) 
                        for order_date in data['Order_Date']]
    
    # Product categories and subcategories
    data['Product_Category'] = np.random.choice(list(product_categories.keys()), n_records)
    data['Sub_Category'] = [random.choice(product_categories[cat]) for cat in data['Product_Category']]
    data['Product_Name'] = [f"{sub} Model-{np.random.randint(2020, 2025)}" 
                           for sub in data['Sub_Category']]
    
    # Sales metrics with realistic distributions
    base_price = np.random.exponential(scale=500, size=n_records) + 100
    data['Quantity'] = np.random.randint(1, 8, n_records)
    data['Discount'] = np.random.choice([0, 0.05, 0.10, 0.15, 0.20], n_records, p=[0.50, 0.20, 0.15, 0.10, 0.05])
    
    data['Sales'] = np.round(base_price * data['Quantity'] * (1 - data['Discount']), 2)
    
    # Profit with realistic margin (15-35%)
    profit_margin = np.random.uniform(0.15, 0.35, n_records)
    data['Profit'] = np.round(data['Sales'] * profit_margin, 2)
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Reorder columns
    column_order = [
        'Order_ID', 'Order_Date', 'Ship_Date', 'Region', 'State', 'City',
        'Product_Category', 'Sub_Category', 'Product_Name',
        'Sales', 'Quantity', 'Discount', 'Profit', 'Customer_Segment'
    ]
    df = df[column_order]
    
    # Add some intentional data quality issues (for cleaning demonstration)
    # Add ~20 duplicates
    duplicate_indices = np.random.choice(df.index, 20, replace=False)
    df_duplicates = df.loc[duplicate_indices].copy()
    df = pd.concat([df, df_duplicates], ignore_index=True)
    
    # Add ~30 missing values in random columns
    for _ in range(30):
        random_row = np.random.randint(0, len(df))
        random_col = np.random.choice(['City', 'Sub_Category', 'Discount'])
        df.loc[random_row, random_col] = np.nan
    
    df = df.reset_index(drop=True)
    
    return df


if __name__ == "__main__":
    print("Generating synthetic sales dataset...")
    
    # Generate dataset
    df = generate_synthetic_sales_data(n_records=10000)
    
    # Save to CSV
    output_path = 'd:/DA/data/sales_data_raw.csv'
    df.to_csv(output_path, index=False)
    
    print(f"\n✓ Dataset generated successfully!")
    print(f"  Total records: {len(df):,}")
    print(f"  Columns: {len(df.columns)}")
    print(f"  Date range: {df['Order_Date'].min().date()} to {df['Order_Date'].max().date()}")
    print(f"\nDataset preview:")
    print(df.head(10))
    print(f"\nDataset info:")
    print(df.info())
    print(f"\nDataset saved to: {output_path}")
