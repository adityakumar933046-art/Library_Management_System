-- =============================================================================
-- SQL Analysis Queries
-- Project: Library Management System Analysis Using SQL
-- =============================================================================

USE library_db;

-- =============================================================================
-- PART 1: BASIC ANALYSIS
-- =============================================================================
-- =============================================================================
-- Script 05: Basic SQL Analysis
-- Project: Library Management System Analysis Using SQL
-- Description: Core summary and descriptive statistics queries providing
--              immediate operational visibility into the library system.
-- =============================================================================

USE library_db;

-- -----------------------------------------------------------------------------
-- 1. Executive Summary KPI Snapshot
-- -----------------------------------------------------------------------------
SELECT 
    (SELECT COUNT(*) FROM books) AS total_unique_titles,
    (SELECT SUM(total_copies) FROM books) AS total_inventory_volume,
    (SELECT SUM(available_copies) FROM books) AS currently_available_books,
    (SELECT COUNT(*) FROM members WHERE status = 'Active') AS active_members,
    (SELECT COUNT(*) FROM borrowing) AS total_borrowing_transactions,
    (SELECT COUNT(*) FROM borrowing WHERE status IN ('Borrowed', 'Overdue')) AS active_rentals,
    (SELECT ROUND(SUM(fine_amount), 2) FROM fines) AS total_fines_levied,
    (SELECT ROUND(SUM(fine_amount), 2) FROM fines WHERE payment_status = 'Paid') AS total_fines_collected;

-- -----------------------------------------------------------------------------
-- 2. Top 10 Most Frequently Borrowed Books
-- -----------------------------------------------------------------------------
SELECT 
    bk.book_id,
    bk.title,
    bk.author,
    bk.category,
    COUNT(b.borrow_id) AS borrow_count
FROM books bk
JOIN borrowing b ON bk.book_id = b.book_id
GROUP BY bk.book_id, bk.title, bk.author, bk.category
ORDER BY borrow_count DESC
LIMIT 10;

-- -----------------------------------------------------------------------------
-- 3. Book Distribution and Catalog Breakdown by Category
-- -----------------------------------------------------------------------------
SELECT 
    category,
    COUNT(book_id) AS total_titles,
    SUM(total_copies) AS total_copies,
    SUM(available_copies) AS available_copies,
    ROUND(AVG(price), 2) AS average_price,
    ROUND(SUM(total_copies * price), 2) AS total_category_asset_value
FROM books
GROUP BY category
ORDER BY total_copies DESC;

-- -----------------------------------------------------------------------------
-- 4. Member Composition by Membership Tier and Status
-- -----------------------------------------------------------------------------
SELECT 
    membership_type,
    status,
    COUNT(member_id) AS member_count,
    ROUND(COUNT(member_id) * 100.0 / (SELECT COUNT(*) FROM members), 2) AS percentage_of_total
FROM members
GROUP BY membership_type, status
ORDER BY membership_type, status;

-- -----------------------------------------------------------------------------
-- 5. Borrowing Lifecycle Status Breakdown
-- -----------------------------------------------------------------------------
SELECT 
    status,
    COUNT(borrow_id) AS total_records,
    ROUND(COUNT(borrow_id) * 100.0 / (SELECT COUNT(*) FROM borrowing), 2) AS percentage
FROM borrowing
GROUP BY status;

-- -----------------------------------------------------------------------------
-- 6. Financial Overview: Fine Realization & Outstanding Penalties
-- -----------------------------------------------------------------------------
SELECT 
    payment_status,
    COUNT(fine_id) AS fine_records,
    ROUND(SUM(fine_amount), 2) AS total_amount,
    ROUND(AVG(fine_amount), 2) AS average_fine
FROM fines
GROUP BY payment_status
ORDER BY total_amount DESC;

-- -----------------------------------------------------------------------------
-- 7. Top 10 Most Active Patrons by Volume of Borrowings
-- -----------------------------------------------------------------------------
SELECT 
    m.member_id,
    CONCAT(m.first_name, ' ', m.last_name) AS member_name,
    m.membership_type,
    m.status AS account_status,
    COUNT(b.borrow_id) AS total_books_borrowed
