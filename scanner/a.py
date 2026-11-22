import pandas as pd

df = pd.read_excel('folder_names.xlsx')
for index, row in df.iterrows():
    folder_name = row['folder_name']
    record_id = folder_name.split('_')[0]  # Extract the record ID from the folder name
    # Perform scanning or processing on the folder_name
    # For example, you can check if the folder exists or list its contents
    # Here, we just print the folder name for demonstration
    print(f"Scanning folder: {folder_name}")
    print(f"Record ID: {record_id}")
    df.at[index, 'record_id'] = record_id  # Add the record ID to the DataFrame
df.to_csv('scanned_dataset_folders.csv', index=False)