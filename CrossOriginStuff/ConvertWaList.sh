#!/bin/bash

url="https://data.wago.io/search/es?q=User%3A%22Jodsderechte%22&mode=wow"
page_size=25
output_file="Data/WaList_Converted.json"

# Get total number of results
total_results=$(curl -s "$url&page=0" | jq '.total')

# Calculate total pages
total_pages=$(( (total_results + page_size - 1) / page_size )) # This rounds up

# Initialize empty JSON array to hold the results
echo "[]" > "$output_file"

# Loop through each page and append the results to the output file
for ((page=0; page<total_pages; page++)); do
  page_results=$(curl -s "${url}page=$page" | jq -c '[.hits[].id]')
  # Append the page results to the output file
  jq -s 'add' "$output_file" <(echo "$page_results") > tmp.json && mv tmp.json "$output_file"
done

echo "Data written to $output_file"