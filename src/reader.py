import pandas as pd
import os
# from utils import UNWANTED


class DataCollector():
    def __init__(self, club):
        self.club = club
        self.club_folder = '01_new_eden' if 'new' in club else '02_edens_gate'
        self.data_path = f'../data/{self.club_folder}'
        self.current_week = None
        self.week_data = self._collect_week_data()

    def _collect_week_data(self):
        week_data = {}
        week_path = f'{self.data_path}/03_weekly_data'
        weeks = [file for file in os.listdir(week_path) if not any(un in file for un in ['.DS'])]
        self.current_week = len(weeks)
        for week_file in weeks:
            week = week_file.split('-')[0]
            week_data[week] = pd.read_csv(f'{week_path}/{week_file}')
        return week_data


if __name__ == '__main__':
    if 'src' not in os.getcwd():
        os.chdir('src')

    collector = DataCollector('new_eden')
    print(collector.current_week)

    print('hello')
