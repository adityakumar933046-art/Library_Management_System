# 📚 Library Management System Analysis Using SQL, Python and Power BI

## 📌 Project Introduction

The **Library Management System Analysis** is a college-level Data Analytics project designed to examine library circulation, book availability, patron activity, overdue penalties, and category popularity.

By integrating **MySQL**, **SQL**, **Python (Pandas, NumPy, Matplotlib)**, **Jupyter Notebook**, and **Power BI**, this project converts raw operational data into actionable insights for effective library inventory management and patron policy design.

---

## 🎯 Project Objectives

* Analyze book borrowing and return patterns over time.
* Identify the most frequently borrowed books and popular categories.
* Identify the most active library members.
* Detect overdue borrowing records and track late return behavior.
* Calculate total fine collections and outstanding unpaid amounts.
* Provide an interactive Power BI dashboard model for library operations.
* Keep the data pipeline simple, beginner-friendly, and easy to explain in a viva.

---

## 🛠️ Technology Stack

| Technology | Purpose |
| :--- | :--- |
| **MySQL / SQL** | Relational database schema, data integrity, and analytical queries |
| **Python 3.x** | Data processing, automated cleaning, and statistical summaries |
| **Pandas** | Data cleaning, type conversion, merging, and transformations |
| **NumPy** | Numeric operations and metrics calculation |
| **Matplotlib** | Generating analytical visualizations and charts |
| **Jupyter Notebook** | Interactive step-by-step exploratory analysis with code & visuals |
| **Power BI** | Data modeling, interactive KPI cards, and dashboard design |
| **Git & GitHub** | Source code version control and project documentation |

---

## 📁 Project Structure

```text
Library_Management_System/
│
├── README.md
├── requirements.txt
│
├── dataset/
│   ├── raw/
│   │   ├── books.csv
│   │   ├── members.csv
│   │   ├── borrowing.csv
│   │   └── fines.csv
│   │
│   └── processed/
│       ├── books_cleaned.csv
│       ├── members_cleaned.csv
│       ├── borrowing_cleaned.csv
│       └── fines_cleaned.csv
│
├── database/
│   ├── create_tables.sql
│   └── analysis_queries.sql
│
├── python/
│   ├── data_cleaning.py
│   └── data_analysis.py
│
├── notebooks/
│   └── Library_Analysis.ipynb
│
├── powerbi/
│   └── README.md
│
└── outputs/
    └── charts/
        ├── top_borrowed_books.png
        ├── popular_categories.png
        ├── monthly_borrowing_trend.png
        ├── active_members.png
        └── fine_analysis.png
```

---

## 🗄️ Dataset Description

The system consists of 4 relational tables:

1. **Books (`books.csv` / `books_cleaned.csv`)** - 50 titles:
   - `book_id`: Unique identifier (e.g., `B101`)
   - `title`: Book title
   - `author`: Author name
   - `category`: Genre / subject (Fiction, Computer Science, etc.)
   - `isbn`: Unique ISBN code
   - `publication_year`: Year of publication
   - `total_copies`: Total inventory count
   - `available_copies`: Currently available copies on shelf
   - `price`: Unit replacement cost

2. **Members (`members.csv` / `members_cleaned.csv`)** - 50 patrons:
   - `member_id`: Unique patron identifier (e.g., `M101`)
   - `first_name`, `last_name`: Patron full name
   - `email`, `phone`: Contact details
   - `membership_type`: Student, Faculty, General, Premium
   - `registration_date`: Date member joined
   - `status`: Active, Inactive, Suspended

3. **Borrowing (`borrowing.csv` / `borrowing_cleaned.csv`)** - 320 records:
   - `borrow_id`: Unique transaction identifier (e.g., `BR1001`)
   - `book_id`: Foreign key referencing books
   - `member_id`: Foreign key referencing members
   - `borrow_date`: Date book was checked out
   - `due_date`: Expected return date
   - `return_date`: Actual return date
   - `status`: Transaction status (e.g., `Returned`)

4. **Fines (`fines.csv` / `fines_cleaned.csv`)** - 106 records:
   - `fine_id`: Unique fine identifier (e.g., `FN501`)
   - `borrow_id`: Foreign key referencing borrowing
   - `member_id`: Foreign key referencing members
   - `fine_amount`: Dollar penalty levied
   - `fine_date`: Date fine was assessed
   - `payment_status`: Paid or Unpaid
   - `payment_date`: Date penalty was settled (empty if unpaid)

---

## 🧹 Data Cleaning (`python/data_cleaning.py`)

The cleaning pipeline performs essential preprocessing tasks using simple Pandas code:
1. Loads all 4 raw CSV files and previews the top 5 records.
2. Identifies and prints missing values and duplicate rows.
3. Removes potential duplicates and strips whitespace from text columns.
4. Standardizes all date columns into `YYYY-MM-DD` ISO format.
5. Handles missing `payment_date` values for unpaid fines.
6. Saves the validated cleaned tables into `dataset/processed/`.

---

## 📊 SQL Analysis (`database/analysis_queries.sql`)

