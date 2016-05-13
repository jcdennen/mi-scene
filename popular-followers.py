# twitter-crawloer.py
#
# Description:
# This file is mainly used as a crawler to look at things such as a user's
# followers, top followers, their followers' networks, their followers'
# geolocation, etc.
# NOTE: More to come on this
#
# Author: Jeremy Dennen
# Date: 4-5-2016

import twitter
import spotipy
import json
import time
import sys

# separate file with twitter credentials to use for oauth_login
import twitter_credentials

from pymongo import MongoClient
from sys import maxint
from functools import partial

spotify = spotipy.Spotify()

def main():
    twitter_api = oauth_login()

    artist_name = raw_input("Enter an Artist Name:\n")
    search_results = spotify.search(q='artist:' + artist_name, type='artist')

    # ability for user to select one of the search results (top 5)
    print '\nWhich of the following is the correct Artist?'
    range_max = 5 if (len(search_results['artists']['items']) > 5) else len(search_results['artists']['items'])
    for i in range(0,range_max):
        print '%d. %s - %s' % (i+1, search_results['artists']['items'][i]['name'],
                (search_results['artists']['items'][i]['genres'][0] if search_results['artists']['items'][i]['genres'] else 'No genre specified'))
    x = raw_input('Enter the correct number:\n')
    x = int(x) - 1 # convert and decrease by 1
    # if the user chooses a number out of bounds
    while x > 4 or x < 0:
        x = raw_input('Try that again with a number between 1 and 5.\n')
        x = int(x) - 1
    spotify_info = search_results['artists']['items'][x]

    screen_name = raw_input("Enter a username:\n")

    influential_followers = get_influential_followers(twitter_api, screen_name=screen_name)
    # TODO: gather network information here
    mongo_object = {'artist':artist_name, 'username':screen_name, 'top_followers':influential_followers, 'spotify_info':spotify_info}
    save_to_mongo(mongo_object, 'test', 'influential_followers')

# oauth_login() function taken from Twitter Cookbook
# TODO: MOVE TO A SEPARATE MODULE
def oauth_login():
    # gets imported credentials
    auth = twitter.OAuth(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET, twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)

    twitter_api = twitter.Twitter(auth=auth)
    return twitter_api

# crawl_followers function from Twitter Cookbook
def crawl_followers(twitter_api, screen_name, limit=1000000, depth=2):

    # Resolve the ID for screen_name and start working with IDs for consistency
    # in storage

    seed_id = str(twitter_api.users.show(screen_name=screen_name)['id'])

    _, next_queue = get_friends_followers_ids(twitter_api, user_id=seed_id,
                                              friends_limit=limit, followers_limit=limit)

    # Store a seed_id => _follower_ids mapping in MongoDB

    # save_to_mongo({'followers' : [ _id for _id in next_queue ]}, 'followers_crawl',
                #   '{0}-follower_ids'.format(seed_id))

    d = 1
    while d < depth:
        d += 1
        (queue, next_queue) = (next_queue, [])
        for fid in queue:
            _, follower_ids = get_friends_followers_ids(twitter_api, user_id=fid,
                                                     friends_limit=0,
                                                     followers_limit=limit)

            # Store a fid => follower_ids mapping in MongoDB
            # save_to_mongo({'followers' : [ _id for _id in follower_ids ]},
                        #   'followers_crawl', '{0}-follower_ids'.format(fid))

            print "followers :"
            print follower_ids

            next_queue += follower_ids

# save_to_mongo function taken from Twitter Cookbook
def save_to_mongo(data, mongo_db, mongo_db_coll):

    # Connects to the MongoDB server running on localhost:27017
    client = MongoClient("mongodb://localhost:27017/")

    # Get a reference to a particular database
    db = client[mongo_db]

    # Reference a particular collection in the database
    coll = db[mongo_db_coll]

    # Perform a bulk insert and  return the IDs
    return coll.insert(data)

# helper function for get_influential_followers() used to break up a huge list
# of ids so that we can call users.lookup() on them 100 ids at a time (the max)
def chunk_list(seq, size):
    return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))

# get_influential_followers will work to get a list of followers of a user,
# then filter out those that do not have geo ralted
def get_influential_followers(twitter_api, screen_name):
    # get a giant list of user ids of users that follow the specified screen_name
    follower_ids = get_followers_ids(twitter_api, screen_name=screen_name)
    follower_objects = []

    # define this function that we will use later
    users_lookup = partial(make_twitter_request, twitter_api.users.lookup)

    # break up the list of user ids into subsets of 100 at a time so we can
    # call users.lookup without any issues
    id_count = 0
    for user_id_subset in chunk_list(follower_ids, 100):
        follower_objects += users_lookup(user_id=user_id_subset)
        id_count += 100
        print "looked up next ",id_count," users"

    # filter out users without geo enabled and take top 100 most popular
    follower_objects = [d for d in follower_objects if 'status' in d]
    geo_enabled_users = [d for d in follower_objects if d['status']['place'] != None]
    geo_enabled_users = [d for d in geo_enabled_users if d['followers_count'] > d['friends_count']]
    geo_enabled_users.sort(key=lambda k : k['followers_count'], reverse=True)
    print "length of list before clipping: ",len(geo_enabled_users)
    geo_enabled_users = geo_enabled_users[:500]

    # print json.dumps(geo_enabled_users, indent=2)

    return geo_enabled_users

