
# Introduction

This is a python script witten for running percentile of contribution calculation for donations coming from the same area to the same recepient. Sample tests were included.

Usage: ./run.sh or python3.6 donation_calc.py -i ./input/itcont.txt -p ./input/percentile.txt -o ./output/repeat_donors.txt

# Method and Discussion

## 1. Data cleaning
This project involves substantial data cleaning in advance to data processing. Understanding the data structure and the corresponding tools is essential in this step. Pandas has a high tolerance level over input data and is capable of handling the subsequent data manipulation.

* Taking out the records that are out of the chronologic order

Being part of the aforementioned steps, this is a very interesting task given its resemblance of daily senario. Instead of trying to re-order the whole list, output data on-the-fly might be necessary in our daily life. `Pandas.groupby` method is chosen using `name` and `zip code` as a combination of key. The donation date in each column is then shifted to the next, obtaining the time span at the same time. The time span is used to determine if the record in each `name` & `zip code` group is of first occurence or out of chronological order, both of which will be deleted.

## 2. Rolling data calculation
This is certianly a very intriguing yet challenging question. The most intuivite thought would be looping through the `keys` as the corresponding list increases in size (code attached). Several attempts have been made to tackel the problem without looping through the whole pandas dataframe. Pandas incoorperates `expanding` option for grouped data with a specified window, which enables the running percentile of contribution calculation. This also applies to the total amount and total times of contribution calculations. Test results shows that the calculation expensen is at around O(1.3). However, the "intuitive method" also gives me O(1.3). There could be bether ways to do it.

# Summary
I found the coding challenge very inspiring and rewarding. Not only did I learn from the project, but also developed lots of other data science related ideas. I do hope the experience would help me come to more insightful thoughts and solid skills. 

# Notes

* Pandas{0.22.0} bug: panda is not using interpolation when expanding/rolling of windows is called. All of the interpolation options ended up getting 'linear' percentile of contribution. Bug reported. As indicated by the code below, calculating the running percentile of contribution can be achieved from sratch.

* The "intuitive method":
>
    dd = defaultdict(list)
    dataset_final = dataset_calc.to_dict('records', into=dd)
    dataset_final[0]['Identity']
    d1 = defaultdict(list)
    d2 = defaultdict(list)
    for item in dataset_final:
        identity=item['Identity']
        amount=item['TRANS_AMT']
        d1[identity].append(amount)
        if len(d1[identity]) >1:
            ranked = sorted(d1[identity])
            n = int(round(percent * len(d1[identity])))
            perc_of_cont=ranked[n-1]
            total_cont=sum(d1[identity])
            time_of_cont=len(d1[identity])
        else:
            perc_of_cont = amount
            total_cont = amount
            time_of_cont =1
        d2[index1].append(identity)
        d2[index1].append(perc_of_cont)
        d2[index1].append(total_cont)
        d2[index1].append(time_of_cont)  




