from matplotlib import cm
import dataframe_image as dfi
import pandas as pd
import itertools

RED_GREEN = cm.get_cmap('RdYlGn')
RED_GREEN_r = cm.get_cmap('RdYlGn_r')

YELLOW_GREEN = cm.get_cmap('summer_r')
GREEN_YELLOW = cm.get_cmap('summer')
PLOT_PATH = '../plots'

def plot_player_dataframe(player_data, club_folder):
    '''
    Function to create a styled dataframe to plot the player scores over all weeks.
    '''
    weeks = [c for c in player_data.columns if 'week' in c]
    cols = weeks + ['ave', 'win_rate','teaming_rate']
    formats = {col:'{:20,.2f}' for col in cols}
    styled_players= player_data.style.format(formats)\
            .bar(subset=weeks, color='lightgreen', vmin=0, vmax=63)\
            .background_gradient(axis=0,vmin=0, subset=['ave'],cmap=RED_GREEN)\
            .background_gradient(axis=0,vmin=0,vmax=2, subset=['win_rate'],cmap=RED_GREEN)\
            .background_gradient(axis=0,vmin=0,vmax=3, subset=['teaming_rate'],cmap=RED_GREEN)\
            .background_gradient(axis=0,vmin=0,vmax=6, subset=['no_shows' ],cmap=RED_GREEN_r)\
            .set_properties(subset=weeks, **{'width': '50px'})

    styled_players.set_table_styles({
            'ave': [{'selector': '', 'props': 'border-left: 1px solid black'}],
                    },
                        overwrite=False, axis=0)
    dfi.export(styled_players, f'{PLOT_PATH}/{club_folder}/players/{weeks[-1]}.png')

def plot_current_week_dataframe(current_week, week_data, club_folder):
    '''
    Function to plot a styled dataframe for a certain week.
    '''
    week = week_data[current_week].copy()
    week = week.set_index(['team','player'])
    days = ['day1','day2','day3']
    columns = list(itertools.product([current_week], days))
    week.columns = pd.MultiIndex.from_tuples(columns)
    week.columns.names = ['Week', 'Day']

    styled_week = week.style\
        .background_gradient(axis=0,vmin=0, vmax=18, subset=[(current_week,'day1'),(current_week,'day2')],cmap=RED_GREEN)\
        .background_gradient(axis=0,vmin=0, vmax=27, subset=[(current_week,'day3')],cmap=RED_GREEN)
    for team in range(1, 11):
        styled_week.set_table_styles({(team, week.loc[team].index[0]): [{'selector': '', 'props': 'border-bottom: 1px solid black'}],
                            (team, week.loc[team].index[1]): [{'selector': '', 'props': 'border-bottom: 1px solid black'}],
                            (team, week.loc[team].index[2]): [{'selector': '', 'props': 'border-bottom: 1px solid black'}]},
                        overwrite=False, axis=1)
    for team in range(1, 11):
        styled_week.set_table_styles({(team, week.loc[team].index[2]): [{'selector': '', 'props': 'border-bottom: 2px solid black'}],
                            (team, week.loc[team].index[0]): [{'selector': '.level0', 'props': 'border-bottom: 2px solid black'}]},
                        overwrite=False, axis=1)
    styled_week.set_table_styles({
        (current_week, 'day1'): [{'selector': 'th', 'props': 'border-left: 1px solid white'},
                                {'selector': 'td', 'props': 'border-left: 1px solid #000066'}]},
                        overwrite=False)
    dfi.export(styled_week, f'{PLOT_PATH}/{club_folder}/weeks/{current_week}.png')
