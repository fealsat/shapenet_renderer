#!/bin/bash

work_dir="$(pwd)/hdris"
config_file="$work_dir/config.json"
user_agent="ShapeNetRenderer/1.0"

# Ensure config file exists
if [[ ! -f "$config_file" ]]; then
    echo "Config file not found: $config_file"
    exit 1
fi

# Extract "name" values using grep/sed
names=$(grep -o '"name": *"[^"]*"' "$config_file" | sed -E 's/.*"name": *"([^"]*)".*/\1/')

# Loop through each name
for name in $names; do
    echo "Downloading: $name"
    curl -X GET -H "User-Agent: $user_agent" \
         "https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr/2k/$name" \
         --output "$work_dir/$name"
done
