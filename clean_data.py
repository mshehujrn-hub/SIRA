# # from pathlib import Path
# # import pandas as pd
# # from src.preprocessing import DataCleaner

# # def main():
# #     base_dir = Path(__file__).resolve().parent

# #     # Try finding the CSV in data/raw/ first, then fallback to data/
# #     raw_path = base_dir / "data" / "raw" / "incident_reports_1000.csv"
# #     if not raw_path.exists():
# #         raw_path = base_dir / "data" / "incident_reports_1000.csv"

# #     if not raw_path.exists():
# #         raise FileNotFoundError(f"Could not find incident_reports_1000.csv in {base_dir / 'data'}")

# #     # Save clean dataset directly inside data/ as required by assignment rules
# #     output_file = base_dir / "data" / "incident_reports_clean.csv"

# #     print("=" * 60)
# #     print(f"Loading raw dataset from: {raw_path}")
# #     df = pd.read_csv(raw_path)
# #     initial_count = len(df)

# #     print("Cleaning dataset...")
# #     cleaner = DataCleaner(df)

# #     text_cols = ["facility", "incident_type", "severity", "root_cause", "status"]
# #     date_cols = ["incident_date", "report_date"]
# #     numeric_cols = ["downtime_hours", "estimated_cost_usd"]

# #     clean_df = (
# #         cleaner.remove_duplicates()
# #         .strip_and_clean_text(text_cols)
# #         .fix_dates(date_cols)
# #         .fix_numeric_anomalies(numeric_cols)
# #         .fill_missing(categorical_cols=text_cols, numeric_cols=numeric_cols)
# #         .get_df()
# #     )

# #     clean_df.to_csv(output_file, index=False)

# #     print(f"\nSuccess! Clean dataset saved to: {output_file}")
# #     print(f"Original Rows: {initial_count} | Clean Rows: {len(clean_df)}")
# #     print("=" * 60)

# # if __name__ == "__main__":
# #     main()

# """
# clean_data.py
# -------------
# Main execution entry point to run the SIRA data cleaning pipeline.
# """

# from pathlib import Path
# from src.data_loader import DataLoader
# from src.preprocessing import IncidentDataCleaner


# def main():
#     # Define directory paths dynamically
#     base_dir = Path(__file__).resolve().parent
#     raw_data_path = base_dir / "data" / "incident_reports_1000.csv"
#     output_data_path = base_dir / "data" / "incident_reports_clean.csv"

#     print("=" * 60)
#     print("SIRA: Smart Incident Report Analyzer - Data Cleaning Pipeline")
#     print("=" * 60)

#     # 1. Load Data
#     print(f"[1/4] Loading raw dataset from: {raw_data_path}")
#     loader = DataLoader(filepath=str(raw_data_path))
#     raw_df = loader.load_data()
#     print(f"      Successfully loaded {len(raw_df)} raw records.")

#     # 2. Identify and Clean Data
#     print("[2/4] Executing preprocessing pipeline...")
#     cleaner = IncidentDataCleaner(raw_df)

#     # Columns targeted for specific cleaning operations
#     text_cols = ["facility", "incident_type", "severity", "root_cause", "status"]
#     date_cols = ["incident_date", "report_date"]
#     numeric_cols = ["downtime_hours", "estimated_cost_usd"]

#     cleaned_df = (
#         cleaner.remove_duplicates()
#         .standardize_text_fields(text_cols)
#         .fix_date_formats(date_cols)
#         .handle_numeric_anomalies(numeric_cols)
#         .handle_missing_values(categorical_cols=text_cols, numeric_cols=numeric_cols)
#         .get_cleaned_data()
#     )

#     # 3. Output Quality Metrics
#     dropped_rows = len(raw_df) - len(cleaned_df)
#     print(f"[3/4] Data processing complete.")
#     print(f"      - Initial Rows: {len(raw_df)}")
#     print(f"      - Rows Retained: {len(cleaned_df)}")
#     print(f"      - Duplicates Removed: {dropped_rows}")

#     # 4. Save Cleaned Dataset
#     output_data_path.parent.mkdir(parents=True, exist_ok=True)
#     cleaned_df.to_csv(output_data_path, index=False)
#     print(f"[4/4] Cleaned dataset saved to: {output_data_path}")
#     print("=" * 60)
#     print("Pipeline executed successfully! Ready for downstream ML modeling.")
#     print("=" * 60)


# if __name__ == "__main__":
#     main()

from pathlib import Path
from src.data_loader import DataLoader
from src.preprocessing import IncidentDataCleaner


def main():
    # Define directory paths dynamically
    base_dir = Path(__file__).resolve().parent
    raw_data_path = base_dir / "data" / "raw" / "incident_reports_1000.csv"
    output_data_path = (
        base_dir / "data" / "processed" / "incident_reports_clean.csv"
    )

    print("=" * 60)
    print("SIRA: Smart Incident Report Analyzer - Data Cleaning Pipeline")
    print("=" * 60)

    # 1. Load Data
    print(f"[1/4] Loading raw dataset from: {raw_data_path}")
    loader = DataLoader(filepath=str(raw_data_path))
    raw_df = loader.load_data()
    print(f"      Successfully loaded {len(raw_df)} raw records.")

    # 2. Identify and Clean Data
    print("[2/4] Executing preprocessing pipeline...")
    cleaner = IncidentDataCleaner(raw_df)

    # Columns targeted for specific cleaning operations
    text_cols = [
        "facility",
        "incident_type",
        "severity",
        "root_cause",
        "status",
    ]
    date_cols = ["incident_date", "report_date"]
    numeric_cols = ["downtime_hours", "estimated_cost_usd"]

    cleaned_df = (
        cleaner.remove_duplicates()
        .standardize_text_fields(text_cols)
        .fix_date_formats(date_cols)
        .handle_numeric_anomalies(numeric_cols)
        .handle_missing_values(
            categorical_cols=text_cols, numeric_cols=numeric_cols
        )
        .get_cleaned_data()
    )

    # 3. Output Quality Metrics
    dropped_rows = len(raw_df) - len(cleaned_df)
    print(f"[3/4] Data processing complete.")
    print(f"      - Initial Rows: {len(raw_df)}")
    print(f"      - Rows Retained: {len(cleaned_df)}")
    print(f"      - Duplicates Removed: {dropped_rows}")

    # 4. Save Cleaned Dataset
    output_data_path.parent.mkdir(parents=True, exist_ok=True)
    cleaned_df.to_csv(output_data_path, index=False)
    print(f"[4/4] Cleaned dataset saved to: {output_data_path}")
    print("=" * 60)
    print("Pipeline executed successfully! Ready for downstream ML modeling.")
    print("=" * 60)


if __name__ == "__main__":
    main()