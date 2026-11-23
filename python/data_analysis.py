"""
=============================================================================
Exploratory Data Analysis & Visualization Pipeline
Project: Library Management System Analysis Using SQL
Script: python/data_analysis.py
Description: Computes comprehensive statistical summaries, KPI metrics,
             and outputs high-resolution analytical charts to outputs/charts/.
=============================================================================
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set professional styling for charts
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8


def get_paths():
    """Resolves data and output directories."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    proc_dir = os.path.join(base_dir, "dataset", "processed")
    charts_dir = os.path.join(base_dir, "outputs", "charts")
    return base_dir, proc_dir, charts_dir


def load_cleaned_data(proc_dir):
    """Loads all 4 cleaned datasets."""
    books = pd.read_csv(os.path.join(proc_dir, "books_cleaned.csv"))
    members = pd.read_csv(os.path.join(proc_dir, "members_cleaned.csv"))
    borrowing = pd.read_csv(os.path.join(proc_dir, "borrowing_cleaned.csv"), keep_default_na=False)
    fines = pd.read_csv(os.path.join(proc_dir, "fines_cleaned.csv"), keep_default_na=False)
    return books, members, borrowing, fines


def print_executive_kpis(books, members, borrowing, fines):
    """Prints core executive KPIs to console."""
    print("=" * 70)
    print("LIBRARY MANAGEMENT SYSTEM - EXECUTIVE KPI SUMMARY")
    print("=" * 70)

    total_titles = len(books)
    total_copies = books["total_copies"].sum()
    available_copies = books["available_copies"].sum()
    inventory_val = (books["total_copies"] * books["price"]).sum()
    avg_price = books["price"].mean()

    total_members = len(members)
    active_members = (members["status"] == "Active").sum()

    total_loans = len(borrowing)
    late_loans = borrowing["is_late"].sum()
    late_rate = (late_loans / total_loans * 100) if total_loans else 0

    total_fines = fines["fine_amount"].sum()
    collected_fines = fines[fines["payment_status"] == "Paid"]["fine_amount"].sum()
    unpaid_fines = fines[fines["payment_status"] == "Unpaid"]["fine_amount"].sum()
    collection_rate = (collected_fines / total_fines * 100) if total_fines else 0

    print(f"Catalog & Inventory:")
    print(f"  * Total Titles                  : {total_titles:,}")
    print(f"  * Total Physical Copies         : {total_copies:,}")
    print(f"  * Currently Available Copies    : {available_copies:,}")
    print(f"  * Total Inventory Value         : ${inventory_val:,.2f}")
    print(f"  * Average Book Price            : ${avg_price:.2f}")
    print(f"\nMembership Base:")
    print(f"  * Total Registered Patrons      : {total_members:,}")
    print(f"  * Active Status Patrons         : {active_members:,} ({active_members/total_members*100:.1f}%)")
    print(f"\nCirculation Performance:")
    print(f"  * Total Borrowing Transactions  : {total_loans:,}")
    print(f"  * Late / Delinquent Returns     : {late_loans:,} ({late_rate:.1f}%)")
    print(f"\nFinancial Overview:")
    print(f"  * Total Penalties Assessed      : ${total_fines:,.2f}")
    print(f"  * Total Fines Collected         : ${collected_fines:,.2f} ({collection_rate:.1f}%)")
    print(f"  * Outstanding Unpaid Fines      : ${unpaid_fines:,.2f}")
    print("=" * 70)


