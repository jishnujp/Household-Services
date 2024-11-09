#! /bin/bash 

dirname=$( realpath $(dirname $0)/..)
cd $dirname
python3 -m scripts.$(basename $0 .sh)