"""
=============================================================================
Data Cleaning Pipeline
Project: Library Management System Analysis Using SQL
Script: python/data_cleaning.py
Description: Ingests raw library datasets, handles data types, removes whitespace,
             validates relational constraints, engineers analytical features,
             and outputs cleaned datasets to dataset/processed/.
=============================================================================
"""

import os
import sys
import pandas as pd
import numpy as np


def get_project_paths():
    """Resolves base directory and data paths relative to script location."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    raw_dir = os.path.join(base_dir, "dataset", "raw")
    proc_dir = os.path.join(base_dir, "dataset", "processed")
    return base_dir, raw_dir, proc_dir


def clean_books(raw_dir, proc_dir):
    """Loads, cleans, and standardizes books dataset."""
    file_path = os.path.join(raw_dir, "books.csv")
    print(f"[+] Processing books: {file_path}")
    df = pd.read_csv(file_path, dtype={"book_id": str, "isbn": str})

    # 1. Clean string fields
    string_cols = ["book_id", "title", "author", "category", "isbn"]
    for col in string_cols:
        df[col] = df[col].astype(str).str.strip()

    # 2. Type conversions and numeric validations
    df["publication_year"] = pd.to_numeric(df["publication_year"], errors="coerce").fillna(0).astype(int)
    df["total_copies"] = pd.to_numeric(df["total_copies"], errors="coerce").fillna(1).astype(int)
    df["available_copies"] = pd.to_numeric(df["available_copies"], errors="coerce").fillna(1).astype(int)
    df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0.0).round(2)

    # 3. Constraint sanity checks
    df["total_copies"] = df["total_copies"].clip(lower=0)
    df["available_copies"] = np.minimum(df["available_copies"].clip(lower=0), df["total_copies"])

    # 4. Feature engineering: total asset inventory value
    df["inventory_value"] = (df["total_copies"] * df["price"]).round(2)

    # 5. Deduplicate
    df = df.drop_duplicates(subset=["book_id"])

    out_path = os.path.join(proc_dir, "books_cleaned.csv")
    df.to_csv(out_path, index=False)
    print(f"    Saved cleaned books: {out_path} ({len(df)} records)")
    return df


def clean_members(raw_dir, proc_dir):
    """Loads, cleans, and standardizes members dataset."""
    file_path = os.path.join(raw_dir, "members.csv")
    print(f"[+] Processing members: {file_path}")
    df = pd.read_csv(file_path, dtype={"member_id": str})

    # 1. String formatting & cleanup
    str_cols = ["member_id", "first_name", "last_name", "email", "phone", "membership_type", "status"]
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip()

    df["first_name"] = df["first_name"].str.title()
    df["last_name"] = df["last_name"].str.title()
    df["full_name"] = df["first_name"] + " " + df["last_name"]
    df["email"] = df["email"].str.lower()

    # 2. Date parsing
    df["registration_date"] = pd.to_datetime(df["registration_date"], errors="coerce").dt.strftime("%Y-%m-%d")

    # 3. Categorical validation
    valid_types = ["Student", "Faculty", "General", "Premium"]
    df["membership_type"] = df["membership_type"].apply(lambda x: x if x in valid_types else "General")
    valid_statuses = ["Active", "Inactive", "Suspended"]
    df["status"] = df["status"].apply(lambda x: x if x in valid_statuses else "Active")

    # 4. Deduplicate
    df = df.drop_duplicates(subset=["member_id"])

    out_path = os.path.join(proc_dir, "members_cleaned.csv")
    df.to_csv(out_path, index=False)
    print(f"    Saved cleaned members: {out_path} ({len(df)} records)")
    return df


def clean_borrowing(raw_dir, proc_dir):
    """Loads, cleans, and standardizes borrowing transaction logs."""
    file_path = os.path.join(raw_dir, "borrowing.csv")
    print(f"[+] Processing borrowing records: {file_path}")
    df = pd.read_csv(file_path, dtype={"borrow_id": str, "book_id": str, "member_id": str}, keep_default_na=False)

    # 1. Strip string identifiers
    for col in ["borrow_id", "book_id", "member_id", "status"]:
        df[col] = df[col].astype(str).str.strip()

    # 2. Date parsing
    borrow_dt = pd.to_datetime(df["borrow_date"], errors="coerce")
    due_dt = pd.to_datetime(df["due_date"], errors="coerce")
    return_dt = pd.to_datetime(df["return_date"].replace("", np.nan), errors="coerce")

    df["borrow_date"] = borrow_dt.dt.strftime("%Y-%m-%d")
    df["due_date"] = due_dt.dt.strftime("%Y-%m-%d")
    df["return_date"] = return_dt.dt.strftime("%Y-%m-%d").fillna("")

    # 3. Feature engineering
    # Calculate days held: between return_date (or today if not returned) and borrow_date
    effective_end = return_dt.fillna(pd.Timestamp.now())
    df["borrow_duration_days"] = (effective_end - borrow_dt).dt.days.clip(lower=0)

    # Days overdue calculation: if returned late, return_date - due_date; if not returned and past due, now - due_date
    days_overdue = (effective_end - due_dt).dt.days
    df["days_overdue"] = days_overdue.apply(lambda x: max(0, x))
    df["is_late"] = df["days_overdue"] > 0

    # 4. Ensure status aligns with return_date and overdue logic
    def derive_status(row):
        if row["return_date"] != "":
            return "Returned"
        elif row["days_overdue"] > 0:
            return "Overdue"
        return "Borrowed"

    df["status"] = df.apply(derive_status, axis=1)

    # 5. Deduplicate
    df = df.drop_duplicates(subset=["borrow_id"])

    out_path = os.path.join(proc_dir, "borrowing_cleaned.csv")
    df.to_csv(out_path, index=False)
    print(f"    Saved cleaned borrowing: {out_path} ({len(df)} records)")
    return df


def clean_fines(raw_dir, proc_dir):
    """Loads, cleans, and standardizes fines ledger."""
    file_path = os.path.join(raw_dir, "fines.csv")
    print(f"[+] Processing fines: {file_path}")
    df = pd.read_csv(file_path, dtype={"fine_id": str, "borrow_id": str, "member_id": str}, keep_default_na=False)

    # 1. String formatting
    for col in ["fine_id", "borrow_id", "member_id", "payment_status"]:
        df[col] = df[col].astype(str).str.strip()

    # 2. Fine amount formatting
    df["fine_amount"] = pd.to_numeric(df["fine_amount"], errors="coerce").fillna(0.0).round(2).clip(lower=0.0)

    # 3. Dates parsing
    fine_dt = pd.to_datetime(df["fine_date"], errors="coerce")
    pay_dt = pd.to_datetime(df["payment_date"].replace("", np.nan), errors="coerce")

    df["fine_date"] = fine_dt.dt.strftime("%Y-%m-%d")
    df["payment_date"] = pay_dt.dt.strftime("%Y-%m-%d").fillna("")

    # 4. Feature engineering: days to pay
    df["days_to_pay"] = np.where(pay_dt.notnull(), (pay_dt - fine_dt).dt.days.clip(lower=0), np.nan)

    # 5. Status validation
    df["payment_status"] = np.where(df["payment_date"] != "", "Paid", "Unpaid")

    # 6. Deduplicate
    df = df.drop_duplicates(subset=["fine_id"])

    out_path = os.path.join(proc_dir, "fines_cleaned.csv")
    df.to_csv(out_path, index=False)
    print(f"    Saved cleaned fines: {out_path} ({len(df)} records)")
    return df


def main():
    print("=" * 70)
    print("STARTING DATA CLEANING PIPELINE")
    print("=" * 70)

    base_dir, raw_dir, proc_dir = get_project_paths()
    os.makedirs(proc_dir, exist_ok=True)

    clean_books(raw_dir, proc_dir)
    clean_members(raw_dir, proc_dir)
    clean_borrowing(raw_dir, proc_dir)
    clean_fines(raw_dir, proc_dir)

    print("=" * 70)
    print("DATA CLEANING PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    main()
