import heat_helper as hh
from datetime import date
import pandas as pd


new_df_dict = {'Full Name' : ['Jane Doe', 'Mike Jones', 'Thomas Smith', 'Sarah Brown', 'Christopher Bloggs'], 
               'Date of Birth': [date(2008, 9, 2), date(2009, 7, 25), date(2008, 12, 25), date(2008, 11, 13), date(2010, 12, 30)], 
               'Postcode': ['AA1 1AA', 'BB2 2BB', 'CC3 3CC', 'DD4 4DD', 'EE5 5EE'],
               }

heat_df_dict = {'ID' : ['#00000001', '#00000002', '#00000003', '#00000004', '#00000005', '#00000006'],
                'Student Full Name' : ['Jane Doe', 'Michael Jones', 'Thomas Smith', 'Sarah Brown', 'Jane Doe', 'Sarah Jane Brown'], 
                'Student Date of Birth': [date(2008, 9, 2), date(2009, 7, 25), date(2008, 12, 25), date(2008, 11, 13), date(2008, 9, 2), date(2008, 11, 13)], 
                'Student Postcode': ['AA1 1AA', 'BB2 2BB', 'CC3 3CC', 'DD4 4DD', 'AA1 1AA', 'DD4 4DD'], 
                }

new_data = pd.DataFrame.from_dict(new_df_dict)
heat = pd.DataFrame.from_dict(heat_df_dict)

print(f"------ NEW DATA")
print(new_data)
print(f"------ HEAT DATA")
print(heat)

print(f"------ STARTING MATCH")
matched, unmatched = hh.perform_fuzzy_match(
    new_data,
    heat,
    ['Date of Birth', 'Postcode'],
    ['Student Date of Birth', 'Student Postcode'],
    'Full Name',
    'Student Full Name',
    'Fuzzy: DOB+Postcode',
    70,
)

print(f"------ MATCHED DATA")
print(matched)
print(f"------ UNMATCHED DATA")
print(unmatched)