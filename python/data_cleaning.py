# Data cleaning script for Library Management System
import os
import pandas as pd

# Define paths for raw and processed datasets
RAW_DIR = os.path.join("dataset", "raw")
PROCESSED_DIR = os.path.join("dataset", "processed")

# Create processed directory if it does not exist
os.makedirs(PROCESSED_DIR, exist_ok=True)

# -------------------------------------------------------------
# 1. Load Datasets
# -------------------------------------------------------------
print("--- Loading Raw Datasets ---")
books_df = pd.read_csv(os.path.join(RAW_DIR, "books.csv"))
members_df = pd.read_csv(os.path.join(RAW_DIR, "members.csv"))
borrowing_df = pd.read_csv(os.path.join(RAW_DIR, "borrowing.csv"))
fines_df = pd.read_csv(os.path.join(RAW_DIR, "fines.csv"))

# Display first 5 records of each dataset
print("\nFirst 5 Books:")
print(books_df.head())

print("\nFirst 5 Members:")
print(members_df.head())

print("\nFirst 5 Borrowing Records:")
print(borrowing_df.head())

print("\nFirst 5 Fines:")
print(fines_df.head())

# -------------------------------------------------------------
# 2. Check Missing Values & Duplicates
# -------------------------------------------------------------
print("\n--- Checking Missing Values ---")
print("Books missing:\n", books_df.isnull().sum())
print("Members missing:\n", members_df.isnull().sum())
print("Borrowing missing:\n", borrowing_df.isnull().sum())
print("Fines missing:\n", fines_df.isnull().sum())

# Remove duplicate records if any exist
books_df = books_df.drop_duplicates()
members_df = members_df.drop_duplicates()
borrowing_df = borrowing_df.drop_duplicates()
fines_df = fines_df.drop_duplicates()

# -------------------------------------------------------------
# 3. Clean and Transform Data
# -------------------------------------------------------------
# Strip whitespace from text columns in books
text_columns_books = ["book_id", "title", "author", "category", "isbn"]
for col in text_columns_books:
    books_df[col] = books_df[col].astype(str).str.strip()

# Strip whitespace from text columns in members
text_columns_members = ["member_id", "first_name", "last_name", "email", "phone", "membership_type", "status"]
for col in text_columns_members:
    members_df[col] = members_df[col].astype(str).str.strip()

# Convert registration_date to datetime format in members
members_df["registration_date"] = pd.to_datetime(members_df["registration_date"]).dt.strftime("%Y-%m-%d")

# Convert date columns to standard format in borrowing
borrowing_df["borrow_date"] = pd.to_datetime(borrowing_df["borrow_date"]).dt.strftime("%Y-%m-%d")
borrowing_df["due_date"] = pd.to_datetime(borrowing_df["due_date"]).dt.strftime("%Y-%m-%d")
borrowing_df["return_date"] = pd.to_datetime(borrowing_df["return_date"]).dt.strftime("%Y-%m-%d")

# Convert date columns in fines
fines_df["fine_date"] = pd.to_datetime(fines_df["fine_date"]).dt.strftime("%Y-%m-%d")
# Handle missing payment_date for unpaid fines by filling with empty string
fines_df["payment_date"] = pd.to_datetime(fines_df["payment_date"]).dt.strftime("%Y-%m-%d").fillna("")

# Ensure numeric values are non-negative and properly rounded
books_df["price"] = books_df["price"].round(2)
fines_df["fine_amount"] = fines_df["fine_amount"].round(2)

# -------------------------------------------------------------
# 4. Save Cleaned Datasets
# -------------------------------------------------------------
books_df.to_csv(os.path.join(PROCESSED_DIR, "books_cleaned.csv"), index=False)
members_df.to_csv(os.path.join(PROCESSED_DIR, "members_cleaned.csv"), index=False)
borrowing_df.to_csv(os.path.join(PROCESSED_DIR, "borrowing_cleaned.csv"), index=False)
fines_df.to_csv(os.path.join(PROCESSED_DIR, "fines_cleaned.csv"), index=False)

print("\n--- Data Cleaning Complete ---")
print(f"Books cleaned: {len(books_df)} records")
print(f"Members cleaned: {len(members_df)} records")
print(f"Borrowing cleaned: {len(borrowing_df)} records")
print(f"Fines cleaned: {len(fines_df)} records")