FROM members m
JOIN borrowing b ON m.member_id = b.member_id
GROUP BY m.member_id, m.first_name, m.last_name, m.membership_type, m.status
ORDER BY total_books_borrowed DESC
LIMIT 10;

-- -----------------------------------------------------------------------------
-- 8. Current Active Loans (Borrowed or Overdue)
-- -----------------------------------------------------------------------------
SELECT 
    b.borrow_id,
    bk.title,
    CONCAT(m.first_name, ' ', m.last_name) AS member_name,
    b.borrow_date,
    b.due_date,
    b.status,
    DATEDIFF(CURRENT_DATE(), b.due_date) AS days_overdue
FROM borrowing b
JOIN books bk ON b.book_id = bk.book_id
JOIN members m ON b.member_id = m.member_id
WHERE b.status IN ('Borrowed', 'Overdue')
ORDER BY b.due_date ASC;


-- =============================================================================
-- PART 2: INTERMEDIATE ANALYSIS
-- =============================================================================
-- =============================================================================
-- Script 06: Intermediate SQL Analysis
-- Project: Library Management System Analysis Using SQL
-- Description: Aggregated business metrics, trend analysis, circulation rates,
--              overdue patterns, and ranking functions.
-- =============================================================================

USE library_db;

-- -----------------------------------------------------------------------------
-- 1. Monthly Borrowing Velocity and Seasonal Trends
-- -----------------------------------------------------------------------------
SELECT 
    DATE_FORMAT(borrow_date, '%Y-%m') AS year_month,
    YEAR(borrow_date) AS borrow_year,
    MONTHNAME(borrow_date) AS month_name,
    COUNT(borrow_id) AS total_borrowings,
    COUNT(DISTINCT member_id) AS unique_borrowers,
    COUNT(DISTINCT book_id) AS unique_titles_loaned,
    ROUND(COUNT(borrow_id) / COUNT(DISTINCT member_id), 2) AS loans_per_active_borrower
FROM borrowing
GROUP BY DATE_FORMAT(borrow_date, '%Y-%m'), YEAR(borrow_date), MONTHNAME(borrow_date)
ORDER BY year_month ASC;

-- -----------------------------------------------------------------------------
-- 2. Category Circulation Rate & Utilization
-- Circulation rate = total borrowings / total stock volume
-- -----------------------------------------------------------------------------
SELECT 
    bk.category,
    COUNT(b.borrow_id) AS total_loans,
    SUM(bk.total_copies) AS total_category_inventory,
    ROUND(COUNT(b.borrow_id) * 1.0 / NULLIF(SUM(bk.total_copies), 0), 2) AS inventory_turnover_ratio,
    ROUND(AVG(DATEDIFF(COALESCE(b.return_date, CURRENT_DATE()), b.borrow_date)), 1) AS avg_days_checked_out
FROM books bk
LEFT JOIN borrowing b ON bk.book_id = b.book_id
GROUP BY bk.category
ORDER BY total_loans DESC;

-- -----------------------------------------------------------------------------
-- 3. Overdue & Late Return Analysis by Membership Type
-- Identifies behavioral differences between Students, Faculty, and General members.
-- -----------------------------------------------------------------------------
SELECT 
    m.membership_type,
    COUNT(b.borrow_id) AS total_loans,
    SUM(CASE WHEN b.return_date > b.due_date THEN 1 ELSE 0 END) AS late_returns,
    ROUND(SUM(CASE WHEN b.return_date > b.due_date THEN 1 ELSE 0 END) * 100.0 / COUNT(b.borrow_id), 2) AS late_return_rate_pct,
    ROUND(AVG(CASE WHEN b.return_date > b.due_date THEN DATEDIFF(b.return_date, b.due_date) ELSE NULL END), 1) AS avg_days_overdue
FROM members m
JOIN borrowing b ON m.member_id = b.member_id
GROUP BY m.membership_type
ORDER BY late_return_rate_pct DESC;

