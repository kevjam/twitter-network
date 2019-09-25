import os
import argparse
import tweepy
import pandas as pd

# Class for crawling a Twitter user's follower network
class Crawler:
    # Initialize the crawler with an API object by loading in the API/Access keys from
    # the environment variables
    def __init__(self, wait_on_rate_limit=True, wait_on_rate_limit_notify=True):
        API_Key         = os.environ.get('Twitter_API_Key')
        API_Secret      = os.environ.get('Twitter_API_Secret')
        Access_Token    = os.environ.get('Twitter_Access_Key')
        Access_Secret   = os.environ.get('Twitter_Access_Secret')

        auth = tweepy.OAuthHandler(API_Key,API_Secret)
        auth.set_access_token(Access_Token, Access_Secret)
        self.api = tweepy.API(auth, wait_on_rate_limit=wait_on_rate_limit, wait_on_rate_limit_notify=wait_on_rate_limit_notify)
    
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

    # Crawls a user's network of followers for the people they follow, and
    # writes it to a CSV. Takes a user's id or screen name as input.
    def network_to_csv(self,user_id_or_name):
        user = self.api.get_user(user_id_or_name)
        id = user.id
        name = user.screen_name

        # Initializes the DataFrame for storing the network
        df = pd.DataFrame()

        # Crawl over each follower's followed list and append it to the dataframe
        followers = self.get_follower_ids(id)
        for follower in followers:
            followed = self.get_followed_ids(follower)
            df = df.append([[follower,*followed]])

        # Writes the network to a CSV file
        df.to_csv(name+'_network.csv', mode='w', index=False, header=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser();
    parser.add_argument('user_id_or_name', help='The id or name of the user to build a network for.')
    args = parser.parse_args();

    crawler = Crawler();
    crawler.network_to_csv(args.user_id_or_name)