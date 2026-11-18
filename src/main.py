# src/main.py
from data import load_data
from analysis import autocorrelation_data
from plots import plot_swing_autocorrelation, plot_state_margins

if __name__ == '__main__':
    df = load_data()
    plot_swing_autocorrelation(autocorrelation_data(df, exclude_years=[1988]))
    plot_state_margins(df, 'Wisconsin')