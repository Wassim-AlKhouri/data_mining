import pandas as pd
import ast
import os
from multiprocessing import Pool
import numpy as np
import csv

# Create a list of all sequences for each incident
def listofallsequences(args):
    """Crée une liste de toutes les séquences pour chaque incident."""
    incident, results7 = args  # Extract arguments
    sequences = []
    for sequence in results7[f'results7_{incident}.csv']['itemsets']:
        sequences.append(sequence)
    print(f"done with list of sequences {incident}")
    return sequences

# Compute h_all_class
def compute_relevance_for_sequence(args):
    """Calcule la pertinence d'une séquence."""
    sequence, events_summary = args  # Extract arguments
    count = 0
    for row in events_summary:
        if set(sequence).issubset(set(row)):
            count += 1
    return count

# Compute relevance for each incident
def compute_relevance_for_incident(args):
    sequence, results7_file, df_i, len_df_i, sequences_by_incident = args  # Extract arguments
    h_in_value = 0
    h_in_best_case_value = 0
    h_in_worst_case_value = 0

    # Calcul de h_in
    if sequence in sequences_by_incident:
        index = sequences_by_incident.index(sequence)
        h_in_value = results7_file['support'][sequences_by_incident.index(sequence)]

    # Calcul de h_in_best_case
    h_in_best_case_value = sum(1 for row in df_i['events_sequence'])

    # Calcul de h_in_worst_case
    h_in_worst_case_value = 1

    # Normalisation pour h_in_best_case et h_in_worst_case
    h_in_best_case_value /= len_df_i
    h_in_worst_case_value /= len_df_i

    return h_in_value, h_in_best_case_value, h_in_worst_case_value



if __name__ == '__main__':
    # Charger les données
    data_alim = pd.read_csv('sncb_speed.csv', sep=';')
    data_alim['events + speed + alimentation'] = data_alim['events + speed + alimentation'].apply(ast.literal_eval)

    # Charger les résultats depuis le dossier results7
    results7 = {}
    for file in os.listdir('results/results7'):
        if file.endswith('.csv'):
            results7[file] = pd.read_csv('results/results7/' + file, sep=';')
            results7[file]['itemsets'] = results7[file]['itemsets'].apply(ast.literal_eval)

    # Liste de tous les incidents
    incidents = data_alim['incident_type'].unique()

    #################################################################################################################################
    ####################################### Lisst of all sequences for each incident ################################################

    args = [(incident, results7) for incident in incidents]

    with Pool() as pool:
        listsequences = pool.map(listofallsequences, args)
    sequences_by_incident = {incident: sequences for incident, sequences in zip(incidents, listsequences)}
    print("type of sequences_by_incident", type(sequences_by_incident[incidents[0]]))
    sequences = {tuple(sequence) for sequences_ in listsequences for sequence in sequences_}
    sequences = [list(seq) for seq in sequences]
    print(len(sequences))
    print("done Pool 1")

    #################################################################################################################################
    ############################################# Compute h_all_class ###############################################################

    events_summary = data_alim['events + speed + alimentation']

    pool_args2 = [(sequence, events_summary) for sequence in sequences]

    with Pool() as pool:
        relevance_counts = pool.map(compute_relevance_for_sequence, pool_args2)

    h_all_class = np.array(relevance_counts) / len(events_summary)
    print("done Pool 2")

    #################################################################################################################################
    ############################################# Compute relevance for each incident ################################################
     # Rassembler les résultats dans des dictionnaires
    relevance = {}
    relevance_best_case = {}
    relevance_worst_case = {}
    
    for incident in incidents:
        df_i = data_alim[data_alim['incident_type'] == incident]
        file = f'results7_{incident}.csv'
        results7_file = results7[file]
        len_df_i = len(df_i)
        
        pool_args3 = [(sequence, results7_file, df_i, len_df_i, sequences_by_incident[incident]) for sequence in sequences]

        # Paralléliser le calcul des pertinences
        with Pool() as pool:
            results = pool.map(compute_relevance_for_incident, pool_args3)

        # Séparer les résultats
        h_in = np.array([res[0] for res in results])
        h_in_best_case = np.array([res[1] for res in results])
        h_in_worst_case = np.array([res[2] for res in results])

        # Calculer les pertinences
        relevance[incident] = h_in / h_all_class
        relevance_best_case[incident] = h_in_best_case / h_all_class
        relevance_worst_case[incident] = h_in_worst_case / h_all_class

        print(f"done with incident {incident}")
  
    print("Relevance computed for all incidents")
    print("done Pool 3")

    #################################################################################################################################
    ############################################# Save results ######################################################################

    relevance_max_incident = {}
    for incident in incidents:
        relevance_max_incident[incident] = []
        for i, sequence in enumerate(sequences):
                relevance_max_incident[incident].append((sequence,float(relevance[incident][i]), i, float(relevance[incident][i]*h_all_class[i])))
        relevance_max_incident[incident] = sorted(relevance_max_incident[incident], key=lambda x: x[1],reverse=True)
  
    print("Relevance max incident computed")

    for incident in incidents:
        with open(f'Relevance_event speed {incident} sequence.txt', 'w') as file:
            # Écrire l'incident dans le fichier
            file.write(f"{incident}\n")
            
            for i in range(len(relevance_max_incident[incident])):
                if relevance_max_incident[incident][i][1] > 0:
                    # Écrire les informations pertinentes dans le fichier
                    file.write(f" max relevance: {relevance_best_case[incident][relevance_max_incident[incident][i][2]]}\n")
                    file.write(f"{relevance_max_incident[incident][i]}\n")
                    file.write(f" min relevance: {relevance_worst_case[incident][relevance_max_incident[incident][i][2]]}\n")
                    file.write("\n")
            
            # Écrire les séparateurs
            file.write('====================================================== END ======================================================\n')
            file.write('=============================================================================================================\n')

    for incident in incidents:
        with open(f'relevance\\event_speed_alim\\Relevance_event_speed__alim_{incident}_sequence.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Écrire l'en-tête
            writer.writerow(['Relevance', 'Sequence', 'Support', 'Max Relevance', 'Min Relevance'])

            # Écrire les données
            for i in range(len(relevance_max_incident[incident])):
                relevance_score = relevance_max_incident[incident][i][1]
                if relevance_score > 0:
                    max_relevance = relevance_best_case[incident][relevance_max_incident[incident][i][2]]
                    min_relevance = relevance_worst_case[incident][relevance_max_incident[incident][i][2]]
                    
                    # Ajouter une ligne au CSV
                    writer.writerow([
                        relevance_score,                        # Relevance
                        #incident,
                        relevance_max_incident[incident][i][0],  # Sequence
                        relevance_max_incident[incident][i][3],  # Support
                        max_relevance,                           # Max Relevance
                        min_relevance                            # Min Relevance
                    ])
        print(f"File written: Relevance_event_{incident}_alim_sequence.csv")