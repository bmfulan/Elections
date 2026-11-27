# src/plots.py
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

FIGURES_DIR = Path(__file__).resolve().parent.parent / 'figures'


def _save(fig, outfile):
    outfile.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(outfile, dpi=200, bbox_inches='tight')
    plt.close(fig)


def _annotate_corr(data, **kws):
    r = data['Previous Swing'].corr(data['D Adj Margin Swing'])
    plt.gca().text(0.05, 0.85, f"r = {r:.2f}", transform=plt.gca().transAxes,
                   fontsize=11, weight='bold',
                   bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))


def plot_swing_autocorrelation(autocorr_df, outfile=FIGURES_DIR / 'swing_autocorrelation.png'):
    correlation = autocorr_df['Previous Swing'].corr(autocorr_df['D Adj Margin Swing'])
    g = sns.FacetGrid(autocorr_df, col='Year', col_wrap=3, height=2.6, aspect=1.2, sharex=False, sharey=False)
    g.set(xlim=(-15, 15), ylim=(-15, 15))
    g.map_dataframe(sns.regplot, x='Previous Swing', y='D Adj Margin Swing', ci=None, truncate=False,
        scatter_kws={'alpha': 0.5, 'color': 'purple', 'edgecolor': 'w'},
        line_kws={'color': 'black', 'linewidth': 2})
    g.map_dataframe(_annotate_corr)

    # Iterate through the dictionary of axes (key = Year, value = matplotlib Axis)
    for year, ax in g.axes_dict.items():
        year = int(year)
        
        # Construct and apply the dynamic labels
        ax.set_xlabel(f"{year - 8}-{year - 4} Swing (%)", fontsize=10)
        ax.set_ylabel(f"{year - 4}-{year} Swing (%)", fontsize=10)
        
        # Clean up the title to just show the focal election year
        ax.set_title(f"{year} Election", weight='bold')
        
        # Add zero-line crosshairs
        ax.axhline(0, color='gray', linestyle='--', linewidth=1)
        ax.axvline(0, color='gray', linestyle='--', linewidth=1)

    g.figure.subplots_adjust(top=0.9, hspace=0.6, wspace=0.6)
    g.figure.suptitle(f"Year-by-Year State Swing Autocorrelation; Overall Autocorrelation: r = {correlation:.2f}", fontsize=16, weight='bold')

    _save(g.figure, outfile)


def plot_state_margins(df, outfile=None):
    # Currently set up for only Wisconsin - have to modify if I want to generalize to other states
    wi = df[df['State'] == 'Wisconsin']

    # Reshape from wide (two margin columns) to long (one 'Measure' column, one value column)
    wi_long = wi.melt(
        id_vars='Year',
        value_vars=['D Raw Margin', 'D Adj Margin'],
        var_name='Measure',
        value_name='Margin (percentage points)'
    )

    wi_long['Measure'] = wi_long['Measure'].replace({
        'D Raw Margin' : 'Democratic Raw Margin',
        'D Adj Margin' : 'Democratic Adjusted Margin'
    })

    fig, ax = plt.subplots(figsize=(10, 6))
    g = sns.lineplot(
        ax=ax,
        data=wi_long,
        x='Year',
        y='Margin (percentage points)',
        hue='Measure',
        marker='o',
        linewidth=2
    )

    # Shade the gap between the two lines (this gap is the national margin each year)
    g.fill_between(wi['Year'], wi['D Raw Margin'], wi['D Adj Margin'], alpha=0.12, color='gray')

    # Zero line: above = Democratic, below = Republican
    g.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.7)

    g.set_xticks(sorted(wi['Year'].unique()))
    g.tick_params(axis='x', rotation=45)
    g.set_title("Wisconsin: Raw vs. Adjusted Democratic Two-Party Margin, 1980-2024")
    plt.tight_layout()
    _save(fig, outfile or FIGURES_DIR / 'wisconsin_raw_vs_adjusted.png')


def plot_adj_margin_heatmap(df, outfile=None):
    # Remove DC since it skews the colors
    df = df[df['State'] != 'District of Columbia'].copy()

    # Pivot the long-format data into a wide matrix for the heatmap
    heatmap_data = df.pivot(index='State', columns='Year', values='D Adj Margin')

    # Configure the visualization canvas
    fig, ax = plt.subplots(figsize=(12, 13.5))

    # Generate the heatmap
    # 'RdBu' maps negative numbers to Red (Republican swing) and positive to Blue (Dem swing)
    g = sns.heatmap(
        ax=ax,
        data=heatmap_data, 
        cmap='RdBu', 
        center=0,          # Anchors the color white at exactly 0.0 swing
        annot=True,        # Displays the actual numeric value in the cell
        fmt=".1f",         # Formats the decimal places
        linewidths=0.5     # Adds gridlines between cells
    )

    g.set_title("State-by-State Democratic Adjusted Margin, 1980-2024")
    g.set_xlabel("Election Year")
    g.set_ylabel("State")
    plt.tight_layout()
    _save(fig, outfile or FIGURES_DIR / 'adj_margin_heatmap.png')