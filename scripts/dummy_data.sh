#! /bin/bash 

dirname=$( realpath $(dirname $0)/..)
#  create folders "images", "storage", "storage/documents", "storage/profile_pics" if they don't exist
folders=("images" "storage" "storage/documents" "storage/profile_pics")
for folder in "${folders[@]}"; do
    if [ ! -d "$dirname/static/$folder" ]; then
        mkdir -p $dirname/static/$folder
        echo "Created $dirname/static/$folder directory"
    fi
done

python3 -m scripts.$(basename $0 .sh)