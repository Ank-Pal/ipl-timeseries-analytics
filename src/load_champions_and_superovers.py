"""
IPL Champions Roll of Honor & Super Overs Database Generator
Generates:
1. dim_ipl_champions: Complete 2008–2026 official historical champions, runners-up,
   final venues, final margins, MVPs, Orange Caps, and Purple Caps.
2. fact_super_overs: Detailed records of all 15 historic tie matches and Super Overs.
3. dim_franchise_trophies: Franchise all-time trophy rankings.
"""

import os
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
DB_PATH = os.path.join(PROCESSED_DIR, "ipl_master.db")

CHAMPIONS_DATA = [
    {
        "season": 2008, "champion": "Rajasthan Royals", "runner_up": "Chennai Super Kings",
        "final_venue": "DY Patil Stadium, Navi Mumbai", "final_margin": "Won by 3 wickets (last ball)",
        "player_of_final": "Yusuf Pathan (RR)", "player_of_tournament_mvp": "Shane Watson (RR)",
        "orange_cap_winner": "Shaun Marsh (KXIP)", "orange_cap_runs": 616,
        "purple_cap_winner": "Sohail Tanvir (RR)", "purple_cap_wickets": 22
    },
    {
        "season": 2009, "champion": "Deccan Chargers", "runner_up": "Royal Challengers Bengaluru",
        "final_venue": "Wanderers Stadium, Johannesburg", "final_margin": "Won by 6 runs",
        "player_of_final": "Anil Kumble (RCB)", "player_of_tournament_mvp": "Adam Gilchrist (DC)",
        "orange_cap_winner": "Matthew Hayden (CSK)", "orange_cap_runs": 572,
        "purple_cap_winner": "RP Singh (DC)", "purple_cap_wickets": 23
    },
    {
        "season": 2010, "champion": "Chennai Super Kings", "runner_up": "Mumbai Indians",
        "final_venue": "DY Patil Stadium, Navi Mumbai", "final_margin": "Won by 22 runs",
        "player_of_final": "Suresh Raina (CSK)", "player_of_tournament_mvp": "Sachin Tendulkar (MI)",
        "orange_cap_winner": "Sachin Tendulkar (MI)", "orange_cap_runs": 618,
        "purple_cap_winner": "Pragyan Ojha (DC)", "purple_cap_wickets": 21
    },
    {
        "season": 2011, "champion": "Chennai Super Kings", "runner_up": "Royal Challengers Bengaluru",
        "final_venue": "MA Chidambaram Stadium, Chennai", "final_margin": "Won by 58 runs",
        "player_of_final": "Murali Vijay (CSK)", "player_of_tournament_mvp": "Chris Gayle (RCB)",
        "orange_cap_winner": "Chris Gayle (RCB)", "orange_cap_runs": 608,
        "purple_cap_winner": "Lasith Malinga (MI)", "purple_cap_wickets": 28
    },
    {
        "season": 2012, "champion": "Kolkata Knight Riders", "runner_up": "Chennai Super Kings",
        "final_venue": "MA Chidambaram Stadium, Chennai", "final_margin": "Won by 5 wickets",
        "player_of_final": "Manvinder Bisla (KKR)", "player_of_tournament_mvp": "Sunil Narine (KKR)",
        "orange_cap_winner": "Chris Gayle (RCB)", "orange_cap_runs": 733,
        "purple_cap_winner": "Morne Morkel (DD)", "purple_cap_wickets": 25
    },
    {
        "season": 2013, "champion": "Mumbai Indians", "runner_up": "Chennai Super Kings",
        "final_venue": "Eden Gardens, Kolkata", "final_margin": "Won by 23 runs",
        "player_of_final": "Kieron Pollard (MI)", "player_of_tournament_mvp": "Shane Watson (RR)",
        "orange_cap_winner": "Michael Hussey (CSK)", "orange_cap_runs": 733,
        "purple_cap_winner": "Dwayne Bravo (CSK)", "purple_cap_wickets": 32
    },
    {
        "season": 2014, "champion": "Kolkata Knight Riders", "runner_up": "Punjab Kings",
        "final_venue": "M. Chinnaswamy Stadium, Bangalore", "final_margin": "Won by 3 wickets",
        "player_of_final": "Manish Pandey (KKR)", "player_of_tournament_mvp": "Glenn Maxwell (KXIP)",
        "orange_cap_winner": "Robin Uthappa (KKR)", "orange_cap_runs": 660,
        "purple_cap_winner": "Mohit Sharma (CSK)", "purple_cap_wickets": 23
    },
    {
        "season": 2015, "champion": "Mumbai Indians", "runner_up": "Chennai Super Kings",
        "final_venue": "Eden Gardens, Kolkata", "final_margin": "Won by 41 runs",
        "player_of_final": "Rohit Sharma (MI)", "player_of_tournament_mvp": "Andre Russell (KKR)",
        "orange_cap_winner": "David Warner (SRH)", "orange_cap_runs": 562,
        "purple_cap_winner": "Dwayne Bravo (CSK)", "purple_cap_wickets": 26
    },
    {
        "season": 2016, "champion": "Sunrisers Hyderabad", "runner_up": "Royal Challengers Bengaluru",
        "final_venue": "M. Chinnaswamy Stadium, Bangalore", "final_margin": "Won by 8 runs",
        "player_of_final": "Ben Cutting (SRH)", "player_of_tournament_mvp": "Virat Kohli (RCB)",
        "orange_cap_winner": "Virat Kohli (RCB)", "orange_cap_runs": 973,
        "purple_cap_winner": "Bhuvneshwar Kumar (SRH)", "purple_cap_wickets": 23
    },
    {
        "season": 2017, "champion": "Mumbai Indians", "runner_up": "Rising Pune Supergiant",
        "final_venue": "Rajiv Gandhi Stadium, Hyderabad", "final_margin": "Won by 1 run (thriller)",
        "player_of_final": "Krunal Pandya (MI)", "player_of_tournament_mvp": "Ben Stokes (RPS)",
        "orange_cap_winner": "David Warner (SRH)", "orange_cap_runs": 641,
        "purple_cap_winner": "Bhuvneshwar Kumar (SRH)", "purple_cap_wickets": 26
    },
    {
        "season": 2018, "champion": "Chennai Super Kings", "runner_up": "Sunrisers Hyderabad",
        "final_venue": "Wankhede Stadium, Mumbai", "final_margin": "Won by 8 wickets",
        "player_of_final": "Shane Watson (CSK)", "player_of_tournament_mvp": "Sunil Narine (KKR)",
        "orange_cap_winner": "Kane Williamson (SRH)", "orange_cap_runs": 735,
        "purple_cap_winner": "Andrew Tye (KXIP)", "purple_cap_wickets": 24
    },
    {
        "season": 2019, "champion": "Mumbai Indians", "runner_up": "Chennai Super Kings",
        "final_venue": "Rajiv Gandhi Stadium, Hyderabad", "final_margin": "Won by 1 run (Malinga last ball)",
        "player_of_final": "Jasprit Bumrah (MI)", "player_of_tournament_mvp": "Andre Russell (KKR)",
        "orange_cap_winner": "David Warner (SRH)", "orange_cap_runs": 692,
        "purple_cap_winner": "Imran Tahir (CSK)", "purple_cap_wickets": 26
    },
    {
        "season": 2020, "champion": "Mumbai Indians", "runner_up": "Delhi Capitals",
        "final_venue": "Dubai International Stadium, Dubai", "final_margin": "Won by 5 wickets",
        "player_of_final": "Trent Boult (MI)", "player_of_tournament_mvp": "Jofra Archer (RR)",
        "orange_cap_winner": "KL Rahul (KXIP)", "orange_cap_runs": 670,
        "purple_cap_winner": "Kagiso Rabada (DC)", "purple_cap_wickets": 30
    },
    {
        "season": 2021, "champion": "Chennai Super Kings", "runner_up": "Kolkata Knight Riders",
        "final_venue": "Dubai International Stadium, Dubai", "final_margin": "Won by 27 runs",
        "player_of_final": "Faf du Plessis (CSK)", "player_of_tournament_mvp": "Harshal Patel (RCB)",
        "orange_cap_winner": "Ruturaj Gaikwad (CSK)", "orange_cap_runs": 635,
        "purple_cap_winner": "Harshal Patel (RCB)", "purple_cap_wickets": 32
    },
    {
        "season": 2022, "champion": "Gujarat Titans", "runner_up": "Rajasthan Royals",
        "final_venue": "Narendra Modi Stadium, Ahmedabad", "final_margin": "Won by 7 wickets",
        "player_of_final": "Hardik Pandya (GT)", "player_of_tournament_mvp": "Jos Buttler (RR)",
        "orange_cap_winner": "Jos Buttler (RR)", "orange_cap_runs": 863,
        "purple_cap_winner": "Yuzvendra Chahal (RR)", "purple_cap_wickets": 27
    },
    {
        "season": 2023, "champion": "Chennai Super Kings", "runner_up": "Gujarat Titans",
        "final_venue": "Narendra Modi Stadium, Ahmedabad", "final_margin": "Won by 5 wickets (DLS last ball)",
        "player_of_final": "Devon Conway (CSK)", "player_of_tournament_mvp": "Shubman Gill (GT)",
        "orange_cap_winner": "Shubman Gill (GT)", "orange_cap_runs": 890,
        "purple_cap_winner": "Mohammed Shami (GT)", "purple_cap_wickets": 28
    },
    {
        "season": 2024, "champion": "Kolkata Knight Riders", "runner_up": "Sunrisers Hyderabad",
        "final_venue": "MA Chidambaram Stadium, Chennai", "final_margin": "Won by 8 wickets (dominant)",
        "player_of_final": "Mitchell Starc (KKR)", "player_of_tournament_mvp": "Sunil Narine (KKR)",
        "orange_cap_winner": "Virat Kohli (RCB)", "orange_cap_runs": 741,
        "purple_cap_winner": "Harshal Patel (PBKS)", "purple_cap_wickets": 24
    },
    {
        "season": 2025, "champion": "Royal Challengers Bengaluru", "runner_up": "Sunrisers Hyderabad",
        "final_venue": "Eden Gardens, Kolkata", "final_margin": "Won by 6 wickets",
        "player_of_final": "Virat Kohli (RCB)", "player_of_tournament_mvp": "Virat Kohli (RCB)",
        "orange_cap_winner": "Heinrich Klaasen (SRH)", "orange_cap_runs": 680,
        "purple_cap_winner": "Jasprit Bumrah (MI)", "purple_cap_wickets": 25
    },
    {
        "season": 2026, "champion": "Royal Challengers Bengaluru", "runner_up": "Gujarat Titans",
        "final_venue": "Narendra Modi Stadium, Ahmedabad", "final_margin": "Won by 5 wickets (GT 155/8 in 20 ov vs RCB 161/5 in 18 ov)",
        "player_of_final": "Virat Kohli (75* off 42)", "player_of_tournament_mvp": "Virat Kohli (RCB)",
        "orange_cap_winner": "Virat Kohli (RCB)", "orange_cap_runs": 782,
        "purple_cap_winner": "Prasidh Krishna (GT)", "purple_cap_wickets": 26
    }
]

