from matplotlib.pyplot import hist
import pandas as pd
import numpy as np

class Player():
    def __init__(self, name, entry_week, current_team) -> None:
        self.name = name
        self.entry_week = entry_week
        self.win_rate = 0
        self.coord_rate = 0
        self.days_not_played = 0
        self.current_team = current_team
        self.team_history = self._fill_team_history()
        self.score_history = pd.DataFrame(columns=['day1', 'day2', 'day3'])
        self.coordination_history = pd.DataFrame(columns=['day1', 'day2', 'day3'])

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

    def add_week_scores(self, week, scores):
        history = self.score_history.copy().T
        history[week] = scores
        self.score_history = history.T
        self.score_history.index.name=self.name
        self._update_player_info()


    def _update_player_info(self):
        self.win_rate = self._calc_win_rate()
        self.coordination_history = self._coordination_overview()
        self.coord_rate = self._calc_coord_rate()
        self.days_not_played = self._count_days_not_played()

    def _coordination_overview(self):
        coordination = self.score_history.copy()
        team_socores = [10,14,18]
        team_scores_day3 = [15, 19, 23, 27]
        for c in coordination:
            scores = team_socores if c != 'day3' else team_scores_day3
            activity = [1 if a in scores else 0 if not np.isnan(a) else np.nan for a in coordination[c]]
            coordination[c] = activity
        return coordination

    def _calc_win_rate(self):
        data = self.score_history
        wins = 0
        for week in data.index:
            wins += data.loc[week].apply(np.vectorize(lambda x: int(x/9) if not np.isnan(x) else np.nan)).sum().sum()
        games = 0
        for c in data.columns:
            multiplyer = 2 if c !='day3' else 3
            games += len(data[c].dropna()) * multiplyer
        losses = games - wins if games - wins != 0 else 1
        return round(wins / losses, 3)

    def _calc_coord_rate(self):
        data = self.coordination_history
        successes = data.sum().sum()
        games = 0
        for c in data.columns:
            games += len(data[c].dropna())
        fails = games - successes if games - successes != 0 else 1
        return round(successes / fails, 3)

    def _count_days_not_played(self):
        data = self.score_history
        return data[data==0].count().sum()
