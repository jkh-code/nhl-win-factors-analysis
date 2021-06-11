import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

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
        Two column dataframe with one column containing continuous data 
        and the second column containing 1's for counting each row.
    
    group_col : str
        The name of the column from `df` to aggregate by. This function 
        will only accept one column to aggregate by.
    
    Returns
    -------
    df_agg : pd.DataFrame
        A dataframe with number of wins by group, `num_wins`, cumulative 
        wins, `cum_wins`, total wins, `total`, and cumulative percentage 
        of wins, `cum_perc`.
    """
    df_agg = df.groupby(group_col).sum().reset_index()
    df_agg.rename(columns={'gp': 'num_wins'}, inplace=True)
    df_agg['cum_wins'] = df_agg['num_wins'].cumsum()
    df_agg['total'] = df_agg['num_wins'].sum()
    df_agg['cum_perc'] = df_agg['cum_wins'] / df_agg['total']
    return df_agg

def plot_win_hist(s: pd.Series, title: str, 
        bins: int=20) -> Tuple[plt.Figure, plt.Axes]:
    """Plot a histogram and return figure and axes objects."""
    fig, ax = plt.subplots()
    ax.hist(s, bins=bins)
    ax.set_title(title)
    fig.tight_layout()
    return fig, ax

def plot_win_cum_dist(perc: pd.Series, cum_perc_wins: pd.Series, title: str, 
        ylims: Tuple[int, int]=(-0.05, 1.05)) -> Tuple[plt.Figure, plt.Axes]:
    """Create a cumulative distribution line plot and return figure and 
    axes objects."""
    fig, ax = plt.subplots()
    ax.plot(perc, cum_perc_wins)
    ax.set_ylim(ylims)
    ax.set_title(title)
    fig.tight_layout()
    return fig, ax

def estimate_times_shorthand(pk_percent: float, limit: int=12) -> int:
    """Estimate the number of times a team was shorthand based on the 
    team's penalty kill percentage."""
    if pk_percent in (0.0, 50.0, 100.0):
        return np.nan
    if np.isnan(pk_percent):
        return 0
    
    target = round(100.0 - pk_percent, 1)
    for d in range(2, limit+1):
        for n in range(1, d):
            perc = round(100 * n/d, 1)
            if perc == target:
                return d


