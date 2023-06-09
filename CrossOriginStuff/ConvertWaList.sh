#!/bin/bash

#!/bin/bash

# Read and parse the JSON file into a variable
json_data=$(jq -c '.' WeakAurasList.json)

# Extract the 'id' values using 'jq' command
ids=$(echo "$json_data" | jq -r '.hits[].id')

# Convert the extracted IDs to JSON array
result=$(echo "$ids" | jq -s '.')

# Print the JSON array of IDs
echo "$result" >> WaList_Converted.json

