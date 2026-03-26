-- ============================================================================
-- ADVANCED SQL ANALYSIS QUERIES
-- ============================================================================
-- Production-ready queries for BI analysis using window functions, CTEs, and
-- complex aggregations

-- ============================================================================
-- 1. REVENUE ANALYSIS BY GEOGRAPHY
-- ============================================================================
-- Query 1.1: Revenue by Region with rankings
WITH regional_performance AS (
    SELECT
        Region,
        SUM(Sales) as total_sales,
        SUM(Profit) as total_profit,
        COUNT(DISTINCT Order_ID) as order_count,
        COUNT(DISTINCT Customer_Segment) as segment_count,
        ROUND(SUM(Profit) / SUM(Sales) * 100, 2) as profit_margin_pct,
        RANK() OVER (ORDER BY SUM(Sales) DESC) as sales_rank,
        ROUND(SUM(Sales) / SUM(SUM(Sales)) OVER () * 100, 2) as sales_contribution_pct
    FROM sales_cleaned
    GROUP BY Region
)
SELECT
    Region,
    total_sales,
    total_profit,
    order_count,
    profit_margin_pct,
    sales_rank,
    sales_contribution_pct,
    CASE
        WHEN sales_rank = 1 THEN 'Top Performer'
        WHEN sales_rank <= 2 THEN 'Strong Performer'
        ELSE 'Needs Development'
    END as performance_tier
FROM regional_performance
ORDER BY sales_rank;

-- Query 1.2: State-level performance with YoY comparison
WITH state_yearly_sales AS (
    SELECT
        State,
        Region,
        Year,
        SUM(Sales) as yearly_sales,
        SUM(Profit) as yearly_profit,
        COUNT(DISTINCT Order_ID) as yearly_orders,
        LAG(SUM(Sales)) OVER (PARTITION BY State ORDER BY Year) as prev_year_sales,
        ROUND(
            ((SUM(Sales) - LAG(SUM(Sales)) OVER (PARTITION BY State ORDER BY Year)) 
             / LAG(SUM(Sales)) OVER (PARTITION BY State ORDER BY Year) * 100), 2
        ) as yoy_growth_pct
    FROM sales_cleaned
    GROUP BY State, Region, Year
)
SELECT
    State,
    Region,
    Year,
    yearly_sales,
    yearly_profit,
    yearly_orders,
    yoy_growth_pct,
    CASE
        WHEN yoy_growth_pct > 20 THEN 'High Growth'
        WHEN yoy_growth_pct > 0 THEN 'Positive Growth'
        WHEN yoy_growth_pct > -10 THEN 'Slight Decline'
        ELSE 'Significant Decline'
    END as growth_category
FROM state_yearly_sales
WHERE Year IS NOT NULL
ORDER BY Region, State, Year DESC;

-- ============================================================================
-- 2. PRODUCT ANALYSIS
-- ============================================================================
-- Query 2.1: Top 5 Products by Profit with detailed metrics
WITH product_ranked AS (
    SELECT
        Product_Name,
        Product_Category,
        Sub_Category,
        SUM(Sales) as total_sales,
        SUM(Profit) as total_profit,
        COUNT(Order_ID) as units_sold,
        ROUND(AVG(Profit_Margin_Percentage), 2) as avg_margin_pct,
        ROUND(SUM(Sales) / COUNT(Order_ID), 2) as avg_sale_value,
        RANK() OVER (ORDER BY SUM(Profit) DESC) as profit_rank,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY Profit) OVER () as median_profit
    FROM sales_cleaned
    GROUP BY Product_Name, Product_Category, Sub_Category
)
SELECT
    profit_rank,
    Product_Name,
    Product_Category,
    Sub_Category,
    total_sales,
    total_profit,
    units_sold,
    avg_margin_pct,
    avg_sale_value,
    ROUND(total_profit / median_profit, 2) as profit_vs_median_ratio
FROM product_ranked
WHERE profit_rank <= 5
ORDER BY profit_rank;

-- Query 2.2: Bottom 5 underperforming products
WITH bottom_products AS (
    SELECT
        Product_Name,
        Product_Category,
        SUM(Sales) as total_sales,
        SUM(Profit) as total_profit,
        ROUND(SUM(Profit) / SUM(Sales) * 100, 2) as margin_pct,
        COUNT(Order_ID) as times_sold,
        ROW_NUMBER() OVER (ORDER BY SUM(Profit) ASC) as row_num
    FROM sales_cleaned
    GROUP BY Product_Name, Product_Category
    HAVING COUNT(Order_ID) > 5  -- Only products sold more than 5 times
)
SELECT
    Product_Name,
    Product_Category,
    total_sales,
    total_profit,
    margin_pct,
    times_sold,
    'Recommendation: ' ||
        CASE
            WHEN margin_pct < 5 THEN 'Review pricing or discontinue'
            WHEN margin_pct < 10 THEN 'Reduce costs or increase price'
            ELSE 'Monitor closely'
        END as action_item
FROM bottom_products
WHERE row_num <= 5
ORDER BY row_num;

