import pandas as pd
import numpy as np
import os
from utils import UNWANTED, add_stats
from players import Player


class ClubStatsTracker():
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
        week_data = {}
        week_path = f'{self.data_path}/03_weekly_data'
        weeks = [file for file in os.listdir(week_path) if not any(un in file for un in UNWANTED)]
        self.current_week = len(weeks)
        for week_file in weeks:
            week = week_file.split('-')[0]
            week_data[week] = pd.read_csv(f'{week_path}/{week_file}')
        return week_data

    def _create_team_data(self):
        team_data = pd.DataFrame()
        for week_num, data in self.week_data.items():
            data = data.copy()
            data['sum'] = data.loc[:,'day1':'day3'].sum(axis=1)
            team_data[week_num] = data[['team','sum']].groupby(['team']).sum()
        return team_data

    def _read_players(self):
        player_dict = {}
        for week_num, data in self.week_data.items():
            for player_name in data['player']:
                current_team = data['team'][data['player'] == player_name].values[0]
                if player_name not in player_dict.keys():
                    player_dict[player_name] = Player(player_name, week_num, current_team)
                else:
                    player_dict[player_name].add_team(week_num, current_team)
        return player_dict

    def _collect_current_teams(self, player_data):
        teams = []
        for player in player_data.index:
            teams.append(self.players[player].current_team)
        player_data.insert(loc=0, column='current_team',value=teams)
        return player_data

    def _add_rates(self, df):
        df = df.copy()
        win_rates, coord_rates, days_not_played = [], [], []
        for name in df.index:
            player = self.players[name]
            win_rates.append(player.win_rate)
            coord_rates.append(player.coord_rate)
            days_not_played.append(player.days_not_played)

        df['win_rate'] = win_rates
        df['team_coordination_rate'] = coord_rates
        df['days_not_played'] = days_not_played
        return df

    def _create_player_data(self):
        player_names = list(self.players.keys())
        player_data = pd.DataFrame(index=player_names)
        player_data.index.name = 'player'
        for week_num, data in self.week_data.items():
            data = data.copy().set_index('player')
            scores = []
            for name in player_names:
                if name in data.index.values:
                    player_scores = data.loc[name,'day1':'day3']
                    scores.append(player_scores.sum())
                    self.players[name].add_week_scores(week_num, player_scores.values)
                else:
                    scores.append(np.nan)
                    self.players[name].add_week_scores(week_num, [np.nan] * 3)
            player_data[week_num] = scores

        player_data = self._collect_current_teams(player_data)
        player_data = add_stats(player_data, axis=1, descriptive_cols=1)
        player_data = self._add_rates(player_data)
        return player_data.sort_values(by=['ave','current_team'], ascending=False)

    def save_data(self):
        player_path = f'{self.data_path}/01_player_performance'
        team_path = f'{self.data_path}/02_team_performance'
        self.player_data.to_csv(f'{player_path}/players.csv', index=True, sep=',')
        self.team_data.to_csv(f'{team_path}/teams.csv', index=True, sep=',')





if __name__ == '__main__':
    if 'src' not in os.getcwd():
        os.chdir('src')

    collector = ClubStatsTracker('new_eden')
    data = collector.week_data
    players = collector.players
    collector.save_data()
