# Business Intelligence Dashboard Design Specification
## Revenue Optimization & Sales Forecasting

**Project**: Revenue Optimization & Sales Forecasting BI Dashboard  
**Version**: 1.0  
**Date**: March 26, 2026  
**Audience**: Executive Leadership, Sales Management, Operations Team

---

## Executive Overview

This dashboard provides real-time visibility into key business metrics, regional performance, product profitability, and 6-month sales forecasts. Designed for C-suite executives and operational teams, it enables data-driven decision-making across all departments.

---

## 📊 Dashboard Architecture

### **Page 1: EXECUTIVE SUMMARY (Landing Page)**

**Purpose**: High-level KPI overview for C-suite visibility (30-second glance)

#### Layout: Top Analytics Row (5 KPI Cards)
```
┌─────────────────┬──────────────────┬──────────────────┬──────────────────┬─────────────────┐
│   Total Revenue │   Total Profit   │  Profit Margin % │  Growth Rate YoY │ Avg Order Value │
│  $22.73M        │  $5.71M          │      25.14%      │     1.04%        │    $2,273       │
│  ↑ 1.0% MoM     │  ↑ 0.8% MoM      │  ↓ 0.3% MoM      │  ↓ -2.1% YoY     │  ↓ -8.5% YoY    │
└─────────────────┴──────────────────┴──────────────────┴──────────────────┴─────────────────┘
```

#### Layout: 4 Primary Visualizations (2x2 Grid)

