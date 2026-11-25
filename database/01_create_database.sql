CREATE DATABASE library_db;

USE library_db;

CREATE TABLE books (
    book_id VARCHAR(20) PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    author VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    isbn VARCHAR(30),
    publication_year INT,
    total_copies INT,
    available_copies INT,
    price DECIMAL(10,2)
);

CREATE TABLE members (
    member_id VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    membership_type VARCHAR(30),
    registration_date DATE,
    status VARCHAR(20)
);

CREATE TABLE borrowing (
    borrow_id VARCHAR(20) PRIMARY KEY,
    book_id VARCHAR(20),
    member_id VARCHAR(20),
    borrow_date DATE,
    due_date DATE,
    return_date DATE,
    status VARCHAR(20),
    FOREIGN KEY (book_id) REFERENCES books(book_id),
    FOREIGN KEY (member_id) REFERENCES members(member_id)
);

CREATE TABLE fines (
    fine_id VARCHAR(20) PRIMARY KEY,
    borrow_id VARCHAR(20),
    member_id VARCHAR(20),
    fine_amount DECIMAL(10,2),
    fine_date DATE,
    payment_status VARCHAR(20),
    payment_date DATE,
    FOREIGN KEY (borrow_id) REFERENCES borrowing(borrow_id),
    FOREIGN KEY (member_id) REFERENCES members(member_id)
);
