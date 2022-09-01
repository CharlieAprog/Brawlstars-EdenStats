import os
import pandas as pd
from src.club_stats_tracker import ClubStatsTracker

def main():

    new = ClubStatsTracker('new_eden')
    gate = ClubStatsTracker('edens_gate')
    print('next')
    new.save_data()
    gate.save_data()



if __name__ == '__main__':
    main()
