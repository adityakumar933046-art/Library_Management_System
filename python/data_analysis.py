# Data analysis and visualization script for Library Management System
import os
import pandas as pd
import matplotlib.pyplot as plt

# Define directory paths
PROCESSED_DIR = os.path.join("dataset", "processed")
CHARTS_DIR = os.path.join("outputs", "charts")

# Create charts directory if it does not exist
os.makedirs(CHARTS_DIR, exist_ok=True)

# -------------------------------------------------------------
# 1. Load Cleaned Datasets
# -------------------------------------------------------------
books_df = pd.read_csv(os.path.join(PROCESSED_DIR, "books_cleaned.csv"))
members_df = pd.read_csv(os.path.join(PROCESSED_DIR, "members_cleaned.csv"))
borrowing_df = pd.read_csv(os.path.join(PROCESSED_DIR, "borrowing_cleaned.csv"))
fines_df = pd.read_csv(os.path.join(PROCESSED_DIR, "fines_cleaned.csv"))

print("=== Library Management System Analysis ===\n")

# -------------------------------------------------------------
# 2. Key Metrics Summary
# -------------------------------------------------------------
total_books = len(books_df)
total_members = len(members_df)
total_borrowings = len(borrowing_df)
total_fines = fines_df["fine_amount"].sum()
collected_fines = fines_df[fines_df["payment_status"] == "Paid"]["fine_amount"].sum()

print(f"Total Books: {total_books}")
print(f"Total Members: {total_members}")
print(f"Total Borrowings: {total_borrowings}")
print(f"Total Fine Amount: ${total_fines:,.2f}")
print(f"Collected Fine Amount: ${collected_fines:,.2f}\n")

# -------------------------------------------------------------
# 3. Analysis 1: Top 5 Borrowed Books
# -------------------------------------------------------------
book_borrow = borrowing_df.merge(books_df, on="book_id")
top_books = book_borrow["title"].value_counts().head(5)

print("--- Top 5 Borrowed Books ---")
print(top_books)
print()

# Chart 1: Top 5 Borrowed Books
plt.figure(figsize=(8, 5))
top_books.plot(kind="barh", color="#2b5c8f")
plt.title("Top 5 Borrowed Books", fontsize=14, fontweight="bold")
plt.xlabel("Borrow Count")
plt.ylabel("Book Title")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, "top_borrowed_books.png"), dpi=300)
plt.close()

# -------------------------------------------------------------
# 4. Analysis 2: Popular Book Categories
# -------------------------------------------------------------
category_counts = book_borrow["category"].value_counts()

print("--- Popular Categories ---")
print(category_counts)
print()

# Chart 2: Popular Book Categories
plt.figure(figsize=(8, 5))
category_counts.plot(kind="bar", color="#3b82f6")
plt.title("Popular Book Categories", fontsize=14, fontweight="bold")
plt.xlabel("Category")
plt.ylabel("Total Borrowings")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, "popular_categories.png"), dpi=300)
plt.close()

# -------------------------------------------------------------
# 5. Analysis 3: Monthly Borrowing Trends
# -------------------------------------------------------------
borrowing_df["month"] = pd.to_datetime(borrowing_df["borrow_date"]).dt.to_period("M").astype(str)
monthly_trend = borrowing_df["month"].value_counts().sort_index()

print("--- Monthly Borrowing Trends ---")
print(monthly_trend)
print()

# Chart 3: Monthly Borrowing Trends
plt.figure(figsize=(10, 5))
monthly_trend.plot(kind="line", marker="o", color="#10b981", linewidth=2)
plt.title("Monthly Borrowing Trends", fontsize=14, fontweight="bold")
plt.xlabel("Month")
plt.ylabel("Borrow Count")
plt.xticks(rotation=45)
plt.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, "monthly_borrowing_trend.png"), dpi=300)
plt.close()

# -------------------------------------------------------------
# 6. Analysis 4: Top 5 Active Members
# -------------------------------------------------------------
member_borrow = borrowing_df.merge(members_df, on="member_id")
member_borrow["member_name"] = member_borrow["first_name"] + " " + member_borrow["last_name"]
top_members = member_borrow["member_name"].value_counts().head(5)

print("--- Top 5 Active Members ---")
print(top_members)
print()

# Chart 4: Top 5 Active Members
plt.figure(figsize=(8, 5))
top_members.plot(kind="bar", color="#f59e0b")
plt.title("Top 5 Active Members", fontsize=14, fontweight="bold")
plt.xlabel("Member Name")
plt.ylabel("Total Borrowings")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, "active_members.png"), dpi=300)
plt.close()

# -------------------------------------------------------------
# 7. Analysis 5: Fine Analysis
# -------------------------------------------------------------
fine_summary = fines_df.groupby("payment_status")["fine_amount"].sum()

print("--- Fine Analysis ---")
print(fine_summary)
print()

# Chart 5: Fine Analysis
plt.figure(figsize=(6, 6))
fine_summary.plot(kind="pie", autopct="%1.1f%%", colors=["#10b981", "#ef4444"], startangle=90)
plt.title("Fine Collection Status (Paid vs Unpaid)", fontsize=14, fontweight="bold")
plt.ylabel("")
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, "fine_analysis.png"), dpi=300)
plt.close()

print(f"All 5 charts saved successfully inside {CHARTS_DIR}/")