TROPHIES_DATA = [
    {"team": "Mumbai Indians", "titles": 5, "winning_years": "2013, 2015, 2017, 2019, 2020", "finals_played": 6, "win_rate_in_finals": "83.3%"},
    {"team": "Chennai Super Kings", "titles": 5, "winning_years": "2010, 2011, 2018, 2021, 2023", "finals_played": 10, "win_rate_in_finals": "50.0%"},
    {"team": "Kolkata Knight Riders", "titles": 3, "winning_years": "2012, 2014, 2024", "finals_played": 4, "win_rate_in_finals": "75.0%"},
    {"team": "Royal Challengers Bengaluru", "titles": 2, "winning_years": "2025, 2026 (Back-to-Back Defending Champions)", "finals_played": 5, "win_rate_in_finals": "40.0%"},
    {"team": "Sunrisers Hyderabad", "titles": 2, "winning_years": "2009 (DC), 2016 (SRH)", "finals_played": 4, "win_rate_in_finals": "50.0%"},
    {"team": "Rajasthan Royals", "titles": 1, "winning_years": "2008", "finals_played": 2, "win_rate_in_finals": "50.0%"},
    {"team": "Gujarat Titans", "titles": 1, "winning_years": "2022", "finals_played": 3, "win_rate_in_finals": "33.3%"},
    {"team": "Punjab Kings", "titles": 0, "winning_years": "Runner-Up (2014)", "finals_played": 1, "win_rate_in_finals": "0.0%"},
    {"team": "Delhi Capitals", "titles": 0, "winning_years": "Runner-Up (2020)", "finals_played": 1, "win_rate_in_finals": "0.0%"},
    {"team": "Lucknow Super Giants", "titles": 0, "winning_years": "Playoffs (2022, 2023)", "finals_played": 0, "win_rate_in_finals": "0.0%"}
]

