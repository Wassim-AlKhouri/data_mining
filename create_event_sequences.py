import pandas as pd
from mlxtend.frequent_patterns import fpgrowth
import ast
from multiprocessing import Pool

MIN_SUPPORT = 0.7  # Adjusted to avoid overly restrictive filtering

def process_incident_type(args):
    """
    Processes a single incident type and finds frequent itemsets using FP-Growth.
    """
    incident, filtered_data, min_support = args
    print("Processing incident type:", incident)

    if incident == 17 or incident == 16:
        min_support = 0.8

    # Prepare transactions: each transaction is a sequence of events
    transactions = filtered_data['events_sequence']

    # Create a one-hot encoded DataFrame for the events
    unique_events = set(event for sequence in transactions for event in sequence)  # All unique events
    transaction_df = pd.DataFrame([
        {event: (event in sequence) for event in unique_events} for sequence in transactions
    ])

    # Apply FP-Growth algorithm
    frequent_itemsets = fpgrowth(transaction_df, min_support=min_support, use_colnames=True)

    # Sort by support and keep top results
    if not frequent_itemsets.empty:
        most_frequent = frequent_itemsets.sort_values(by='support', ascending=False)
        most_frequent['itemsets'] = frequent_itemsets['itemsets'].apply(lambda x: list(x))
        # Save results to CSV
        most_frequent.to_csv(f'results/results/results_{incident}.csv', sep=';', index=False)
        print("Done with incident type:", incident)
        return (incident, most_frequent)
    else:
        print("No frequent itemsets for incident type:", incident)
        return (incident, None)


def find_frequent_itemsets_fp_growth(data, min_support=MIN_SUPPORT):
    """
    Finds the most frequent sequences of events for each incident type using FP-Growth.
    Uses multiprocessing for parallel processing of incident types.
    """
    # Get all unique incident types
    incident_types = data['incident_type'].unique()
    print("Incident types:", incident_types)

    # Convert stringified lists to actual lists of integers
    data['events_sequence'] = data['events_sequence'].apply(lambda x: ast.literal_eval(x))

    # Prepare data for multiprocessing
    incident_data_list = [
        (incident, data[data['incident_type'] == incident], min_support) for incident in incident_types
    ]

    # Use multiprocessing to process each incident type in parallel
    with Pool() as pool:
        print("Starting multiprocessing pool")
        results = pool.map(process_incident_type, incident_data_list)

    # Combine results into a dictionary
    results_dict = {incident: result for incident, result in results}

    # Run for the entire database
    transactions = data['events_sequence'].tolist()
    unique_events = set(event for sequence in transactions for event in sequence)  # All unique events
    transaction_df = pd.DataFrame([
        {event: (event in sequence) for event in unique_events} for sequence in transactions
    ])
    database_frequent_itemsets = fpgrowth(transaction_df, min_support=min_support, use_colnames=True)
    database_frequent_itemsets = database_frequent_itemsets.sort_values(by='support', ascending=False)
    database_frequent_itemsets['itemsets'] = database_frequent_itemsets['itemsets'].apply(lambda x: list(x))
    database_frequent_itemsets.to_csv(f'results/results/results_database.csv', sep=';', index=False)

    return results_dict

if __name__ == '__main__':
    # Assuming `data` is already defined in your notebook:
    data = pd.read_csv('sncb_prepared.csv', sep=';')

    # Run the function
    results = find_frequent_itemsets_fp_growth(data)