-- -----------------------------------------------------------------------------
-- 4. Inactive Patron Identification (Zero-Borrow Members)
-- Identifies members who registered but have never checked out a single book.
-- -----------------------------------------------------------------------------
SELECT 
    m.member_id,
    CONCAT(m.first_name, ' ', m.last_name) AS member_name,
    m.email,
    m.membership_type,
    m.registration_date,
    m.status,
    DATEDIFF(CURRENT_DATE(), m.registration_date) AS days_since_registration
FROM members m
LEFT JOIN borrowing b ON m.member_id = b.member_id
WHERE b.borrow_id IS NULL
ORDER BY m.registration_date ASC;

-- -----------------------------------------------------------------------------
-- 5. Fine Settlement Velocity (Days to Pay)
-- Analyzes payment turnaround for members who have been fined.
-- -----------------------------------------------------------------------------
SELECT 
    m.membership_type,
    COUNT(f.fine_id) AS total_fines_issued,
    SUM(CASE WHEN f.payment_status = 'Paid' THEN 1 ELSE 0 END) AS total_fines_cleared,
    ROUND(SUM(CASE WHEN f.payment_status = 'Paid' THEN 1 ELSE 0 END) * 100.0 / COUNT(f.fine_id), 2) AS payment_compliance_pct,
    ROUND(AVG(CASE WHEN f.payment_status = 'Paid' THEN DATEDIFF(f.payment_date, f.fine_date) ELSE NULL END), 1) AS avg_days_to_pay,
    ROUND(SUM(f.fine_amount), 2) AS total_assessed_amount,
    ROUND(SUM(CASE WHEN f.payment_status = 'Paid' THEN f.fine_amount ELSE 0 END), 2) AS total_collected_amount
FROM fines f
JOIN members m ON f.member_id = m.member_id
GROUP BY m.membership_type
ORDER BY payment_compliance_pct DESC;

-- -----------------------------------------------------------------------------
-- 6. Top 3 Most Borrowed Books per Category (Window Functions)
-- Uses DENSE_RANK() to find leading titles within each category partition.
-- -----------------------------------------------------------------------------
WITH ranked_category_books AS (
    SELECT 
        bk.category,
        bk.book_id,
        bk.title,
        bk.author,
        COUNT(b.borrow_id) AS borrow_count,
        DENSE_RANK() OVER (
            PARTITION BY bk.category 
            ORDER BY COUNT(b.borrow_id) DESC
        ) AS rank_in_category
    FROM books bk
    LEFT JOIN borrowing b ON bk.book_id = b.book_id
    GROUP BY bk.category, bk.book_id, bk.title, bk.author
)
SELECT 
    category,
    rank_in_category,
    title,
    author,
    borrow_count
FROM ranked_category_books
WHERE rank_in_category <= 3
ORDER BY category, rank_in_category;

-- -----------------------------------------------------------------------------
-- 7. Author Popularity and Catalog Reach
-- Aggregates performance by author across their entire catalog.
-- -----------------------------------------------------------------------------
SELECT 
    bk.author,
    COUNT(DISTINCT bk.book_id) AS catalog_titles,
    COUNT(b.borrow_id) AS total_borrowings,
    ROUND(COUNT(b.borrow_id) * 1.0 / COUNT(DISTINCT bk.book_id), 2) AS avg_loans_per_title
FROM books bk
LEFT JOIN borrowing b ON bk.book_id = b.book_id
GROUP BY bk.author
ORDER BY total_borrowings DESC
LIMIT 15;


-- =============================================================================
-- PART 3: ADVANCED ANALYSIS
-- =============================================================================
-- =============================================================================
-- Script 07: Advanced SQL Analysis
-- Project: Library Management System Analysis Using SQL
-- Description: Advanced analytical queries utilizing window functions, Common
--              Table Expressions (CTEs), cumulative aggregations, member risk
--              segmentation, operational views, and stored procedures.
-- =============================================================================

USE library_db;

