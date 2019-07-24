#!/bin/sh
./clean.sh $1
python3 eval_repos.py -warn -unannotated $1
cat bugs*.txt > ~/github/gradual-verification/infer-gv-data/$1/unannotated.txt
./clean.sh $1
