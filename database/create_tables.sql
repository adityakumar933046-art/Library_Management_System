-- SQL script to create library management system database and tables

-- Create database if it does not already exist
CREATE DATABASE IF NOT EXISTS library_db;
USE library_db;

-- Drop tables in reverse order of foreign key dependency
DROP TABLE IF EXISTS fines;
DROP TABLE IF EXISTS borrowing;
DROP TABLE IF EXISTS members;
DROP TABLE IF EXISTS books;

-- 1. Create Books table matching books.csv
CREATE TABLE books (
    book_id VARCHAR(10) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    isbn VARCHAR(20) NOT NULL,
    publication_year INT,
    total_copies INT DEFAULT 1,
    available_copies INT DEFAULT 1,
    price DECIMAL(6, 2) DEFAULT 0.00
);

-- 2. Create Members table matching members.csv
CREATE TABLE members (
    member_id VARCHAR(10) PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    membership_type VARCHAR(50),
    registration_date DATE,
    status VARCHAR(20) DEFAULT 'Active'
);

-- 3. Create Borrowing table matching borrowing.csv
CREATE TABLE borrowing (
    borrow_id VARCHAR(10) PRIMARY KEY,
    book_id VARCHAR(10),
    member_id VARCHAR(10),
    borrow_date DATE,
    due_date DATE,
    return_date DATE,
    status VARCHAR(20),
    FOREIGN KEY (book_id) REFERENCES books(book_id),
    FOREIGN KEY (member_id) REFERENCES members(member_id)
);

-- 4. Create Fines table matching fines.csv
CREATE TABLE fines (
    fine_id VARCHAR(10) PRIMARY KEY,
    borrow_id VARCHAR(10),
    member_id VARCHAR(10),
    fine_amount DECIMAL(6, 2) DEFAULT 0.00,
    fine_date DATE,
    payment_status VARCHAR(20),
    payment_date DATE NULL,
    FOREIGN KEY (borrow_id) REFERENCES borrowing(borrow_id),
    FOREIGN KEY (member_id) REFERENCES members(member_id)
);
