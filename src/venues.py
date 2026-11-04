"""
Canonical IPL Venue Alias Map
-----------------------------
CricSheet venue strings vary (with/without city suffix, historical renames).
This module maps all 59 raw strings to 36 canonical venue names.
"""

CANON = {
    "Arun Jaitley Stadium, Delhi": [
        "Arun Jaitley Stadium", "Arun Jaitley Stadium, Delhi", "Feroz Shah Kotla"
    ],
    "Barabati Stadium, Cuttack": ["Barabati Stadium"],
    "Barsapara Cricket Stadium, Guwahati": ["Barsapara Cricket Stadium, Guwahati"],
    "Ekana Cricket Stadium, Lucknow": [
        "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium, Lucknow"
    ],
    "Brabourne Stadium, Mumbai": ["Brabourne Stadium", "Brabourne Stadium, Mumbai"],
    "Buffalo Park, East London": ["Buffalo Park"],
    "De Beers Diamond Oval, Kimberley": ["De Beers Diamond Oval"],
    "Dr DY Patil Sports Academy, Navi Mumbai": [
        "Dr DY Patil Sports Academy", "Dr DY Patil Sports Academy, Mumbai"
    ],
    "ACA-VDCA Stadium, Visakhapatnam": [
        "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium",
        "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium, Visakhapatnam",
    ],
    "Dubai International Cricket Stadium": ["Dubai International Cricket Stadium"],
    "Eden Gardens, Kolkata": ["Eden Gardens", "Eden Gardens, Kolkata"],
    "Green Park, Kanpur": ["Green Park"],
    "HPCA Stadium, Dharamsala": [
        "Himachal Pradesh Cricket Association Stadium",
        "Himachal Pradesh Cricket Association Stadium, Dharamsala",
    ],
    "Holkar Cricket Stadium, Indore": ["Holkar Cricket Stadium"],
    "JSCA International Stadium, Ranchi": ["JSCA International Stadium Complex"],
    "Kingsmead, Durban": ["Kingsmead"],
    "M Chinnaswamy Stadium, Bengaluru": [
        "M Chinnaswamy Stadium", "M Chinnaswamy Stadium, Bengaluru", "M.Chinnaswamy Stadium"
    ],
    "MA Chidambaram Stadium, Chennai": [
        "MA Chidambaram Stadium", "MA Chidambaram Stadium, Chepauk",
        "MA Chidambaram Stadium, Chepauk, Chennai",
    ],
    "Mullanpur Stadium (New Chandigarh)": [
        "Maharaja Yadavindra Singh International Cricket Stadium, Mullanpur",
        "Maharaja Yadavindra Singh International Cricket Stadium, New Chandigarh",
    ],
    "MCA Stadium, Pune": [
        "Maharashtra Cricket Association Stadium",
        "Maharashtra Cricket Association Stadium, Pune",
        "Subrata Roy Sahara Stadium",
    ],
    "Narendra Modi Stadium, Ahmedabad": [
        "Narendra Modi Stadium, Ahmedabad", "Sardar Patel Stadium, Motera"
    ],
    "Nehru Stadium": ["Nehru Stadium"],
    "New Wanderers Stadium, Johannesburg": ["New Wanderers Stadium"],
    "Newlands, Cape Town": ["Newlands"],
    "OUTsurance Oval, Bloemfontein": ["OUTsurance Oval"],
    "IS Bindra Stadium, Mohali": [
        "Punjab Cricket Association IS Bindra Stadium",
        "Punjab Cricket Association IS Bindra Stadium, Mohali",
        "Punjab Cricket Association IS Bindra Stadium, Mohali, Chandigarh",
        "Punjab Cricket Association Stadium, Mohali",
    ],
    "Rajiv Gandhi Stadium, Hyderabad": [
        "Rajiv Gandhi International Stadium",
        "Rajiv Gandhi International Stadium, Uppal",
        "Rajiv Gandhi International Stadium, Uppal, Hyderabad",
    ],
    "Saurashtra Cricket Association Stadium, Rajkot": [
        "Saurashtra Cricket Association Stadium"
    ],
    "Sawai Mansingh Stadium, Jaipur": [
        "Sawai Mansingh Stadium", "Sawai Mansingh Stadium, Jaipur"
    ],
    "Shaheed Veer Narayan Singh Stadium, Raipur": [
        "Shaheed Veer Narayan Singh International Stadium"
    ],
    "Sharjah Cricket Stadium": ["Sharjah Cricket Stadium"],
    "Sheikh Zayed Stadium, Abu Dhabi": [
        "Sheikh Zayed Stadium", "Zayed Cricket Stadium, Abu Dhabi"
    ],
    "St George's Park, Gqeberha": ["St George's Park"],
    "SuperSport Park, Centurion": ["SuperSport Park"],
    "VCA Stadium, Jamtha, Nagpur": ["Vidarbha Cricket Association Stadium, Jamtha"],
    "Wankhede Stadium, Mumbai": ["Wankhede Stadium", "Wankhede Stadium, Mumbai"],
}

# Reverse lookup: raw string -> canonical name
VENUE = {raw: canon for canon, raws in CANON.items() for raw in raws}
