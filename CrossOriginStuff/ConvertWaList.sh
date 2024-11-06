#!/bin/bash

url="https://data.wago.io/search/es?q=User%3A%22Jodsderechte%22&mode=wow&"
page_size=25
output_file="Data/WaList_Converted.json"

# Get total number of results
total_results=$(curl -s "$url&page=0" | jq '.total')

# If total_results is empty, abort
if [ -z "$total_results" ]; then
  echo "Error: Total results not found or invalid response"
  exit 1
fi

# Calculate total pages
total_pages=$(( (total_results + page_size - 1) / page_size )) # This rounds up

echo "Checking for a total of: $total_pages pages"

# Initialize empty JSON array to hold the results
results="[]"
echo "[]" > "$output_file"
# Loop through each page and append the results
for ((page=0; page<total_pages; page++)); do
  echo "Checking page: $page with url ${url}page=$page"
  page_results=$(curl -s "${url}page=$page" | jq -c '[.hits[].id]')
  # Merge the page results into the results array
  results=$(echo "$results" | jq -s 'add + '"$page_results")
done

# Filter out duplicates and make the list unique
unique_results=$(echo "$results" | jq 'unique')

# Debugging: Output the raw JSON to make sure it's correct
echo "Unique results: $unique_results"

# Set the unique results as an environment variable
echo "$(echo "$unique_results" | jq -cr .)" >> "$output_file"
echo "Data written to $output_file"