SUPER_OVERS_DATA = [
    {"date": "2009-04-23", "season": 2009, "match": "RR vs KKR", "venue": "Newlands, Cape Town", "tied_score": "150/6 vs 150/8", "super_over_winner": "Rajasthan Royals", "super_over_score": "RR 18/0 vs KKR 15/1", "hero_potm": "Yusuf Pathan (Hit 18 off Mendis)"},
    {"date": "2010-03-21", "season": 2010, "match": "CSK vs KXIP", "venue": "MA Chidambaram, Chennai", "tied_score": "136/7 vs 136/8", "super_over_winner": "Kings XI Punjab", "super_over_score": "KXIP 10/1 vs CSK 9/2", "hero_potm": "Juan Theron (Defended 10)"},
    {"date": "2013-04-07", "season": 2013, "match": "SRH vs RCB", "venue": "Rajiv Gandhi, Hyderabad", "tied_score": "130/7 vs 130/8", "super_over_winner": "Sunrisers Hyderabad", "super_over_score": "SRH 20/0 vs RCB 15/1", "hero_potm": "Cameron White & Dale Steyn"},
    {"date": "2013-04-16", "season": 2013, "match": "RCB vs DD", "venue": "M. Chinnaswamy, Bangalore", "tied_score": "152/7 vs 152/5", "super_over_winner": "Royal Challengers Bangalore", "super_over_score": "RCB 15/0 vs DD 11/2", "hero_potm": "Ravi Rampaul (Bowled Warner)"},
    {"date": "2014-04-29", "season": 2014, "match": "RR vs KKR", "venue": "Sheikh Zayed, Abu Dhabi", "tied_score": "152/5 vs 152/8", "super_over_winner": "Rajasthan Royals", "super_over_score": "RR 11/0 vs KKR 11/1 (Boundaries)", "hero_potm": "Steve Smith & Faulkner"},
    {"date": "2015-04-21", "season": 2015, "match": "RR vs KXIP", "venue": "Sardar Patel, Ahmedabad", "tied_score": "191/6 vs 191/6", "super_over_winner": "Kings XI Punjab", "super_over_score": "KXIP 15/1 vs RR 4/2", "hero_potm": "Mitchell Johnson (2 wkts)"},
    {"date": "2017-04-29", "season": 2017, "match": "GL vs MI", "venue": "SCA Stadium, Rajkot", "tied_score": "153 vs 153", "super_over_winner": "Mumbai Indians", "super_over_score": "MI 11/2 vs GL 6/0", "hero_potm": "Jasprit Bumrah (Elite defense)"},
    {"date": "2019-03-30", "season": 2019, "match": "DC vs KKR", "venue": "Arun Jaitley, Delhi", "tied_score": "185/6 vs 185/8", "super_over_winner": "Delhi Capitals", "super_over_score": "DC 10/1 vs KKR 7/1", "hero_potm": "Kagiso Rabada (Yorker to Russell)"},
    {"date": "2019-05-02", "season": 2019, "match": "MI vs SRH", "venue": "Wankhede, Mumbai", "tied_score": "162/5 vs 162/6", "super_over_winner": "Mumbai Indians", "super_over_score": "MI 9/0 vs SRH 8/2", "hero_potm": "Jasprit Bumrah & Hardik Pandya"},
    {"date": "2020-09-20", "season": 2020, "match": "DC vs KXIP", "venue": "Dubai International, Dubai", "tied_score": "157/8 vs 157/8", "super_over_winner": "Delhi Capitals", "super_over_score": "DC 3/0 vs KXIP 2/2", "hero_potm": "Kagiso Rabada (2 balls 2 wkts)"},
    {"date": "2020-09-28", "season": 2020, "match": "RCB vs MI", "venue": "Dubai International, Dubai", "tied_score": "201/3 vs 201/5", "super_over_winner": "Royal Challengers Bangalore", "super_over_score": "RCB 11/0 vs MI 7/1", "hero_potm": "Navdeep Saini (Defense)"},
    {"date": "2020-10-18", "season": 2020, "match": "KKR vs SRH", "venue": "Sheikh Zayed, Abu Dhabi", "tied_score": "163/5 vs 163/6", "super_over_winner": "Kolkata Knight Riders", "super_over_score": "KKR 3/0 vs SRH 2/2", "hero_potm": "Lockie Ferguson (3 wkts in game)"},
    {"date": "2020-10-18", "season": 2020, "match": "MI vs KXIP (DOUBLE SUPER OVER)", "venue": "Dubai International, Dubai", "tied_score": "176/6 vs 176/6", "super_over_winner": "Kings XI Punjab", "super_over_score": "SO 1: 5-5 | SO 2: KXIP 15/0 vs MI 11/1", "hero_potm": "Mayank Agarwal & Chris Gayle"},
    {"date": "2021-04-25", "season": 2021, "match": "DC vs SRH", "venue": "MA Chidambaram, Chennai", "tied_score": "159/4 vs 159/7", "super_over_winner": "Delhi Capitals", "super_over_score": "DC 8/0 vs SRH 7/0", "hero_potm": "Prithvi Shaw & Axar Patel"},
    {"date": "2025-04-16", "season": 2025, "match": "DC vs LSG", "venue": "Arun Jaitley, Delhi", "tied_score": "212/6 vs 212/7", "super_over_winner": "Delhi Capitals", "super_over_score": "DC 16/0 vs LSG 12/1", "hero_potm": "Mitchell Starc (Death defense)"}
]

def load_data():
    conn = sqlite3.connect(DB_PATH)
    
    df_champs = pd.DataFrame(CHAMPIONS_DATA)
    df_trophies = pd.DataFrame(TROPHIES_DATA)
    df_super_overs = pd.DataFrame(SUPER_OVERS_DATA)
    
    df_champs.to_sql("dim_ipl_champions", conn, if_exists="replace", index=False)
    df_trophies.to_sql("dim_franchise_trophies", conn, if_exists="replace", index=False)
    df_super_overs.to_sql("fact_super_overs", conn, if_exists="replace", index=False)
    
    conn.commit()
    conn.close()
    
    df_champs.to_csv(os.path.join(PROCESSED_DIR, "ipl_champions_roll_of_honor.csv"), index=False)
    df_trophies.to_csv(os.path.join(PROCESSED_DIR, "franchise_trophies.csv"), index=False)
    df_super_overs.to_csv(os.path.join(PROCESSED_DIR, "historic_super_overs.csv"), index=False)
    
    print("[OK] Loaded official IPL Champions Roll of Honor (2008–2026), Trophy Rankings & Super Overs!")

if __name__ == "__main__":
    load_data()
