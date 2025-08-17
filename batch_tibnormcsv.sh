#!/bin/bash

# Usage: ./batch_tibnormcsv.sh /path/to/input_dir /path/to/output_dir

input_dir="$1"
output_dir="$2"

# Create output directory if it doesn't exist
mkdir -p "$output_dir"

# Recursively find all CSV files
find "$input_dir" -type f -name "*.csv" | while read -r filepath; do
    # Extract just the filename from the path
    filename=$(basename "$filepath")

    # Construct the output file path
    outpath="$output_dir/$filename"

    # Run your Python script
    python src/main.py "$filepath" "$outpath"
done
