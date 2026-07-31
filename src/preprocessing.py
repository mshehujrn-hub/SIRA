# import pandas as pd


# class DataCleaner:

#     def remove_duplicates(self, df):
#         return df.drop_duplicates()

#     def remove_missing(self, df):
#         return df.dropna()

#     def strip_spaces(self, df):
#         df["report_text"] = df["report_text"].str.strip()
#         return df

#     def lowercase(self, df):
#         df["report_text"] = df["report_text"].str.lower()
#         return df


"""
preprocessing.py
----------------
Modular Data Cleaning & Preprocessing Pipeline for SIRA.
"""

import pandas as pd
import numpy as np
from typing import List, Optional


class IncidentDataCleaner:
    """
    A robust preprocessing class to inspect and clean incident report datasets.
    """

    def __init__(self, df: pd.DataFrame):
        """
        Initialize with a raw DataFrame copy to prevent side effects.
        """
        self.df = df.copy()
        self.initial_rows = len(df)

    def remove_duplicates(self, subset: Optional[List[str]] = None) -> "IncidentDataCleaner":
        """
        Remove exact duplicate rows or duplicates based on specific primary keys.
        """
        self.df.drop_duplicates(subset=subset, keep="first", inplace=True)
        return self

    def standardize_text_fields(self, text_columns: List[str]) -> "IncidentDataCleaner":
        """
        Strip white spaces and standardize text casing (Title Case / Lowercase).
        """
        for col in text_columns:
            if col in self.df.columns:
                self.df[col] = (
                    self.df[col]
                    .astype(str)
                    .str.strip()
                    .str.replace(r"\s+", " ", regex=True)
                    .str.title()
                )
                # Convert string 'Nan' or 'None' back to true NaN
                self.df[col] = self.df[col].replace(["Nan", "None", ""], np.nan)
        return self

    def fix_date_formats(self, date_columns: List[str]) -> "IncidentDataCleaner":
        """
        Parse non-standard dates into a uniform ISO 8601 string format (YYYY-MM-DD).
        """
        for col in date_columns:
            if col in self.df.columns:
                self.df[col] = pd.to_datetime(self.df[col], errors="coerce").dt.strftime("%Y-%m-%d")
        return self

    def handle_numeric_anomalies(self, numeric_cols: List[str]) -> "IncidentDataCleaner":
        """
        Convert negative values to absolute values where negative quantities 
         are physically impossible (e.g., downtime hours, financial loss).
        """
        for col in numeric_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors="coerce")
                # Correct invalid negative values
                self.df[col] = self.df[col].apply(lambda x: abs(x) if pd.notnull(x) and x < 0 else x)
        return self

    def handle_missing_values(
        self, 
        categorical_cols: List[str], 
        numeric_cols: List[str]
    ) -> "IncidentDataCleaner":
        """
        Impute missing categorical data with 'Unknown' and numerical with median values.
        """
        for col in categorical_cols:
            if col in self.df.columns:
                self.df[col] = self.df[col].fillna("Unknown")

        for col in numeric_cols:
            if col in self.df.columns:
                median_val = self.df[col].median()
                self.df[col] = self.df[col].fillna(median_val)
                
        return self

    def get_cleaned_data(self) -> pd.DataFrame:
        """
        Return the clean DataFrame.
        """
        return self.df.reset_index(drop=True)