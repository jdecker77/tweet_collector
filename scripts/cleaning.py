'''
Imports
-------------------------------------------------------------------------------------------
'''
# Python
import json
import datetime
import sys
import os

# 3rd Party
import numpy as np
import pandas as pd

# Local 
import config


'''
C
-------------------------------------------------------------------------------------------
'''

def ExtractUsers():
    # Get list of user files
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    user_folder = config.GetUsersFolder().replace('../','')
    tmp = APP_ROOT.replace('scripts',user_folder+'/')
    users = os.listdir(os.path.dirname(tmp))
    # print(users)

    df = pd.DataFrame(users,index=np.arange(0,len(users)),columns=['user'])
    df = FlattenUser(df)

    return df

'''
Get statuses as dataframe
'''
def ExtractTweets(month,days,sets,calls,num_tweets,collection_type,clean=True,useWeights=True,wrapEntities=True):
    # Change days to interval days to pull from multiple months.
    # Determine file combos     
    file_combos = []
    for i in days:
        for j in sets:
            for k in calls:
                file_combo = (i,j,k)
                file_combos.append(file_combo)

    # Get statuses for all combos    
    statusCollection = []
    for file_combo in file_combos:
        day_num = file_combo[0] 
        set_name = file_combo[1]
        call_num = file_combo[2]
        filename = config.GetTweetFileName(month,day_num,set_name,call_num,collection_type)
        if filename != '':
            # Add in sample data 
            status = config.ReadJSON(filename)
            filename = config.GetSetsFileName(month,day_num,collection_type)
            sets = config.ReadJSON(filename)
            # Validate numtweets
            if num_tweets <= 0:
                num_tweets = 10
            elif num_tweets > len(status):
                num_tweets = len(status)
            # Add each set attribute
            status = status[:num_tweets]
            for tweet in status:
                tweet['day'] = day_num
                tweet['set'] = set_name
                tweet['call'] = call_num
                offset = datetime.timedelta(hours=5)
                time = sets[set_name-1]['call_times'][call_num-1]
                tweet['calltime'] = time
                if useWeights == True:
                    influence_score = (tweet['favorite_count']*config.GetWeights()['favorite_count']) + (tweet['retweet_count']*config.GetWeights()['retweet_count']) + (tweet['user']['followers_count']*config.GetWeights()['followers_count']) + (tweet['user']['listed_count']*config.GetWeights()['listed_count']) 
                else:
                    influence_score = tweet['favorite_count'] + tweet['retweet_count']  
                    
                
                tweet['influence_score'] = influence_score

            statusCollection.append(status)
    
    # Load each into dict     
    count = 0
    status_dict = {}
    for statuses in statusCollection:
        for status in statuses:
            status_dict[count] = status
            count += 1

    # Get sorted df from dicts   
    tweets = pd.DataFrame(status_dict).T
    # tweets = tweets.sort_values(by=['influence_score'],ascending=False)
    
    if clean:
        tweets = CleanTweets(tweets)

    if wrapEntities:
        tweets = WrapEntities(tweets)

    return tweets

def FlattenUser(df):

    users = df['user'].tolist()

    user_fields = [
     'created_at',
     'description',
     'favourites_count',
     'followers_count',
     'friends_count',
     'id_str',
     'listed_count',
     'location',
     'name',
     'profile_background_color',
     'profile_background_image_url',
     'profile_image_url',
     'profile_text_color',
     'profile_use_background_image',
     'screen_name',
     'statuses_count',
     'verified']
            

    created_at = []
    description = []
    name = []
    id_str = []
    followers_counts = []
    friends_counts = []
    favorites_counts = []
    listed_count = []
    location = []
    profile_background_color = []
    profile_background_image_url = []
    profile_image_url = []
    profile_text_color = []
    profile_use_background_image = []
    screen_name = []
    statuses_count = []
    verified = []
    for user in users:
        created_at.append(user['created_at'])
        description.append(user['description'])
        favorites_counts.append(user['favourites_count'])
        followers_counts.append(user['followers_count'])
        friends_counts.append(user['friends_count'])
        id_str.append(user['id_str'])
        listed_count.append(user['listed_count'])
        location.append(user['location'])
        name.append(user['name'])
        profile_background_color.append(user['profile_background_color'])
        # profile_background_image_url.append(user['profile_background_image_url'])
        profile_image_url.append(user['profile_image_url'])
        profile_text_color.append(user['profile_text_color'])
        # profile_use_background_image.append(user['profile_use_background_image'])
        screen_name.append(user['screen_name'])
        statuses_count.append(user['statuses_count'])
        verified.append(user['verified'])

    # Add column to df
    df['user_created_at'] = created_at
    df['user_description'] = description
    df['favorites_counts'] = favorites_counts
    df['followers_count'] = followers_counts
    df['friends_count'] = friends_counts
    df['user_id_str'] = id_str
    df['listed_count'] = listed_count
    df['user_name'] = name
    df['user_location'] = location
    df['profile_background_color'] = profile_background_color
    # df['profile_background_image_url'] = profile_background_image_url
    df['profile_image_url'] = profile_image_url
    df['profile_text_color'] = profile_text_color
    # df['profile_use_background_image'] = profile_use_background_image
    df['user_screen_name'] = screen_name
    df['statuses_count'] = statuses_count
    df['verified'] = verified

    df = df.drop(columns= 'user')

    return df


