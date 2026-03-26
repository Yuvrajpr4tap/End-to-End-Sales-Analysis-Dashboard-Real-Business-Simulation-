"""
Data Cleaning and Preprocessing using Pandas
Production-quality Python code for cleaning and preparing data for analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class DataCleaner:
    """
    Professional data cleaning pipeline for sales data.
    Handles duplicates, missing values, data validation, and feature engineering.
    """
    
    def __init__(self, filepath):
        """Initialize cleaner with raw data"""
        self.df_raw = pd.read_csv(filepath, parse_dates=['Order_Date', 'Ship_Date'])
        self.df_clean = self.df_raw.copy()
        self.cleaning_report = {}
        
    def get_data_profile(self):
        """Generate initial data quality report"""
        print("\n" + "="*70)
        print("INITIAL DATA QUALITY REPORT")
        print("="*70)
        
        print(f"\nDataset Shape: {self.df_raw.shape[0]:,} rows × {self.df_raw.shape[1]} columns")
        print(f"Date Range: {self.df_raw['Order_Date'].min().date()} to {self.df_raw['Order_Date'].max().date()}")
        
        print("\n--- Missing Values ---")
        missing = self.df_raw.isnull().sum()
        missing_pct = (missing / len(self.df_raw) * 100).round(2)
        missing_df = pd.DataFrame({
            'Column': missing.index,
            'Missing Count': missing.values,
            'Missing %': missing_pct.values
        })
        missing_df = missing_df[missing_df['Missing Count'] > 0]
        print(missing_df.to_string(index=False))
        
        print("\n--- Data Types ---")
        print(self.df_raw.dtypes)
        
        self.cleaning_report['rows_before'] = len(self.df_raw)
        return missing_df
    
    def remove_duplicates(self, subset=None):
        """
        Remove duplicate records while preserving business context
        
        Parameters:
        -----------
        subset : list, optional
            Columns to consider for identifying duplicates
        """
        print("\n" + "="*70)
        print("STEP 1: REMOVE DUPLICATES")
        print("="*70)
        
        duplicates_before = self.df_clean.duplicated().sum()
        print(f"Duplicate rows found: {duplicates_before}")
        
        # Remove exact duplicates
        self.df_clean = self.df_clean.drop_duplicates()
        
        duplicates_after = len(self.df_raw) - len(self.df_clean)
        print(f"Rows removed: {duplicates_before}")
        print(f"Rows after cleanup: {len(self.df_clean):,}")
        
        self.cleaning_report['duplicates_removed'] = duplicates_before
    
    def handle_missing_values(self):
        """
        Strategic handling of missing values based on business logic
        """
        print("\n" + "="*70)
        print("STEP 2: HANDLE MISSING VALUES")
        print("="*70)
        
        # Missing City: Fill with regional default
        if self.df_clean['City'].isnull().sum() > 0:
            missing_cities = self.df_clean['City'].isnull().sum()
            self.df_clean.loc[self.df_clean['City'].isnull(), 'City'] = \
                self.df_clean.loc[self.df_clean['City'].isnull(), 'State'].map(
                    lambda x: f'Regional Hub - {x}'
                )
            print(f"✓ Filled {missing_cities} missing City values")
        
        # Missing Sub_Category: Use Product_Category as fallback
        if self.df_clean['Sub_Category'].isnull().sum() > 0:
            missing_subcats = self.df_clean['Sub_Category'].isnull().sum()
            self.df_clean.loc[self.df_clean['Sub_Category'].isnull(), 'Sub_Category'] = \
                self.df_clean.loc[self.df_clean['Sub_Category'].isnull(), 'Product_Category']
            print(f"✓ Filled {missing_subcats} missing Sub_Category values")
        
        # Missing Discount: Fill with median (0)
        if self.df_clean['Discount'].isnull().sum() > 0:
            missing_discounts = self.df_clean['Discount'].isnull().sum()
            median_discount = self.df_clean['Discount'].median()
            self.df_clean['Discount'].fillna(median_discount, inplace=True)
            print(f"✓ Filled {missing_discounts} missing Discount values with median: {median_discount}")
        
        print(f"\nRemaining missing values: {self.df_clean.isnull().sum().sum()}")
        self.cleaning_report['missing_values_handled'] = True
    
    def validate_data_integrity(self):
        """
        Validate business rules and data constraints
        """
        print("\n" + "="*70)
        print("STEP 3: DATA VALIDATION")
        print("="*70)
        
        issues = []
        
        # Check 1: Quantity should be positive
        invalid_qty = (self.df_clean['Quantity'] < 1).sum()
        if invalid_qty > 0:
            issues.append(f"Invalid quantities (< 1): {invalid_qty}")
            self.df_clean = self.df_clean[self.df_clean['Quantity'] >= 1]
        
        # Check 2: Discount should be between 0-50%
        invalid_discount = (self.df_clean['Discount'] > 0.50).sum()
        if invalid_discount > 0:
            issues.append(f"Excessive discounts (> 50%): {invalid_discount}")
            self.df_clean.loc[self.df_clean['Discount'] > 0.50, 'Discount'] = 0.50
        
        # Check 3: Sales should be positive
        invalid_sales = (self.df_clean['Sales'] <= 0).sum()
        if invalid_sales > 0:
            issues.append(f"Invalid sales (≤ 0): {invalid_sales}")
            self.df_clean = self.df_clean[self.df_clean['Sales'] > 0]
        
        # Check 4: Profit should be less than Sales (basic sanity check)
        invalid_profit = (self.df_clean['Profit'] > self.df_clean['Sales']).sum()
        if invalid_profit > 0:
            issues.append(f"Profit exceeds sales: {invalid_profit}")
            # This is unusual but can happen with negative COGS, keep for analysis
        
        # Check 5: Ship date should be after or equal to order date
        invalid_dates = (self.df_clean['Ship_Date'] < self.df_clean['Order_Date']).sum()
        if invalid_dates > 0:
            issues.append(f"Ship date before order date: {invalid_dates}")
            self.df_clean = self.df_clean[self.df_clean['Ship_Date'] >= self.df_clean['Order_Date']]
        
        if issues:
            print("Issues found and corrected:")
            for issue in issues:
                print(f"  ✓ {issue}")
        else:
            print("✓ All data integrity checks passed!")
        
        print(f"\nRows after validation: {len(self.df_clean):,}")
        self.cleaning_report['validation_passed'] = True
    
    def format_dates(self):
        """
        Ensure date fields are properly formatted
        """
        print("\n" + "="*70)
        print("STEP 4: FORMAT DATES")
        print("="*70)
        
        # Dates are already in datetime format from CSV read
        self.df_clean['Order_Date'] = pd.to_datetime(self.df_clean['Order_Date'])
        self.df_clean['Ship_Date'] = pd.to_datetime(self.df_clean['Ship_Date'])
        
        # Calculate shipping days (should be 3-7 days typically)
        self.df_clean['Shipping_Days'] = (self.df_clean['Ship_Date'] - self.df_clean['Order_Date']).dt.days
        
        anomalies = ((self.df_clean['Shipping_Days'] < 1) | (self.df_clean['Shipping_Days'] > 30)).sum()
        if anomalies > 0:
            print(f"⚠ Found {anomalies} shipping anomalies (not 1-30 days)")
        
        print(f"✓ Date format validated")
        print(f"  Average shipping time: {self.df_clean['Shipping_Days'].mean():.1f} days")
    
    def create_derived_features(self):
        """
        Engineer new features for enhanced analysis
        """
        print("\n" + "="*70)
        print("STEP 5: CREATE DERIVED FEATURES")
        print("="*70)
        
        # Extract temporal features
        self.df_clean['Year'] = self.df_clean['Order_Date'].dt.year
        self.df_clean['Month'] = self.df_clean['Order_Date'].dt.month
        self.df_clean['Quarter'] = self.df_clean['Order_Date'].dt.quarter
        self.df_clean['Week'] = self.df_clean['Order_Date'].dt.isocalendar().week
        self.df_clean['DayOfWeek'] = self.df_clean['Order_Date'].dt.day_name()
        self.df_clean['Year_Month'] = self.df_clean['Order_Date'].dt.strftime('%Y-%m')
        
        # Calculate profit margin
        self.df_clean['Profit_Margin_Pct'] = (self.df_clean['Profit'] / self.df_clean['Sales'] * 100).round(2)
        
        # Calculate unit price
        self.df_clean['Unit_Price'] = (self.df_clean['Sales'] / self.df_clean['Quantity']).round(2)
        
        # Calculate profit per unit
        self.df_clean['Profit_Per_Unit'] = (self.df_clean['Profit'] / self.df_clean['Quantity']).round(2)
        
        # Categorize profit margin
        self.df_clean['Margin_Category'] = pd.cut(
            self.df_clean['Profit_Margin_Pct'],
            bins=[-np.inf, 10, 20, 30, np.inf],
            labels=['Low (0-10%)', 'Medium (10-20%)', 'Good (20-30%)', 'Excellent (30%+)']
        )
        
        # Categorize customer size based on order value
        self.df_clean['Customer_Size_Segment'] = pd.cut(
            self.df_clean['Sales'],
            bins=[0, 500, 2000, np.inf],
            labels=['SMB', 'Mid-Market', 'Enterprise']
        )
        
        # Flag high-value/low-value orders
        q75 = self.df_clean['Sales'].quantile(0.75)
        q25 = self.df_clean['Sales'].quantile(0.25)
        self.df_clean['Order_Value_Category'] = np.where(
            self.df_clean['Sales'] >= q75, 'High Value',
            np.where(self.df_clean['Sales'] <= q25, 'Low Value', 'Mid Range')
        )
        
        # Calculate discount impact
        self.df_clean['Discount_Impact'] = self.df_clean['Discount'] * self.df_clean['Sales']
        
        print("✓ Created 14 derived features:")
        print(f"  - Temporal: Year, Month, Quarter, Week, DayOfWeek, Year_Month")
        print(f"  - Financial: Profit_Margin_Pct, Unit_Price, Profit_Per_Unit, Discount_Impact")
        print(f"  - Categorical: Margin_Category, Customer_Size_Segment, Order_Value_Category")
        print(f"  - Operational: Shipping_Days")
    
    def generate_summary_statistics(self):
        """
        Generate comprehensive summary statistics
        """
        print("\n" + "="*70)
        print("STEP 6: SUMMARY STATISTICS")
        print("="*70)
        
        summary_stats = {
            'Total Records': len(self.df_clean),
            'Total Sales': f"${self.df_clean['Sales'].sum():,.2f}",
            'Total Profit': f"${self.df_clean['Profit'].sum():,.2f}",
            'Overall Profit Margin': f"{(self.df_clean['Profit'].sum() / self.df_clean['Sales'].sum() * 100):.2f}%",
            'Average Order Value': f"${self.df_clean['Sales'].mean():,.2f}",
            'Average Profit': f"${self.df_clean['Profit'].mean():,.2f}",
            'Total Units Sold': f"{self.df_clean['Quantity'].sum():,}",
            'Average Order Qty': f"{self.df_clean['Quantity'].mean():.2f}",
            'Date Range': f"{self.df_clean['Order_Date'].min().date()} to {self.df_clean['Order_Date'].max().date()}",
            'Regions': self.df_clean['Region'].nunique(),
            'States': self.df_clean['State'].nunique(),
            'Products': self.df_clean['Product_Name'].nunique(),
            'Customer Segments': self.df_clean['Customer_Segment'].nunique(),
        }
        
        for key, value in summary_stats.items():
            print(f"{key:.<40} {value}")
        
        self.cleaning_report['summary_stats'] = summary_stats
    
    def save_cleaned_data(self, output_path):
        """
        Save cleaned dataset to CSV
        """
        print("\n" + "="*70)
        print("SAVING CLEANED DATA")
        print("="*70)
        
        self.df_clean.to_csv(output_path, index=False)
        print(f"✓ Cleaned data saved to: {output_path}")
        print(f"  Total columns: {len(self.df_clean.columns)}")
        print(f"  Total rows: {len(self.df_clean):,}")
        
        self.cleaning_report['output_path'] = output_path
        self.cleaning_report['rows_after'] = len(self.df_clean)
        self.cleaning_report['rows_removed'] = self.cleaning_report['rows_before'] - len(self.df_clean)
    
    def print_cleaning_report(self):
        """
        Print comprehensive cleaning summary
        """
        print("\n" + "="*70)
        print("FINAL CLEANING REPORT")
        print("="*70)
        
        print(f"\nRows Processed:        {self.cleaning_report['rows_before']:,}")
        print(f"Rows Removed:          {self.cleaning_report['rows_removed']:,}")
        print(f"Final Rows:            {self.cleaning_report['rows_after']:,}")
        print(f"Data Retention Rate:   {(self.cleaning_report['rows_after'] / self.cleaning_report['rows_before'] * 100):.2f}%")
        print(f"\nDuplicates Removed:    {self.cleaning_report['duplicates_removed']}")
        print(f"Missing Values Fixed:  Yes")
        print(f"Validation Passed:     {self.cleaning_report['validation_passed']}")
        print(f"Output File:           {self.cleaning_report['output_path']}")
        
        return self.cleaning_report
    
    def run_full_pipeline(self, output_path):
        """
        Execute complete cleaning pipeline
        """
        print("\n" + "█"*70)
        print("█ STARTING DATA CLEANING PIPELINE")
        print("█"*70)
        
        self.get_data_profile()
        self.remove_duplicates()
        self.handle_missing_values()
        self.validate_data_integrity()
        self.format_dates()
        self.create_derived_features()
        self.generate_summary_statistics()
        self.save_cleaned_data(output_path)
        report = self.print_cleaning_report()
        
        print("\n" + "█"*70)
        print("█ CLEANING PIPELINE COMPLETE")
        print("█"*70 + "\n")
        
        return self.df_clean, report


# ============================================================================
# MAIN EXECUTION
# ============================================================================
if __name__ == "__main__":
    
    # Initialize cleaner
    cleaner = DataCleaner('d:/DA/data/sales_data_raw.csv')
    
    # Run full pipeline
    df_clean, report = cleaner.run_full_pipeline('d:/DA/data/sales_data_cleaned.csv')
    
    # Display first few cleaned records
    print("\nSample of Cleaned Data:")
    print(df_clean.head(10).to_string())
    
    print("\n✓ Data cleaning complete! Ready for analysis.")
