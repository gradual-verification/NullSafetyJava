#!/bin/sh
mkdir ~/github/gradual-verification/infer-gv-data/$1
python3 eval_repos.py -warn -eradicate $1
cat bugs*.txt > ~/github/gradual-verification/infer-gv-data/$1/eradicate.txt
./clean.sh $1
python3 eval_repos.py -warn -nullsafe $1
cat bugs*.txt > ~/github/gradual-verification/infer-gv-data/$1/nullsafe.txt
./clean.sh $1
python3 eval_repos.py -warn -gradual $1
cat bugs*.txt > ~/github/gradual-verification/infer-gv-data/$1/gradual.txt
./clean.sh $1
