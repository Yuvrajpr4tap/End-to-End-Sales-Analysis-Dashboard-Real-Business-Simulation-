"""
Interactive BI Dashboard - Sales Analysis & Forecasting
Streamlit web application for portfolio showcasing revenue optimization insights
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Page Configuration
st.set_page_config(
    page_title="BI Dashboard - Sales Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 30px;
    }
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    .insight-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-left: 5px solid #1f77b4;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== LOAD DATA ====================
@st.cache_data
def load_data():
    """Load cleaned sales data"""
    try:
        df = pd.read_csv('data/sales_data_cleaned.csv', parse_dates=['Order_Date', 'Ship_Date', 'Year_Month'])
        return df
    except FileNotFoundError:
        st.error("❌ Data file not found. Please ensure 'data/sales_data_cleaned.csv' exists.")
        return None

# ==================== SIDEBAR FILTERS ====================
st.sidebar.markdown("## 🎯 Dashboard Filters")

df = load_data()
if df is not None:
    # Date Range Filter
    st.sidebar.markdown("### Date Range")
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(df['Order_Date'].min().date(), df['Order_Date'].max().date()),
        min_value=df['Order_Date'].min().date(),
        max_value=df['Order_Date'].max().date()
    )
    
    # Region Filter
    st.sidebar.markdown("### Region")
    regions = st.sidebar.multiselect(
        "Select Regions",
        options=sorted(df['Region'].unique()),
        default=sorted(df['Region'].unique())
    )
    
    # Category Filter
    st.sidebar.markdown("### Product Category")
    categories = st.sidebar.multiselect(
        "Select Categories",
        options=sorted(df['Product_Category'].unique()),
        default=sorted(df['Product_Category'].unique())
    )
    
    # Customer Segment Filter
    st.sidebar.markdown("### Customer Segment")
    segments = st.sidebar.multiselect(
        "Select Segments",
        options=sorted(df['Customer_Segment'].unique()),
        default=sorted(df['Customer_Segment'].unique())
    )
    
    # Apply Filters
    df_filtered = df[
        (df['Order_Date'].dt.date >= date_range[0]) &
        (df['Order_Date'].dt.date <= date_range[1]) &
        (df['Region'].isin(regions)) &
        (df['Product_Category'].isin(categories)) &
        (df['Customer_Segment'].isin(segments))
    ].copy()
    
    # ==================== MAIN CONTENT ====================
    st.markdown("# 📊 Sales Intelligence Dashboard")
    st.markdown("**Real-Time Business Analytics & Revenue Optimization Insights**")
    st.markdown("---")
    
    # ==================== KEY METRICS ====================
    st.markdown("## 💰 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_revenue = df_filtered['Sales'].sum()
        st.metric(
            label="Total Revenue",
            value=f"${total_revenue:,.0f}",
            delta=f"({len(df_filtered):,} orders)",
            help="Sum of all sales in filtered period"
        )
    
    with col2:
        total_profit = df_filtered['Profit'].sum()
        st.metric(
            label="Total Profit",
            value=f"${total_profit:,.0f}",
            delta=f"{(total_profit/total_revenue*100):.1f}% margin" if total_revenue > 0 else "0%",
            help="Net profit after costs"
        )
    
    with col3:
        avg_order_value = df_filtered['Sales'].mean()
        st.metric(
            label="Avg Order Value",
            value=f"${avg_order_value:,.0f}",
            delta=f"{df_filtered['Quantity'].mean():.1f} units/order",
            help="Average order size"
        )
    
    with col4:
        profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        st.metric(
            label="Profit Margin",
            value=f"{profit_margin:.1f}%",
            delta="Healthy" if profit_margin > 15 else "Review Needed",
            help="Profit as % of Revenue"
        )
    
    st.markdown("---")
    
    # ==================== CHARTS - ROW 1 ====================
    st.markdown("## 📈 Sales Performance Analysis")
    
    col1, col2 = st.columns(2)
    
    # Monthly Revenue Trend
    with col1:
        st.subheader("📊 Monthly Revenue Trend")
        monthly_sales = df_filtered.groupby(df_filtered['Order_Date'].dt.to_period('M'))['Sales'].sum()
        monthly_sales.index = monthly_sales.index.to_timestamp()
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(monthly_sales.index, monthly_sales.values, marker='o', linewidth=2, markersize=8, color='#1f77b4')
        ax.fill_between(monthly_sales.index, monthly_sales.values, alpha=0.3, color='#1f77b4')
        ax.set_xlabel('Date', fontsize=11, fontweight='bold')
        ax.set_ylabel('Sales ($)', fontsize=11, fontweight='bold')
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
    
    # Regional Sales Breakdown
    with col2:
        st.subheader("🌍 Sales by Region")
        regional_sales = df_filtered.groupby('Region')['Sales'].sum().sort_values(ascending=False)
        
        fig, ax = plt.subplots(figsize=(10, 5))
        bars = ax.barh(regional_sales.index, regional_sales.values, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
        ax.set_xlabel('Sales ($)', fontsize=11, fontweight='bold')
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2, 
                   f'${width:,.0f}', ha='left', va='center', fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)
    
    # ==================== CHARTS - ROW 2 ====================
    col1, col2 = st.columns(2)
    
    # Top Products
    with col1:
        st.subheader("⭐ Top 10 Products by Sales")
        top_products = df_filtered.groupby('Product_Name')['Sales'].sum().nlargest(10).sort_values()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(range(len(top_products)), top_products.values, color='#2ca02c')
        ax.set_yticks(range(len(top_products)))
        ax.set_yticklabels(top_products.index, fontsize=9)
        ax.set_xlabel('Sales ($)', fontsize=11, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
    
    # Category Distribution
    with col2:
        st.subheader("📦 Sales by Product Category")
        category_sales = df_filtered.groupby('Product_Category')['Sales'].sum()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        wedges, texts, autotexts = ax.pie(category_sales.values, labels=category_sales.index, autopct='%1.1f%%',
                                            colors=colors, startangle=90, textprops={'fontsize': 10})
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        plt.tight_layout()
        st.pyplot(fig)
    
    # ==================== CHARTS - ROW 3 ====================
    col1, col2 = st.columns(2)
    
    # Profit vs Sales Scatter
    with col1:
        st.subheader("📊 Profit vs Sales Correlation")
        fig, ax = plt.subplots(figsize=(10, 6))
        scatter = ax.scatter(df_filtered['Sales'], df_filtered['Profit'], 
                           c=df_filtered['Discount'], cmap='RdYlGn_r', alpha=0.6, s=50)
        ax.set_xlabel('Sales ($)', fontsize=11, fontweight='bold')
        ax.set_ylabel('Profit ($)', fontsize=11, fontweight='bold')
        ax.grid(True, alpha=0.3)
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Discount (%)', fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)
    
    # Customer Segment Performance
    with col2:
        st.subheader("👥 Performance by Customer Segment")
        segment_data = df_filtered.groupby('Customer_Segment').agg({
            'Sales': 'sum',
            'Profit': 'sum',
            'Order_ID': 'count'
        }).sort_values('Sales', ascending=False)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        x = range(len(segment_data))
        width = 0.35
        ax.bar([i - width/2 for i in x], segment_data['Sales'], width, label='Sales', color='#1f77b4')
        ax.bar([i + width/2 for i in x], segment_data['Profit'], width, label='Profit', color='#2ca02c')
        ax.set_ylabel('Amount ($)', fontsize=11, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(segment_data.index)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
    
    # ==================== DATA INSIGHTS ====================
    st.markdown("---")
    st.markdown("## 💡 Key Insights & Recommendations")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📊 Revenue Insights")
        top_region = df_filtered.groupby('Region')['Sales'].sum().idxmax()
        top_region_sales = df_filtered.groupby('Region')['Sales'].sum().max()
        st.info(f"**{top_region}** is the top region generating **${top_region_sales:,.0f}** in sales")
    
    with col2:
        st.markdown("### 🎯 Profitability")
        highest_margin_cat = df_filtered.groupby('Product_Category').apply(
            lambda x: (x['Profit'].sum() / x['Sales'].sum() * 100)
        ).idxmax()
        highest_margin = df_filtered.groupby('Product_Category').apply(
            lambda x: (x['Profit'].sum() / x['Sales'].sum() * 100)
        ).max()
        st.success(f"**{highest_margin_cat}** has highest margin at **{highest_margin:.1f}%**")
    
    with col3:
        st.markdown("### ⚠️ Alerts")
        negative_profit = len(df_filtered[df_filtered['Profit'] < 0])
        if negative_profit > 0:
            st.warning(f"⚠️ **{negative_profit}** unprofitable orders detected - review pricing/costs")
        else:
            st.success("✅ All orders are profitable! Strong business model.")
    
    # ==================== DETAILED TABLES ====================
    st.markdown("---")
    st.markdown("## 📋 Detailed Data Views")
    
    tab1, tab2, tab3 = st.tabs(["Top Products", "Regional Performance", "Raw Data"])
    
    with tab1:
        st.subheader("Top 20 Products by Profit")
        top_20 = df_filtered.groupby('Product_Name').agg({
            'Sales': 'sum',
            'Profit': 'sum',
            'Quantity': 'sum',
            'Order_ID': 'count'
        }).sort_values('Profit', ascending=False).head(20)
        
        top_20.columns = ['Total Sales', 'Total Profit', 'Qty Sold', 'Orders']
        st.dataframe(top_20.style.format({
            'Total Sales': '${:,.0f}',
            'Total Profit': '${:,.0f}',
            'Qty Sold': '{:,.0f}',
            'Orders': '{:,.0f}'
        }), use_container_width=True)
    
    with tab2:
        st.subheader("Regional Performance Summary")
        regional_summary = df_filtered.groupby('Region').agg({
            'Sales': 'sum',
            'Profit': 'sum',
            'Order_ID': 'count',
            'Discount': 'mean'
        }).sort_values('Sales', ascending=False)
        
        regional_summary.columns = ['Total Sales', 'Total Profit', 'Orders', 'Avg Discount %']
        regional_summary['Profit Margin %'] = (
            (regional_summary['Total Profit'] / regional_summary['Total Sales'] * 100).round(2)
        )
        
        st.dataframe(regional_summary.style.format({
            'Total Sales': '${:,.0f}',
            'Total Profit': '${:,.0f}',
            'Orders': '{:,.0f}',
            'Avg Discount %': '{:.2f}%',
            'Profit Margin %': '{:.2f}%'
        }), use_container_width=True)
    
    with tab3:
        st.subheader("Raw Sales Data")
        display_cols = ['Order_Date', 'Product_Name', 'Region', 'Sales', 'Profit', 'Discount', 'Quantity']
        st.dataframe(
            df_filtered[display_cols].sort_values('Order_Date', ascending=False).head(100),
            use_container_width=True
        )
    
    # ==================== FOOTER ====================
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; margin-top: 50px;'>
        <p><strong>📊 Sales Analysis Dashboard</strong> | Built with Streamlit | Data-Driven Insights</p>
        <p>Last Updated: """ + datetime.now().strftime("%B %d, %Y") + """</p>
        <p>Repository: <a href='https://github.com/Yuvrajpr4tap/End-to-End-Sales-Analysis-Dashboard-Real-Business-Simulation-' target='_blank'>GitHub</a></p>
    </div>
    """, unsafe_allow_html=True)

else:
    st.error("❌ Unable to load data. Check that the data file exists and is properly formatted.")