The database script contains exactly **10 beginner-friendly SQL queries** demonstrating standard SQL operations (`SELECT`, `WHERE`, `JOIN`, `GROUP BY`, `ORDER BY`, `COUNT`, `SUM`):

1. **Total Books**: Counts unique book titles and total physical copies in catalog.
2. **Total Members**: Counts registered members and active members.
3. **Most Borrowed Books**: Identifies the top 5 most borrowed books by joining `books` and `borrowing`.
4. **Most Active Members**: Finds the top 5 patrons with the highest number of borrowing transactions.
5. **Popular Categories**: Calculates total borrowings grouped by book category.
6. **Monthly Borrowing Trends**: Aggregates loans by month using `DATE_FORMAT()`.
7. **Overdue Books**: Filters loans where `return_date > due_date`.
8. **Total Fine Collection**: Computes total fine revenue collected versus pending unpaid fines.
9. **Department-wise Borrowing**: Analyzes circulation across membership tiers (`membership_type`).
10. **Books Never Borrowed**: Identifies books with zero borrowings using a `LEFT JOIN` and `IS NULL` check.

---

## 🐍 Python Data Analysis & Visualizations (`python/data_analysis.py`)

The Python analysis script computes summary statistics and generates 5 clean charts saved to `outputs/charts/`:

1. **`top_borrowed_books.png`**: Horizontal bar chart of the top 5 borrowed titles (e.g., *Dune*, *The Republic*).
2. **`popular_categories.png`**: Bar chart of borrowing volume by category (led by Fiction and Computer Science).
3. **`monthly_borrowing_trend.png`**: Line chart showing circulation trends from 2023 through 2025.
4. **`active_members.png`**: Bar chart showing the top 5 most frequent patrons.
5. **`fine_analysis.png`**: Pie chart displaying fine collection distribution (Paid: 75.1% vs Unpaid: 24.9%).

---

## 📓 Jupyter Notebook (`notebooks/Library_Analysis.ipynb`)

A fully executed notebook divided into 9 clear sections:
1. **Project Introduction**: Overview of the library analytics scope.
2. **Import Libraries**: Pandas, NumPy, Matplotlib, Seaborn.
3. **Load Datasets**: Ingesting the CSV datasets.
4. **Data Understanding**: Inspecting shapes, column datatypes, and null values.
5. **Data Cleaning**: String trimming, standardizing dates, handling missing values.
6. **Exploratory Data Analysis**: Merging relational tables and computing key metrics.
7. **Data Visualization**: Five embedded Matplotlib / Seaborn figures.
8. **Key Findings**: Bulleted summary of insights.
9. **Conclusion**: Operational recommendations for library management.

---

## 📈 Power BI Dashboard Design (`powerbi/README.md`)

The project includes complete instructions and DAX formulas to build an interactive dashboard:
* **KPI Cards**: Total Books (50), Total Members (50), Total Borrowings (320), Overdue Loans (106), Total Fines ($1,695.00).
* **Charts**: Most Borrowed Books, Popular Categories, Monthly Borrowing Trends, Membership Type Breakdown.
* **Slicers**: Year, Book Category, Membership Type.
* See [powerbi/README.md](powerbi/README.md) for full DAX formulas and relationship diagram.

---

## 🚀 Execution Instructions

### 1. Prerequisites
Ensure Python 3.8+ and MySQL Server are installed.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Data Cleaning
```bash
python python/data_cleaning.py
```
*Cleaned CSV files will be generated inside `dataset/processed/`.*

### 4. Run Python Analysis & Generate Charts
```bash
python python/data_analysis.py
```
*Charts will be exported to `outputs/charts/`.*

### 5. Launch Jupyter Notebook
```bash
jupyter notebook notebooks/Library_Analysis.ipynb
```

### 6. Run MySQL Scripts
Open MySQL Workbench or the MySQL command line client:
```sql
SOURCE database/create_tables.sql;
SOURCE database/analysis_queries.sql;
```

---

## 💡 Key Findings & Conclusion

1. **Circulation Concentration**: Titles like *Dune* (15 loans) and *The Republic* (11 loans) experience peak circulation. Procuring additional copies will reduce hold times.
2. **Category Demand**: Fiction (63 borrowings) and Computer Science (50 borrowings) represent the highest circulation categories.
3. **Overdue Risk**: 106 out of 320 transactions (33.1%) were returned late, totaling $1,695.00 in fines.
4. **Fine Recovery**: $1,273.50 (75.1%) has been collected, with $421.50 remaining outstanding.
5. **Recommendation**: Implement automated SMS or email reminders 2 days prior to the due date to reduce late returns.

---

## 🎓 College Viva Questions & Answers

* **Q: Why use relational tables instead of one big Excel sheet?**
  * *A: Relational tables avoid data redundancy, maintain referential integrity with primary/foreign keys, and scale better.*
* **Q: How are overdue books calculated?**
  * *A: By comparing `return_date > due_date` in SQL and Pandas.*
* **Q: Why was `LEFT JOIN` used in Query 10?**
  * *A: A `LEFT JOIN` keeps all books even if they have no borrow records; checking `WHERE borrowing.borrow_id IS NULL` finds never-borrowed titles.*
