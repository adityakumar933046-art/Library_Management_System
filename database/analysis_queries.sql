-- 10 SQL Analysis Queries for Library Management System
USE library_db;

-- Query 1: Total Books (count of distinct book titles and total book copies)
SELECT 
    COUNT(book_id) AS total_book_titles,
    SUM(total_copies) AS total_book_copies
FROM books;

-- Query 2: Total Members (total registered members and active members)
SELECT 
    COUNT(member_id) AS total_members,
    SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) AS active_members
FROM members;

-- Query 3: Most Borrowed Books (top 5 books by borrow frequency)
SELECT 
    b.book_id,
    b.title,
    b.author,
    COUNT(br.borrow_id) AS borrow_count
FROM books b
JOIN borrowing br ON b.book_id = br.book_id
GROUP BY b.book_id, b.title, b.author
ORDER BY borrow_count DESC
LIMIT 5;

-- Query 4: Most Active Members (top 5 members by number of books borrowed)
SELECT 
    m.member_id,
    m.first_name,
    m.last_name,
    COUNT(br.borrow_id) AS total_borrowed
FROM members m
JOIN borrowing br ON m.member_id = br.member_id
GROUP BY m.member_id, m.first_name, m.last_name
ORDER BY total_borrowed DESC
LIMIT 5;

-- Query 5: Popular Categories (total borrowings grouped by book category)
SELECT 
    b.category,
    COUNT(br.borrow_id) AS total_borrowed
FROM books b
JOIN borrowing br ON b.book_id = br.book_id
GROUP BY b.category
ORDER BY total_borrowed DESC;

-- Query 6: Monthly Borrowing Trends (borrowing count by year and month)
SELECT 
    DATE_FORMAT(borrow_date, '%Y-%m') AS borrow_month,
    COUNT(borrow_id) AS total_borrowings
FROM borrowing
GROUP BY DATE_FORMAT(borrow_date, '%Y-%m')
ORDER BY borrow_month;

-- Query 7: Overdue Books (records where return date exceeds due date)
SELECT 
    br.borrow_id,
    b.title,
    m.first_name,
    m.last_name,
    br.borrow_date,
    br.due_date,
    br.return_date
FROM borrowing br
JOIN books b ON br.book_id = b.book_id
JOIN members m ON br.member_id = m.member_id
WHERE br.return_date > br.due_date;

-- Query 8: Total Fine Collection (total fine amount levied vs paid)
SELECT 
    payment_status,
    COUNT(fine_id) AS total_records,
    SUM(fine_amount) AS total_amount
FROM fines
GROUP BY payment_status;

-- Query 9: Department-wise Borrowing (Note: dataset uses membership_type instead of department)
SELECT 
    m.membership_type,
    COUNT(br.borrow_id) AS total_borrowed
FROM members m
JOIN borrowing br ON m.member_id = br.member_id
GROUP BY m.membership_type
ORDER BY total_borrowed DESC;

-- Query 10: Books Never Borrowed (books with no matching record in borrowing table)
SELECT 
    b.book_id,
    b.title,
    b.author,
    b.category
FROM books b
LEFT JOIN borrowing br ON b.book_id = br.book_id
WHERE br.borrow_id IS NULL;
