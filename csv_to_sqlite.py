#!/usr/bin/env python3
"""Convert `combined_table.csv` into an SQLite database `combined_table.db`.

This script:
- reads `combined_table.csv` from the repo root
- attempts to coerce numeric columns to numeric dtypes where appropriate
- writes a single table named `combined_table` into `combined_table.db`
- creates a simple index on `name` to speed lookups

Run: python3 csv_to_sqlite.py
"""
from pathlib import Path
import pandas as pd
import sqlite3

ROOT = Path(__file__).resolve().parent
CSV = ROOT / 'combined_table.csv'
DB = ROOT / 'combined_table.db'


def coerce_numeric_columns(df, threshold=0.8):
    """Attempt to convert columns to numeric if a high fraction of values convert.

    threshold: fraction of non-null values after coercion required to accept numeric conversion.
    """
    for col in df.columns:
        # Try to parse numeric values
        try:
            conv = pd.to_numeric(df[col], errors='coerce')
        except Exception:
            continue
        non_null_ratio = conv.notna().mean()
        if non_null_ratio >= threshold:
            df[col] = conv
    return df


def main():
    if not CSV.exists():
        print(f'Error: {CSV} not found')
        return

    # Read CSV using pandas (latin1 fallback not needed here but safe)
    try:
        df = pd.read_csv(CSV, encoding='utf-8', on_bad_lines='skip')
    except Exception:
        df = pd.read_csv(CSV, encoding='latin1', on_bad_lines='skip')

    # Coerce numeric-like columns (if any) to numeric types
    df = coerce_numeric_columns(df, threshold=0.8)

    # Connect to SQLite and write table
    conn = sqlite3.connect(DB)
    try:
        df.to_sql('combined_table', conn, if_exists='replace', index=False)
        # Create a small index on name for faster lookups
        try:
            conn.execute('CREATE INDEX IF NOT EXISTS idx_combined_name ON combined_table(name);')
        except Exception:
            pass
        conn.commit()
    finally:
        conn.close()

    print(f'Wrote SQLite DB: {DB} (table: combined_table, rows: {len(df)})')


if __name__ == '__main__':
    main()
