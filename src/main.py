import os
import pandas as pd
from club_stats_tracker import ClubStatsTracker

def main():
    new = ClubStatsTracker('new_eden')
    gate = ClubStatsTracker('edens_gate')

    new.save_data()
    gate.save_data()



if __name__ == '__main__':
    if 'src' not in os.getcwd():
        os.chdir('src')
    main()
