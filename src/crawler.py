import os
import tweepy

class Crawler:
    def __init__(self, wait_on_rate_limit=True, wait_on_rate_limit_notify=True):
        API_Key         = os.environ.get('Twitter_API_Key')
        API_Secret      = os.environ.get('Twitter_API_Secret')
        Access_Token    = os.environ.get('Twitter_Access_Key')
        Access_Secret   = os.environ.get('Twitter_Access_Secret')

        auth = tweepy.OAuthHandler(API_Key,API_Secret)
        auth.set_access_token(Access_Token, Access_Secret)
        self.api = tweepy.API(auth, wait_on_rate_limit=wait_on_rate_limit, wait_on_rate_limit_notify=wait_on_rate_limit_notify)
    
    def get_follower_ids(self, user_id_or_name):
        ids=[]
        for page in tweepy.Cursor(self.api.followers_ids, user_id_or_name).pages():
            ids.extend(page)
        return ids