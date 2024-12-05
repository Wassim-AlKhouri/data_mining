import pandas as pd
import ast
import os
from multiprocessing import Pool
import numpy as np
import csv

# Create a list of all sequences for each incident
def listofallsequences(args):
    """Crée une liste de toutes les séquences pour chaque incident."""
    incident, results3 = args  # Extract arguments
    sequences = []
    for sequence in results3[f'results3_{incident}.csv']['itemsets']:
        if sequence not in sequences:
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
    """Calcul de la pertinence pour chaque incident."""
    incident, data_alim, sequences, results3, h_all_class = args
    df_i = data_alim
    file = f'results3_{incident}.csv'

    # Calcul de h_in pour chaque séquence
    h_in = np.zeros(len(sequences))
    for i, sequence in enumerate(sequences):
        for row in range(len(results3[file])):
            if sequence == results3[file]['itemsets'][row]:
                h_in[i] = results3[file]['support'][row]
                break

    # Calcul des meilleurs et pires cas
    h_in_best_case = np.zeros(len(sequences))
    h_in_worst_case = np.zeros(len(sequences))
    for i, sequence in enumerate(sequences):
        for row in df_i['events_sequence']:
            h_in_best_case[i] += 1
        h_in_worst_case[i] = 1

    # Normalisation des résultats
    h_in_best_case = h_in_best_case / len(df_i)
    h_in_worst_case = h_in_worst_case / len(df_i)

    # Calcul des pertinences pour chaque type de pertinence
    relevance = h_in / h_all_class
    relevance_best_case = h_in_best_case / h_all_class
    relevance_worst_case = h_in_worst_case / h_all_class

    print(f"done with incident {incident}")
    return (incident, relevance, relevance_best_case, relevance_worst_case)



if __name__ == '__main__':
    # Charger les données
    data_alim = pd.read_csv('sncb_alimentation.csv', sep=';')
    data_alim['events + summary'] = data_alim['events + summary'].apply(lambda x: ast.literal_eval(x))

    # Charger les résultats depuis le dossier results3
    results3 = {}
    for file in os.listdir('results/results3'):
        if file.endswith('.csv'):
            results3[file] = pd.read_csv('results/results3/' + file, sep=';')
            results3[file]['itemsets'] = results3[file]['itemsets'].apply(ast.literal_eval)

    # Liste de tous les incidents
    incidents = data_alim['incident_type'].unique()

    #################################################################################################################################
    ####################################### Lisst of all sequences for each incident ################################################

    args = [(incident, results3) for incident in incidents]

    with Pool() as pool:
        listsequences = pool.map(listofallsequences, args)
    sequences = {tuple(sequence) for sequences_ in listsequences for sequence in sequences_}
    sequences = [list(seq) for seq in sequences]
    print(len(sequences))
    print("done Pool 1")

    #################################################################################################################################
    ############################################# Compute h_all_class ###############################################################

    events_summary = data_alim['events + summary']

    pool_args2 = [(sequence, events_summary) for sequence in sequences]

    with Pool() as pool:
        relevance_counts = pool.map(compute_relevance_for_sequence, pool_args2)

    h_all_class = np.array(relevance_counts) / len(events_summary)
    print("done Pool 2")

    #################################################################################################################################
    ############################################# Compute relevance for each incident ################################################

    pool_args3 = [(incident, data_alim[data_alim['incident_type'] == incident], sequences, results3, h_all_class) for incident in incidents]

    # Paralléliser le calcul des pertinences
    with Pool() as pool:
        results = pool.map(compute_relevance_for_incident, pool_args3)

    # Rassembler les résultats dans des dictionnaires
    relevance = {}
    relevance_best_case = {}
    relevance_worst_case = {}

    for result in results:
        incident, rel, rel_best_case, rel_worst_case = result
        relevance[incident] = rel
        relevance_best_case[incident] = rel_best_case
        relevance_worst_case[incident] = rel_worst_case

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
        with open(f'Relevance_event {incident} alim sequence.txt', 'w') as file:
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
        with open(f'Relevance_event_{incident}_alim_sequence.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Écrire l'en-tête
            writer.writerow(['Incident', 'Sequence', 'Relevance', 'Support', 'Max Relevance', 'Min Relevance'])

            # Écrire les données
            for i in range(len(relevance_max_incident[incident])):
                relevance_score = relevance_max_incident[incident][i][1]
                if relevance_score > 0:
                    max_relevance = relevance_best_case[incident][relevance_max_incident[incident][i][2]]
                    min_relevance = relevance_worst_case[incident][relevance_max_incident[incident][i][2]]
                    
                    # Ajouter une ligne au CSV
                    writer.writerow([
                        incident,
                        relevance_max_incident[incident][i][0],  # Sequence
                        relevance_score,                        # Relevance
                        relevance_max_incident[incident][i][3],  # Support
                        max_relevance,                           # Max Relevance
                        min_relevance                            # Min Relevance
                    ])
        print(f"File written: Relevance_event_{incident}_alim_sequence.csv")