from matplotlib.pyplot import hist
import pandas as pd
import numpy as np

class Player():
    def __init__(self, name, entry_week, current_team) -> None:
        self.name = name
        self.entry_week = entry_week
        self.ratio = 0
        self.current_team = current_team
        self.team_history = self._fill_team_history()

    def _fill_team_history(self):
        entry = int(self.entry_week[-1])
        history = {f'week{i}':np.nan for i in range(1,entry)}
        history[self.entry_week] = self.current_team
        return history

    def add_team(self, week, team):
        last = int(list(self.team_history.keys())[-1][-1])
        current = int(week[-1])
        fill = {f'week{i}':np.nan for i in range(last + 1,current)}
        self.team_history.update(fill)
        self.team_history[week] = team
        self.current_team = team
