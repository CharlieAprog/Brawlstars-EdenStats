from matplotlib.pyplot import hist
import pandas as pd
import numpy as np

class Player():
    '''
    Class corresponding to a player, contains various info and stats corresponding
    to that player. The entire history of a player in a club is tracked.
    '''
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
        '''
        Helper method to fill team history leading up to the week of entry.
        If a player joins after week 1, the team for the weeks where they were not yet there
        are given a nan value.
        '''
        entry = int(self.entry_week[-1])
        history = {f'week{i}':np.nan for i in range(1,entry)}
        history[self.entry_week] = self.current_team
        return history

    def add_team(self, week, team):
        '''
        Method to add a team to a players team history. If a player rejoins the club after
        a number of weeks of absence the weeks in which the player is not present
        will be filled with nan values.
        '''
        last = int(list(self.team_history.keys())[-1][-1])
        current = int(week[-1])
        fill = {f'week{i}':np.nan for i in range(last + 1,current)}
        self.team_history.update(fill)
        self.team_history[week] = team
        self.current_team = team

    def add_week_scores(self, week, scores):
        '''
        Method that will add weekly scores to a players record. Returns a dataframe with
        weeks as indices and days as columns. After new scores are added, a players personal
        stats are recalculated, according to the new scores.
        '''
        history = self.score_history.copy().T
        history[week] = scores
        self.score_history = history.T
        self.score_history.index.name = self.name
        self._update_player_info()

    def _update_player_info(self):
        '''
        Helper method to call methods to calculate a players stats. Called when scores
        are added to a players score history.
        '''
        self.win_rate = self._calc_win_rate()
        self.coordination_history = self._coordination_overview()
        self.coord_rate = self._calc_coord_rate()
        self.days_not_played = self._count_days_not_played()

    def _coordination_overview(self):
        '''
        Helper method that returns a dataframe with weeks as indices and days as columns.
        The values are either 0 or 1 with 1 indicating that a player played in a team for
        a given game day and a 0 indicating that the player achieve a score that is only possible
        if they did not play in a team.
        '''
        coordination = self.score_history.copy()
        team_socores = [10,14,18]
        team_scores_day3 = [15, 19, 23, 27]
        for c in coordination:
            scores = team_socores if c != 'day3' else team_scores_day3
            activity = [1 if a in scores else 0 if not np.isnan(a) else np.nan for a in coordination[c]]
            coordination[c] = activity
        return coordination

    def _calc_coord_rate(self):
        '''
        Helper method that assumes coordination history has been calculated.
        From the coordination history return the ratio of games played in a team
        over games not played in a team.
        '''
        data = self.coordination_history
        successes = data.sum().sum()
        games = 0
        for c in data.columns:
            games += len(data[c].dropna())
        fails = games - successes if games - successes != 0 else 1
        return round(successes / fails, 3)

    def _calc_win_rate(self):
        '''
        Helper method to calculate the winrate of a player. Wins counted by summing the score of
        game days over the max score of 9. Losses are calculated by subtracting wins from total games
        minus wins minus times not in a team (nans).
        '''
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

    def _count_days_not_played(self):
        '''
        Helper method to return the number of days a player did not participate in
        a game day while assigned to a team.
        '''
        data = self.score_history
        return data[data==0].count().sum()
