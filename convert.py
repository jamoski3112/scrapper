import pandas as pd

# Load the CSV file
df = pd.read_csv('filtered_formatted_ctf_writeups.csv', usecols=["title", "url", "tags", "description"])

# Convert the DataFrame to JSON Lines format
jsonl_data = df.to_json(orient='records', lines=True)

# Write the JSON Lines data to a file
with open('filtered_formatted_ctf_writeups.jsonl', 'w') as jsonl_file:
    jsonl_file.write(jsonl_data)
