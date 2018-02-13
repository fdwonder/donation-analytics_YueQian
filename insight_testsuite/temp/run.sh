#!/bin/bash
#
# Use this shell script to compile (if necessary) your code and then execute it.
#

# Key environment variables: 
# conda  4.4.9
# python-3.6.3
# pandas  0.20.3

#------ Download data if necessary ------
#for file in 2016 2018
#do
#    year=${file:2:4}
#    echo "Downloading year:" $file
#    curl https://cg-519a459a-0ea3-42c2-b7bc-fa1143481f74.s3-us-gov-west-1.amazonaws.com/bulk-downloads/"$file"/indiv"$year".zip
#    wait
#    unzip indiv"$year".zip
#    wait
#done
#cp indiv16/itcont.txt ./input
#cat indiv18/itcont.txt >> ./input/itcont.txt

#------ Running python script      ------

python3.6 ./src/donation_calc.py -i ./input/itcont.txt -p ./input/percentile.txt -o ./output/repeat_donors.txt