'''
Return a list tweet ids for all tweets in a flat json file
'''
def CleanTweets(tweets):
    # Set initial columns
    columns = ['created_at', 'entities','favorite_count', 'id_str','in_reply_to_status_id_str','in_reply_to_user_id_str', 'is_quote_status', 'lang', 'place','retweet_count', 'retweeted', 'source', 'text', 'user','truncated','calltime', 'day','set','call','influence_score']

    tweets = tweets[columns]

    # Get list of entities foe each type. Must return in order no NA
    entities_list = tweets['entities'].tolist()
    entities = FlattenEntities(entities_list)
    tweets['hashtags'] = entities[0]
    tweets['media'] = entities[1]
    tweets['symbols'] = entities[2]
    tweets['urls'] = entities[3]
    tweets['user_mentions'] = entities[4]
    tweets = tweets.drop(columns= 'entities')
    

    # Flatten user
    tweets = FlattenUser(tweets)
    
    '''
    Flatten place
    Using fullname, id
    '''
    places_list = tweets['place'].tolist()
    place_names = []
    place_ids = []
    for place in places_list:
        place_name = place['full_name']
        place_id = place['id']
        place_names.append(place_name)
        place_ids.append(place_id)

    tweets['place_names'] = place_names
    tweets['place_ids'] = place_ids

    tweets = tweets.drop(columns='place')
    
    '''
    Convert sources to readable types
    '''
    sources = tweets['source'].tolist()
    source_types = []
    for txt in sources:
        start = '>'
        end = '</'  
    #     txt = sample_0.iloc[0]['source']
        x = txt.find(start)
        y = txt.find(end)
        substring = txt[x+1:y]
        source_types.append(substring)

    tweets['sources'] = source_types
    tweets = tweets.drop(columns= 'source')

    
    '''
    Offset time with utc offset
    '''
    offsets = []
    created_times = tweets['user_created_at'].tolist()
    created_dotw = []
    created_hr = []
    for time in created_times:
        time_obj = datetime.datetime.strptime(time,'%a %b %d %H:%M:%S %z %Y')
        offset = datetime.timedelta(hours=5)
        adjusted_time = time_obj-offset
#         adjusted_time = adjusted_time. tz.replace(tzinfo=None)
        offsets.append(adjusted_time)
        created_dotw.append(time[0:3])
        created_hr.append(adjusted_time.hour)
    tweets['created_dotw'] = created_dotw
    tweets['created_hr'] = created_hr

    tweets['created_time'] = offsets

    '''
    Convert user created date to interval
    '''
    user_created_at = tweets['user_created_at']
    user_since = []
    for c_date in user_created_at:
        time_obj = datetime.datetime.strptime(c_date,'%a %b %d %H:%M:%S %z %Y')
        time_now = datetime.date.today()
        years_delta = time_now.year-time_obj.year
        month_delta = time_now.month-time_obj.month
        if month_delta < 0:
            years_delta -= 1
        user_since.append(years_delta)

    tweets['user_since'] = user_since


    
    '''
    Set order
    '''
    cols_final = [
        'id_str',
        'text',
        'hashtags',
        'media',                                                                       
        'symbols',
        'urls',
        'user_mentions',
        # 'created_at',
        'created_hr',
        'created_dotw',
        'calltime',
        'day',
        'set',
        'call',
        'favorite_count',
        'retweet_count',
        'place_names',
        'place_ids',
        'sources',
        'influence_score',
        'in_reply_to_status_id_str',
        'in_reply_to_user_id_str',
        'lang',
        'is_quote_status',
        'retweeted',
        'truncated',
        'user_id_str',
        'user_name',
        'user_description',
        # 'user_created_at',
        'user_location',
        'user_since',
        'favorites_counts',
        'followers_count',
        'friends_count',
        'listed_count',
        'profile_background_color',
        # 'profile_background_image_url',
        # 'profile_image_url',
        'profile_text_color',
        # 'profile_use_background_image',
        'user_screen_name',
        'statuses_count',
        'verified'
    ]
    tweets = tweets[cols_final]

    '''
    Set datatypes
    '''
    tweets['favorite_count'] = tweets['favorite_count'].astype(int)
    tweets['retweet_count'] = tweets['retweet_count'].astype(int)
    # tweets['calltime'] = tweets['favorite_count'].astype(datetime.datetime)
    tweets['followers_count'] = tweets['followers_count'].astype(int)
    tweets['friends_count'] = tweets['friends_count'].astype(int)
    tweets['statuses_count'] = tweets['statuses_count'].astype(int)
    tweets['listed_count'] = tweets['listed_count'].astype(int)
    tweets['influence_score'] = tweets['influence_score'].astype(float)
    tweets['created_hr'] = tweets['created_hr'].astype(object)
    tweets['user_since'] = tweets['user_since'].astype(int)

    return tweets


