import pandas as pd
import os
from utils import UNWANTED
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

    # def create_player_data

    def save_team_data(self):
        path = f'{self.data_path}/02_team_performance'
        self.team_data.to_csv(f'{path}/teams.csv', index=True, sep=',')





if __name__ == '__main__':
    if 'src' not in os.getcwd():
        os.chdir('src')

    collector = ClubStatsTracker('new_eden')
    data = collector.week_data
    players = collector.players
    collector.save_team_data()