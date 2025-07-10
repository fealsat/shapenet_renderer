#!/bin/bash

work_dir="$(pwd)/hdris"

# Load JSON from file
json="$(cat $work_dir/config.json)"

echo $json

# Get the length of the array
length="$(printf '%d' $(echo "$json" | jq '. | length'))"
user_agent=$"ShapeNetRenderer/1.0"

# Iterate over the array
i=0
while [ "$i" -lt "$length" ]; do
    name=$(echo "$json" | jq -r ".[$i].name")
    echo "Downloading: $name"
    curl -X GET -H "User-Agent: $user_agent" "https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr/2k/$name" --output $work_dir/$name
    i=$((i + 1))
done