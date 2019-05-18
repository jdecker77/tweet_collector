'''
Imports
-------------------------------------------------------------------------------------------
'''
# Python
import json
import sys
import numpy as np
import pandas as pd
import datetime
import time as sleeper
import os

# 3rd Party
from pathlib import Path

# Local 
import collection
import config


'''
Scheduling

All runs require unique run times.
-------------------------------------------------------------------------------------------
'''
# Create set obj for each day in collection interval.
def MakeSets(year,month,day,collection_interval,interval_identifier,user_schedule,collection_type):

    for interval in range(1,collection_interval+1):

        # Get start times from schedule
        num_sets = len(user_schedule.columns)
        num_calls = len(user_schedule.index)
        cols = list(user_schedule.columns)
        all_times = []
        for col in cols:
            set_runtimes = user_schedule[col]
            for set_runtime in set_runtimes:
                # Create starting time for day. All times midnight to start time get called on following day but recorded for set start day.
                a = datetime.time(hour = 6)
                if set_runtime < a:
                    StartDate = datetime.datetime(year,month,day+1) 
                else:
                    StartDate = datetime.datetime(year,month,day)
                runtime = datetime.datetime.combine(StartDate,set_runtime)
                all_times.append(runtime)
        
        # Create sets obj
        sets = []
        j=0
        for i in range(1,num_sets+1):
            k=j+num_calls
            name = 'set_'+str(i)
            runs = all_times[j:k]
            day = day
            set_x = {
                'interval_name':interval_identifier,
                'total_intervals':collection_interval,
                'collection_type':collection_type,
                'interval':interval,
                'year':year,
                'month':month,
                'day':day,
                'name':name,
                'set':i,
                'call':1,
                'runtimes':runs,
                'call_times':[]
                }
            sets.append(set_x)
            j+=num_calls
        
        # Add month and day folders if needed
        APP_ROOT = os.path.dirname(os.path.abspath(__file__))
        tweets_folder = config.GetTweetsFolder().replace('../','')
        MONTH_ROOT = APP_ROOT.replace('scripts',tweets_folder+'/'+collection_type+'/M'+str(month))
        if not os.path.isdir(MONTH_ROOT):
            os.mkdir(MONTH_ROOT)

        DAY_ROOT = MONTH_ROOT+"/D"+str(day)
        if not os.path.isdir(DAY_ROOT):
            os.mkdir(DAY_ROOT)

        config.WriteJSON(sets,config.GetSetsFileName(month,day,collection_type))
        
        # increment day. if day is in next month, increment month, set day to 1
        # Add year by EOY!
        day += 1
        try:
            datetime.datetime(year,month,day)
        except ValueError as e:
            if str(e) == "day is out of range for month":
                month += 1
                day = 1
            try:
                datetime.datetime(year,month,day)
            except ValueError as e:
                if str(e) == "month must be in 1..12":
                    month = 1


def PreviewSchedule(month,day,collection_type):
    
    sets = config.ReadJSON(config.GetSetsFileName(month,day,collection_type))
    
    print("\n")
    print("Preview Schedule")
    print("____________________________________________")
    print("Interval Name:",sets[0]['interval_name'])
    print("Interval Type:",sets[0]['interval_type'])
    print("Total Intervals:",sets[0]['total_intervals'])
    print("Interval Number:",sets[0]['interval'])

    times = []
    for set_n in sets:
        for time in set_n['runtimes']:
            times.append(time)
    
    print('\n')
    print("Number Sets:",len(sets))
    print("Number Calls:",len(sets[0]['runtimes']))
    print("Current Call:",sets[0]['call'])
    print('\n')
    
    sorted_times = sorted(times)

    call_copy = 1       
    for sorted_time in sorted_times:
        for set_n in sets:
            if sorted_time in set_n['runtimes']:
                timer = sorted_time
                timex = datetime.datetime.strptime(timer,'%Y-%m-%d %H:%M:%S')
                print('Set:',set_n['set'],' Call:',call_copy,'Runtime:',timer)
                call_copy += 1


