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

# import pandas as pd
# import numpy as np
# from typing import List, Optional


# class IncidentDataCleaner:
#     """
#     A robust preprocessing class to inspect and clean incident report datasets.
#     """

#     def __init__(self, df: pd.DataFrame):
#         """
#         Initialize with a raw DataFrame copy to prevent side effects.
#         """
#         self.df = df.copy()
#         self.initial_rows = len(df)

#     def remove_duplicates(self, subset: Optional[List[str]] = None) -> "IncidentDataCleaner":
#         """
#         Remove exact duplicate rows or duplicates based on specific primary keys.
#         """
#         self.df.drop_duplicates(subset=subset, keep="first", inplace=True)
#         return self

#     def standardize_text_fields(self, text_columns: List[str]) -> "IncidentDataCleaner":
#         """
#         Strip white spaces and standardize text casing (Title Case / Lowercase).
#         """
#         for col in text_columns:
#             if col in self.df.columns:
#                 self.df[col] = (
#                     self.df[col]
#                     .astype(str)
#                     .str.strip()
#                     .str.replace(r"\s+", " ", regex=True)
#                     .str.title()
#                 )
#                 # Convert string 'Nan' or 'None' back to true NaN
#                 self.df[col] = self.df[col].replace(["Nan", "None", ""], np.nan)
#         return self

#     def fix_date_formats(self, date_columns: List[str]) -> "IncidentDataCleaner":
#         """
#         Parse non-standard dates into a uniform ISO 8601 string format (YYYY-MM-DD).
#         """
#         for col in date_columns:
#             if col in self.df.columns:
#                 self.df[col] = pd.to_datetime(self.df[col], errors="coerce").dt.strftime("%Y-%m-%d")
#         return self

#     def handle_numeric_anomalies(self, numeric_cols: List[str]) -> "IncidentDataCleaner":
#         """
#         Convert negative values to absolute values where negative quantities 
#          are physically impossible (e.g., downtime hours, financial loss).
#         """
#         for col in numeric_cols:
#             if col in self.df.columns:
#                 self.df[col] = pd.to_numeric(self.df[col], errors="coerce")
#                 # Correct invalid negative values
#                 self.df[col] = self.df[col].apply(lambda x: abs(x) if pd.notnull(x) and x < 0 else x)
#         return self

#     def handle_missing_values(
#         self, 
#         categorical_cols: List[str], 
#         numeric_cols: List[str]
#     ) -> "IncidentDataCleaner":
#         """
#         Impute missing categorical data with 'Unknown' and numerical with median values.
#         """
#         for col in categorical_cols:
#             if col in self.df.columns:
#                 self.df[col] = self.df[col].fillna("Unknown")

#         for col in numeric_cols:
#             if col in self.df.columns:
#                 median_val = self.df[col].median()
#                 self.df[col] = self.df[col].fillna(median_val)
                
#         return self

#     def get_cleaned_data(self) -> pd.DataFrame:
#         """
#         Return the clean DataFrame.
#         """
#         return self.df.reset_index(drop=True)

from typing import Dict, List, Optional
import numpy as np
import pandas as pd


