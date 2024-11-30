#!/bin/bash

dirname=$( realpath $(dirname $0)/..)
cd $dirname

export FLASK_APP="app:create_app"
flask db upgrade

python3 run.py