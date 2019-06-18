'''
Imports
-------------------------------------------------------------------------------------------
'''
# Python
import sys
import time as sleeper

# 3rd Party
import twitter
import pandas as pd
import geopandas as gpd

# Local 
import config


'''
Configure API 
-------------------------------------------------------------------------------------------
'''
def GetTwitterRest():
    try:
        pathToKey = config.GetPathToKey()
        with open(pathToKey,'r') as infile:
            keys = infile.read().split('\n')
            CONSUMER_KEY = keys[0]
            CONSUMER_SECRET = keys[1]
            OAUTH_TOKEN = keys[2]
            OAUTH_TOKEN_SECRET = keys[3]

        auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,CONSUMER_KEY, CONSUMER_SECRET)
        twitter_api = twitter.Twitter(auth=auth)

    except Exception as e:
        print(e, file=sys.stderr)
        print('Could not get rest api.')

    return twitter_api


def GetTwitterStream():
    try:
        pathToKey = config.GetPathToKey()
        with open(pathToKey,'r') as infile:
            keys = infile.read().split('\n')
            CONSUMER_KEY = keys[0]
            CONSUMER_SECRET = keys[1]
            OAUTH_TOKEN = keys[2]
            OAUTH_TOKEN_SECRET = keys[3]

        auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,CONSUMER_KEY, CONSUMER_SECRET)
        twitter_stream=twitter.TwitterStream(auth=auth)

    except Exception as e:
        print(e, file=sys.stderr)
        print('Could not get stream api.')
    
    return twitter_stream


'''
API Calls
-------------------------------------------------------------------------------------------
'''

# 
def GetPlacesByGeo(coords):
    twit_api = GetTwitterRest()

    return twit_api.geo.search(lat=coords[0],long=coords[1],granularity = 'neighborhood')

def GetLocationBoundries(coords,buffer_value):
    
    df = pd.DataFrame(coords,columns=['Latitude','Longitude'])
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude))
    envelope = gdf.geometry.buffer(buffer_value).envelope
    
    area = envelope[0]
    
    minx = area.bounds[0]
    miny = area.bounds[1]
    maxx = area.bounds[2]
    maxy = area.bounds[3]

    geometry = [minx,miny,maxx,maxy]
    
    return geometry


# Query tweets by term and location. Writes to file with query name.
def ReadTweets(list_ofQueries,search_location):
    twit_api = GetTwitterRest()
    
    for x in range(0,len(list_ofQueries)):
        query = list_ofQueries[x]
        search_results = twitter_api.search.tweets(q=query, geocode=search_location, count=100)
    
        filename = GetTweetsFolder()+query+'.json'
        config.WriteJSON(search_results,filename)



# Get user object by user_id and write to file.
def GetUser(user_id):
    print('Getting users')
    twit_api = GetTwitterRest()
    user = twit_api.users.show(user_id=user_id)
    
    filename = config.GetUserFileName(userid)
    config.WriteJSON(user,filename)

'''
Get friends of user by user_id and write to file.
'''
def GetFriends(userid):
    print('Getting friends of ',userid)
    twit_api = GetTwitterRest()

    filename = config.GetUserFileName(userid)
    user = config.ReadJSON(filename)

    pageCount = 0
    friends = []
    next_cursor = -1
    while(next_cursor != 0 and pageCount < 5):
        if twit_api.application.rate_limit_status()['resources']['friends']['/friends/list']['remaining'] > 0:
            friend = twit_api.friends.list(user_id=user['id_str'],count=200, cursor = next_cursor)
            influence_score = 0
            for frnd in friend:
                influence_score = (frnd['followers_count']*config.GetWeights()['followers_count']) + (frnd['listed_count']*config.GetWeights()['listed_count'])
                frnd['influence_score'] = influence_score

            friends.append(friend['users'])
            next_cursor = friend['next_cursor']
            pageCount += 1
        else:
            print("Sleeping")
            delta = 15*60
            sleeper.sleep(delta)
            
    user['friends'] = friends
    config.WriteJSON(user, filename)

'''
Get followers of user by user_id and write to file.
'''
# Add limit and timer. Count is temporary
# twit_api.application.rate_limit_status()['resources']['followers']['/followers/list']['remaining']

def GetFollowers(userid):
    print('Getting followers of',userid)
    twit_api = GetTwitterRest()

    filename = config.GetUserFileName(userid)
    user = config.ReadJSON(filename)
        
    pageCount = 0
    followers = []
    next_cursor = -1
    while (next_cursor != 0 and pageCount < 5):
        if twit_api.application.rate_limit_status()['resources']['followers']['/followers/list']['remaining'] > 0:
            follower = twit_api.followers.list(user_id=userid,count=200, cursor = next_cursor)
            influence_score = 0
            for user in follower:
                influence_score = (user['followers_count']*config.GetWeights()['followers_count']) + (user['listed_count']*config.GetWeights()['listed_count'])
                user['influence_score'] = influence_score

            followers.append(follower['users'])
            next_cursor = follower['next_cursor']
            pageCount += 1
        else:
            print("Sleeping")
            delta = 15*60
            sleeper.sleep(delta)

    user['followers'] = followers
    config.WriteJSON(user, filename)


'''
Filter Statuses - Use streaming API to filter n-number tweets by location.
Each tweet is written to to tweets folder as json file with tweet_id as filename.
'''
def FilterStatusByLocation(params):
    print('Getting new tweets by location')
    
    month_num = params['month']  
    day_num = params['day']  
    set_name = params['set']
    call_num = params['call']
    search_box =  params['boundaries']
    
    if call_num == 1:

        max_tweets=100
        twit_stream = GetTwitterStream()
        try:
            stream = twit_stream.statuses.filter(locations=search_box)
            # Load tweets to list
            statuses = []
            for status in stream:
                statuses.append(status)
                if len(statuses) == max_tweets:
                    break
            
            # Write tweets to file  
            filename = config.GetTweetFileName(month_num,day_num,set_name,call_num)
            config.WriteJSON(statuses,filename)
            call_num +=1
            print('Saved',len(statuses),'statuses to file.')
            
        except Exception as e:
            print(e, file=sys.stderr)
            print('Could not get statuses.')
            
        return call_num 
         
    else:
        print('Error. Check call number.')


'''
API call to get updated statuses for a seed. 
'''
def GetUpdatedStatuses(params):
    print('Updating tweets')
    
    month_num = params['month']  
    day_num = params['day']  
    set_name = params['set']
    call_num = params['call']
    
    filename = config.GetTweetFileName(month_num,day_num,set_name,call_num-1)
    tweet_ids = config.GetTweetIds(filename)
    
    # Pass id get status  
    twit_api = GetTwitterRest()
    statuses = []
    for tweet_id in tweet_ids:
        try:
            status = twit_api.statuses.show(id=tweet_id)
            statuses.append(status)
        except Exception as e:
            print(e, file=sys.stderr)
            print('Skipped tweet id:',tweet_id)
            continue

    # Update call count and write updated statuses to file
    filename = config.GetTweetFileName(month_num,day_num,set_name,call_num)
    call_num +=1
    config.WriteJSON(statuses,filename) 
    print('Saved',len(statuses),'statuses to file.')
    
    # Do i need to return this value or is it saved like streaming
    return call_num


