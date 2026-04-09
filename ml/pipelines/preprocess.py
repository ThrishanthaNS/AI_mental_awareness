"""
Data preprocessing pipeline.
"""
import pandas as pd
from typing import Tuple


def load_data(filepath: str) -> pd.DataFrame:
    """Load raw data from file."""
    pass


def clean_text(text: str) -> str:
    """Clean and normalize text data."""
    pass


def preprocess_pipeline(input_path: str, output_path: str):
    """Run the full preprocessing pipeline."""
    pass


if __name__ == "__main__":
    preprocess_pipeline("../data/raw/", "../data/processed/")