**Chart 1 - Revenue Trend (Top Left)**
- **Type**: Line Chart with dual axis
- **Series 1**: Monthly Sales (Primary Y-axis, Blue #2E86AB)
- **Series 2**: Cumulative Revenue YTD (Secondary Y-axis, Green)
- **Features**:
  - 36-month historical data + 6-month forecast bands (light red shaded area)
  - Hover tooltip: Date, Sales $, % Change MoM, Forecast Range
  - Trend line showing overall direction
  - Reference lines: Average historical sales, Target sales
- **Size**: 50% of dashboard width, 50% of height

**Chart 2 - Regional Performance (Top Right)**
- **Type**: Clustered Bar Chart + Overlay Line
- **Axes**:
  - X-axis: Regions (North, South, East, West)
  - Y-axis: Sales $ (Left), Profit Margin % (Right)
- **Bars**: Sales by region (color-coded: #A23B72, #F18F01, #C73E1D, #6A994E)
- **Line**: Profit margin % trend across regions
- **Features**:
  - Data labels on bars ($ and %)
  - Conditional formatting: Colors indicate performance tiers
  - Drill-down capability: Click to see state-level breakdown
  - Sort ascending/descending toggle
- **Size**: 50% of dashboard width, 50% of height

**Chart 3 - Product Category Mix (Bottom Left)**
- **Type**: Pie Chart + Donut Ring
- **Inner Ring**: Revenue distribution by category (Technology 34%, Office Supplies 33%, Furniture 33%)
- **Outer Ring**: Profit distribution by category
- **Colors**: #06A77D, #E76F51, #F4A261 with hover highlight
- **Features**:
  - Percentage labels with actual $ values
  - Interactive legend with on/off toggle
  - Click segment to filter all other dashboard charts
  - Animation on load showing growth sequence
- **Size**: 35% of dashboard width, 50% of height

**Chart 4 - Top 5 Products (Bottom Right)**
- **Type**: Horizontal Bar Chart (Profit-sorted)
- **Y-axis**: Product Name (truncated with ellipsis at 30 chars)
- **X-axis**: Total Profit ($)
- **Color Gradient**: Green (high) → Yellow (medium) → Red (low) based on profit margin
- **Features**:
  - Data labels: Profit $, Margin %, # Orders
  - Hover shows full product name, sales, quantity sold
  - Benchmark line showing average profit line
  - Highlight top performer with star icon
- **Size**: 65% of dashboard width, 50% of height

---

### **Page 2: SALES PERFORMANCE DEEP DIVE**

**Purpose**: Detailed analysis for sales and operations teams

#### Header Section
```
Filter Panel (Left Sidebar, 20% width):
├── Date Range Slider [2022-01-01 to 2024-12-31]
├── Region Multi-Select [All, North, South, East, West]
├── Product Category [All, Technology, Furniture, Office Supplies]
├── Customer Segment [All, Consumer, Corporate, VIP, One-time]
├── Sales Range Slider [$0 - $2500]
└── Margin Range Slider [0% - 40%]
```

#### Main Content Area (80% width)

**Chart 1 - Sales by Region & State (Top, 100% width)**
- **Type**: Treemap or Sunburst Chart
- **Hierarchy**: Region > State > City
- **Size Represents**: Sales amount
- **Color Represents**: Profit margin %
- **Features**:
  - Click to drill down/up
  - Hover shows: State/City name, Sales $, Orders, Profit $, Margin %
  - Regional averages line at bottom
  - Identify underperformers (red) vs stars (green)
- **Height**: 35% of page

**Chart 2 - Customer Segment Analysis (Middle Left, 50% width)**
- **Type**: Combination chart
- **Bars**: Revenue per segment (color-coded)
- **Line**: Profit trend over time
- **Features**:
  - Toggle between absolute $ and percentage
  - Segment ranking table below showing:
    - Segment name
    - Orders count
    - Avg order value
    - Retention rate
    - LTV (Lifetime Value)
  - Year-over-year comparison
- **Height**: 35% of page

**Chart 3 - Discount Impact Analysis (Middle Right, 50% width)**
- **Type**: Scatter plot + column overlay
- **X-axis**: Discount rate (0-50%)
- **Y-axis**: Profit margin %
- **Bubble Size**: Order volume
- **Bubble Color**: Sales velocity (blue slow, red fast)
- **Features**:
  - Regression line showing relationship
  - Quadrant lines (target profitability zone in green)
  - Hover: Specific order details
  - KPI alert if too many orders in red zone
- **Height**: 35% of page

**Chart 4 - Monthly Performance Table (Bottom, 100% width)**
- **Type**: Data table with conditional formatting
- **Columns**:
  - Month (YYYY-MM)
  - Sales $ (light green if >avg, light red if <avg)
  - Growth % MoM (arrows: ↑ green, ↓ red)
  - Profit $ 
  - Margin %
  - Orders
  - Avg Order Value
  - Top Product
- **Features**:
  - Sortable columns
  - Export to CSV button
  - Pagination (10/25/50 rows per page)
  - Conditional row highlighting
- **Height**: 30% of page

---

### **Page 3: PROFIT & MARGIN ANALYSIS**

**Purpose**: Finance/CFO-focused view on profitability metrics

#### Key Metrics Row
```
┌──────────────────┬──────────────────┬──────────────────┬──────────────────┐
│ Gross Profit     │ Operating Margin │ Profit/Order Avg │  Target vs Actual│
│  $5.71M          │      25.14%       │      $571        │   104.2% (Green) │
│  vs Target: 105% │  vs Target: 104%  │  vs Target: 100% │ ↑ $28K vs prev mo│
└──────────────────┴──────────────────┴──────────────────┴──────────────────┘
```

**Chart 1 - Profit Waterfall (Top, 100% width)**
- **Type**: Waterfall chart showing profit build-up
- **Flow**:
  - Starting: Total Sales ($22.73M)
  - Less: COGS (estimated from margin)
  - Less: Discounts (impact of promotional activity)
  - Equals: Gross Profit ($5.71M)
  - Less: Operating expenses (estimated)
  - Equals: Net Profit
- **Features**:
  - Hover shows detailed P&L breakdown
  - Drill-down to category level
  - Budget vs actual comparison
- **Height**: 40% of page

**Chart 2 - Margin by Category & Segment (Middle, 100% width)**
- **Type**: Heatmap / Matrix
- **Rows**: Product Categories (Technology, Furniture, Office Supplies)
- **Columns**: Customer Segments (Consumer, Corporate, VIP, One-time)
- **Color Intensity**: Profit margin % (Dark Green = High, Light Red = Low)
- **Feature**: Cell value shows margin % and trend indicator (↑/↓)
- **Interactive**: Click cell to see detailed breakdown
- **Height**: 35% of page

**Chart 3 - Top 10 Products by Margin (Bottom Left, 50% width)**
- **Type**: Column chart with overlay
- **Primary**: Profit margin % (bars)
- **Secondary**: Sales volume (line)
- **Colors**: Green (high margin) to Red (low margin)
- **Features**:
  - Data labels: Margin %, $ Profit, # Orders
  - Reference line: Company average margin
  - Trend indicator next to each product
  - Ability to add/remove from featured list
- **Height**: 25% of page

**Chart 4 - Margin Trend (Bottom Right, 50% width)**
- **Type**: Line chart with confidence bands
- **Series**: Overall margin %, Category margins (stacked area)
- **Features**:
  - 36-month history + projection forward
  - Seasonality pattern highlighted
  - Benchmark against industry average (dotted line)
  - Alert if margin drops below threshold
- **Height**: 25% of page

---

### **Page 4: FORECASTING & PREDICTIONS**

**Purpose**: Strategic planning with forecast models

#### Header
```
Forecast Model Selector: ○ Prophet  ○ ARIMA  ● Consensus (Both)
Confidence Level: ◆────●────◆ 80% (adjustable slider 50%-95%)
Forecast Period: 6 Months
Last Updated: [Timestamp]
```

**Chart 1 - Sales Forecast (Top, 100% width)**
- **Type**: Line chart + confidence band
- **Series**:
  - Historical sales (blue solid line, 36 months)
  - Prophet forecast (red dashed, 6 months ahead)
  - ARIMA forecast (green dashed, 6 months ahead)
  - Consensus band (shaded area between models)
- **Confidence Intervals**: 80% CI as semi-transparent bands
- **Features**:
  - Tooltip shows:
    - Actual $ for historical
    - Forecast $, Prophet $, ARIMA $, Upper/Lower CI for forecast period
    - Growth rate vs same month prior year
  - Vertical line marking forecast boundary
  - Seasonal indicators (shaded bands showing peak/trough seasons)
  - Pinpoint anomalies that influenced historical data
- **Height**: 45% of page

**Chart 2 - Category Forecast (Middle Left, 50% width)**
- **Type**: Multi-line forecast chart
- **Series**: Separate forecast line for each product category
- **Color**: Category colors (#06A77D, #E76F51, #F4A261)
- **Features**:
  - Toggle categories on/off
  - Show only high/low confidence predictions
  - Trend indicators (↑↓) on each forecast line
  - Click legend to highlight one category
- **Height**: 30% of page

**Chart 3 - Regional Forecast (Middle Right, 50% width)**
- **Type**: Small multiples (4 mini line charts, one per region)
- **Each Chart**:
  - 12-month history + 6-month forecast
  - Region-specific confidence bands
  - Trend direction indicator
- **Features**:
  - Synchronized hover across all 4 charts
  - Compare regions at a glance
  - Tap to expand individual region to full size
- **Height**: 30% of page

**Chart 4 - Forecast Accuracy Metrics (Bottom, 100% width)**
- **Type**: KPI tile grid + Model comparison table
- **Left Side (60%)**:
  - Prophet MAPE: 15.18%
  - ARIMA MAPE: 3.37%
  - Ensemble RMSE: $[Value]
  - Test period R²: [Value]
  - Recommended model: ARIMA (based on MAPE)
- **Right Side (40%)**: Data table comparing models
  - Model Name | RMSE | MAPE | Best Use Case
  - Detailed methodology notes
- **Features**:
  - Link to detailed model documentation
  - Button to retrain models
  - Download forecast as CSV
- **Height**: 25% of page

---

### **Page 5: INTERACTIVE DASHBOARD (Admin/Developer View)**

**Purpose**: Real-time data health monitoring and drill-down

#### Global Filters (Top, full width)
```
┌─────────────────────────────────────────────────────────────────────────┐
│ Date: [__|__/__|__] to [__|__/__|__]  |  Quick: [YTD] [Last 30] [Last Year]
│ Region: ▼ Multiple   |  Category: ▼ All  |  Product: ▼ Top 20  |  Refresh [⟳]
└─────────────────────────────────────────────────────────────────────────┘
```

**KPI Dashboard (Top Row)**
- Tiles showing: Revenue, Profit, Orders, Units, Margin%, Regions, Products

**Detail Grids (Main Content)**
- **Grid 1**: Order-level transaction details
  - Columns: Order ID, Date, Customer Segment, Region, Product, Qty, Sale $, Discount, Profit, Margin%
  - Sortable, filterable
  - Export button
  - Click row to view full order details popup
- **Grid 2**: Product master data
  - Columns: Product ID, Name, Category, Sub Category, Avg Price, QTY Sold, Revenue, Profit
  - Conditional formatting for underperformers
  - Edit capability for admins
- **Grid 3**: Regional summary
  - Columns: Region, State, City, Sales, Profit, Orders, Avg Order Value, Trend

---

## 🎨 Design Specifications

### Color Palette
- **Primary**: #2E86AB (Blue - Professional)
- **Success/Growth**: #06A77D (Green)
- **Warning/Risk**: #E63946 (Red)
- **Accent 1**: #F4A261 (Orange)
- **Accent 2**: #A23B72 (Purple)
- **Neutral**: #F1FAEE (Off-white background)
- **Text**: #1D3557 (Dark blue-gray for readability)

### Typography
- **Headers**: Seg UI, Verdana (20-24px, bold)
- **Subheaders**: Seg UI, Verdana (14-18px, semi-bold)
- **Body/Data**: Seg UI, Courier New (11-13px, regular)
- **Numbers**: Courier New (11px, monospace for alignment)

### Visual Hierarchy
- **Level 1**: KPI Tile Cards (Large, prominent)
- **Level 2**: Main analysis charts (50% screen width minimum)
- **Level 3**: Supporting metrics and tables (25-35% width)
- **Level 4**: Details on demand (tooltips, drill-downs)

### Interactive Elements
- **Hover Effects**: Tooltip appears, relevant data highlighted
- **Click Actions**: 
  - Charts → Drill to next level
  - Segments/Filters → Cross-filter other visuals
  - Data rows → Detailed view modal
- **Animation**: Smooth transitions (200-300ms) on data load/filter change
- **Accessibility**: High contrast, keyboard navigation, alt text for images

---

## 🔧 Technical Implementation

### Data Refresh Schedule
- Executive dashboard: Real-time (every 15 minutes)
- Detailed dashboards: Hourly
- Forecasts: Weekly (every Sunday 02:00 UTC)
- Historical archives: Monthly

### Performance Targets
- Dashboard load time: < 2 seconds
- Visual interaction response: < 500ms
- Filter application: < 1 second
- Drill-down navigation: < 800ms

### Data Source Architecture
```
Raw Data Layer:
├── sales_data_cleaned.csv (10K+ records)

ETL Processing:
├── python/data_cleaning.py → Data validation & transformation
├── sql/advanced_queries.sql → Aggregations & business logic

BI Tool (Power BI/Tableau):
├── Imported tables (raw data)
├── Calculated tables (monthly agg, category agg)
├── DAX/LookupML formulas (derived metrics)
└── Dashboards (interactive views)
```

### Key Measures (DAX/LookupML)
```
Total Sales = SUM(Sales[Sales])
Total Profit = SUM(Sales[Profit])
Profit Margin % = [Total Profit] / [Total Sales]
YoY Growth % = ([Current Year Sales] - [Prior Year Sales]) / [Prior Year Sales]
Forecast Sales = [Prophet Forecast] or [ARIMA Forecast]
```

---

## 📱 Mobile Optimization

- **Responsive Design**: Adapts to 768px+ (tablets, 1024px+ laptops)
- **Touch-Friendly**: 40px+ tap targets
- **Mobile Pages**: Simplified versions with essential KPIs
- **Mobile Filters**: Collapsible sidebar, sticky filter bar
- **Mobile Charts**: Smaller multiples, one per line

---

## 🔐 Security & Governance

### Row-Level Security (RLS)
- Regional managers: See only their region's data
- Sales reps: See only their territory
- Finance: See all data with detailed breakdowns
- Executives: See regional aggregates

### Audit Logging
- Track dashboard access: User, Time, Actions
- Monitor data refreshes: Success/failure, duration
- Log modifications: Who changed what, when

---

## 📊 Success Metrics

### Adoption
- % of target users accessing dashboard monthly: Goal 80%+
- Average time spent in dashboard: 5-10 minutes
- Repeat usage frequency: 5+ times per week for executives

### Business Impact
- Decisions made faster: Reduce decision cycle from 3 days to <1 day
- Variance detection: Identify anomalies within 24 hours
- Forecast accuracy: MAPE <5% for next quarter
- Revenue optimization: Identify top-performing regions/products within 2 hours

---

## 📝 Maintenance & Support

### Updated Schedule
- Monthly: Add new KPIs/metrics based on business needs
- Quarterly: Major redesign review, UX improvements
- Annually: Comprehensive audit, new data sources

### Support Contact
- Business Analyst: [Contact]
- BI Developer: [Contact]
- Help Desk: [Phone/Email]

---

**Dashboard designed to provide 95%+ data literacy to all users regardless of technical background.**