-- Query 2.3: Product performance by category with running totals
WITH category_performance AS (
    SELECT
        Product_Category,
        Sub_Category,
        SUM(Sales) as category_sales,
        SUM(Profit) as category_profit,
        COUNT(DISTINCT Order_ID) as category_orders,
        SUM(SUM(Sales)) OVER (
            PARTITION BY Product_Category ORDER BY SUM(Profit) DESC
        ) as running_total_sales_in_category,
        ROUND(
            100.0 * SUM(SUM(Sales)) OVER (
                PARTITION BY Product_Category ORDER BY SUM(Profit) DESC
            ) / SUM(SUM(Sales)) OVER (PARTITION BY Product_Category),
            2
        ) as cumulative_pct_of_category
    FROM sales_cleaned
    GROUP BY Product_Category, Sub_Category
)
SELECT
    Product_Category,
    Sub_Category,
    category_sales,
    category_profit,
    category_orders,
    cumulative_pct_of_category,
    CASE
        WHEN cumulative_pct_of_category <= 50 THEN 'Core Products'
        WHEN cumulative_pct_of_category <= 80 THEN 'Secondary Products'
        ELSE 'Niche Products'
    END as product_tier
FROM category_performance
ORDER BY Product_Category, cumulative_pct_of_category;

-- ============================================================================
-- 3. TEMPORAL ANALYSIS: GROWTH RATES
-- ============================================================================
-- Query 3.1: Month-over-Month growth rates
WITH monthly_sales AS (
    SELECT
        Year_Month,
        Year,
        Month,
        SUM(Sales) as monthly_sales,
        SUM(Profit) as monthly_profit,
        COUNT(DISTINCT Order_ID) as monthly_orders,
        LAG(SUM(Sales)) OVER (ORDER BY Year, Month) as prev_month_sales,
        LAG(SUM(Profit)) OVER (ORDER BY Year, Month) as prev_month_profit
    FROM sales_cleaned
    GROUP BY Year_Month, Year, Month
)
SELECT
    Year_Month,
    monthly_sales,
    monthly_profit,
    monthly_orders,
    ROUND(
        ((monthly_sales - prev_month_sales) / prev_month_sales * 100), 2
    ) as mom_sales_growth_pct,
    ROUND(
        ((monthly_profit - prev_month_profit) / prev_month_profit * 100), 2
    ) as mom_profit_growth_pct,
    CASE
        WHEN ((monthly_sales - prev_month_sales) / prev_month_sales * 100) >= 10 THEN 'Strong Growth'
        WHEN ((monthly_sales - prev_month_sales) / prev_month_sales * 100) >= 0 THEN 'Positive Growth'
        ELSE 'Decline'
    END as growth_status
FROM monthly_sales
WHERE prev_month_sales IS NOT NULL
ORDER BY Year DESC, Month DESC;

-- Query 3.2: Quarterly trend analysis
WITH quarterly_trends AS (
    SELECT
        Year,
        Quarter,
        Region,
        SUM(Sales) as quarterly_sales,
        SUM(Profit) as quarterly_profit,
        COUNT(DISTINCT Order_ID) as quarterly_orders,
        ROUND(AVG(Profit_Margin_Percentage), 2) as avg_margin,
        ROW_NUMBER() OVER (
            PARTITION BY Region ORDER BY Year, Quarter
        ) as quarter_sequence
    FROM sales_cleaned
    GROUP BY Year, Quarter, Region
)
SELECT
    Year,
    Quarter,
    Region,
    quarterly_sales,
    quarterly_profit,
    quarterly_orders,
    avg_margin,
    LAG(quarterly_sales) OVER (
        PARTITION BY Region ORDER BY Year, Quarter
    ) as prev_quarter_sales,
    ROUND(
        ((quarterly_sales - LAG(quarterly_sales) OVER (PARTITION BY Region ORDER BY Year, Quarter)) 
         / LAG(quarterly_sales) OVER (PARTITION BY Region ORDER BY Year, Quarter) * 100), 2
    ) as qoq_growth_pct
FROM quarterly_trends
ORDER BY Region, Year DESC, Quarter DESC;

-- ============================================================================
-- 4. CUSTOMER SEGMENT ANALYSIS
-- ============================================================================
-- Query 4.1: Segment profitability and contribution
WITH segment_analytics AS (
    SELECT
        Customer_Segment,
        COUNT(DISTINCT Order_ID) as total_orders,
        COUNT(DISTINCT CASE WHEN Year = EXTRACT(YEAR FROM CURRENT_DATE) THEN Order_ID END) as ytd_orders,
        SUM(Sales) as total_sales,
        SUM(Profit) as total_profit,
        AVG(Sales) as avg_order_value,
        AVG(Profit_Margin_Percentage) as avg_margin_pct,
        MAX(Sales) as largest_order,
        MIN(Sales) as smallest_order,
        ROUND(SUM(Sales) / SUM(SUM(Sales)) OVER () * 100, 2) as sales_share_pct,
        ROUND(SUM(Profit) / SUM(SUM(Profit)) OVER () * 100, 2) as profit_share_pct
    FROM sales_cleaned
    GROUP BY Customer_Segment
)
SELECT
    Customer_Segment,
    total_orders,
    ytd_orders,
    ROUND(total_sales, 2) as total_sales,
    ROUND(total_profit, 2) as total_profit,
    ROUND(avg_order_value, 2) as avg_order_value,
    ROUND(avg_margin_pct, 2) as avg_margin_pct,
    sales_share_pct,
    profit_share_pct,
    CASE
        WHEN profit_share_pct >= 40 THEN 'Strategic Priority'
        WHEN profit_share_pct >= 25 THEN 'Important'
        ELSE 'Monitor'
    END as segment_priority
