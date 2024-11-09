#! bin/bash 

dirname=$( realpath $(dirname $0)/..)
# Remove dirname/instance directory and all its contents; if it exists
if [ -d "$dirname/instance" ]; then
    rm -r $dirname/instance
    echo "Removed $dirname/instance directory and all its contents"
fi


# Remove dirname/static/storage directory and all its contents; if it exists
if [ -d "$dirname/app/static/" ]; then
    rm -r $dirname/app/static/uploads
    echo "Removed $dirname/app/static/uploads directory and all its contents"
fi

cd $dirname
export FLASK_APP="app:create_app"
flask db upgrade