class IncidentDataCleaner:
    """A robust preprocessing class to inspect and clean incident report datasets."""

    # Comprehensive sentinel set for disguised text missing values
    TEXT_SENTINELS = {
        "nan",
        "null",
        "none",
        "n/a",
        "na",
        "?",
        "-",
        "",
        "unknown",
    }

    # Domain-specific typo mapping for incident report narrative text
    TYPO_MAP = {
        r"\btemprature\b": "temperature",
        r"\bpipleine\b": "pipeline",
        r"\bpressue\b": "pressure",
        r"\bcorosion\b": "corrosion",
        r"\bequipement\b": "equipment",
        r"\bflang\b": "flange",
    }

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.initial_rows = len(df)

    def remove_duplicates(
        self, subset: Optional[List[str]] = None
    ) -> "IncidentDataCleaner":
        """Remove duplicate records based on full row or specific subset of columns."""
        self.df.drop_duplicates(subset=subset, keep="first", inplace=True)
        return self

    def clean_text_sentinels(
        self, extra_sentinels: Optional[List[str]] = None
    ) -> "IncidentDataCleaner":
        """Replace disguised text placeholders with true np.nan before formatting."""
        sentinels = self.TEXT_SENTINELS.union(
            set(s.lower() for s in (extra_sentinels or []))
        )
        obj_cols = self.df.select_dtypes(include=["object"]).columns

        for col in obj_cols:
            cleaned_series = self.df[col].astype(str).str.strip().str.lower()
            self.df[col] = self.df[col].mask(
                cleaned_series.isin(sentinels), np.nan
            )
        return self

    def clean_free_text(
        self,
        text_cols: List[str] = ["report_text"],
        typo_map: Optional[Dict[str, str]] = None,
    ) -> "IncidentDataCleaner":
        """Standardizes narrative descriptions: fixes domain typos, collapses spaces,

        and applies proper Sentence Casing (e.g. 'Pressure leak detected...').
        """
        replacements = typo_map or self.TYPO_MAP

        for col in text_cols:
            if col in self.df.columns:
                mask = self.df[col].notna()
                series = (
                    self.df.loc[mask, col]
                    .astype(str)
                    .str.strip()
                    .str.replace(r"\s+", " ", regex=True)
                )

                # Correct domain spelling errors
                for pattern, repl in replacements.items():
                    series = series.str.replace(
                        pattern, repl, regex=True, case=False
                    )

                # Convert title-cased sentences to natural sentence case
                self.df.loc[mask, col] = series.str.capitalize()
        return self

    def standardize_text_fields(
        self, categorical_cols: List[str]
    ) -> "IncidentDataCleaner":
        """Strip whitespace, collapse extra spaces, and apply Title Case ONLY to structured categorical columns."""
        for col in categorical_cols:
            if col in self.df.columns and col != "report_text":
                mask = self.df[col].notna()
                self.df.loc[mask, col] = (
                    self.df.loc[mask, col]
                    .astype(str)
                    .str.strip()
                    .str.replace(r"\s+", " ", regex=True)
                    .str.title()
                )
        return self

    def fix_date_formats(
        self, date_columns: List[str]
    ) -> "IncidentDataCleaner":
        """Parse non-standard dates into unified ISO format (YYYY-MM-DD)."""
        for col in date_columns:
            if col in self.df.columns:
                parsed = pd.to_datetime(self.df[col], errors="coerce")
                self.df[col] = parsed.dt.strftime("%Y-%m-%d")
        return self

    def handle_numeric_anomalies(
        self,
        numeric_cols: List[str],
        sentinel_values: Optional[List[float]] = None,
    ) -> "IncidentDataCleaner":
        """Mask error codes (-999, -1) and convert valid negative values using absolute values."""
        invalid_codes = sentinel_values or [-999, -9999, -1]
        for col in numeric_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors="coerce")
                self.df[col] = self.df[col].mask(
                    self.df[col].isin(invalid_codes), np.nan
                )
                self.df[col] = self.df[col].abs()
        return self

    def handle_missing_values(
        self,
        categorical_cols: List[str],
        numeric_cols: List[str],
        drop_empty_text: bool = True,
    ) -> "IncidentDataCleaner":
        """Impute missing categorical data with 'Unknown', numeric with median values,

        and drop records missing report narrative text.
        """
        # Impute structured categorical columns (excluding report_text)
        for col in categorical_cols:
            if col in self.df.columns and col != "report_text":
                self.df[col] = self.df[col].fillna("Unknown")

        # Impute numeric columns with median
        for col in numeric_cols:
            if col in self.df.columns:
                median_val = self.df[col].median()
                self.df[col] = self.df[col].fillna(median_val)

        # Remove rows without narrative report text to eliminate noise for ML/NLP tasks
        if drop_empty_text and "report_text" in self.df.columns:
            self.df = self.df.dropna(subset=["report_text"])

        return self

    def get_cleaned_data(self) -> pd.DataFrame:
        """Return the finalized clean DataFrame with reset index."""
        return self.df.reset_index(drop=True)