FROM segment_analytics
ORDER BY profit_share_pct DESC;

-- ============================================================================
-- 5. ADVANCED WINDOW FUNCTION ANALYSIS
-- ============================================================================
-- Query 5.1: Running totals and percentile ranks
WITH sales_with_percentiles AS (
    SELECT
        Order_ID,
        Order_Date,
        Month,
        Year,
        Product_Category,
        Sales,
        Profit,
        ROUND(
            100 * PERCENT_RANK() OVER (
                PARTITION BY Month, Year ORDER BY Profit
            ), 2
        ) as profit_percentile,
        SUM(Sales) OVER (
            PARTITION BY Month, Year ORDER BY Order_Date
        ) as running_monthly_sales,
        DENSE_RANK() OVER (
            PARTITION BY Product_Category ORDER BY Profit DESC
        ) as category_profit_rank,
        ROUND(
            100 * SUM(Profit) OVER (
                PARTITION BY Product_Category ORDER BY Order_Date
            ) / SUM(Profit) OVER (PARTITION BY Product_Category),
            2
        ) as cumulative_profit_contribution_pct
    FROM sales_cleaned
)
SELECT
    Year,
    Month,
    Product_Category,
    COUNT(*) as transaction_count,
    ROUND(AVG(profit_percentile), 2) as avg_profit_percentile,
    ROUND(AVG(running_monthly_sales), 2) as avg_running_monthly_sales,
    MAX(cumulative_profit_contribution_pct) as max_cumulative_contribution
FROM sales_with_percentiles
GROUP BY Year, Month, Product_Category
ORDER BY Year DESC, Month DESC, Product_Category;

-- Query 5.2: Identify sales outliers using quantiles
WITH sales_quartiles AS (
    SELECT
        Order_ID,
        Order_Date,
        Sales,
        Profit,
        QUARTILE(Profit) OVER () as profit_quartile,
        ROUND(
            (Profit - AVG(Profit) OVER ()) / STDDEV(Profit) OVER (), 2
        ) as profit_z_score
    FROM sales_cleaned
)
SELECT
    'Q1 (Bottom 25%)' as quartile_label,
    COUNT(*) as transaction_count,
    ROUND(AVG(Sales), 2) as avg_sales,
    ROUND(AVG(Profit), 2) as avg_profit
FROM sales_quartiles
WHERE profit_quartile = 1
UNION ALL
SELECT
    'Q2' as quartile_label,
    COUNT(*) as transaction_count,
    ROUND(AVG(Sales), 2) as avg_sales,
    ROUND(AVG(Profit), 2) as avg_profit
FROM sales_quartiles
WHERE profit_quartile = 2
UNION ALL
SELECT
    'Q3' as quartile_label,
    COUNT(*) as transaction_count,
    ROUND(AVG(Sales), 2) as avg_sales,
    ROUND(AVG(Profit), 2) as avg_profit
FROM sales_quartiles
WHERE profit_quartile = 3
UNION ALL
SELECT
    'Q4 (Top 25%)' as quartile_label,
    COUNT(*) as transaction_count,
    ROUND(AVG(Sales), 2) as avg_sales,
    ROUND(AVG(Profit), 2) as avg_profit
FROM sales_quartiles
WHERE profit_quartile = 4
ORDER BY CASE quartile_label
    WHEN 'Q1 (Bottom 25%)' THEN 1
    WHEN 'Q2' THEN 2
    WHEN 'Q3' THEN 3
    WHEN 'Q4 (Top 25%)' THEN 4
END;

-- ============================================================================
-- EXECUTIVE SUMMARY QUERY
-- ============================================================================
SELECT
    'Total Revenue' as KPI,
    TO_CHAR(SUM(Sales), '$999,999,999.99') as value
FROM sales_cleaned
UNION ALL
SELECT
    'Total Profit' as KPI,
    TO_CHAR(SUM(Profit), '$999,999,999.99') as value
FROM sales_cleaned
UNION ALL
SELECT
    'Overall Profit Margin' as KPI,
    ROUND(SUM(Profit) / SUM(Sales) * 100, 2)::VARCHAR || '%' as value
FROM sales_cleaned
UNION ALL
SELECT
    'Average Order Value' as KPI,
    TO_CHAR(AVG(Sales), '$999,999.99') as value
FROM sales_cleaned
UNION ALL
SELECT
    'Total Orders' as KPI,
    COUNT(DISTINCT Order_ID)::VARCHAR as value
FROM sales_cleaned
UNION ALL
SELECT
    'Total Units Sold' as KPI,
    SUM(Quantity)::VARCHAR as value
FROM sales_cleaned;
