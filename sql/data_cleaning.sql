-- ============================================================================
-- DATA CLEANING QUERIES
-- ============================================================================
-- These queries demonstrate production-ready SQL practices for data cleaning
-- and preparation for business intelligence analysis

-- ============================================================================
-- 1. CREATE MAIN SALES TABLE WITH DATA TYPES
-- ============================================================================
CREATE TABLE sales (
    Order_ID VARCHAR(20) PRIMARY KEY NOT NULL,
    Order_Date DATE NOT NULL,
    Ship_Date DATE NOT NULL,
    Region VARCHAR(50) NOT NULL,
    State VARCHAR(10) NOT NULL,
    City VARCHAR(50),
    Product_Category VARCHAR(100) NOT NULL,
    Sub_Category VARCHAR(100),
    Product_Name VARCHAR(200) NOT NULL,
    Sales DECIMAL(10, 2) NOT NULL,
    Quantity INT NOT NULL,
    Discount DECIMAL(5, 2),
    Profit DECIMAL(10, 2) NOT NULL,
    Customer_Segment VARCHAR(50) NOT NULL,
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 2. IDENTIFY AND REMOVE DUPLICATES
-- ============================================================================
-- Query 1.1: Find duplicate records
SELECT 
    Order_ID, 
    Order_Date, 
    Sales, 
    COUNT(*) as duplicate_count
FROM sales
GROUP BY Order_ID, Order_Date, Sales
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;

-- Query 1.2: Remove duplicates (keeping first occurrence)
DELETE FROM sales
WHERE Order_ID IN (
    SELECT Order_ID
    FROM (
        SELECT 
            Order_ID,
            ROW_NUMBER() OVER(PARTITION BY Order_ID, Order_Date, Sales ORDER BY CreatedAt) as rn
        FROM sales
    ) duplicates
    WHERE rn > 1
);

-- ============================================================================
-- 3. HANDLE MISSING VALUES
-- ============================================================================
-- Query 2.1: Identify missing values
SELECT
    'City' as column_name,
    COUNT(*) - COUNT(City) as missing_count,
    ROUND(100.0 * (COUNT(*) - COUNT(City)) / COUNT(*), 2) as missing_percentage
FROM sales
UNION ALL
SELECT
    'Sub_Category' as column_name,
    COUNT(*) - COUNT(Sub_Category) as missing_count,
    ROUND(100.0 * (COUNT(*) - COUNT(Sub_Category)) / COUNT(*), 2) as missing_percentage
FROM sales
UNION ALL
SELECT
    'Discount' as column_name,
    COUNT(*) - COUNT(Discount) as missing_count,
    ROUND(100.0 * (COUNT(*) - COUNT(Discount)) / COUNT(*), 2) as missing_percentage
FROM sales;

-- Query 2.2: Fill missing City values with state default or 'Unknown'
UPDATE sales
SET City = COALESCE(City, 'Unknown - ' || State)
WHERE City IS NULL;

-- Query 2.3: Fill missing Sub_Category with Product_Category
UPDATE sales
SET Sub_Category = COALESCE(Sub_Category, Product_Category)
WHERE Sub_Category IS NULL;

-- Query 2.4: Fill missing Discount with median discount (default 0)
UPDATE sales
SET Discount = COALESCE(Discount, 0)
WHERE Discount IS NULL;

-- ============================================================================
-- 4. VALIDATE DATA QUALITY
-- ============================================================================
-- Query 3.1: Validate data ranges and business rules
SELECT
    'Invalid quantity (< 1)' as validation_rule,
    COUNT(*) as issue_count
FROM sales
WHERE Quantity < 1
UNION ALL
SELECT
    'Discount > 50%' as validation_rule,
    COUNT(*) as issue_count
FROM sales
WHERE Discount > 0.50
UNION ALL
SELECT
    'Profit > Sales' as validation_rule,
    COUNT(*) as issue_count
FROM sales
WHERE Profit > Sales
UNION ALL
SELECT
    'Ship date before order date' as validation_rule,
    COUNT(*) as issue_count
FROM sales
WHERE Ship_Date < Order_Date;

-- Query 3.2: Validate date formats and consistency
SELECT
    COUNT(*) as total_records,
    COUNT(DISTINCT DATE(Order_Date)) as distinct_order_dates,
    MIN(DATE(Order_Date)) as earliest_order,
    MAX(DATE(Order_Date)) as latest_order,
    DATEDIFF(day, MIN(DATE(Order_Date)), MAX(DATE(Order_Date))) as days_span
FROM sales;

-- ============================================================================
-- 5. CREATE DERIVED COLUMNS
-- ============================================================================
-- Query 4.1: Create enhanced sales table with derived metrics
CREATE TABLE sales_cleaned AS
SELECT
    Order_ID,
    Order_Date,
    Ship_Date,
    EXTRACT(MONTH FROM Order_Date)::INT as Month,
    EXTRACT(YEAR FROM Order_Date)::INT as Year,
    TO_CHAR(Order_Date, 'YYYY-MM') as Year_Month,
    EXTRACT(QUARTER FROM Order_Date)::INT as Quarter,
    Region,
    State,
    City,
    Product_Category,
    Sub_Category,
    Product_Name,
    Sales,
    Quantity,
    Discount,
    Profit,
    ROUND(Profit / Sales * 100, 2) as Profit_Margin_Percentage,
    ROUND(Sales - Quantity * 
        (SELECT AVG(Sales / Quantity) FROM sales), 2) as Revenue_Above_Avg,
    Customer_Segment,
    CASE 
        WHEN Profit > Sales * 0.30 THEN 'High Margin'
        WHEN Profit > Sales * 0.15 THEN 'Medium Margin'
        ELSE 'Low Margin'
    END as Margin_Category,
    CASE
        WHEN Sales > 2000 THEN 'Enterprise'
        WHEN Sales > 500 THEN 'Mid-Market'
        ELSE 'SMB'
    END as Customer_Size_Segment
FROM sales;

-- ============================================================================
-- 6. AGGREGATE TABLES FOR PERFORMANCE
-- ============================================================================
-- Query 4.2: Create monthly summary for rapid dashboard queries
CREATE TABLE sales_monthly_summary AS
SELECT
    Year_Month,
    Year,
    Month,
    Region,
    Product_Category,
    COUNT(Order_ID) as order_count,
    SUM(Sales) as total_sales,
    SUM(Profit) as total_profit,
    ROUND(AVG(Profit_Margin_Percentage), 2) as avg_profit_margin,
    SUM(Quantity) as total_units_sold,
    ROUND(SUM(Sales) / COUNT(Order_ID), 2) as avg_order_value
FROM sales_cleaned
GROUP BY Year_Month, Year, Month, Region, Product_Category;

-- Query 4.3: Create product performance summary
CREATE TABLE product_performance_summary AS
SELECT
    Product_Name,
    Product_Category,
    Sub_Category,
    COUNT(Order_ID) as times_sold,
    SUM(Sales) as total_revenue,
    SUM(Profit) as total_profit,
    ROUND(AVG(Profit_Margin_Percentage), 2) as avg_profit_margin,
    ROUND(AVG(Discount), 4) as avg_discount_rate,
    MAX(Sales) as highest_sale,
    MIN(Sales) as lowest_sale
FROM sales_cleaned
GROUP BY Product_Name, Product_Category, Sub_Category
ORDER BY total_revenue DESC;

-- ============================================================================
-- Final Data Quality Report
-- ============================================================================
SELECT
    'Cleaned Records' as metric,
    COUNT(*) as value
FROM sales_cleaned
UNION ALL
SELECT
    'Date Range (Years)' as metric,
    EXTRACT(YEAR FROM MAX(Order_Date))::VARCHAR - EXTRACT(YEAR FROM MIN(Order_Date))::VARCHAR as value
FROM sales_cleaned
UNION ALL
SELECT
    'Regions' as metric,
    COUNT(DISTINCT Region)::VARCHAR as value
FROM sales_cleaned
UNION ALL
SELECT
    'Products' as metric,
    COUNT(DISTINCT Product_Name)::VARCHAR as value
FROM sales_cleaned
UNION ALL
SELECT
    'Customer Segments' as metric,
    COUNT(DISTINCT Customer_Segment)::VARCHAR as value
FROM sales_cleaned;
