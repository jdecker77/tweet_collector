'''
Imports
-------------------------------------------------------------------------------------------
'''
# Python
import json
import sys
import numpy as np
import pandas as pd
from pathlib import Path

# 3rd Party


# Local 


'''
Set program parameters
-------------------------------------------------------------------------------------------
'''

# Set tweet storage folder
def GetTweetsFolder():
    return '../data/tweets'

# Set user storage folder
def GetUsersFolder():
    return '../data/users'

# Set model storage folder
def GetUsersFolder():
    return '../data/models'

# Set key location. Add to gitignore
def GetPathToKey():
    return '../resources/usr_auth.txt'

# Set influence score weights
def GetWeights():
    weights = {
        'favorite_count': .3,
        'retweet_count': .6,
        'followers_count': .025,
        'listed_count': .075,
    }
    return weights


'''
Helper functions
-------------------------------------------------------------------------------------------
'''
# Get filename for a set of tweets
def GetTweetFileName(month,day,set_n,call=0):
    filename = ''
    if call >= 0 or call <= 10:
        filename = GetTweetsFolder()+'/M'+str(month)+'/D'+str(day)+'/tweets'+'_S'+str(set_n)+'_C'+str(call)+'.json'        
    return filename

def GetUserFileName(user_id):
    return GetUsersFolder()+'/user_'+str(user_id)+'.json'

# Get a filename for given 3 digit combo. Uses stub for all. Add as default stubto allow arg.
def GetSetsFileName(month,day):   
    return GetTweetsFolder()+'/M'+str(month)+'/D'+str(day)+'/sets.json'

# Return a list tweet ids for all tweets in a flat json file
def GetTweetIds(filename):
    statuses = file_io.ReadJSON(filename)
    status_ids = []
    for status in statuses:
        status_ids.append(status['id_str'])
    return status_ids

# Write json to file
def WriteJSON(obj,filename):
    try:
        with open(filename, 'w') as outfile:
            obj_json = json.dumps(obj, sort_keys=True, indent=4,default=str)
            outfile.write(obj_json)
    except Exception as e:
        print(e, file=sys.stderr)
        print('File not written.')

# Read and return json object from file. If none, return empty object.
def ReadJSON(filename):
    try: 
        with open(filename, 'r') as infile:
            obj = json.load(infile)
    except Exception as e: 
        obj = [] 
    return obj

# Write df to csv
def WriteCSV(data,filename):
    with open(filestring,'w') as outfile:
        data.to_csv(outfile)

# Read csv to df
def ReadCSV(filename):
    stub = '../data/models/'
    filestring = stub+filename+'.csv'
    # print('filename:',filestring)
    featureSet = pd.read_csv(filestring,index_col='Unnamed: 0')
    return featureSet

