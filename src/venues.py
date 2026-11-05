"""
Canonical IPL Venue Alias Map
-----------------------------
CricSheet venue strings vary (with/without city suffix, historical renames).
This module maps all 59 raw strings to 36 canonical venue names.
"""

CANON = {
    "Arun Jaitley Stadium, Delhi": [
        "Arun Jaitley Stadium", "Arun Jaitley Stadium, Delhi", "Feroz Shah Kotla", "Feroz Shah Kotla, Delhi"
    ],
    "Barabati Stadium, Cuttack": ["Barabati Stadium", "Barabati Stadium, Cuttack"],
    "Barsapara Cricket Stadium, Guwahati": ["Barsapara Cricket Stadium, Guwahati"],
    "Ekana Cricket Stadium, Lucknow": [
        "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium, Lucknow"
    ],
    "Brabourne Stadium, Mumbai": ["Brabourne Stadium", "Brabourne Stadium, Mumbai"],
    "Buffalo Park, East London": ["Buffalo Park", "Buffalo Park, East London"],
    "De Beers Diamond Oval, Kimberley": ["De Beers Diamond Oval", "Diamond Oval, Kimberley"],
    "Dr DY Patil Sports Academy, Navi Mumbai": [
        "Dr DY Patil Sports Academy", "Dr DY Patil Sports Academy, Mumbai", "Dr DY Patil Sports Academy, Navi Mumbai"
    ],
    "ACA-VDCA Stadium, Visakhapatnam": [
        "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium",
        "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium, Visakhapatnam",
        "Andhra Cricket Association-Visakhapatnam District Cricket Association Stadium, Visakhapatnam",
    ],
    "Dubai International Cricket Stadium": ["Dubai International Cricket Stadium"],
    "Eden Gardens, Kolkata": ["Eden Gardens", "Eden Gardens, Kolkata"],
    "Green Park, Kanpur": ["Green Park", "Green Park, Kanpur"],
    "HPCA Stadium, Dharamsala": [
        "Himachal Pradesh Cricket Association Stadium",
        "Himachal Pradesh Cricket Association Stadium, Dharamsala",
    ],
    "Holkar Cricket Stadium, Indore": ["Holkar Cricket Stadium", "Holkar Cricket Stadium, Indore"],
    "JSCA International Stadium, Ranchi": [
        "JSCA International Stadium Complex", "JSCA International Stadium Complex, Ranchi"
    ],
    "Kingsmead, Durban": ["Kingsmead", "Kingsmead, Durban"],
    "M Chinnaswamy Stadium, Bengaluru": [
        "M Chinnaswamy Stadium", "M Chinnaswamy Stadium, Bengaluru", "M.Chinnaswamy Stadium",
        "M Chinnaswamy Stadium, Bangalore"
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
        "Subrata Roy Sahara Stadium, Pune",
    ],
    "Narendra Modi Stadium, Ahmedabad": [
        "Narendra Modi Stadium, Ahmedabad", "Sardar Patel Stadium, Motera",
        "Sardar Patel Stadium, Motera, Ahmedabad",
    ],
    "Nehru Stadium": ["Nehru Stadium", "Nehru Stadium, Kochi"],
    "New Wanderers Stadium, Johannesburg": [
        "New Wanderers Stadium", "Wanderers Stadium, Johannesburg"
    ],
    "Newlands, Cape Town": ["Newlands", "Newlands, Cape Town"],
    "OUTsurance Oval, Bloemfontein": [
        "OUTsurance Oval", "Mangaung Oval, Bloemfontein"
    ],
    "IS Bindra Stadium, Mohali": [
        "Punjab Cricket Association IS Bindra Stadium",
        "Punjab Cricket Association IS Bindra Stadium, Mohali",
        "Punjab Cricket Association IS Bindra Stadium, Mohali, Chandigarh",
        "Punjab Cricket Association Stadium, Mohali",
        "Punjab Cricket Association Stadium, Mohali, Chandigarh",
    ],
    "Rajiv Gandhi Stadium, Hyderabad": [
        "Rajiv Gandhi International Stadium",
        "Rajiv Gandhi International Stadium, Uppal",
        "Rajiv Gandhi International Stadium, Uppal, Hyderabad",
    ],
    "Saurashtra Cricket Association Stadium, Rajkot": [
        "Saurashtra Cricket Association Stadium",
        "Saurashtra Cricket Association Stadium, Rajkot",
    ],
    "Sawai Mansingh Stadium, Jaipur": [
        "Sawai Mansingh Stadium", "Sawai Mansingh Stadium, Jaipur"
    ],
    "Shaheed Veer Narayan Singh Stadium, Raipur": [
        "Shaheed Veer Narayan Singh International Stadium",
        "Shaheed Veer Narayan Singh International Stadium, Raipur",
    ],
    "Sharjah Cricket Stadium": ["Sharjah Cricket Stadium"],
    "Sheikh Zayed Stadium, Abu Dhabi": [
        "Sheikh Zayed Stadium", "Sheikh Zayed Stadium, Abu Dhabi", "Zayed Cricket Stadium, Abu Dhabi"
    ],
    "St George's Park, Gqeberha": [
        "St George's Park", "St George's Park, Port Elizabeth"
    ],
    "SuperSport Park, Centurion": [
        "SuperSport Park", "SuperSport Park, Centurion"
    ],
    "VCA Stadium, Jamtha, Nagpur": [
        "Vidarbha Cricket Association Stadium, Jamtha",
        "Vidarbha Cricket Association Stadium, Jamtha, Nagpur",
    ],
    "Wankhede Stadium, Mumbai": ["Wankhede Stadium", "Wankhede Stadium, Mumbai"],
}

# Reverse lookup: raw string -> canonical name
VENUE = {raw: canon for canon, raws in CANON.items() for raw in raws}
