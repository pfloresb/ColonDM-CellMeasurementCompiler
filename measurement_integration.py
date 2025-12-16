# Author: Patricio Flores-Bringas
# Date: 2025-12-16
# Description: Script to convert CellProfiler output to average counts per condition
import pandas as pd
import numpy as np
import argparse
import os
import sys

# Reading in CSV and processing (mean + SEM)
from pathlib import Path
from IPython.display import display

def read_csv(file_path):
    """Read a CSV file into a pandas DataFrame. Exits on failure."""
    try:
        data = pd.read_csv(file_path)
        return data
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        sys.exit(1)

def process_data(data, condition_cols, measure_col):
    """Group rows by one or more condition columns and compute mean, count, std, and sem."""
    try:
        if isinstance(condition_cols, str):
            cols = [c.strip() for c in condition_cols.split(',') if c.strip()]
        else:
            cols = list(condition_cols)

        agg = data.groupby(cols)[measure_col].agg(['mean', 'count', 'std']).reset_index()
        agg['sem'] = agg.apply(lambda r: (r['std'] / (np.sqrt(r['count']))) if r['count'] > 0 else np.nan, axis=1)
        agg = agg.rename(columns={'mean': f'{measure_col}_mean', 'count': f'{measure_col}_n', 'std': f'{measure_col}_std', 'sem': f'{measure_col}_sem'})
        return agg
    except Exception as e:
        print(f"Error processing data: {e}")
        sys.exit(1)

def process_matching_day_condition(data, day_col, cond_col, measure_col):
    """Filter rows where day_col == cond_col, then compute mean, n, std, sem grouped by that shared value."""
    try:
        # Find actual column names (allow for small typos)
        def find_column(df, requested):
            if requested in df.columns:
                return requested
            # case-insensitive match
            lower_map = {c.lower(): c for c in df.columns}
            if requested.lower() in lower_map:
                return lower_map[requested.lower()]
            # fuzzy match
            import difflib
            matches = difflib.get_close_matches(requested, df.columns, n=1, cutoff=0.7)
            if matches:
                return matches[0]
            return None

        day_actual = find_column(data, day_col)
        cond_actual = find_column(data, cond_col)
        if day_actual is None or cond_actual is None:
            print('Could not find columns requested. Available columns:')
            print(list(data.columns))
            return pd.DataFrame()

        # Ensure string comparison to avoid dtype issues
        mask = data[day_actual].astype(str) == data[cond_actual].astype(str)
        filtered = data[mask].copy()
        if filtered.empty:
            print(f'No rows where {day_col} == {cond_col}')
            return pd.DataFrame()

        agg = filtered.groupby(day_col)[measure_col].agg(['mean', 'count', 'std']).reset_index()
        agg['sem'] = agg.apply(lambda r: (r['std'] / (np.sqrt(r['count']))) if r['count'] > 0 else np.nan, axis=1)
        agg = agg.rename(columns={'mean': f'{measure_col}_mean', 'count': f'{measure_col}_n', 'std': f'{measure_col}_std', 'sem': f'{measure_col}_sem'})
        return agg
    except Exception as e:
        print(f"Error in process_matching_day_condition: {e}")
        raise

def write_csv(data, output_path):
    try:
        data.to_csv(output_path, index=False)
        print(f"Output written to {output_path}")
    except Exception as e:
        print(f"Error writing to {output_path}: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Convert CellProfiler output to average counts per condition (and SEM)")
    parser.add_argument("input_csv", help="Path to input CSV file from CellProfiler")
    parser.add_argument("output_csv", help="Path to output CSV file")
    parser.add_argument("condition_col", help="Column name for conditions. For multiple columns, provide a comma-separated list (e.g. Metadata_Day,Metadata_Condition)")
    parser.add_argument("measure_col", help="Column name for measurements to average (e.g. Count_Cells)")

    args = parser.parse_args()

    data = read_csv(args.input_csv)
    processed_data = process_data(data, args.condition_col, args.measure_col)
    write_csv(processed_data, args.output_csv)

main()

