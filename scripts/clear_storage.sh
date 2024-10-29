#! bin/bash 

dirname=$( realpath $(dirname $0)/..)
# Remove dirname/instance directory and all its contents; if it exists
if [ -d "$dirname/instance" ]; then
    rm -r $dirname/instance
    echo "Removed $dirname/instance directory and all its contents"
fi


# Remove dirname/static/storage directory and all its contents; if it exists
if [ -d "$dirname/static/storage" ]; then
    rm -r $dirname/static/storage
    echo "Removed $dirname/static/storage directory and all its contents"
fi