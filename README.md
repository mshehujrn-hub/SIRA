Smart Incident Report Analyzer (SIRA) - Data Preprocessing

About the SIRA Application
The Smart Incident Report Analyzer (SIRA) is an AI-driven system designed to process and analyze operational incident reports collected across Oil & Gas facilities. By standardizing and evaluating historical incident data, SIRA enables safety engineers to detect operational patterns, analyze downtime drivers, and prepare clean data for downstream machine learning models focused on risk classification and severity prediction. 

This repository contains the Phase 1 automated data preprocessing pipeline required to transform raw, noisy facility reports into a clean, machine-learning-ready dataset.

Data Quality Investigation

What data quality issues did you discover?
During the Exploratory Data Analysis (EDA) of the raw `incident_reports_1000.csv` dataset, four primary data quality issues were identified:

*Duplicate Records:The raw export contained exact duplicate rows resulting from redundant log entries.
*Missing Values:Key numerical metrics (such as financial cost and downtime hours) and categorical descriptors (such as severity and incident type) contained missing (`NaN`) entries.
*Inconsistent Text Formatting:Categorical text fields suffered from leading/trailing whitespace anomalies and inconsistent casing (e.g., entries like `" minor"`, `"MINOR"`, and `"Minor"` referring to the same category).
*Data Type Mismatches:Date attributes were stored as unparsed text strings (`object` data type) rather than structured datetime objects, preventing temporal analysis.

How did you identify them?
The data assessment was conducted programmatically using Python and `pandas` inside the `notebooks/` directory:
*`df.duplicated().sum()`was used to calculate the exact count of identical rows across all columns.
*`df.isnull().sum()`mapped the distribution and frequency of missing values across every feature.
*`df.info()` and `df.dtypes`highlighted primitive data type assignments and identified object-encoded date columns.
*`df[col].unique()` and `df[col].value_counts(dropna=False)` were run on categorical text features to expose hidden string variations, whitespace padding, and capitalization inconsistencies.

Preprocessing Implementation

What steps did you take to clean the data?
The preprocessing logic is modularized inside the `DataPreprocessor` class (`src/preprocessing.py`) and executed sequentially through method chaining:

1.Deduplication:Dropped all exact duplicate rows using `.drop_duplicates()`.

2.Numeric Imputation:Filled missing numerical values with the median of their respective columns.

3.Categorical Imputation:Replaced missing categorical values with the explicit placeholder category `"Unknown"`.

4.Text Standardization:Applied `.str.strip()` to strip leading/trailing whitespaces and `.str.title()` to enforce standard Title Case formatting across all string columns.

5.Datetime Parsing:Converted date string fields into formal Pandas `datetime64` objects using `pd.to_datetime(errors='coerce')`.

Why did you choose those approaches?

Median Imputation for Numbers:Industrial incident data like financial loss or downtime hours is right-skewed by rare, severe events. The median was selected over the mean because it is robust against outliers and prevents statistical distortion.

"Unknown" Category for Text:Deleting rows with missing categorical descriptors would cause unnecessary loss of valuable operational data in other columns. Creating an `"Unknown"` label preserves sample size while allowing downstream ML models to treat missingness as an explicit feature.

Title-Case Standardization:Unifying text casing merges redundant categories (e.g., standardizing `"MINOR"`, `"minor"`, and `" Minor "` into `"Minor"`), reducing categorical cardinality and avoiding sparse feature matrices during encoding.

Object-Oriented Architecture:** Encapsulating the cleaning logic inside a reusable class ensures idempotency (the pipeline can run multiple times without failure) and seamlessly bridges raw data ingestion in `clean_data.py` with future phase models.