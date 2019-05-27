## Tweet Collector
Tweet Collector is a tool built to automate the collection, storage, and retrieval of tweets for data analysis. Tweet are collected from either the Twitter stream or REST API based based on a user-designated schedule and a selected collection algorithm. Collection is performed over a set number of intervals each day and tweets are saved as JSON files in a numbered folder system. Tweets can be collected through a notebook or shell script. Stored tweets can be pulled from the folder system into a PANDAS DataFrame for analysis.

#### Origin
This project is an extension of an assignment for a social media mining class and is intended to serve as a learning tool with multiple applications. For this reason, I have updated the scripts to better capture my specific interests in the data and to publish the tool for others to use. To view my analysis of collected Twitter data using the initial version of this tool, checkout my Twitter_Analysis repository.

#### Components
The scripts folder contains the python scripts that run the application.
The notebooks folder contains a notebook for the collection of tweets and one that allows a user to select one or more tweet as a PANDAS DataFrame.
A data folder is used to store saved tweets according the structure defined in the config file.

#### config.py
The config file contains a set of file paths for tweet storage and the functions needed by the application to access the folders. File paths and folder names can be changed but must be in sync.

A file path to the user's (supplied) Twitter developer authorization file is provided. Add keys in the following line-separated order.

CONSUMER_KEY

CONSUMER_SECRET

OAUTH_TOKEN

OAUTH_TOKEN_SECRET


A python dictionary is used store weights used to determine a tweet/user's influence score.

#### schedule.py
The schedule script contains a set of user-facing functions that manage the creation of a daily schedule and the selection of the collection algorithm. Users create and import an Excel-based sheet and input a starting date and set collection interval parameters. This information is stored in a JSON file (one for each day) inside the data folder and is used to manage the associated saved tweets and to provide information on the collection interval.

#### collection.py
The collection script contains functions that manage the Twitter API and is not accessed directly by the user. 

#### app.py
The app script is an alternative to the collection notebook for scheduling the collection interval and running the collection algorithms through a command line. 

#### cleaning.py
The cleaning script manages an ETL pipeline from stored JSON files to PANDAS DataFrame and is not accessed directly by the user.

#### Collection Algorithms
There are currently two collection algorithms to choose from: one focused on gathering tweets for machine learning and one focused on collecting information on users and their friends and followers for network analysis. Both algorithms limit tweets to a geographic area set by a 4 point bounding box within the collection script. Both algorithms incorporate the concept of a weighted influence score based on use several user/tweet parameters which I use in determining the time a tweet will reach its peak influence. See my analysis projects for information on influence score. 


For the ML algorithm, tweets are initially captured from the Twitter stream and then updated at set intervals over a 24-hour period. Delta values are used to determine when a tweet is influential relative to its release time.


For the NW algorithm, tweets are collected from the stream and users that fall into the geographic area are saved to JSON. Their friends and followers information is collected and the influence score is determined for each.

#### On-Going Work
I am currently collecting new data and reworking a set of scripts for automating feature extraction and network analysis based on my initial work that will be added to this repo.