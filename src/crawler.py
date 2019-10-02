import os
import argparse
import tweepy
import pandas as pd

# Class for crawling a Twitter user's follower network
# Includes functions for writing to a CSV as an adjacency list format.
class Crawler:
    # Initialize the crawler with an API object by loading in the API/Access keys from
    # the environment variables
    def __init__(self, debug=False, wait_on_rate_limit=True, wait_on_rate_limit_notify=True):
        API_Key         = os.environ.get('Twitter_API_Key')
        API_Secret      = os.environ.get('Twitter_API_Secret')
        Access_Token    = os.environ.get('Twitter_Access_Key')
        Access_Secret   = os.environ.get('Twitter_Access_Secret')

        auth = tweepy.OAuthHandler(API_Key,API_Secret)
        auth.set_access_token(Access_Token, Access_Secret)
        self.api = tweepy.API(auth, wait_on_rate_limit=wait_on_rate_limit, wait_on_rate_limit_notify=wait_on_rate_limit_notify)
        self.debug = debug
    
    # Crawls over a Twitter user's followers and returns it as a list of ids.
    def get_follower_ids(self, user_id_or_name):
        ids=[]
        for page in tweepy.Cursor(self.api.followers_ids, user_id_or_name).pages():
            ids.extend(page)
        return ids

    # Crawls over a Twitter user's list of followed users and returns it as a list of ids.
    def get_followed_ids(self, user_id_or_name):
        ids=[]
        for page in tweepy.Cursor(self.api.friends_ids, user_id_or_name).pages():
            ids.extend(page)
        return ids

    # Crawls a user's network of followed and followers, and
    # writes it to a CSV. Takes a user's id or screen name as input.
    def friendship_network(self,user_id_or_name):
        user = self.api.get_user(user_id_or_name)
        id = user.id
        name = user.screen_name
        if self.debug: print("Building friendship network for user with id {} and screen name {}.".format(id,name))
        
        filename = name+'_friendship_network.csv'

        # Request follower and followed list
        followers = self.get_follower_ids(id)
        followed = self.get_followed_ids(id)

        # Store the lists to a CSV as a directed adjacency list
        pd.DataFrame([[id,*followed]]).to_csv(filename, mode='w', encoding='utf-8', index=False, header=False)
        for follower in followers:
            pd.DataFrame([[follower, id]]).to_csv(filename, mode='a', encoding='utf-8', index=False, header=False)

    # Crawls a user's network of followers for the people they follow, and
    # writes it to a CSV. Takes a user's id or screen name as input.
    def similarity_network(self,user_id_or_name):
        user = self.api.get_user(user_id_or_name)
        id = user.id
        name = user.screen_name
        if self.debug: print("Building similarity network for user with id {} and screen name {}.".format(id,name))
        
        filename = name+'_similarity_network.csv'

        # Get list of visited followers, if the code has already been ran.
        visited_followers = None
        if os.path.exists(filename):
            with open(filename, 'r') as temp_f:
                cols = [ len(l.split(",")) for l in temp_f.readlines() ]
            indexed_cols = [i for i in range(0, max(cols))]
            visited_followers = pd.read_csv(filename, header=None, delimiter=",", names=indexed_cols).iloc[:,0]
        else:
            if self.debug: print('CSV file does not already exist.')

        # Crawl over each follower's followed list and append it to the dataframe
        followers = self.get_follower_ids(id)
        if self.debug: print("User has {} followers..".format(len(followers)))

        for idx,follower in enumerate(followers):  
            if visited_followers is not None and follower in visited_followers.values:
                # User is already tracked in the CSV, skip them
                if self.debug: print('{}. User with id {} already has been visited, skiping...'.format(idx,follower))
            else:
                try:
                    # Write row to CSV in append mode
                    if self.debug: print("{}. Getting followed users of user with id {}.".format(idx,follower))
                    followed = self.get_followed_ids(follower)
                    row = pd.DataFrame([[follower,*followed]])
                    row = row.to_csv(filename, mode='a', encoding='utf-8', index=False, header=False)
                except tweepy.TweepError:
                    # ERROR: User is under a protected account and can't be crawled, skip them.
                    if self.debug: print('{}. Failed to run the command on user {}, skipping...'.format(idx,follower))

if __name__ == '__main__':
    parser = argparse.ArgumentParser();
    parser.add_argument('user_id_or_name', help='The id or name of the user to build a network for.')
    parser.add_argument('-d','--debug', action="store_true", help='Outputs additional information about what the script is doing.')
    parser.add_argument('-t','--type', choices=['friendship','similarity'], help='Type of network to produce.')
    args = parser.parse_args();

    crawler = Crawler(debug=args.debug);
    if args.type == 'similarity':
        crawler.similarity_network(args.user_id_or_name)
    else: # default option
        crawler.friendship_network(args.user_id_or_name)