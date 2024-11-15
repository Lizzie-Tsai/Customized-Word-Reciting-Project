# Assumption:
# 1. Different people may have different learning curve.
# 2. A single person may have different learning curve on different vocabularies,
#    depends on the vocabulary's difficulty

# Performance Evaluation:
# 1. After three times of learning, if the learner correctly answer a vocabulary question twice consecutively,
#    we say the learner successfully learned the word. If not, the learner will have to continue to learn the word
#    until he successfully answers the vocabulary question twice.
# 2. With every day doing same number of questions, we evaluate how much time every user use to successfully
#    learn a fixed number of vocabularies. And calculate the sum, the average, the coefficient of the time
#    required as the final result.
# 3. We compare the results with and without our algorithms.

# Algorithms:
# Benchmark: using the basic forgetting curve. (首次學習後的第20min(remain 58.2%) 、1hr(remain 44.2%) 、
# 9hr(remain 35.8%) 、1day(remain 33.7%)、2day(remain 27.8%)、6day(remain 25.4%)、31day(remain 21.1%))
# https://std.stheadline.com/education/article/1434740/%E6%95%99%E8%82%B2-%E7%86%B1%E8%A9%B1-%E4%B8%AD%E6%96%87%E6%95%99%E5%AE%A4-%E5%B0%88%E5%AE%B6%E6%8C%87%E5%8D%B3%E6%97%A5%E6%BA%AB%E7%BF%92-%E8%83%BD%E6%B8%9B%E6%85%A2%E9%81%BA%E5%BF%98%E6%9B%B2%E7%B7%9A%E9%80%9F%E5%BA%A6-%E5%8A%A0%E6%B7%B1%E8%A8%98%E6%86%B6
# review whenever retaining vocabularies fall around 80%
# 1day(remain 33.7%)、2day(remain 27.8%)、6day(remain 25.4%)、31day(remain 21.1%))
# https://www.soleisure.com.hk/article/T2
#
# Our Algo:
# 1. When ever a learner answer incorrectly for more than 20% of review question, shorten the time between reviewing for half day.
# 2. When ever a learner answer correctly for more than 90% of review question, increase the time between reviewing for half day.


# Testing Dataset:
# 1. randomly design forgetting curve for each learner.
# eg. 1, 2, 6, 31
# eg. 1.5, 4, 8, 33
# setting: (0.5-1.5), (1-3), (4-8), (26-36)
# When and how does a learner forget?
# A: a learner will forget 80% of vocabularies in that round whenever it reaches a reviewing day.
import pandas as pd
from datetime import datetime
import random
import math
import time

def recite_new_vocab(user_id, suit_review_time, quota, vocab, start_learn_id, day, batch_size):
    x = round(quota/4*2)
    record = pd.DataFrame()
    record['user_id'] = [user_id for i in range(x)]
    record['vocab_id'] = vocab['vocab_id'][:x]
    record['mean_id'] = vocab['mean_id'][:x]
    record['learn_id'] = [ i for i in range(start_learn_id,start_learn_id + x)]
    record['learn_date'] = [day for i in range(x)]
    record['learn_time'] = [datetime.now() for i in range(x)]
    record['level'] = [0 for i in range(x)]
    record['r_count'] = [0 for i in range(x)]
    # Generate a list with 50% True and 50% False values
    is_right = [True] * int(x * (50/100)) + [False] * (x-int(x * (50/100)))
    # Shuffle the list randomly
    random.shuffle(is_right)
    record['is_right'] = is_right
    record['new_learned'] = [~(record['is_right'][i]) for i in range(x)]
    record['last_r'] = [True for i in range(x)]
    record['w_is_right'] = [True for i in range(x)]
    record['forget_rate'] = [(round((20)/(suit_review_time[1]-suit_review_time[0])) if ~(record['is_right'][i]) else round((20)/(suit_review_time[-1]-suit_review_time[-2]))) for i in range(x)]
    record['batch_size'] = [batch_size for i in range(x)]
    record['ready_for_review'] = [False for i in range(x)]
    record['interval'] = [0 for i in range(x)]
    record['complete_count'] = [1 if record['is_right'][i] else 0 for i in range(x)]
    return record

