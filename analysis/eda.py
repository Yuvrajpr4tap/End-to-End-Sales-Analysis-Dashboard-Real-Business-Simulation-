"""
Exploratory Data Analysis with Professional Visualizations
Comprehensive statistical analysis and insights generation
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import pearsonr
import warnings
warnings.filterwarnings('ignore')

# Set style for professional visualizations
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

class SalesAnalyzer:
    """
    Comprehensive EDA class for sales data analysis
    Generates insights, statistics, and visualizations
    """
    
    def __init__(self, filepath):
        """Initialize analyzer with cleaned data"""
        self.df = pd.read_csv(filepath, parse_dates=['Order_Date', 'Ship_Date', 'Year_Month'])
        self.insights = {}
        
        print("="*70)
        print("EXPLORATORY DATA ANALYSIS - SALES INTELLIGENCE")
        print("="*70)
        print(f"\nDataset loaded: {len(self.df):,} records | {len(self.df.columns)} features")
    
    # ========================================================================
    # 1. REVENUE ANALYSIS
    # ========================================================================
    
    def analyze_revenue_trends(self):
        """Analyze monthly revenue trends and identify patterns"""
        print("\n" + "-"*70)
        print("1. REVENUE TREND ANALYSIS")
        print("-"*70)
        
        monthly_data = self.df.groupby('Year_Month').agg({
            'Sales': ['sum', 'mean', 'count'],
            'Profit': 'sum',
            'Quantity': 'sum'
        }).reset_index()
        
        monthly_data.columns = ['Year_Month', 'Total_Sales', 'Avg_Sale', 'Order_Count', 'Total_Profit', 'Units']
        
        # Calculate growth rates
        monthly_data['MoM_Growth'] = monthly_data['Total_Sales'].pct_change() * 100
        
        # Statistics
        avg_monthly_sales = monthly_data['Total_Sales'].mean()
        peak_month = monthly_data.loc[monthly_data['Total_Sales'].idxmax()]
        worst_month = monthly_data.loc[monthly_data['Total_Sales'].idxmin()]
        
        print(f"\nMonthly Insights:")
        print(f"  Average Monthly Sales:    ${avg_monthly_sales:,.2f}")
        print(f"  Peak Month (by sales):    {peak_month['Year_Month']} - ${peak_month['Total_Sales']:,.2f}")
        print(f"  Worst Month (by sales):   {worst_month['Year_Month']} - ${worst_month['Total_Sales']:,.2f}")
        print(f"  Volatility (Std Dev):     ${monthly_data['Total_Sales'].std():,.2f}")
        
        # Revenue by year
        yearly_data = self.df.groupby('Year').agg({
            'Sales': 'sum',
            'Profit': 'sum',
            'Order_ID': 'count'
        }).reset_index()
        yearly_data.columns = ['Year', 'Annual_Sales', 'Annual_Profit', 'Orders']
        yearly_data['Growth_Rate'] = yearly_data['Annual_Sales'].pct_change() * 100
        
        print("\nYearly Performance:")
        for _, row in yearly_data.iterrows():
            growth = f"↑ {row['Growth_Rate']:.1f}%" if pd.notna(row['Growth_Rate']) and row['Growth_Rate'] > 0 else ""
            print(f"  {int(row['Year'])}: ${row['Annual_Sales']:,.0f} ({row['Orders']:,} orders) {growth}")
        
        self.insights['monthly_data'] = monthly_data
        self.insights['yearly_data'] = yearly_data
        
        return monthly_data, yearly_data
    
    def analyze_regional_performance(self):
        """Segment revenue analysis by geography"""
        print("\n" + "-"*70)
        print("2. REGIONAL PERFORMANCE ANALYSIS")
        print("-"*70)
        
        regional_data = self.df.groupby('Region').agg({
            'Sales': ['sum', 'mean', 'count'],
            'Profit': 'sum',
            'Quantity': 'sum'
        }).reset_index()
        
        regional_data.columns = ['Region', 'Total_Sales', 'Avg_Sale', 'Orders', 'Total_Profit', 'Units']
        regional_data['Profit_Margin'] = (regional_data['Total_Profit'] / regional_data['Total_Sales'] * 100).round(2)
        regional_data = regional_data.sort_values('Total_Sales', ascending=False)
        
        total_sales = regional_data['Total_Sales'].sum()
        regional_data['Sales_Share'] = (regional_data['Total_Sales'] / total_sales * 100).round(2)
        
        print("\nRegional Rankings by Sales:")
        for idx, row in regional_data.iterrows():
            print(f"  {idx+1}. {row['Region']:12} → ${row['Total_Sales']:>12,.0f} ({row['Sales_Share']:>5.1f}%) | " +
                  f"Margin: {row['Profit_Margin']:>6.2f}% | Orders: {row['Orders']:>5.0f}")
        
        # State performance
        state_data = self.df.groupby(['Region', 'State']).agg({
            'Sales': 'sum',
            'Profit': 'sum',
            'Order_ID': 'count'
        }).reset_index()
        state_data.columns = ['Region', 'State', 'Sales', 'Profit', 'Orders']
        state_data = state_data.sort_values('Sales', ascending=False).head(10)
        
        print("\nTop 10 States by Revenue:")
        for idx, row in state_data.iterrows():
            print(f"  {row['State']:5} ({row['Region']:8}) → ${row['Sales']:>10,.0f} | Profit: ${row['Profit']:>10,.0f}")
        
        self.insights['regional_data'] = regional_data
        self.insights['state_data'] = state_data
        
        return regional_data
    
    def analyze_product_performance(self):
        """Identify top and bottom performing products"""
        print("\n" + "-"*70)
        print("3. PRODUCT PERFORMANCE ANALYSIS")
        print("-"*70)
        
        product_data = self.df.groupby('Product_Category').agg({
            'Sales': 'sum',
            'Profit': 'sum',
            'Order_ID': 'count',
            'Quantity': 'sum'
        }).reset_index()
        
        product_data.columns = ['Category', 'Sales', 'Profit', 'Orders', 'Units']
        product_data['Profit_Margin'] = (product_data['Profit'] / product_data['Sales'] * 100).round(2)
        product_data = product_data.sort_values('Profit', ascending=False)
        
        print("\nProduct Category Performance:")
        for idx, row in product_data.iterrows():
            print(f"  {row['Category']:20} → Sales: ${row['Sales']:>12,.0f} | Profit: ${row['Profit']:>10,.0f} | " +
                  f"Margin: {row['Profit_Margin']:>6.2f}% | Units: {row['Units']:>6.0f}")
        
        # Top products
        top_products = self.df.groupby('Product_Name').agg({
            'Sales': 'sum',
            'Profit': 'sum',
            'Order_ID': 'count'
        }).reset_index()
        top_products.columns = ['Product_Name', 'Sales', 'Profit', 'Orders']
        top_products = top_products.nlargest(10, 'Profit')
        
        print("\nTop 10 Products by Profit:")
        for idx, row in top_products.iterrows():
            print(f"  {row['Product_Name']:40} → ${row['Profit']:>10,.0f} ({row['Orders']:>4.0f} orders)")
        
        # Bottom products
        bottom_products = self.df.groupby('Product_Name').agg({
            'Sales': 'sum',
            'Profit': 'sum',
            'Order_ID': 'count'
        }).reset_index()
        bottom_products.columns = ['Product_Name', 'Sales', 'Profit', 'Orders']
        bottom_products = bottom_products[bottom_products['Orders'] > 5]  # Min 5 orders
        bottom_products = bottom_products.nsmallest(10, 'Profit')
        
        print("\nBottom 10 Products by Profit (min 5 orders):")
        for idx, row in bottom_products.iterrows():
            print(f"  {row['Product_Name']:40} → ${row['Profit']:>10,.0f} ({row['Orders']:>4.0f} orders)")
        
        self.insights['product_data'] = product_data
        self.insights['top_products'] = top_products
        self.insights['bottom_products'] = bottom_products
        
        return product_data
    
    # ========================================================================
    # 2. CORRELATION & STATISTICAL ANALYSIS
    # ========================================================================
    
    def analyze_profit_sales_correlation(self):
        """Examine relationship between Sales and Profit"""
        print("\n" + "-"*70)
        print("4. PROFIT vs SALES CORRELATION ANALYSIS")
        print("-"*70)
        
        correlation, p_value = pearsonr(self.df['Sales'], self.df['Profit'])
        
        print(f"\nPearson Correlation Coefficient: {correlation:.4f}")
        print(f"P-Value: {p_value:.4e}")
        print(f"Statistical Significance: {'Highly Significant (p < 0.001)' if p_value < 0.001 else 'Significant'}")
        
        # Linear regression
        z = np.polyfit(self.df['Sales'], self.df['Profit'], 1)
        p = np.poly1d(z)
        
        print(f"\nRegression Analysis:")
        print(f"  Slope: {z[0]:.4f} (for every $1 in sales, profit increases ${z[0]:.2f})")
        print(f"  Intercept: ${z[1]:,.2f}")
        print(f"  Model: Profit = {z[0]:.3f} * Sales + {z[1]:,.2f}")
        
        # Profit margin analysis
        profit_margin_mean = self.df['Profit_Margin_Pct'].mean()
        profit_margin_std = self.df['Profit_Margin_Pct'].std()
        profit_margin_median = self.df['Profit_Margin_Pct'].median()
        
        print(f"\nProfit Margin Distribution:")
        print(f"  Mean: {profit_margin_mean:.2f}%")
        print(f"  Median: {profit_margin_median:.2f}%")
        print(f"  Std Dev: {profit_margin_std:.2f}%")
        print(f"  Range: {self.df['Profit_Margin_Pct'].min():.2f}% to {self.df['Profit_Margin_Pct'].max():.2f}%")
        
        self.insights['correlation'] = correlation
        self.insights['profit_margin_mean'] = profit_margin_mean
        
        return correlation, p
    
    def analyze_customer_segments(self):
        """Analyze performance across customer segments"""
        print("\n" + "-"*70)
        print("5. CUSTOMER SEGMENT ANALYSIS")
        print("-"*70)
        
        segment_data = self.df.groupby('Customer_Segment').agg({
            'Sales': ['sum', 'mean', 'count'],
            'Profit': 'sum',
            'Order_ID': 'count'
        }).reset_index()
        
        segment_data.columns = ['Segment', 'Total_Sales', 'Avg_Sale', 'Repeat_Orders', 'Total_Profit', 'Orders']
        segment_data['Profit_Margin'] = (segment_data['Total_Profit'] / segment_data['Total_Sales'] * 100).round(2)
        segment_data['Sales_Share'] = (segment_data['Total_Sales'] / segment_data['Total_Sales'].sum() * 100).round(2)
        segment_data = segment_data.sort_values('Total_Sales', ascending=False)
        
        print("\nSegment Performance Rankings:")
        for idx, row in segment_data.iterrows():
            print(f"  {row['Segment']:18} → Sales: ${row['Total_Sales']:>12,.0f} ({row['Sales_Share']:>5.1f}%) | " +
                  f"Avg Order: ${row['Avg_Sale']:>8,.0f} | Margin: {row['Profit_Margin']:>6.2f}%")
        
        self.insights['segment_data'] = segment_data
        
        return segment_data
    
    def analyze_discount_impact(self):
        """Analyze how discounts affect profitability"""
        print("\n" + "-"*70)
        print("6. DISCOUNT IMPACT ANALYSIS")
        print("-"*70)
        
        # Discount vs Profit correlation
        discount_profit_corr, _ = pearsonr(self.df['Discount'], self.df['Profit_Margin_Pct'])
        
        print(f"\nDiscount Impact on Profitability:")
        print(f"  Correlation (Discount vs Margin): {discount_profit_corr:.4f}")
        
        # Compare no discount vs discounted
        no_discount = self.df[self.df['Discount'] == 0]
        discounted = self.df[self.df['Discount'] > 0]
        
        print(f"\nNo Discount Orders: {len(no_discount):,} ({len(no_discount)/len(self.df)*100:.1f}%)")
        print(f"  Avg Order Value: ${no_discount['Sales'].mean():,.2f}")
        print(f"  Avg Margin: {no_discount['Profit_Margin_Pct'].mean():.2f}%")
        print(f"  Avg Profit: ${no_discount['Profit'].mean():,.2f}")
        
        print(f"\nDiscounted Orders: {len(discounted):,} ({len(discounted)/len(self.df)*100:.1f}%)")
        print(f"  Avg Order Value: ${discounted['Sales'].mean():,.2f}")
        print(f"  Avg Margin: {discounted['Profit_Margin_Pct'].mean():.2f}%")
        print(f"  Avg Profit: ${discounted['Profit'].mean():,.2f}")
        
        # By discount level
        discount_bins = self.df.groupby(pd.cut(self.df['Discount'], bins=5)).agg({
            'Sales': 'mean',
            'Profit': 'mean',
            'Profit_Margin_Pct': 'mean',
            'Order_ID': 'count'
        })
        
        self.insights['discount_impact'] = discount_profit_corr
        
        return discount_profit_corr
    
    # ========================================================================
    # 3. VISUALIZATION GENERATION
    # ========================================================================
    
    def create_visualizations(self):
        """Generate publication-quality visualizations"""
        print("\n" + "-"*70)
        print("GENERATING VISUALIZATIONS")
        print("-"*70)
        
        # Create figure with subplots
        fig = plt.figure(figsize=(20, 24))
        
        # 1. Revenue Trend Line Chart
        ax1 = plt.subplot(4, 3, 1)
        monthly_sales = self.df.groupby('Year_Month')['Sales'].sum()
        monthly_sales.plot(ax=ax1, color='#2E86AB', linewidth=2.5, marker='o', markersize=4)
        ax1.set_title('Monthly Revenue Trend', fontsize=14, fontweight='bold', pad=10)
        ax1.set_xlabel('Month', fontsize=11)
        ax1.set_ylabel('Sales ($)', fontsize=11)
        ax1.grid(True, alpha=0.3)
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=9)
        
        # 2. Regional Sales Distribution Bar Chart
        ax2 = plt.subplot(4, 3, 2)
        regional_sales = self.df.groupby('Region')['Sales'].sum().sort_values(ascending=True)
        colors = ['#A23B72', '#F18F01', '#C73E1D', '#6A994E']
        regional_sales.plot(kind='barh', ax=ax2, color=colors)
        ax2.set_title('Sales by Region', fontsize=14, fontweight='bold', pad=10)
        ax2.set_xlabel('Total Sales ($)', fontsize=11)
        ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
        for i, v in enumerate(regional_sales):
            ax2.text(v, i, f' ${v/1000:.0f}K', va='center', fontsize=10, fontweight='bold')
        
        # 3. Product Category Performance
        ax3 = plt.subplot(4, 3, 3)
        category_profit = self.df.groupby('Product_Category')['Profit'].sum().sort_values(ascending=False)
        colors_cat = ['#06A77D', '#E76F51', '#F4A261']
        ax3.bar(range(len(category_profit)), category_profit, color=colors_cat)
        ax3.set_xticks(range(len(category_profit)))
        ax3.set_xticklabels(category_profit.index, rotation=15, ha='right')
        ax3.set_title('Profit by Product Category', fontsize=14, fontweight='bold', pad=10)
        ax3.set_ylabel('Profit ($)', fontsize=11)
        ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
        for i, v in enumerate(category_profit):
            ax3.text(i, v, f'${v/1000:.0f}K', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # 4. Profit vs Sales Scatter Plot
        ax4 = plt.subplot(4, 3, 4)
        scatter = ax4.scatter(self.df['Sales'], self.df['Profit'], 
                             c=self.df['Profit_Margin_Pct'], cmap='RdYlGn', 
                             alpha=0.5, s=30, edgecolors='none')
        z = np.polyfit(self.df['Sales'], self.df['Profit'], 1)
        p = np.poly1d(z)
        ax4.plot(self.df['Sales'].sort_values(), p(self.df['Sales'].sort_values()), 
                "r--", linewidth=2.5, label='Trend Line')
        ax4.set_title('Profit vs Sales Correlation', fontsize=14, fontweight='bold', pad=10)
        ax4.set_xlabel('Sales ($)', fontsize=11)
        ax4.set_ylabel('Profit ($)', fontsize=11)
        ax4.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
        ax4.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
        cbar = plt.colorbar(scatter, ax=ax4)
        cbar.set_label('Profit Margin %', fontsize=10)
        ax4.legend(fontsize=10)
        
        # 5. Customer Segment Distribution Pie Chart
        ax5 = plt.subplot(4, 3, 5)
        segment_sales = self.df.groupby('Customer_Segment')['Sales'].sum()
        colors_seg = ['#264653', '#2A9D8F', '#E9C46A', '#F4A261']
        wedges, texts, autotexts = ax5.pie(segment_sales, labels=segment_sales.index, autopct='%1.1f%%',
                                            colors=colors_seg, startangle=90)
        ax5.set_title('Sales by Customer Segment', fontsize=14, fontweight='bold', pad=10)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)
        
        # 6. Profit Margin Distribution
        ax6 = plt.subplot(4, 3, 6)
        ax6.hist(self.df['Profit_Margin_Pct'], bins=50, color='#06A77D', edgecolor='black', alpha=0.7)
        ax6.axvline(self.df['Profit_Margin_Pct'].mean(), color='red', linestyle='--', 
                   linewidth=2.5, label=f'Mean: {self.df["Profit_Margin_Pct"].mean():.2f}%')
        ax6.set_title('Profit Margin Distribution', fontsize=14, fontweight='bold', pad=10)
        ax6.set_xlabel('Profit Margin (%)', fontsize=11)
        ax6.set_ylabel('Frequency', fontsize=11)
        ax6.legend(fontsize=10)
        ax6.grid(True, alpha=0.3, axis='y')
        
        # 7. Top 10 Products
        ax7 = plt.subplot(4, 3, 7)
        top_products = self.df.groupby('Product_Name')['Profit'].sum().nlargest(10)
        ax7.barh(range(len(top_products)), top_products.values, color='#E76F51')
        ax7.set_yticks(range(len(top_products)))
        ax7.set_yticklabels([name[:20] + '...' if len(name) > 20 else name for name in top_products.index], fontsize=9)
        ax7.set_title('Top 10 Products by Profit', fontsize=14, fontweight='bold', pad=10)
        ax7.set_xlabel('Profit ($)', fontsize=11)
        ax7.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
        
        # 8. Discount Impact
        ax8 = plt.subplot(4, 3, 8)
        discount_groups = self.df.groupby(pd.cut(self.df['Discount'], bins=5)).agg({
            'Profit_Margin_Pct': 'mean',
            'Sales': 'count'
        })
        discount_groups.plot(y='Profit_Margin_Pct', ax=ax8, legend=False, 
                           color='#F4A261', linewidth=2.5, marker='o', markersize=8)
        ax8.set_title('Impact of Discount on Profit Margin', fontsize=14, fontweight='bold', pad=10)
        ax8.set_xlabel('Discount Level', fontsize=11)
        ax8.set_ylabel('Avg Profit Margin (%)', fontsize=11)
        ax8.grid(True, alpha=0.3)
        plt.setp(ax8.xaxis.get_majorticklabels(), rotation=15, ha='right')
        
        # 9. Regional Profit Margins
        ax9 = plt.subplot(4, 3, 9)
        regional_margins = self.df.groupby('Region')['Profit_Margin_Pct'].mean().sort_values()
        ax9.barh(regional_margins.index, regional_margins.values, color=['#6A994E', '#BC4749', '#C73E1D', '#A23B72'])
        ax9.set_title('Average Profit Margin by Region', fontsize=14, fontweight='bold', pad=10)
        ax9.set_xlabel('Profit Margin (%)', fontsize=11)
        for i, v in enumerate(regional_margins):
            ax9.text(v, i, f' {v:.1f}%', va='center', fontsize=10, fontweight='bold')
        
        # 10. Sales by Day of Week
        ax10 = plt.subplot(4, 3, 10)
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_sales = self.df.groupby('DayOfWeek')['Sales'].mean().reindex(day_order)
        ax10.plot(range(len(dow_sales)), dow_sales.values, marker='o', linewidth=2.5, 
                 markersize=8, color='#2E86AB')
        ax10.fill_between(range(len(dow_sales)), dow_sales.values, alpha=0.3, color='#2E86AB')
        ax10.set_xticks(range(len(dow_sales)))
        ax10.set_xticklabels([day[:3] for day in day_order], fontsize=10)
        ax10.set_title('Average Sale by Day of Week', fontsize=14, fontweight='bold', pad=10)
        ax10.set_ylabel('Average Sales ($)', fontsize=11)
        ax10.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
        ax10.grid(True, alpha=0.3)
        
        # 11. Quantity vs Profit Correlation
        ax11 = plt.subplot(4, 3, 11)
        ax11.scatter(self.df['Quantity'], self.df['Profit'], 
                    c=self.df['Sales'], cmap='viridis', alpha=0.5, s=30, edgecolors='none')
        ax11.set_title('Order Quantity vs Profit', fontsize=14, fontweight='bold', pad=10)
        ax11.set_xlabel('Quantity (Units)', fontsize=11)
        ax11.set_ylabel('Profit ($)', fontsize=11)
        cbar2 = plt.colorbar(ax11.collections[0], ax=ax11)
        cbar2.set_label('Sales ($)', fontsize=10)
        
        # 12. Cumulative Revenue
        ax12 = plt.subplot(4, 3, 12)
        cumsum_data = self.df.groupby('Year_Month')['Sales'].sum().cumsum()
        ax12.plot(range(len(cumsum_data)), cumsum_data.values, linewidth=2.5, 
                 marker='o', markersize=4, color='#06A77D')
        ax12.fill_between(range(len(cumsum_data)), cumsum_data.values, alpha=0.3, color='#06A77D')
        ax12.set_title('Cumulative Revenue Over Time', fontsize=14, fontweight='bold', pad=10)
        ax12.set_xlabel('Month', fontsize=11)
        ax12.set_ylabel('Cumulative Sales ($)', fontsize=11)
        ax12.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000000:.1f}M'))
        ax12.grid(True, alpha=0.3)
        plt.setp(ax12.xaxis.get_majorticklabels(), rotation=0, fontsize=9)
        
        plt.tight_layout()
        
        # Save visualization
        output_path = 'd:/DA/visualizations/eda_comprehensive_analysis.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Comprehensive visualization saved: {output_path}")
        
        plt.close()
        
        self.insights['visualization_saved'] = True
    
    def generate_executive_summary(self):
        """Generate executive-level insights"""
        print("\n" + "="*70)
        print("EXECUTIVE SUMMARY - KEY INSIGHTS")
        print("="*70)
        
        print(f"\n📊 FINANCIAL PERFORMANCE:")
        print(f"  Total Revenue:              ${self.df['Sales'].sum():>15,.2f}")
        print(f"  Total Profit:               ${self.df['Profit'].sum():>15,.2f}")
        print(f"  Overall Profit Margin:      {(self.df['Profit'].sum()/self.df['Sales'].sum()*100):>15.2f}%")
        print(f"  Average Order Value:        ${self.df['Sales'].mean():>15,.2f}")
        print(f"  Total Orders:               {len(self.df):>15,}")
        print(f"  Total Units Sold:           {self.df['Quantity'].sum():>15,}")
        
        print(f"\n🌍 GEOGRAPHIC INSIGHTS:")
        top_region = self.df.groupby('Region')['Sales'].sum().idxmax()
        top_region_sales = self.df.groupby('Region')['Sales'].sum().max()
        print(f"  Top Region:                 {top_region} (${top_region_sales:,.0f})")
        print(f"  Number of States:           {self.df['State'].nunique()}")
        print(f"  Number of Cities:           {self.df['City'].nunique()}")
        
        print(f"\n📦 PRODUCT INSIGHTS:")
        top_category = self.df.groupby('Product_Category')['Profit'].sum().idxmax()
        print(f"  Top Category:               {top_category}")
        print(f"  Total Products:             {self.df['Product_Name'].nunique()}")
        top_product = self.df.groupby('Product_Name')['Profit'].sum().idxmax()
        top_product_profit = self.df.groupby('Product_Name')['Profit'].sum().max()
        print(f"  Top Product:                {top_product} (${top_product_profit:,.0f})")
        
        print(f"\n👥 CUSTOMER INSIGHTS:")
        top_segment = self.df.groupby('Customer_Segment')['Sales'].sum().idxmax()
        print(f"  Top Segment:                {top_segment}")
        print(f"  Segment Diversity:          {self.df['Customer_Segment'].nunique()} segments")
        
        print(f"\n⚠️  AREAS FOR IMPROVEMENT:")
        discounted_pct = (len(self.df[self.df['Discount'] > 0])/len(self.df)*100)
        print(f"  Discounted Orders:          {discounted_pct:.1f}% of all orders")
        low_margin_products = len(self.df[self.df['Profit_Margin_Pct'] < 5])
        print(f"  Low-Margin Orders (<5%):    {low_margin_products:,} ({low_margin_products/len(self.df)*100:.1f}%)")
        
        print("\n" + "="*70)


# ============================================================================
# MAIN EXECUTION
# ============================================================================
if __name__ == "__main__":
    
    # Initialize analyzer
    analyzer = SalesAnalyzer('d:/DA/data/sales_data_cleaned.csv')
    
    # Run all analyses
    monthly_data, yearly_data = analyzer.analyze_revenue_trends()
    analyzer.analyze_regional_performance()
    analyzer.analyze_product_performance()
    analyzer.analyze_profit_sales_correlation()
    analyzer.analyze_customer_segments()
    analyzer.analyze_discount_impact()
    
    # Generate visualizations
    analyzer.create_visualizations()
    
    # Executive summary
    analyzer.generate_executive_summary()
    
    print("\n✓ Exploratory Data Analysis Complete!")