def FlattenEntity(entity_list,catch):
    accum= []
    for y in range(0,len(entity_list)):
        entity = entity_list[y][catch]
        accum.append(entity)

    stringCollector = []    
    for x,y in enumerate(accum):
        tmpstring = ''
        for i in range(0,len(y)):
            tmpstring += y[i]+' '
        stringCollector.append(tmpstring)

    return stringCollector

'''
Flatten entities
'''
def FlattenEntities(entities_list):
    entities = []

    tagStrings = [] 
    mediaStrings = [] 
    symbolStrings = [] 
    urlStrings = []
    userMentionsStrings = []
    for entity in entities_list:
        keys = entity.keys()
        if 'hashtags' in keys:
            tagStrings.append(FlattenEntity(entity['hashtags'],'text'))
        else:
            tagStrings.append('')
        if 'media' in keys:
            mediaStrings.append(FlattenEntity(entity['media'],'type'))
        else:
            mediaStrings.append('')
        if 'symbols' in keys:
            symbolStrings.append(FlattenEntity(entity['symbols'],'text'))
        else:
            symbolStrings.append('')
        if 'urls' in keys:
            urlStrings.append(FlattenEntity(entity['urls'],'url'))
        else:
            urlStrings.append('')
        if 'user_mentions' in keys:
            userMentionsStrings.append(FlattenEntity(entity['user_mentions'],'id_str'))
        else:
            userMentionsStrings.append('')


    entities = [tagStrings,mediaStrings,symbolStrings,urlStrings,userMentionsStrings]

    return entities


def WrapEntities(data):
    data = WrapTags(data)
    data = WrapMedia(data)
    data = WrapSymbols(data)
    data = WrapUrls(data)
    data = WrapMentions(data) 

    return data

def WrapTags(data):
    rows = data.index.tolist()
    
    tags = []
    for row in rows:
        num_tags = list(data.loc[row]['hashtags'])
        if len(num_tags) == 0:
            tags.append(0)
        else:
            tags.append(len(num_tags))

    data['num_tags'] = tags
    data = data.drop(columns=['hashtags'])
    
    return data

def WrapMedia(data):
    rows = data.index.tolist()

    tags = []
    for row in rows:
        num_tags = list(data.loc[row]['media'])
        if len(num_tags) == 0:
            tags.append(0)
        else:
            tags.append(len(num_tags))

    data['num_media'] = tags
    data = data.drop(columns=['media'])
    
    return data

def WrapSymbols(data):
    rows = data.index.tolist()

    tags = []
    for row in rows:
        num_tags = list(data.loc[row]['symbols'])
        if len(num_tags) == 0:
            tags.append(0)
        else:
            tags.append(len(num_tags))

    data['num_symbols'] = tags
    data = data.drop(columns=['symbols'])
    
    return data

def WrapUrls(data):
    rows = data.index.tolist()

    tags = []
    for row in rows:
        num_tags = list(data.loc[row]['urls'])
        if len(num_tags) == 0:
            tags.append(0)
        else:
            tags.append(len(num_tags))

    data['num_urls'] = tags
    data = data.drop(columns=['urls'])
    
    return data

def WrapMentions(data):
    rows = data.index.tolist()

    tags = []
    for row in rows:
        num_tags = list(data.loc[row]['user_mentions'])
        if len(num_tags) == 0:
            tags.append(0)
        else:
            tags.append(len(num_tags))

    data['num_user_mentions'] = tags
    data = data.drop(columns=['user_mentions'])
    
    return data



        