def create_record_after_first_day(user_id, record, review_time, suit_review_time, quota, vocab, day, re_sp_t):
    a_quota = quota
    latest_record = record[record['last_r'] == True]
    latest_record = latest_record.reset_index(drop=True)
    for i in range(len(latest_record)):
        latest_record['interval'][i] = day - latest_record['learn_date'][i]
        # new learned vocab is ready for review after review_time
        if latest_record['r_count'][i] < 3:
            threshold = review_time[latest_record['r_count'][i]+1] - review_time[latest_record['r_count'][i]]
        else:
            threshold = review_time[-1] - review_time[-2]
        if latest_record['new_learned'][i] and latest_record['interval'][i] >= threshold:
            latest_record['ready_for_review'][i] = True
        # not new learned vocab only required to double-check after 5 days
        elif ~(latest_record['new_learned'][i]) and latest_record['interval'][i] >= 5 and latest_record['complete_count'][i] < 2:
            latest_record['ready_for_review'][i] = True

    ready_for_review_record = latest_record[latest_record['ready_for_review'] == True]
    ready_for_review_record = ready_for_review_record.sort_values(by='forget_rate', ascending=False)
    ready_for_review_record = ready_for_review_record.reset_index(drop=True)
    
    index = 0
    sel_re_record = ready_for_review_record.head(0)
    while a_quota > 0 and index <= (len(ready_for_review_record)-1):
        if ready_for_review_record['w_is_right'][index]:
            minus_quota = 0.5
        else:
            minus_quota = 1.5
        if a_quota - minus_quota >= 0:
            entry = ready_for_review_record.loc[ready_for_review_record.index == index]
            sel_re_record = pd.concat([sel_re_record, entry])
        a_quota = a_quota - minus_quota
        index = index + 1
    if len(sel_re_record.columns.tolist()) > 17:
        sel_re_record.drop(sel_re_record.columns[0], axis=1, inplace=True)
    print("sel_re_record: ")
    print(sel_re_record)
    

    # select new vocab
    ready_vocab = vocab[~vocab['mean_id'].isin(list(record['mean_id']))]
    ready_vocab = ready_vocab.reset_index(drop=True)
    print("ready_vocab: ")
    print(ready_vocab)
    if len(ready_vocab) < int(a_quota/2):
        rest_record = latest_record[latest_record['complete_count']<2]
        rest_record = rest_record.reset_index(drop=True)
        if len(rest_record.columns.tolist()) > 17:
            rest_record.drop(rest_record.columns[0], axis=1, inplace=True)
        index = 0
        while a_quota > 0 and index <= (len(rest_record) - 1):
            if rest_record['w_is_right'][index]:
                minus_quota = 0.5
            else:
                minus_quota = 1.5
            if a_quota - minus_quota >= 0:
                entry = rest_record.loc[rest_record.index == index]
                sel_re_record = pd.concat([sel_re_record, entry])
                a_quota = a_quota - minus_quota
            index = index + 1
        total_len = len(sel_re_record)
    else:
        total_len = len(sel_re_record) + round(a_quota/4*2)
        new_vocab_record = recite_new_vocab(user_id, suit_review_time, a_quota, ready_vocab, len(record), day, total_len)

        # append new record
        record = pd.concat([record, new_vocab_record])
        record = record.reset_index(drop=True)
        if len(record.columns.tolist()) > 17:
            record.drop(record.columns[0], axis=1, inplace=True)
        print("record with new vocab: ")
        print(record)


    # update record last review
    for i in range(len(record)):
        if record['learn_id'][i] in list(sel_re_record['learn_id']):
            record['last_r'][i] = False
            
    sel_re_record = sel_re_record.reset_index(drop=True)
    if len(sel_re_record.columns.tolist()) > 17:
        sel_re_record.drop(sel_re_record.columns[0], axis=1, inplace=True)
    
    time.sleep(8)
    sel_re_record_be_up = sel_re_record.copy(deep=True)
    # Update review record
    sel_re_record_be_up['learn_id'] = [i for i in range(len(record), len(record) + len(sel_re_record))]
    sel_re_record_be_up['learn_date'] = [day for i in range(len(sel_re_record))]
    sel_re_record_be_up['batch_size'] = [total_len for i in range(len(sel_re_record))]
    sel_re_record_be_up['ready_for_review'] = [False for i in range(len(sel_re_record))]
    for i in range(len(sel_re_record)):
        sel_re_record_be_up['learn_time'][i] = datetime.now()
        if ((sel_re_record['new_learned'][i]) == True) and (sel_re_record['r_count'][i] < 3):
            sel_re_record_be_up['r_count'][i] = sel_re_record['r_count'][i]+1
        sel_re_record_be_up['is_right'][i] = sel_re_record['w_is_right'][i]
        if sel_re_record['r_count'][i] < 2:
            sel_re_record_be_up['forget_rate'][i] = (round((20) / (suit_review_time[(sel_re_record['r_count'][i]+2)] - suit_review_time[sel_re_record['r_count'][i]+1])) if sel_re_record['new_learned'][i] else round((20) / (suit_review_time[-1] - suit_review_time[-2])))
        if ((sel_re_record['new_learned'][i] == False) and (sel_re_record['w_is_right'][i] == True)):
            sel_re_record_be_up['complete_count'][i] = sel_re_record['complete_count'][i] + 1
        if ((sel_re_record['new_learned'][i] == False) and (sel_re_record['w_is_right'][i] == False)):
            sel_re_record_be_up['new_learned'][i] = True
        if ((sel_re_record['new_learned'][i] == True) and (sel_re_record['r_count'][i] >= 2)):
            sel_re_record_be_up['new_learned'][i] = False
    sel_re_record_be_up['w_is_right'] = [True for i in range(len(sel_re_record))]
    print("sel_re_record: ")
    print(sel_re_record_be_up)

    # append review record
    record = pd.concat([record, sel_re_record_be_up])
    record = record.reset_index(drop=True)
    if len(record.columns.tolist()) > 17:
        record.drop(record.columns[0], axis=1, inplace=True)
    print("final record:")
    print(record)


    sel_re_record_be_up.to_csv("sel_re_record_be_up.csv")
    record.to_csv("record.csv")
    sel_re_record.to_csv("sel_re_record.csv")

    return