'''
Run Collectors

All runs require unique run times.
-------------------------------------------------------------------------------------------
'''
# Collects initial tweet from stream and updates from rest
def RunMLCollector(month,day):
    filename = config.GetSetsFileName(month,day,collection_type)
    sets = config.ReadJSON(filename)
    
    times = []
    for set_n in sets:
        for time in set_n['runtimes']:
            times.append(time)
        
    sorted_times = sorted(times)
    
    for sorted_time in sorted_times:
        for set_n in sets:
            if sorted_time in set_n['runtimes']:
                timer = sorted_time
                timex = datetime.datetime.strptime(timer,'%Y-%m-%d %H:%M:%S')
                if timex > datetime.datetime.now():
                    delta = int((timex - datetime.datetime.now()).total_seconds())
                    print('Waiting',delta,'seconds. Next Up',set_n['name'],set_n['call'],timex)
                    sleeper.sleep(delta)
                    
                    # Set API calls
                    if set_n['call'] == 1:
                        collection.FilterStatusByLocation(set_n)
                    else:
                        set_n['call'] = collection.GetUpdatedStatuses(set_n)
                    calltime = datetime.datetime.now()
                    set_n['call_times'].append(calltime)
                    config.WriteJSON(sets,filename)
                else:
                    print('skipping old runtime.')

# Collect tweets from geo area. Local users are added to users folder and their friends/followers are pulled. Skipping existing users for now.
def RunNWCollector(month,day):
    import config

    filename = config.GetSetsFileName(month,day,collection_type)  
    sets = config.ReadJSON(filename) 
    
    localPlaces = ['Erie, PA','Wesleyville, PA','Harborcreek, PA','Lawrence Park, PA']
    
    times = []
    for set_n in sets:
        for time in set_n['runtimes']:
            times.append(time)
        
    sorted_times = sorted(times)
    
    for sorted_time in sorted_times:
        for set_n in sets:
            if sorted_time in set_n['runtimes']:
                timer = sorted_time
                timex = datetime.datetime.strptime(timer,'%Y-%m-%d %H:%M:%S')
                if timex > datetime.datetime.now():
                    delta = int((timex - datetime.datetime.now()).total_seconds())
                    print('Waiting',delta,'seconds. Next Up',set_n['name'],set_n['call'],timex)
                    sleeper.sleep(delta)
                    
                    # Get tweets 
                    collection.FilterStatusByLocation(set_n)

                    # Update sets
                    calltime = datetime.datetime.now()
                    set_n['call_times'].append(calltime)
                    config.WriteJSON(sets,filename)

                    # Check each user, if in Erie write to users and get friends/followers
                    tweets = config.ReadJSON(config.GetTweetFileName(set_n['month'],set_n['day'],set_n['set'],set_n['call']))
                    newUsers = []
                    for tweet in tweets:
                        influence_score = 0
                        if tweet['place'] and tweet['place']['full_name'] in localPlaces:
                            influence_score = (tweet['user']['followers_count']*config.GetWeights()['followers_count']) + (tweet['user']['listed_count']*config.GetWeights()['listed_count'])
                            tweet['user']['influence_score'] = influence_score
                            newUsers.append(tweet['user'])

                    # Write each user to file, get friends, followers
                    for user in newUsers:
                        filename = config.GetUserFileName(user['id_str'])
                        config = Path(filename)
                        if config.is_file():
                            # Update this - need the most current version but not if user is in this set
                            print('User',user['id_str'],'already exists. Skipping for now.')
                        else:
                            print('Writing user',user['id_str'])
                            config.WriteJSON(user,filename)
                            collection.GetFriends(user['id_str'])
                            collection.GetFollowers(user['id_str'])
                else:
                    print('skipping old runtime.')
 