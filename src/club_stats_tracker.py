import pandas as pd
import numpy as np
import os
from utils import UNWANTED, add_stats
from players import Player
from plotters import plot_player_dataframe, plot_current_week_dataframe

class ClubStatsTracker():
    '''
    Class that saves all of the stats of a specific club.
    This class will read the weekly data and create the team performances and
    the player performances upon initialisation. Afterwards the save_data method
    can be called to make the visuals.
    '''
    def __init__(self, club):
        self.club = club
        self.club_folder = '01_new_eden' if 'new' in club else '02_edens_gate'
        self.data_path = f'../data/{self.club_folder}'
        self.current_week = None
        self.week_data = self._collect_week_data()
        self.team_data = self._create_team_data()
        self.players = self._read_players()
        self.player_data = self._create_player_data()

    def _collect_week_data(self):
        '''
        Method to make a dataframe containing the info from the weekly data
        for each week. The result is a dict with the weeks as keys and dataframes
        containing the weekly info as values.
        '''
        week_data = {}
        week_path = f'{self.data_path}/03_weekly_data'
        weeks = sorted([file for file in os.listdir(week_path) if not any(un in file for un in UNWANTED)])
        weeks = sorted(weeks, key=lambda x: int(x.split('-')[0].split('k')[1]))
        self.current_week = f'week{len(weeks)}'
        for week_file in weeks:
            week = week_file.split('-')[0]
            week_data[week] = pd.read_csv(f'{week_path}/{week_file}')
        return week_data

    def _create_team_data(self):
        '''
        Method that will use the weekly data dict and crate a new dataframe with the summed performance
        of each team in each column.
        '''
        team_data = pd.DataFrame()
        for week_num, data in self.week_data.items():
            data = data.copy()
            data['sum'] = data.loc[:,'day1':'day3'].sum(axis=1)
            team_data[week_num] = data[['team','sum']].groupby(['team']).sum()
        return team_data

    def _read_players(self):
        '''
        Method that initialises all players that occur in the data. Creates a dict
        of Player classes with the names of the players as keys. (each player gets the current team
        attribute based on the most recent weekly data file. If a player does not appear in the
        most recent weekly data file, that player will be given the team 'inactive')
        '''
        player_dict = {}
        for week_num, data in self.week_data.items():
            for player_name in data['player']:
                current_team = data['team'][data['player'] == player_name].values[0]
                if player_name not in player_dict.keys():
                    player_dict[player_name] = Player(player_name, week_num, current_team)
                else:
                    player_dict[player_name].add_team(week_num, current_team)
        player_dict = self._remove_player_teams(player_dict)
        return player_dict

    def _remove_player_teams(self, players):
        '''
        Method called by '_read_players' to set all players that are not in the current week to inactive.
        '''
        for player_name in players:
            if player_name not in self.week_data[self.current_week]['player'].values:
                players[player_name].current_team = 'inactive'
        return players

    def _collect_current_teams(self, player_data):
        '''
        Method called before visualisation, adds current team of players to
        player_data.
        '''
        teams = []
        for player in player_data.index:
            teams.append(self.players[player].current_team)
        player_data.insert(loc=0, column='current_team',value=teams)
        return player_data

    def _remove_inactive_players(self, player_data):
        '''
        Method called before visualisation to remove inactive players from player_data
        so they wont be considered in plots.
        '''
        return player_data[player_data['current_team'] != 'inactive'].copy()

    def _add_rates(self, df):
        '''
        Adding calculations to player_data.
        '''
        df = df.copy()
        win_rates, coord_rates, days_not_played = [], [], []
        for name in df.index:
            player = self.players[name]
            win_rates.append(player.win_rate)
            coord_rates.append(player.coord_rate)
            days_not_played.append(player.days_not_played)

        df['win_rate'] = win_rates
        df['teaming_rate'] = coord_rates
        df['no_shows'] = days_not_played
        return df

    def _finalise_player_data(self, player_data):
        '''
        Method used to add relevant columns to player_data.
        '''
        player_data = self._collect_current_teams(player_data)
        player_data = add_stats(player_data, axis=1, descriptive_cols=1)
        player_data = self._add_rates(player_data)
        player_data = self._remove_inactive_players(player_data)
        player_data = player_data.sort_values(by='current_team')
        return player_data

    def _create_player_data(self):
        '''
        Method that creates a dataframe with information of summed weekly performance of all players.
        Weeks are columns and player names are index. If player not in current week, add
        nan instead of performance.
        '''
        player_names = list(self.players.keys())
        player_data = pd.DataFrame(index=player_names)
        player_data.index.name = 'player'
        for week_num, data in self.week_data.items():
            data = data.copy().set_index('player')
            scores = []
            for name in player_names:
                if name in data.index.values:
                    player_scores = data.loc[name,'day1':'day3']
                    scores.append(int(player_scores.sum()))
                    self.players[name].add_week_scores(week_num, player_scores.values)
                else:
                    scores.append(np.nan)
                    self.players[name].add_week_scores(week_num, [np.nan] * 3)
            player_data[week_num] = scores
        return self._finalise_player_data(player_data)

    def save_data(self):
        '''
        Method to call plotting functions that will create and save plots.
        '''
        player_path = f'{self.data_path}/01_player_performance'
        team_path = f'{self.data_path}/02_team_performance'
        self.player_data.to_csv(f'{player_path}/players_{self.club}.csv', index=True, sep=',')
        self.team_data.to_csv(f'{team_path}/teams_{self.club}.csv', index=True, sep=',')
        plot_player_dataframe(self.player_data, self.club_folder)
        plot_current_week_dataframe(self.current_week, self.week_data, self.club_folder)


if __name__ == '__main__':
    if 'src' not in os.getcwd():
        os.chdir('src')

    new = ClubStatsTracker('new_eden')
    gate = ClubStatsTracker('edens_gate')

    new.save_data()
    gate.save_data()
