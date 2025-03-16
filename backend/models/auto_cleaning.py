import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer

class AutoCleaner:
    """Automatically cleans data by handling missing values, duplicates, and inconsistent formats."""

    def __init__(self):
        """Initialize AutoCleaner."""
        self.imputer = SimpleImputer(strategy="most_frequent")  # ✅ Impute missing values with the most frequent value

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans a DataFrame by:
        1. Handling missing values
        2. Removing duplicate rows
        3. Converting inconsistent data types

        Args:
            df (pd.DataFrame): The input DataFrame.

        Returns:
            pd.DataFrame: Cleaned DataFrame.
        """
        if df.empty:
            raise ValueError("Dataset is empty. Cannot perform cleaning.")

        # ✅ Step 1: Handle Missing Values
        df.replace([np.inf, -np.inf], np.nan, inplace=True)  # Convert infinite values to NaN
        df.fillna(method="ffill", inplace=True)  # Forward Fill as default strategy
        df.fillna(method="bfill", inplace=True)  # Backward Fill as fallback

        # ✅ Step 2: Remove Duplicates
        df.drop_duplicates(inplace=True)

        # ✅ Step 3: Convert Inconsistent Data Types
        for col in df.columns:
            if df[col].dtype == "object":
                try:
                    df[col] = pd.to_datetime(df[col])  # Convert date-like strings to datetime
                except:
                    df[col] = df[col].astype(str)  # Keep as string if conversion fails

        return df