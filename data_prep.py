import numpy as np
import pandas as pd

# Read CSV file
data = pd.read_csv('sncb_data_challenge.csv', sep=';')

#Convert string to list of integers
col_list = ['vehicles_sequence', 'events_sequence','seconds_to_incident_sequence']
for col in col_list:
    print(col)
    data[col] = data[col].apply(lambda x: list(map(int, x.strip('[]').split(','))))

#Convert string to list of floats
data['train_kph_sequence'] = data['train_kph_sequence'].apply(lambda x: list(map(float, x.strip('[]').split(','))))

# Print the type for each column
for col in data.columns:
    print(f"{col}: {type(data[col][0])}")

# Compute the acceleration
data['acceleration_seq'] = data.apply(
    lambda row: [
        (row['train_kph_sequence'][i + 1] - row['train_kph_sequence'][i]) / 
        (row['seconds_to_incident_sequence'][i + 1] - row['seconds_to_incident_sequence'][i])
        if (row['seconds_to_incident_sequence'][i + 1] - row['seconds_to_incident_sequence'][i]) != 0 and row['vehicles_sequence'][i+1] == row['vehicles_sequence'][i] else np.nan
        for i in range(len(row['train_kph_sequence']) - 1)
    ], axis=1)

# Save the modified DataFrame to a new CSV file
data.to_csv('sncb_prepared.csv', sep=';', index=False)