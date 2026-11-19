# src/analysis.py
import pandas as pd


def state_results(df):
    """Remove the national 'Totals' rows."""
    return df[df['State'] != 'Totals'].copy()


def swing_data(df):
    """State rows without 1980 (no prior election, so no swing)."""
    out = state_results(df)
    return out[out['Year'] != 1980].sort_values(['State', 'Year']).copy()


def autocorrelation_data(df, exclude_years=()):
    """Pair each state's swing with its previous swing."""
    swing = swing_data(df)
    swing['Previous Swing'] = swing.groupby('State')['D Adj Margin Swing'].shift(1)
    out = swing.dropna(subset=['Previous Swing', 'D Adj Margin Swing'])
    return out[~out['Year'].isin(exclude_years)].copy()


def swing_summary_by_state(df):
    return (swing_data(df).groupby('State')['D Adj Margin Swing'].agg(['mean', 'std']).reset_index())