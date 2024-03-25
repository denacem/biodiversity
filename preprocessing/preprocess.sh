#!/bin/bash

# The all_yield.csv is an export from this site:
# https://www.fao.org/faostat/en/#data/QCL
# Apply the following selection:
# Countries: all, Elements: Yield, Items: all, desired year

# The all_impex_world.csv is an export from this site:
# https://www.fao.org/faostat/en/#data/TCL
# Apply the following selection:
# Countries: all, Elements: Import Quantity and Export Quantity, Items: Crops and livestock products, desired year

yield_path=./input/all_yield.csv
impex_world_path=./input/all_impex_world.csv

# Read the unique Item codes and titles from the file
IFS=$'\n' read -d '' -r -a codes_and_titles < <(grep -v "g/An" "$yield_path" | awk -F '","' '{print $7 "," $8}' | sort -t ',' -k1,1 -u)

echo $codes_and_titles

# Create a file to store the mapping
mapping_file=output/mapping.csv
echo "code,title,occupation,emoji" > "$mapping_file"

# Loop over each code and title pair
for pair in "${codes_and_titles[@]:1}"; do
    code=$(echo "$pair" | cut -d ',' -f1)
    title=$(echo "$pair" | cut -d ',' -f2-)
    # Append the code and title to the mapping file
    echo "$code,\"$title\",," >> "$mapping_file"
done

# Read the unique Item codes from the file
IFS=$'\n' read -d '' -r -a item_codes < <(grep -v "g/An" "$yield_path" | awk -F '","' '{print $7}' | sort | uniq)

# Add column names to each file
column_names_yield=$(head -n 1 "$yield_path")
column_names_impex=$(head -n 1 "$impex_world_path")

# Loop over each Item code
for code in "${item_codes[@]}"; do
    # Create a file with the corresponding Item code for yield
    output_file_yield=output/yield/"$code.csv"
    echo "$column_names_yield" > "$output_file_yield"
    grep "$code" "$yield_path" >> "$output_file_yield"
    
    # Create a file with the corresponding Item code for impex
    output_file_impex=output/impex/"$code.csv"
    echo "$column_names_impex" > "$output_file_impex"
    grep "$code" "$impex_world_path" >> "$output_file_impex"
done