-- -----------------------------------------------------------------------------
-- 1. Month-over-Month (MoM) Borrowing Growth Rate
-- Uses LAG() window function to calculate growth rate compared to prior month.
-- -----------------------------------------------------------------------------
WITH monthly_volume AS (
    SELECT 
        DATE_FORMAT(borrow_date, '%Y-%m') AS period,
        COUNT(borrow_id) AS current_month_loans
    FROM borrowing
    GROUP BY DATE_FORMAT(borrow_date, '%Y-%m')
)
SELECT 
    period,
    current_month_loans,
    LAG(current_month_loans, 1) OVER (ORDER BY period) AS previous_month_loans,
    current_month_loans - LAG(current_month_loans, 1) OVER (ORDER BY period) AS net_growth_count,
    ROUND(
        (current_month_loans - LAG(current_month_loans, 1) OVER (ORDER BY period)) * 100.0 /
        NULLIF(LAG(current_month_loans, 1) OVER (ORDER BY period), 0),
        2
    ) AS mom_growth_pct
FROM monthly_volume
ORDER BY period;

-- -----------------------------------------------------------------------------
-- 2. Running Total of Financial Realization (Cumulative Fines)
-- Calculates cumulative revenue collection trajectory over calendar quarters.
-- -----------------------------------------------------------------------------
SELECT 
    DATE_FORMAT(fine_date, '%Y-%m') AS year_month,
    ROUND(SUM(fine_amount), 2) AS monthly_fines_assessed,
    ROUND(SUM(CASE WHEN payment_status = 'Paid' THEN fine_amount ELSE 0 END), 2) AS monthly_fines_collected,
    ROUND(SUM(SUM(fine_amount)) OVER (ORDER BY DATE_FORMAT(fine_date, '%Y-%m')), 2) AS cumulative_fines_assessed,
    ROUND(SUM(SUM(CASE WHEN payment_status = 'Paid' THEN fine_amount ELSE 0 END)) OVER (ORDER BY DATE_FORMAT(fine_date, '%Y-%m')), 2) AS cumulative_fines_collected
FROM fines
GROUP BY DATE_FORMAT(fine_date, '%Y-%m')
ORDER BY year_month;

-- -----------------------------------------------------------------------------
-- 3. Comprehensive Patron Delinquency & Risk Profiling Matrix
-- Segments members into risk tiers based on late returns and unpaid fines.
-- -----------------------------------------------------------------------------
WITH member_stats AS (
    SELECT 
        m.member_id,
        CONCAT(m.first_name, ' ', m.last_name) AS member_name,
        m.membership_type,
        m.status,
        COUNT(b.borrow_id) AS total_borrowed,
        SUM(CASE WHEN b.return_date > b.due_date OR b.status = 'Overdue' THEN 1 ELSE 0 END) AS total_delinquencies,
        COALESCE(SUM(f.fine_amount), 0.00) AS total_fines_assessed,
        COALESCE(SUM(CASE WHEN f.payment_status IN ('Unpaid', 'Pending') THEN f.fine_amount ELSE 0 END), 0.00) AS outstanding_balance
    FROM members m
    LEFT JOIN borrowing b ON m.member_id = b.member_id
    LEFT JOIN fines f ON b.borrow_id = f.borrow_id
    GROUP BY m.member_id, m.first_name, m.last_name, m.membership_type, m.status
)
SELECT 
    member_id,
    member_name,
    membership_type,
    status,
    total_borrowed,
    total_delinquencies,
    ROUND(total_delinquencies * 100.0 / NULLIF(total_borrowed, 0), 1) AS delinquency_rate_pct,
    total_fines_assessed,
    outstanding_balance,
    CASE 
        WHEN outstanding_balance > 30.00 OR (total_borrowed > 5 AND (total_delinquencies * 1.0 / total_borrowed) >= 0.5) THEN 'High Risk / Action Required'
        WHEN outstanding_balance > 0.00 OR total_delinquencies >= 2 THEN 'Moderate Risk / Follow-up'
        WHEN total_borrowed > 0 THEN 'Good Standing'
        ELSE 'Inactive Patron'
    END AS risk_tier
FROM member_stats
ORDER BY outstanding_balance DESC, total_delinquencies DESC;

