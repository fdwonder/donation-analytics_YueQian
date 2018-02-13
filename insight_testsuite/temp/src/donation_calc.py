######################################################################
# Name: Script for Data Insight challenge
# Copyright Yue Qian Feb 2018
#
######################################################################

#===================================================================================================
# IMPORTS
#===================================================================================================

import sys
import os                           # for os interface
import csv
import math
import numpy as np
import pandas as pd
from collections import OrderedDict, defaultdict  # append list to disc
import timeit
import argparse

def main():

    parser= argparse.ArgumentParser(
        prog='donation_calc.py',
        description="""
    @author: Yue Qian, yue.qian@yale.edu
    usage: python3.6 test.py -i ./input/itcont.txt -p ./input/percentile.txt -o ./output/repeat_donors.txt
    """
    )

    #defining arguments for parser object
    parser.add_argument(
        "-i", help="input path for itcont.txt")
    parser.add_argument(
        "-p", help="input path for percentile.txt")
    parser.add_argument(
        "-o", help="output path for repeat_donors.txt")

    args = parser.parse_args()

    data_file = args.i
    perc_file = args.p
    output_file= args.o

    # read header line
    indiv_header = []
#    with open(header_file) as f:
#        for line in f:
#            header_ele = [ele.strip() for ele in line.split(',')]
#            indiv_header.extend(header_ele)  # use extend instead of append

    indiv_header=['CMTE_ID','AMNDT_IND','RPT_TP','TRANSACTION_PGI','IMAGE_NUM','TRANSACTION_TP','ENTITY_TP','NAME','CITY','STATE','ZIP_CODE','EMPLOYER','OCCUPATION','TRANSACTION_DT','TRANSACTION_AMT','OTHER_ID','TRAN_ID','FILE_NUM','MEMO_CD','MEMO_TEXT','SUB_ID']
    dataset_raw = pd.read_csv(data_file, delimiter='|', names=indiv_header, keep_default_na=False, dtype=str)

#--- Data Cleaning Starts---
    # keep columns of interest
    dataset_valid = pd.DataFrame()
    dataset_valid = dataset_raw.drop(['AMNDT_IND', 'RPT_TP', 'TRANSACTION_PGI', \
                                      'IMAGE_NUM', 'TRANSACTION_TP', 'ENTITY_TP', \
                                      'CITY', 'STATE', 'EMPLOYER', 'OCCUPATION', 'TRAN_ID',
                                      'FILE_NUM', 'MEMO_CD', 'MEMO_TEXT', 'SUB_ID'], axis=1)
    # drop if OTHER_ID is not empty or if any other field is empty
    dataset_valid = dataset_valid[dataset_valid['OTHER_ID'].notnull()]
    dataset_valid = dataset_valid[dataset_valid.notnull()]

    # 'ZIP_CODE' is valid only when the resulting string length is 5
    dataset_valid = dataset_valid[dataset_valid['ZIP_CODE'].str.len() >= 5]

    # take integer in 'TRANSACTION_AMT'
    dataset_valid['TRANSACTION_AMT'] = dataset_valid['TRANSACTION_AMT'].astype(int)
    # 'TRANSACTION_AMT' is valid only when > 0
    dataset_valid = dataset_valid[dataset_valid['TRANSACTION_AMT'] > 0]

    # Keep all duplicates
    dataset_valid = dataset_valid[dataset_valid.duplicated \
        (['NAME', 'ZIP_CODE'], keep=False)]

    # create new dataframe with combined "Identiey" to identify out-out-order records
    # identity=NAME++ZIP_CODE
    dataset_repeat = pd.DataFrame()
    dataset_repeat['Identity'] = dataset_valid['NAME'] + dataset_valid.ZIP_CODE.str[0:5]
    dataset_repeat['CMTE_ID'] = dataset_valid['CMTE_ID']
    dataset_repeat['TRANS_AMT'] = dataset_valid['TRANSACTION_AMT']
    dataset_repeat['date'] = pd.to_datetime(dataset_valid['TRANSACTION_DT'], format='%m%d%Y', errors='ignore')

    # group by 'Identity'
    grouped = dataset_repeat.groupby('Identity')

    # Shift the previous data from the same group and take the difference
    dataset_repeat['date_shifted'] = dataset_repeat.groupby(['Identity'])['date'].shift(1)
    dataset_repeat['date_diff'] = dataset_repeat['date_shifted'] - dataset_repeat['date']
    dataset_repeat['date_diff'] = pd.to_timedelta(dataset_repeat['date_diff']).astype(str).str[0:2]
    # drop the first occurence
    dataset_repeat = dataset_repeat.dropna(how='any')
    # drop the out of order (positives 'date_diff') records
    dataset_repeat = dataset_repeat[dataset_repeat['date_diff'].astype(int) <= 0]

    # create new dataframe with combined "Identity" and transaction amount
    dataset_arrange = pd.DataFrame()
    dataset_arrange['Identity'] = dataset_repeat['CMTE_ID'] + dataset_repeat['Identity'].str[-5:] + dataset_repeat['date'].dt.year.astype(str)
    dataset_arrange['TRANS_AMT'] = dataset_repeat['TRANS_AMT']

# --- Data Cleaning Ends---

    # readin percentile.txt
    percentile_line = open(perc_file,"r").read() 
    percentile=float(percentile_line.split('\n',1)[0])

    # group by identity
    grouped = dataset_arrange.groupby('Identity')
    #perc = grouped['TRANS_AMT'].expanding(min_periods=1, center=False).quantile(quantile=0.3)
    #total = grouped['TRANS_AMT'].expanding(1).sum()
    #times = grouped['TRANS_AMT'].expanding(1).count()

    # define function to apply to each row of the grouped object
    def f(group):
        return pd.DataFrame({'Identity': group['Identity'],
                             'Perc': group['TRANS_AMT'].expanding(min_periods=1, center=False).quantile(quantile=percentile/100.,interpolation='nearest').astype(int), \
                             'Total': group['TRANS_AMT'].expanding(1).sum().astype(int),
                             'Times': group['TRANS_AMT'].expanding(1).count().astype(int)})
    # apply func on an "expanding" basis - taking the data pts as they steam in
    Results = grouped.apply(f)

    Results['CMTE_ID']=Results['Identity'].str[0:9]
    Results['ZIP_CODE']=Results['Identity'].str[9:14]
    Results['YEAR'] = Results['Identity'].str[14:20]
    
    # write to repeat_donor.txt
    Results.to_csv(output_file, sep='|', columns=['CMTE_ID','ZIP_CODE','YEAR','Perc','Total','Times'], header=False, index=False)


#===================================================================================================
# MAIN
#===================================================================================================

if __name__ == "__main__":

    # run the main function

    main()

#===================================================================================================
#                                   End of the script
#===================================================================================================