if __name__ == '__main__':
    nhl_query = """
                SELECT
                    season, team, game, gp, wins, losses, ot_losses, points,
                    point_percent, reg_wins, reg_ot_wins, so_wins, gf, ga, 
                    gf_per_gp, ga_per_gp, pp_percent, pk_percent, 
                    pp_net_percent, pk_net_percent, sf_per_gp, sa_per_gp, 
                    fo_win_percent
                FROM games
                WHERE season BETWEEN 2009 AND 2018;
                """
    conn = make_postgres_conn('nhl')
    df = pd.read_sql(nhl_query, conn)
    conn.close()

    df.drop(
        ['reg_wins', 'reg_ot_wins', 'so_wins', 'gf_per_gp', 'ga_per_gp', 
            'points', 'point_percent'], 
        axis=1, inplace=True)
    df.insert(
        1, 'date', pd.to_datetime(
            df['game'].str.slice(0, 9+1), format='%Y/%m/%d'))
    df.insert(3, 'home_game', np.where(
        df['game'].str.contains('vs'), 'Home', 'Away'))
    df.insert(4, 'opponent', df['game'].str.slice(-3))
    df.insert(5, 'outcome', np.where(df['wins'] == 1, 'Win', 'Loss'))
    df.insert(13, 'goal_diff', df['gf'] - df['ga'])
    df.insert(20, 'shot_diff', df['sf_per_gp'] - df['sa_per_gp'])
    df.drop(['game'], axis=1, inplace=True)
    df.sort_values(['season', 'team', 'date'], inplace=True)
    df['prev_date'] = df.groupby(['season', 'team'])['date'].shift(1)
    df['days_btwn_games'] = (df['date'] - df['prev_date']).dt.days
    
    # PP percentage influence on number of wins
    pp_data = df.loc[df['outcome']=='Win', ['pp_percent', 'gp']]
    pp_agg = return_aggregate_wins_df(pp_data, 'pp_percent')

    fig, ax = plot_win_hist(pp_data['pp_percent'], 'Number of Wins by Power Play Percent')

    x_labels = range(0, 100+1, 20)
    ax.set_xticks(x_labels)
    ax.set_xticklabels([str(num) + '%' for num in x_labels])

    y_labels = range(0, 5000+1, 1000)
    ax.set_yticks(y_labels)
    ax.set_yticklabels([format(num, ',') for num in y_labels])

    ax.set_xlabel('Percent Successful Power Plays')
    ax.set_ylabel('Wins')

    fig.tight_layout()
    plt.savefig('./images/num-pp-wins.png')

    fig, ax = plot_win_cum_dist(pp_agg['pp_percent'], pp_agg['cum_perc'], 'Cumulative Percent Wins by Power Play Win Percent')

    x_labels = range(0, 100+1, 20)
    ax.set_xticks(x_labels)
    ax.set_xticklabels([str(num) + '%' for num in x_labels])

    y_labels = np.linspace(0, 1, 6)
    ax.set_yticks(y_labels)
    ax.set_yticklabels([f'{num:.0f}%' for num in y_labels * 100])

    ax.set_xlabel('Percent Successful Power Plays')
    ax.set_ylabel('Percent')

    fig.tight_layout()
    plt.savefig('./images/cum-perc-wins-pp.png')

    # Penalty kill percentage influence on wins
    pk_data = df.loc[df['outcome']=='Win', ['pk_percent', 'gp']]
    pk_agg = return_aggregate_wins_df(pk_data, 'pk_percent')

    fig, ax = plot_win_hist(pk_data['pk_percent'], 'Number of Wins by Penalty Kill Percent')

    x_labels = range(0, 100+1, 20)
    ax.set_xticks(x_labels)
    ax.set_xticklabels([str(num) + '%' for num in x_labels])

    y_labels = range(0, 7000+1, 1000)
    ax.set_yticks(y_labels)
    ax.set_yticklabels([format(num, ',') for num in y_labels])

    ax.set_xlabel('Percent Successful Penalty Kills')
    ax.set_ylabel('Wins')

    fig.tight_layout()
    plt.savefig('./images/num-wins-pk.png')

    fig, ax = plot_win_cum_dist(pk_agg['pk_percent'], pk_agg['cum_perc'], 'Cumulative Percent Wins by PK Percent')

    x_labels = range(0, 100+1, 20)
    ax.set_xticks(x_labels)
    ax.set_xticklabels([str(num) + '%' for num in x_labels])

    y_labels = np.linspace(0, 1, 6)
    ax.set_yticks(y_labels)
    ax.set_yticklabels([f'{num:.0f}%' for num in y_labels * 100])

    ax.set_xlabel('Percent Successful Penalty Kills')
    ax.set_ylabel('Percent')

    fig.tight_layout()
    plt.savefig('./images/cum-perc-wins-pk.png')

    # Shots differential influence on wins
    sd_data = df.loc[df['outcome']=='Win', ['shot_diff', 'gp']]
    sd_agg = return_aggregate_wins_df(sd_data, 'shot_diff')

    fig, ax = plot_win_hist(sd_data['shot_diff'], 'Number of Wins by Shot Differential', bins=80)

    ax.set_xlabel('Shot Differential')
    ax.set_ylabel('Wins')

    fig.tight_layout()
    plt.savefig('./images/num-wins-shot-diff.png')

    fig, ax = plot_win_cum_dist(sd_agg['shot_diff'], sd_agg['cum_perc'], 'Cumulative Percent Wins by Shot Differential')

    y_labels = np.linspace(0, 1, 6)
    ax.set_yticks(y_labels)
    ax.set_yticklabels([f'{num:.0f}%' for num in y_labels * 100])

    ax.set_xlabel('Shot Differential')
    ax.set_ylabel('Percent')

    fig.tight_layout()
    plt.savefig('./images/cum-perc-wins-shot-diff.png')

    # Face-Off win percentage influence on winning
    fo_data = df.loc[df['outcome']=='Win', ['fo_win_percent', 'gp']]
    fo_agg = return_aggregate_wins_df(fo_data, 'fo_win_percent')

    fig, ax = plot_win_hist(fo_data['fo_win_percent'], 'Number of Wins by Face-Off Win Percent', bins=75)

    x_labels = range(30, 80+1, 10)
    ax.set_xticks(x_labels)
    ax.set_xticklabels([str(num) + '%' for num in x_labels])

    ax.set_xlabel('Percent Successful Face-Offs')
    ax.set_ylabel('Wins')

    fig.tight_layout()
    plt.savefig('./images/num-face-off-wins.png')

    fig, ax = plot_win_cum_dist(fo_agg['fo_win_percent'], fo_agg['cum_perc'], 'Cumulative Percent Wins by Face-Off Percentage')

    x_labels = range(30, 80+1, 10)
    ax.set_xticks(x_labels)
    ax.set_xticklabels([str(num) + '%' for num in x_labels])

    y_labels = np.linspace(0, 1, 6)
    ax.set_yticks(y_labels)
    ax.set_yticklabels([f'{num:.0f}%' for num in y_labels * 100])

    ax.set_xlabel('Percent Successful Face-Offs')
    ax.set_ylabel('Percent')

    fig.tight_layout()
    plt.savefig('./images/cum-perc-wins-face-off.png')
    