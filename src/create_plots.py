import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from web_scraping import make_postgres_conn

from typing import Tuple

plt.style.use('ggplot')

def num_bins(s: pd.Series) -> int:
    n = np.size(s)
    min_ = np.min(s)
    max_ = np.max(s)
    iqrs = np.percentile(s, [75, 25])
    range_ = iqrs[0] - iqrs[1]
    h = 2 * range_ * np.power(n, -1./3)
    return np.ceil((max_-min_) / h).astype(int)

def return_num_nans(s: pd.Series) -> Tuple[int, int]:
    counts = s.value_counts(dropna=False)
    nans = counts[np.nan]
    total = counts.sum()
    return (nans, total)

def return_aggregate_wins_df(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    """Return Pandas dataframe with aggregated win values.
    
    Parameters
    ----------
    df : pd.DataFrame
        Two column dataframe with one column containing continuous data and the second column containing 1's for counting each row.
    
    group_col : str
        The name of the column from `df` to aggregate by. This function will only accept one column to aggregate by.
    
    Returns
    -------
    df_agg : pd.DataFrame
        A datadrame with number of wins by group, `num_wins`, cumulative wins, `cum_wins`, total wins, `total`, and cumulative percentage of wins, `cum_perc`.
    """
    df_agg = df.groupby(group_col).sum().reset_index()
    df_agg.rename(columns={'gp': 'num_wins'}, inplace=True)
    df_agg['cum_wins'] = df_agg['num_wins'].cumsum()
    df_agg['total'] = df_agg['num_wins'].sum()
    df_agg['cum_perc'] = df_agg['cum_wins'] / df_agg['total']
    return df_agg

def plot_win_hist(s: pd.Series, title: str, bins: int=20) -> Tuple[plt.Figure, plt.Axes]:
    """Plot a histogram and return figure and axes objects."""
    fig, ax = plt.subplots()
    ax.hist(s, bins=bins)
    ax.set_title(title)
    fig.tight_layout()
    return fig, ax

def plot_win_cum_dist(perc: pd.Series, cum_perc_wins: pd.Series, title: str, ylims: Tuple[int, int]=(-0.05, 1.05)) -> Tuple[plt.Figure, plt.Axes]:
    """Create a cumulative distribution line plot and return figure and axes objects."""
    fig, ax = plt.subplots()
    ax.plot(perc, cum_perc_wins)
    ax.set_ylim(ylims)
    ax.set_title(title)
    fig.tight_layout()
    return fig, ax


if __name__ == '__main__':
    pass