-- -----------------------------------------------------------------------------
-- 4. Inventory Optimization: High Demand vs Underutilized Titles
-- Identifies titles where available stock is low relative to borrowing velocity.
-- -----------------------------------------------------------------------------
SELECT 
    bk.book_id,
    bk.title,
    bk.category,
    bk.total_copies,
    bk.available_copies,
    COUNT(b.borrow_id) AS lifetime_borrows,
    ROUND(COUNT(b.borrow_id) * 1.0 / bk.total_copies, 2) AS demand_per_copy_index,
    CASE 
        WHEN bk.available_copies = 0 THEN 'Stock Depleted - Procure Additional Copies'
        WHEN bk.available_copies <= 2 AND (COUNT(b.borrow_id) * 1.0 / bk.total_copies) > 3.0 THEN 'High Demand - Low Buffer'
        WHEN COUNT(b.borrow_id) = 0 THEN 'Zero Circulation - Review Placement'
        ELSE 'Adequately Stocked'
    END AS inventory_recommendation
FROM books bk
LEFT JOIN borrowing b ON bk.book_id = b.book_id
GROUP BY bk.book_id, bk.title, bk.category, bk.total_copies, bk.available_copies
ORDER BY demand_per_copy_index DESC;

-- -----------------------------------------------------------------------------
-- 5. Operational View: Active and Overdue Loans Dashboard
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_active_overdue_rentals AS
SELECT 
    b.borrow_id,
    b.borrow_date,
    b.due_date,
    b.status AS loan_status,
    bk.book_id,
    bk.title AS book_title,
    bk.category,
    m.member_id,
    CONCAT(m.first_name, ' ', m.last_name) AS borrower_name,
    m.email AS borrower_email,
    m.phone AS borrower_phone,
    DATEDIFF(CURRENT_DATE(), b.due_date) AS days_elapsed_past_due,
    CASE 
        WHEN CURRENT_DATE() > b.due_date THEN 'Overdue Action Needed'
        WHEN DATEDIFF(b.due_date, CURRENT_DATE()) <= 2 THEN 'Due Soon'
        ELSE 'Current'
    END AS urgency_level
FROM borrowing b
JOIN books bk ON b.book_id = bk.book_id
JOIN members m ON b.member_id = m.member_id
WHERE b.return_date IS NULL;

-- Query the operational view
SELECT * FROM vw_active_overdue_rentals ORDER BY days_elapsed_past_due DESC;

-- -----------------------------------------------------------------------------
-- 6. Stored Procedure: Patron 360-Degree Historical Report
-- -----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_member_borrowing_profile;

DELIMITER $$
CREATE PROCEDURE sp_member_borrowing_profile(IN p_member_id VARCHAR(10))
BEGIN
    -- 1. Patron Demographic and Account Summary
    SELECT 
        member_id,
        CONCAT(first_name, ' ', last_name) AS full_name,
        email,
        phone,
        membership_type,
        registration_date,
        status AS account_status
    FROM members
    WHERE member_id = p_member_id;

    -- 2. Borrowing Activity Record
    SELECT 
        b.borrow_id,
        bk.title AS book_title,
        bk.category,
        b.borrow_date,
        b.due_date,
        b.return_date,
        b.status,
        CASE 
            WHEN b.return_date IS NOT NULL AND b.return_date > b.due_date THEN DATEDIFF(b.return_date, b.due_date)
            WHEN b.return_date IS NULL AND CURRENT_DATE() > b.due_date THEN DATEDIFF(CURRENT_DATE(), b.due_date)
            ELSE 0 
        END AS days_overdue
    FROM borrowing b
    JOIN books bk ON b.book_id = bk.book_id
    WHERE b.member_id = p_member_id
    ORDER BY b.borrow_date DESC;

    -- 3. Fine & Penalty Ledger
    SELECT 
        fine_id,
        borrow_id,
        fine_amount,
        fine_date,
        payment_status,
        payment_date
    FROM fines
    WHERE member_id = p_member_id
    ORDER BY fine_date DESC;
END$$
DELIMITER ;

-- Test stored procedure for Member M101
-- CALL sp_member_borrowing_profile('M101');

