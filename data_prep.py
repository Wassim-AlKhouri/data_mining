# import numpy as np
# import pandas as pd
   
# # Read CSV file
# data = pd.read_csv('sncb_data_challenge.csv', sep=';')

# #Convert string to list of integers
# col_list = ['vehicles_sequence', 'events_sequence','seconds_to_incident_sequence']
# for col in col_list:
#     print(col)
#     data[col] = data[col].apply(lambda x: list(map(int, x.strip('[]').split(','))))

# #Convert string to list of floats
# data['train_kph_sequence'] = data['train_kph_sequence'].apply(lambda x: list(map(float, x.strip('[]').split(','))))

# # Print the type for each column
# for col in data.columns:
#     print(f"{col}: {type(data[col][0])}")

# # Compute the acceleration
# data['acceleration_seq'] = data.apply(
#     lambda row: [
#         (row['train_kph_sequence'][i + 1] - row['train_kph_sequence'][i]) / 
#         (row['seconds_to_incident_sequence'][i + 1] - row['seconds_to_incident_sequence'][i])
#         if (row['seconds_to_incident_sequence'][i + 1] - row['seconds_to_incident_sequence'][i]) != 0 and row['vehicles_sequence'][i+1] == row['vehicles_sequence'][i] else np.nan
#         for i in range(len(row['train_kph_sequence']) - 1)
#     ], axis=1)

# for i in range(len(data['events_sequence'])):
#     new_vehicles_sequence = []
#     new_events_sequence = []
#     new_train_kph_sequence = []
#     new_seconds_to_incident_sequence = []
#     new_acceleration_seq = []
    
#     for j in range(len(data['events_sequence'][i])):
#         if j == 0 or data['events_sequence'][i][j] != data['events_sequence'][i][j-1]:
#             new_vehicles_sequence.append(data['vehicles_sequence'][i][j])
#             new_events_sequence.append(data['events_sequence'][i][j])
#             new_train_kph_sequence.append(data['train_kph_sequence'][i][j])
#             new_seconds_to_incident_sequence.append(data['seconds_to_incident_sequence'][i][j])
#             if j < len(data['acceleration_seq'][i]):
#                 new_acceleration_seq.append(data['acceleration_seq'][i][j])
    
#     data.at[i, 'vehicles_sequence'] = new_vehicles_sequence
#     data.at[i, 'events_sequence'] = new_events_sequence
#     data.at[i, 'train_kph_sequence'] = new_train_kph_sequence
#     data.at[i, 'seconds_to_incident_sequence'] = new_seconds_to_incident_sequence
#     data.at[i, 'acceleration_seq'] = new_acceleration_seq

# for i in range(len(data['events_sequence'])):
#     for j in range(len(data['events_sequence'][i]) - 1):
#         if data['events_sequence'][i][j] == data['events_sequence'][i][j+1]:
#             print("duplicates")
#             print(i)
#             print(len(data['events_sequence'][i]))
#             print(j)
#             raise ValueError("Duplicates in events_sequence")
    
# # Save the modified DataFrame to a new CSV file
# data.to_csv('sncb_prepared.csv', sep=';', index=False)


import pandas as pd
import numpy as np
import os
import ast

from multiprocessing import Pool, cpu_count

# Charger le dataset
data = pd.read_csv('sncb_speed.csv', sep=';')

# Charger les itemsets
def load_itemsets(directory):
    itemsets = set()
    for filename in os.listdir(directory):
        print(f'Loading {filename}...')
        incident_frequent_itemset = pd.read_csv(f'{directory}/{filename}', sep=',', nrows=100)
        for _, row in incident_frequent_itemset.iterrows():
            itemsets.add(row['Sequence'])
    return list(itemsets)

itemsets = load_itemsets('relevance\\relevance\\event_speed_alim')

# Initialiser la DataFrame finale avec des colonnes pour chaque itemset
final_data = pd.DataFrame(0, index=range(len(data)), columns=[str(itemset) for itemset in itemsets])

# Fonction pour traiter une ligne de données
def process_row(row):
    row_result = [0] * len(itemsets)
    row_set = row['events + speed + alimentation']
    for i, itemset in enumerate(itemsets):
        if set(itemset).issubset(row_set):
            row_result[i] = 1
    return row_result

# Appliquer parallélisation
def parallel_processing(data):
    with Pool(cpu_count()) as pool:
        results = pool.map(process_row, data.to_dict('records'))
    return results

if __name__ == '__main__':
    # Convertir les colonnes des résultats parallèles dans la DataFrame finale
    final_data.iloc[:, :] = parallel_processing(data)

    # Ajouter la colonne cible
    final_data['target'] = data['incident_type']

    # Sauvegarder le fichier
    final_data.to_csv('OHE_speed.csv', sep=';', index=False)