def plot_most_borrowed_books(books, borrowing, charts_dir):
    """Generates bar chart for top 10 most borrowed books."""
    merged = borrowing.merge(books, on="book_id", how="left")
    top_books = (
        merged.groupby("title")["borrow_id"]
        .count()
        .reset_index(name="borrow_count")
        .sort_values(by="borrow_count", ascending=True)
        .tail(10)
    )

    plt.figure(figsize=(10, 6))
    bars = plt.barh(top_books["title"], top_books["borrow_count"], color="#1f77b4", edgecolor="#0e4369", height=0.65)
    plt.title("Top 10 Most Frequently Borrowed Books", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Total Borrowing Transactions", fontsize=11, labelpad=10)
    plt.ylabel("Book Title", fontsize=11)
    plt.xlim(0, max(top_books["borrow_count"]) + 3)

    for bar in bars:
        width = bar.get_width()
        plt.text(width + 0.3, bar.get_y() + bar.get_height() / 2, f"{int(width)}", va="center", fontsize=10, fontweight="bold")

    plt.tight_layout()
    out_path = os.path.join(charts_dir, "01_most_borrowed_books.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[+] Saved chart: {out_path}")


def plot_monthly_borrowing_trends(borrowing, charts_dir):
    """Generates time series line chart for monthly borrowing velocity."""
    borrowing["year_month"] = pd.to_datetime(borrowing["borrow_date"]).dt.to_period("M").astype(str)
    monthly = borrowing.groupby("year_month")["borrow_id"].count().reset_index(name="borrow_count")

    plt.figure(figsize=(11, 5.5))
    plt.plot(monthly["year_month"], monthly["borrow_count"], marker="o", color="#2ca02c", linewidth=2.5, markersize=7)
    plt.fill_between(monthly["year_month"], monthly["borrow_count"], color="#2ca02c", alpha=0.15)
    plt.title("Monthly Book Borrowing Trends", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Period (Year-Month)", fontsize=11, labelpad=10)
    plt.ylabel("Number of Borrowings", fontsize=11, labelpad=10)
    plt.xticks(rotation=45, ha="right", fontsize=9)
    plt.grid(True, linestyle="--", alpha=0.5)

    for i, row in monthly.iterrows():
        plt.text(i, row["borrow_count"] + 0.6, str(row["borrow_count"]), ha="center", fontsize=8.5, fontweight="bold")

    plt.tight_layout()
    out_path = os.path.join(charts_dir, "02_monthly_borrowing_trends.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[+] Saved chart: {out_path}")


def plot_category_distribution(books, charts_dir):
    """Generates bar chart of book titles and copies by genre/category."""
    cat_summary = (
        books.groupby("category")
        .agg(total_titles=("book_id", "count"), total_copies=("total_copies", "sum"))
        .sort_values(by="total_copies", ascending=False)
        .reset_index()
    )

    x = np.arange(len(cat_summary))
    width = 0.38

    fig, ax = plt.subplots(figsize=(11, 5.5))
    rects1 = ax.bar(x - width/2, cat_summary["total_titles"], width, label="Unique Titles", color="#4e79a7")
    rects2 = ax.bar(x + width/2, cat_summary["total_copies"], width, label="Total Physical Copies", color="#f28e2b")

    ax.set_title("Catalog Volume & Physical Copies by Category", fontsize=14, fontweight="bold", pad=15)
    ax.set_ylabel("Count", fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels(cat_summary["category"], rotation=30, ha="right", fontsize=9.5)
    ax.legend(frameon=True)

    for rect in rects1:
        h = rect.get_height()
        ax.annotate(f"{h}", xy=(rect.get_x() + rect.get_width() / 2, h), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontsize=8.5)
    for rect in rects2:
        h = rect.get_height()
        ax.annotate(f"{h}", xy=(rect.get_x() + rect.get_width() / 2, h), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontsize=8.5)

    plt.tight_layout()
    out_path = os.path.join(charts_dir, "03_category_distribution.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[+] Saved chart: {out_path}")


def plot_membership_breakdown(members, charts_dir):
    """Generates donut chart for membership types."""
    counts = members["membership_type"].value_counts()
    colors = ["#3498db", "#9b59b6", "#2ecc71", "#e67e22"]

    plt.figure(figsize=(7, 7))
    wedges, texts, autotexts = plt.pie(
        counts,
        labels=counts.index,
        autopct="%1.1f%%",
        startangle=140,
        colors=colors,
        pctdistance=0.75,
        wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2)
    )
    for at in autotexts:
        at.set_fontsize(11)
        at.set_fontweight("bold")
    for t in texts:
        t.set_fontsize(11)

    plt.title("Patron Membership Tier Distribution", fontsize=14, fontweight="bold", pad=20)
    plt.tight_layout()
    out_path = os.path.join(charts_dir, "04_membership_tier_breakdown.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[+] Saved chart: {out_path}")


def plot_fine_status_and_recovery(fines, charts_dir):
    """Generates financial collection visualization for library fines."""
    status_summary = fines.groupby("payment_status")["fine_amount"].sum()
    labels = ["Collected (Paid)", "Outstanding (Unpaid)"]
    vals = [status_summary.get("Paid", 0.0), status_summary.get("Unpaid", 0.0)]
    colors = ["#27ae60", "#e74c3c"]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, vals, color=colors, width=0.5, edgecolor="#333333", linewidth=0.8)
    ax.set_title("Library Fine Collection Status ($ USD)", fontsize=14, fontweight="bold", pad=15)
    ax.set_ylabel("Total Fine Amount ($)", fontsize=11)
    ax.set_ylim(0, max(vals) * 1.2)

    for bar in bars:
        h = bar.get_height()
        pct = (h / sum(vals)) * 100
        ax.text(bar.get_x() + bar.get_width() / 2, h + 20, f"${h:,.2f}\n({pct:.1f}%)",
                ha="center", va="bottom", fontsize=11, fontweight="bold")

    plt.tight_layout()
    out_path = os.path.join(charts_dir, "05_fine_payment_status.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[+] Saved chart: {out_path}")


def plot_late_rate_by_membership(members, borrowing, charts_dir):
    """Analyzes overdue / late return tendencies across membership tiers."""
    merged = borrowing.merge(members, on="member_id", how="left")
    tier_stats = (
        merged.groupby("membership_type")
        .agg(total_loans=("borrow_id", "count"), late_loans=("is_late", "sum"))
        .reset_index()
    )
    tier_stats["late_rate_pct"] = (tier_stats["late_loans"] / tier_stats["total_loans"] * 100).round(1)
    tier_stats = tier_stats.sort_values(by="late_rate_pct", ascending=False)

    plt.figure(figsize=(8, 5))
    bars = plt.bar(tier_stats["membership_type"], tier_stats["late_rate_pct"], color="#e74c3c", width=0.5, edgecolor="#922b21")
    plt.title("Late Return Rate by Membership Tier (%)", fontsize=14, fontweight="bold", pad=15)
    plt.ylabel("Delinquency Rate (%)", fontsize=11)
    plt.ylim(0, max(tier_stats["late_rate_pct"]) + 10)

    for bar in bars:
        h = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, h + 1, f"{h:.1f}%", ha="center", va="bottom", fontsize=10.5, fontweight="bold")

    plt.tight_layout()
    out_path = os.path.join(charts_dir, "06_late_return_rate_by_tier.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[+] Saved chart: {out_path}")


def main():
    base_dir, proc_dir, charts_dir = get_paths()
    os.makedirs(charts_dir, exist_ok=True)

    print("=" * 70)
    print("STARTING DATA ANALYSIS & VISUALIZATION PIPELINE")
    print("=" * 70)

    books, members, borrowing, fines = load_cleaned_data(proc_dir)
    print_executive_kpis(books, members, borrowing, fines)

    plot_most_borrowed_books(books, borrowing, charts_dir)
    plot_monthly_borrowing_trends(borrowing, charts_dir)
    plot_category_distribution(books, charts_dir)
    plot_membership_breakdown(members, charts_dir)
    plot_fine_status_and_recovery(fines, charts_dir)
    plot_late_rate_by_membership(members, borrowing, charts_dir)

    print("=" * 70)
    print("ANALYSIS & CHARTS GENERATED SUCCESSFULLY")
    print(f"Artifacts saved in: {charts_dir}")
    print("=" * 70)


if __name__ == "__main__":
    main()
