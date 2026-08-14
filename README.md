# IKEA Retail Sales & Customer Analytics

### SQL + Python Case Study on Retail Transaction Data

An end-to-end retail analytics project using **MySQL and Python** to analyse approximately **54K transaction records across 26 variables**, uncovering customer behaviour, product performance, sales patterns, geographic concentration, and revenue loss from cancellations.

The project goes beyond descriptive SQL queries by combining **data cleaning, exploratory analysis, advanced SQL analytics, customer segmentation, cohort analysis, and business recommendations**.

---

## 📌 Project Overview

The objective of this project was to answer business questions that a retail company would actually care about:

- When do customers shop, and what does their purchasing behaviour reveal?
- Which customers contribute the most revenue?
- Which products drive revenue versus sales volume?
- Which products generate disproportionate returns?
- How much revenue is lost through cancellations?
- Where is revenue geographically concentrated?
- Can customer behaviour be used to identify high-value segments?

The analysis was performed primarily in **MySQL 8**, followed by exploratory analysis and validation using **Python/Pandas**.

---

## 📊 Dataset

The dataset contains approximately:

- **54,000+ transaction records**
- **26 columns**
- Invoice-level transaction data
- Product information
- Customer identifiers
- Transaction dates and times
- Quantity and unit price
- Geographic information

### Key Variables

| Variable | Description |
|---|---|
| Invoice Number | Unique transaction/invoice identifier |
| Date | Transaction date |
| Time | Transaction time |
| Stock Code | Product identifier |
| Description | Product description |
| Quantity | Number of units purchased |
| Unit Price | Price per unit |
| Customer ID | Customer identifier |
| Country | Customer location |

Negative quantities were treated as **returns/cancellations** rather than simply removed, allowing cancellation and revenue-loss analysis.

---

## 🔬 Analytical Methodology

The project used **65 SQL queries** across seven analytical themes:

1. Sales Performance
2. Product Performance
3. Customer Behaviour
4. Geographic Analysis
5. Returns & Cancellations
6. Order Patterns
7. Advanced Analytics

Advanced analysis included **RFM analysis, percentile-based segmentation, cohort analysis, purchase-gap analysis, and time-based analysis**. Results were subsequently validated and visualised using Python/Pandas. :contentReference[oaicite:1]{index=1}

--
What I Learned

This project strengthened my ability to:

Work with messy, real-world transactional data.
Design analytical SQL beyond basic SELECT, GROUP BY, and ORDER BY.
Use CTEs and window functions for behavioural analysis.
Apply percentile-based customer segmentation.
Perform RFM and cohort analysis.
Validate analytical outputs across multiple queries.
Identify data-quality issues that can materially affect business conclusions.
Translate raw metrics into actionable business recommendations.

One of the key lessons was that a query returning a result does not necessarily mean the result is analytically correct. Several findings required cross-checking against other metrics and domain logic before being treated as valid insights.

📌 Disclaimer

This is a project developed using multiple public sources, prior similar analytical approaches, and other tools during research, implementation, debugging, and documentation.

It should not be considered original research or independently validated. The findings are intended for educational and portfolio purposes, and the underlying dataset and assumptions should be reviewed before using the analysis for real-world business decisions.
                           