# get_followers_ids function from Twitter Cookbook
def get_followers_ids(twitter_api, screen_name=None, user_id=None, followers_limit=maxint):

    # Must have either screen_name or user_id (logical xor)
    assert (screen_name != None) != (user_id != None),     "Must have screen_name or user_id, but not both"

    # See https://dev.twitter.com/docs/api/1.1/get/friends/ids and
    # https://dev.twitter.com/docs/api/1.1/get/followers/ids for details
    # on API parameters

    # get_friends_ids = partial(make_twitter_request, twitter_api.friends.ids,
                            #   count=5000)
    get_followers_ids = partial(make_twitter_request, twitter_api.followers.ids,
                                count=5000)

    followers_ids = []

    for twitter_api_func, limit, ids, label in [
                    # [get_friends_ids, friends_limit, friends_ids, "friends"],
                    [get_followers_ids, followers_limit, followers_ids, "followers"]
                ]:

        if limit == 0: continue

        cursor = -1
        while cursor != 0:

            # Use make_twitter_request via the partially bound callable...
            if screen_name:
                response = twitter_api_func(screen_name=screen_name, cursor=cursor)
            else: # user_id
                response = twitter_api_func(user_id=user_id, cursor=cursor)

            if response is not None:
                ids += response['ids']
                cursor = response['next_cursor']

            print >> sys.stderr, 'Fetched {0} total {1} ids for {2}'.format(len(ids),
                                                    label, (user_id or screen_name))

            # XXX: You may want to store data during each iteration to provide an
            # an additional layer of protection from exceptional circumstances

            if len(ids) >= limit or response is None:
                print "limit reached"
                break

    # Do something useful with the IDs, like store them to disk...
    print "followers_limit:",followers_limit
    return followers_ids[:followers_limit]

# make_twitter_request function from Twitter Cookbook
def make_twitter_request(twitter_api_func, max_errors=10, *args, **kw):

    # A nested helper function that handles common HTTPErrors. Return an updated
    # value for wait_period if the problem is a 500 level error. Block until the
    # rate limit is reset if it's a rate limiting issue (429 error). Returns None
    # for 401 and 404 errors, which requires special handling by the caller.
    def handle_twitter_http_error(e, wait_period=2, sleep_when_rate_limited=True):

        if wait_period > 3600: # Seconds
            print >> sys.stderr, 'Too many retries. Quitting.'
            raise e

        # See https://dev.twitter.com/docs/error-codes-responses for common codes

        if e.e.code == 401:
            print >> sys.stderr, 'Encountered 401 Error (Not Authorized)'
            return None
        elif e.e.code == 404:
            print >> sys.stderr, 'Encountered 404 Error (Not Found)'
            return None
        elif e.e.code == 429:
            print >> sys.stderr, 'Encountered 429 Error (Rate Limit Exceeded)'
            if sleep_when_rate_limited:
                print >> sys.stderr, "Retrying in 15 minutes...ZzZ..."
                sys.stderr.flush()
                time.sleep(60*15 + 5)
                print >> sys.stderr, '...ZzZ...Awake now and trying again.'
                return 2
            else:
                raise e # Caller must handle the rate limiting issue
        elif e.e.code in (500, 502, 503, 504):
            print >> sys.stderr, 'Encountered %i Error. Retrying in %i seconds' %                 (e.e.code, wait_period)
            time.sleep(wait_period)
            wait_period *= 1.5
            return wait_period
        else:
            raise e

    # End of nested helper function

    wait_period = 2
    error_count = 0

    while True:
        try:
            return twitter_api_func(*args, **kw)
        except twitter.api.TwitterHTTPError, e:
            error_count = 0
            wait_period = handle_twitter_http_error(e, wait_period)
            if wait_period is None:
                return
        except URLError, e:
            error_count += 1
            time.sleep(wait_period)
            wait_period *= 1.5
            print >> sys.stderr, "URLError encountered. Continuing."
            if error_count > max_errors:
                print >> sys.stderr, "Too many consecutive errors...bailing out."
                raise
        except BadStatusLine, e:
            error_count += 1
            time.sleep(wait_period)
            wait_period *= 1.5
            print >> sys.stderr, "BadStatusLine encountered. Continuing."
            if error_count > max_errors:
                print >> sys.stderr, "Too many consecutive errors...bailing out."
                raise

if __name__ == '__main__':
    main()