def Update_w_is_right(record):
    record = record.copy(deep=True)
    latest_record = record[record['last_r'] == True]
    forget_rate = list(set(list(latest_record['forget_rate'])))
    print("before drop:")
    print(latest_record.columns.tolist())
    print(len(latest_record.columns.tolist()))
    print(latest_record)
    if len(latest_record.columns.tolist()) > 17:
        latest_record.drop(latest_record.columns[0], axis=1, inplace=True)
    print("after drop:")
    print(latest_record.columns.tolist())
    print(len(latest_record.columns.tolist()))
    print(latest_record)
    for i in forget_rate:
        target_record = latest_record[latest_record['forget_rate'] == i]

        target_record_t = target_record[target_record['w_is_right'] == True]
        forget_num = math.ceil(len(target_record) * i/100)
        print("forget_num: ", forget_num)
        try:
            forget_record =target_record_t.sample(n=forget_num)
            print("forget record: ")
            print(forget_record)
            for j in range(len(record)):
                if record['learn_id'][j] in list(forget_record['learn_id']):
                    record['w_is_right'][j] = False
        except:
            pass
    return record



def check_if_complete(record):
    complete = False
    latest_record = record[record['last_r'] == True]
    complete_record = latest_record[latest_record['complete_count'] == 2]
    complete_record = complete_record[complete_record['new_learned'] == False]
    print("len(complete_record): ", len(complete_record))
    if len(complete_record) >= 300:
        complete = True
    return complete

def update_forget_curve(record, review_time):
    time.sleep(8)
    record = record
    print("record len:", len(record))
    for i in range(len(review_time)-1):
        record_a = record.loc[record['r_count'] == (i+1)]
        time.sleep(3)
        record_f = record_a.loc[record_a['is_right'] == False]
        time.sleep(8)
        if len(record_a) != 0:
            print(f"{i+1} len(record_f): ", len(record_f))
            print(f"{i+1} len(record_a): ", len(record_a))

            record_per = len(record_f)/len(record_a)
            print(f"{i + 1} record_per: ", record_per)
            if record_per > 0.25:
                review_time[(i+1)] -= 0.5
            elif record_per < 0.15:
                review_time[(i+1)] += 0.5
    print("review time: ", review_time)
    return review_time

review_time = [0, 1, 3, 6]
suit_review_time = [0, 2, 4, 8]
quota = 40
day = 1
user_id = 0
vocab = pd.read_csv('vocab.csv')
record = recite_new_vocab(user_id, suit_review_time, quota, vocab, 0, 0, quota)
record.to_csv("record.csv")
is_complete = False

# while ~is_complete and day < 10:
while ~is_complete:
    print("day: ", day)
    # read record
    record = pd.read_csv("record.csv")
    time.sleep(8)

    # update forget curve
    print("record len:", record.shape[0])
    record_a_1 = record.loc[record['r_count'] == 1]
    time.sleep(3)
    record_f_1 = record_a_1.loc[record_a_1['is_right'] == False]
    time.sleep(2)
    if len(record_a_1) != 0:
        print(f"{1} len(record_f): ", record_a_1.loc[record_a_1['is_right'] == False].shape[0])
        print(f"{1} len(record_a): ", record.loc[record['r_count'] == 1].shape[0])

        record_per = len(record_f_1) / len(record_a_1)
        print(f"{1} record_per: ", record_per)
        if record_per > 0.25:
            review_time[1] -= 0.5
        elif record_per < 0.15:
            review_time[1] += 0.5
    #--------------------------------------------------------------
    
    print("review time: ", review_time)


    # forget
    record = Update_w_is_right(record)
    time.sleep(8)

    # review
    create_record_after_first_day(user_id, record, review_time, suit_review_time, quota, vocab, day, 0.5)
    time.sleep(8)

    # check if complete
    is_complete = check_if_complete(record)
    time.sleep(8)



    if is_complete:
        print(f"Complete on day: {day} !!!!")

    day = day+1


# first day
# recite_new_vocab(user_id, suit_review_time, quota, vocab, start_learn_id, day, batch_size)
# record = recite_new_vocab(user_id, suit_review_time, quota, vocab, 0, day, quota)
# print(record)
# record.to_csv("record.csv")

# forget
# Update_w_is_right(record)
# record = pd.read_csv("new_record.csv")
# record_after_forget = Update_w_is_right(record)
# record_after_forget.to_csv("new_record_after_forget.csv")


# day after the first day
# record = pd.read_csv("new_record_after_forget.csv")
# create_record_after_first_day(user_id, record, review_time, suit_review_time, quota, vocab, day, re_sp_t)
# create_record_after_first_day(user_id, record, review_time, suit_review_time, quota, vocab, day, 0.5)


