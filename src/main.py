# src/main.py
from data import load_data
from analysis import autocorrelation_data, state_results
from plots import plot_swing_autocorrelation, plot_state_margins, plot_adj_margin_heatmap

if __name__ == '__main__':
    df = load_data()
    plot_swing_autocorrelation(autocorrelation_data(df, exclude_years=[1988]))
    plot_state_margins(df, 'Wisconsin')
    plot_adj_margin_heatmap(state_results(df))