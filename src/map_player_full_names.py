"""
Player Full Name Mapper & Enrichment Engine
Maps CricSheet abbreviated names (e.g. RG Sharma, V Kohli, MS Dhoni, R Sharma)
to authentic official full names, preventing ambiguity between players like Rohit Sharma vs Rahul Sharma.
"""

import os
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
DB_PATH = os.path.join(PROCESSED_DIR, "ipl_master.db")

# Comprehensive dictionary mapping CricSheet names to official full cricket names
PLAYER_FULL_NAME_MAP = {
    # Star Batters & All-rounders
    "RG Sharma": "Rohit Sharma",
    "R Sharma": "Rahul Sharma",
    "V Kohli": "Virat Kohli",
    "MS Dhoni": "MS Dhoni",
    "S Dhawan": "Shikhar Dhawan",
    "DA Warner": "David Warner",
    "SK Raina": "Suresh Raina",
    "KL Rahul": "KL Rahul",
    "AM Rahane": "Ajinkya Rahane",
    "AB de Villiers": "AB de Villiers",
    "CH Gayle": "Chris Gayle",
    "RV Uthappa": "Robin Uthappa",
    "SV Samson": "Sanju Samson",
    "KD Karthik": "Dinesh Karthik",
    "F du Plessis": "Faf du Plessis",
    "SA Yadav": "Suryakumar Yadav",
    "AT Rayudu": "Ambati Rayudu",
    "JC Buttler": "Jos Buttler",
    "G Gambhir": "Gautam Gambhir",
    "Shubman Gill": "Shubman Gill",
    "MK Pandey": "Manish Pandey",
    "SS Iyer": "Shreyas Iyer",
    "SR Watson": "Shane Watson",
    "RR Pant": "Rishabh Pant",
    "KA Pollard": "Kieron Pollard",
    "Q de Kock": "Quinton de Kock",
    "RA Jadeja": "Ravindra Jadeja",
    "YK Pathan": "Yusuf Pathan",
    "Ishan Kishan": "Ishan Kishan",
    "DA Miller": "David Miller",
    "WP Saha": "Wriddhiman Saha",
    "BB McCullum": "Brendon McCullum",
    "N Rana": "Nitish Rana",
    "PA Patel": "Parthiv Patel",
    "HH Pandya": "Hardik Pandya",
    "GJ Maxwell": "Glenn Maxwell",
    "MA Agarwal": "Mayank Agarwal",
    "Yuvraj Singh": "Yuvraj Singh",
    "V Sehwag": "Virender Sehwag",
    "AD Russell": "Andre Russell",
    "M Vijay": "Murali Vijay",
    "RD Gaikwad": "Ruturaj Gaikwad",
    "SPD Smith": "Steve Smith",
    "SE Marsh": "Shaun Marsh",
    "JH Kallis": "Jacques Kallis",
    "DR Smith": "Dwayne Smith",
    "YBK Jaiswal": "Yashasvi Jaiswal",
    "N Pooran": "Nicholas Pooran",
    "SR Tendulkar": "Sachin Tendulkar",
    "RA Tripathi": "Rahul Tripathi",
    "R Dravid": "Rahul Dravid",
    "SO Hetmyer": "Shimron Hetmyer",
    "H Klaasen": "Heinrich Klaasen",
    "TM Head": "Travis Head",
    "LS Livingstone": "Liam Livingstone",
    "C Green": "Cameron Green",
    "TH David": "Tim David",
    "Rinku Singh": "Rinku Singh",
    "Tilak Varma": "Tilak Varma",
    "Abhishek Sharma": "Abhishek Sharma",
    "Ashutosh Sharma": "Ashutosh Sharma",
    "Shashank Singh": "Shashank Singh",
    "JM Sharma": "Jitesh Sharma",
    "Jitesh Sharma": "Jitesh Sharma",
    "Prabhsimran Singh": "Prabhsimran Singh",
    "B Sai Sudharsan": "Sai Sudharsan",
    "Sai Sudharsan": "Sai Sudharsan",
    "R Parag": "Riyan Parag",
    "D Padikkal": "Devdutt Padikkal",
    "VR Iyer": "Venkatesh Iyer",
    "RM Patidar": "Rajat Patidar",
    "Abishek Porel": "Abishek Porel",
    "Dhruv Jurel": "Dhruv Jurel",
    "Anuj Rawat": "Anuj Rawat",
    "Ayush Badoni": "Ayush Badoni",
    "Nehal Wadhera": "Nehal Wadhera",
    "N Wadhera": "Nehal Wadhera",
    "Sameer Rizvi": "Sameer Rizvi",
    "JFM McGurk": "Jake Fraser-McGurk",
    "R Powell": "Rovman Powell",
    "MEK Hussey": "Michael Hussey",
    "AC Gilchrist": "Adam Gilchrist",
    "ML Hayden": "Matthew Hayden",
    "KP Pietersen": "Kevin Pietersen",
    "SC Ganguly": "Sourav Ganguly",
    "DPMD Jayawardene": "Mahela Jayawardene",
    "KC Sangakkara": "Kumar Sangakkara",
    "EJG Morgan": "Eoin Morgan",
    "CA Lynn": "Chris Lynn",
    "BA Stokes": "Ben Stokes",
    "MM Ali": "Moeen Ali",
    "SM Curran": "Sam Curran",
    "C de Grandhomme": "Colin de Grandhomme",
    "MP Stoinis": "Marcus Stoinis",
    "KM Jadhav": "Kedar Jadhav",
    "STR Binny": "Stuart Binny",
    "KK Nair": "Karun Nair",
    "Mandeep Singh": "Mandeep Singh",
    "Gurkeerat Singh": "Gurkeerat Singh Mann",
    "DJ Hooda": "Deepak Hooda",
    "Washington Sundar": "Washington Sundar",
    "Shahbaz Ahmed": "Shahbaz Ahmed",
    "Krunal Pandya": "Krunal Pandya",
    "KH Pandya": "Krunal Pandya",

    # Legendary Bowlers
    "YS Chahal": "Yuzvendra Chahal",
    "B Kumar": "Bhuvneshwar Kumar",
    "SP Narine": "Sunil Narine",
    "PP Chawla": "Piyush Chawla",
    "JJ Bumrah": "Jasprit Bumrah",
    "R Ashwin": "Ravichandran Ashwin",
    "DJ Bravo": "Dwayne Bravo",
    "A Mishra": "Amit Mishra",
    "SL Malinga": "Lasith Malinga",
    "Rashid Khan": "Rashid Khan",
    "Sandeep Sharma": "Sandeep Sharma",
    "HV Patel": "Harshal Patel",
    "Harbhajan Singh": "Harbhajan Singh",
    "UT Yadav": "Umesh Yadav",
    "TA Boult": "Trent Boult",
    "Mohammed Shami": "Mohammed Shami",
    "MM Sharma": "Mohit Sharma",
    "AR Patel": "Axar Patel",
    "K Rabada": "Kagiso Rabada",
    "SN Thakur": "Shardul Thakur",
    "JD Unadkat": "Jaydev Unadkat",
    "Mohammed Siraj": "Mohammed Siraj",
    "A Nehra": "Ashish Nehra",
    "R Vinay Kumar": "Vinay Kumar",
    "Kuldeep Yadav": "Kuldeep Yadav",
    "Z Khan": "Zaheer Khan",
    "Arshdeep Singh": "Arshdeep Singh",
    "CV Varun": "Varun Chakravarthy",
    "DW Steyn": "Dale Steyn",
    "I Sharma": "Ishant Sharma",
    "CH Morris": "Chris Morris",
    "Avesh Khan": "Avesh Khan",
    "DL Chahar": "Deepak Chahar",
    "T Natarajan": "T Natarajan",
    "Mujeeb Ur Rahman": "Mujeeb Ur Rahman",
    "Imran Tahir": "Imran Tahir",
    "MG Johnson": "Mitchell Johnson",
    "MA Starc": "Mitchell Starc",
    "PJ Cummins": "Pat Cummins",
    "KK Ahmed": "Khaleel Ahmed",
    "M Prasidh Krishna": "Prasidh Krishna",
    "Prasidh Krishna": "Prasidh Krishna",
    "L Balaji": "Lakshmipathy Balaji",
    "RP Singh": "RP Singh",
    "PP Ojha": "Pragyan Ojha",
    "SK Warne": "Shane Warne",
    "A Kumble": "Anil Kumble",
    "M Muralitharan": "Muttiah Muralitharan",
    "Mustafizur Rahman": "Mustafizur Rahman",
    "LH Ferguson": "Lockie Ferguson",
    "AJ Tye": "Andrew Tye",
    "JC Archer": "Jofra Archer",
    "Anrich Nortje": "Anrich Nortje",
    "A Nortje": "Anrich Nortje",
    "Mukesh Kumar": "Mukesh Kumar",
    "Harshit Rana": "Harshit Rana",
    "Vaibhav Arora": "Vaibhav Arora",
    "Yash Dayal": "Yash Dayal",
    "Tushar Deshpande": "Tushar Deshpande",
    "Mayank Yadav": "Mayank Yadav",
    "Mayank Markande": "Mayank Markande",
    "Ravi Bishnoi": "Ravi Bishnoi",
    "Rahul Chahar": "Rahul Chahar",
    "RD Chahar": "Rahul Chahar",
    "S Gopal": "Shreyas Gopal",
    "M Markande": "Mayank Markande",
    "Navdeep Saini": "Navdeep Saini",
    "Shivam Mavi": "Shivam Mavi",
    "C Sakariya": "Chetan Sakariya",
    "Karan Sharma": "Karn Sharma",
    "KV Sharma": "Karn Sharma",
    "Harpreet Brar": "Harpreet Brar",
    "Swapnil Singh": "Swapnil Singh",
    "Manav Suthar": "Manav Suthar",
    "Suyash Sharma": "Suyash Sharma",
    "Noor Ahmad": "Noor Ahmad",
    "Fazalhaq Farooqi": "Fazalhaq Farooqi",
    "G Coetzee": "Gerald Coetzee",
    "N Burger": "Nandre Burger",
    "Spencer Johnson": "Spencer Johnson",
    "Nuwan Thushara": "Nuwan Thushara",
    "Matheesha Pathirana": "Matheesha Pathirana",
    "M Pathirana": "Matheesha Pathirana",
    "Maheesh Theekshana": "Maheesh Theekshana",
    "M Theekshana": "Maheesh Theekshana",
    "Fazalhaq Farooqi": "Fazalhaq Farooqi",
    "S Joseph": "Shamar Joseph"
}

