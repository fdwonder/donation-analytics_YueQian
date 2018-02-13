######################################################################
# Name: Script for Data Insight challenge
# Copyright Yue Qian Feb 2018
#
# Usage
######################################################################

#===================================================================================================
# IMPORTS
#===================================================================================================

import sys
import os                           # for os interface
import csv
import math
import pickle                       # for full-precision data storage
import numpy as np
import pandas as pd
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

from collections import OrderedDict, defaultdict  # append list to disc
import timeit
import argparse
# from somewhere import somefunc




#===================================================================================================
# INPUT OPTIONS
#===================================================================================================

#===================================================================================================
# FUNCTIONS: xxx
#===================================================================================================

#===================================================================================================
# FUNCTIONS: xxx
#===================================================================================================

#===================================================================================================
# MAIN
#===================================================================================================

def main():

    parser= argparse.ArgumentParser(
        prog='test.py',
        description="""
    @author: Yue Qian, yue.qian@yale.edu
    usage: python3.6 test.py -i ./input/itcont.txt -p ./input/percentile.txt -o ./output/repeat_donors.txt
    """
    )

    #defining arguments for parser object
    parser.add_argument(
        "-i", help="input itcont.txt")
    parser.add_argument(
        "-p", help="input percentile.txt")
    parser.add_argument(
        "-o", help="repeat_donors.txt")

    args = parser.parse_args()



    data_file = args.i
    #test_data = '../input/indiv18/test_data.txt'
    perc_file = args.p
    output_file= args.o

    start_time = timeit.default_timer()
    # read header line
    indiv_header = []
#    with open(header_file) as f:
#        for line in f:
#            header_ele = [ele.strip() for ele in line.split(',')]
#            indiv_header.extend(header_ele)  # use extend instead of append


    indiv_header=['CMTE_ID','AMNDT_IND','RPT_TP','TRANSACTION_PGI','IMAGE_NUM','TRANSACTION_TP','ENTITY_TP','NAME','CITY','STATE','ZIP_CODE','EMPLOYER','OCCUPATION','TRANSACTION_DT','TRANSACTION_AMT','OTHER_ID','TRAN_ID','FILE_NUM','MEMO_CD','MEMO_TEXT','SUB_ID']
    elapsed = timeit.default_timer() - start_time
    #print(elapsed)
    dataset_raw = pd.read_csv(data_file, delimiter='|', names=indiv_header, keep_default_na=False, dtype=str)
    elapsed = timeit.default_timer() - start_time
    #print(elapsed)

    start_time = timeit.default_timer()
    # keep columns of interest
    dataset_valid = pd.DataFrame()
    dataset_valid = dataset_raw.drop(['AMNDT_IND', 'RPT_TP', 'TRANSACTION_PGI', \
                                      'IMAGE_NUM', 'TRANSACTION_TP', 'ENTITY_TP', \
                                      'CITY', 'STATE', 'EMPLOYER', 'OCCUPATION', 'TRAN_ID',
                                      'FILE_NUM', 'MEMO_CD', 'MEMO_TEXT', 'SUB_ID'], axis=1)

    dataset_valid = dataset_valid[dataset_valid['OTHER_ID'].notnull()]
    dataset_valid = dataset_valid[dataset_valid.notnull()]
    elapsed = timeit.default_timer() - start_time
    #print(elapsed)

    start_time = timeit.default_timer()
    # take the first five characters of 'ZIP_CODE'
    # dataset_valid['ZIP_CODE']=dataset_valid['ZIP_CODE'].astype(str).str[0:5]
    # 'ZIP_CODE' is valid only when the resulting string length is 5
    dataset_valid = dataset_valid[dataset_valid['ZIP_CODE'].str.len() >= 5]

    # take integer in 'TRANSACTION_AMT'
    dataset_valid['TRANSACTION_AMT'] = dataset_valid['TRANSACTION_AMT'].astype(int)
    # 'TRANSACTION_AMT' is valid only when > 0
    dataset_valid = dataset_valid[dataset_valid['TRANSACTION_AMT'] > 5]

    # first : Mark duplicates as True except for the first occurrence.
    dataset_repeat = dataset_valid[dataset_valid.duplicated \
        (['NAME', 'ZIP_CODE'], keep='first')]

    elapsed = timeit.default_timer() - start_time
    #print(elapsed)

    start_time = timeit.default_timer()
    dataset_arrange = pd.DataFrame()
    dataset_arrange['Identity'] = dataset_repeat['CMTE_ID'] + dataset_repeat.ZIP_CODE.str[
                                                              0:5] + dataset_repeat.TRANSACTION_DT.str[-4:]
    dataset_arrange['TRANS_AMT'] = dataset_repeat.TRANSACTION_AMT
    dataset_arrange['index1'] = dataset_arrange.index
    elapsed = timeit.default_timer() - start_time
    #print(elapsed)

    # readin percentile.txt
    percentile_line = open(perc_file,"r").read() 
    percentile=float(percentile_line.split('\n',1)[0])
    #print(percentile)


    start_time = timeit.default_timer()
    # group by identity
    grouped = dataset_arrange.groupby('Identity')
    #perc = grouped['TRANS_AMT'].expanding(min_periods=1, center=False).quantile(quantile=0.3)
    #total = grouped['TRANS_AMT'].expanding(1).sum()
    #times = grouped['TRANS_AMT'].expanding(1).count()

    def f(group):
        return pd.DataFrame({'Identity': group['Identity'],
                             'Perc': group['TRANS_AMT'].expanding(min_periods=1, center=False).quantile(quantile=percentile/100.,interpolation='nearest').astype(int), \
                             'Total': group['TRANS_AMT'].expanding(1).sum().astype(int),
                             'Times': group['TRANS_AMT'].expanding(1).count().astype(int)})

    Results = grouped.apply(f)

    elapsed = timeit.default_timer() - start_time
    #print(elapsed)
    Results['CMTE_ID']=Results['Identity'].str[0:9]
    Results['ZIP_CODE']=Results['Identity'].str[9:14]
    Results['YEAR'] = Results['Identity'].str[14:20]
    #print (Results)

    Results.to_csv(output_file, sep='|', columns=['CMTE_ID','ZIP_CODE','YEAR','Perc','Total','Times'], header=False, index=False)

    # merge back to pandas


if __name__ == "__main__":

    # run the main function

    main()

#===================================================================================================
#                                   End of the script
#===================================================================================================
