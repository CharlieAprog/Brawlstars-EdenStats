import pandas as pd

class Player():
    def __init__(self, name, entry_week, current_team) -> None:
        self.name = name
        self.enty_week = entry_week
        self.ratio = 0
        self.current_team = current_team