def enrich_dim_players():
    conn = sqlite3.connect(DB_PATH)
    df_players = pd.read_sql_query("SELECT * FROM dim_players", conn)
    
    # Generate full_name and display_name
    def get_full_name(cric_name):
        if not cric_name or pd.isna(cric_name):
            return "Unknown"
        cric_name = str(cric_name).strip()
        if cric_name in PLAYER_FULL_NAME_MAP:
            return PLAYER_FULL_NAME_MAP[cric_name]
        return cric_name
        
    def get_display_name(row):
        cric_name = str(row['player_name']).strip()
        full_name = get_full_name(cric_name)
        if full_name != cric_name:
            return f"{full_name} ({cric_name})"
        return full_name
        
    df_players['full_name'] = df_players['player_name'].apply(get_full_name)
    df_players['display_name'] = df_players.apply(get_display_name, axis=1)
    
    # Save back to database
    df_players.to_sql("dim_players", conn, if_exists="replace", index=False)
    conn.commit()
    conn.close()
    
    # Export enriched CSV
    csv_out = os.path.join(PROCESSED_DIR, "player_career_stats.csv")
    df_players.to_csv(csv_out, index=False)
    
    print(f"[OK] Successfully enriched dim_players with full_name & display_name for {len(df_players)} players!")
    
    # Verify Rohit Sharma vs Rahul Sharma
    rohit = df_players[df_players['player_name'] == 'RG Sharma'][['player_name', 'full_name', 'display_name', 'runs', 'potm_awards']].iloc[0]
    rahul = df_players[df_players['player_name'] == 'R Sharma'][['player_name', 'full_name', 'display_name', 'runs', 'potm_awards']].iloc[0]
    
    print("\nVerification:")
    print("Rohit:", dict(rohit))
    print("Rahul:", dict(rahul))

if __name__ == "__main__":
    enrich_dim_players()
