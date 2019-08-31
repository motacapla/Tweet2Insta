from twitterscraper import query_tweets

"""
    params
    q: keyword included in tweet
    user: username written after @
"""

q = '自炊'
user = 'malin013'
datapath = 'test.json'

def twitter_scraping():
    with open(datapath, 'w') as f: 
        for tweet in query_tweets(q+" :from "+user, 10):
            #f.write(tweet.encode('utf-8'))
            f.write(tweet)
        f.close()


if __name__ == '__main__':
    twitter_scraping()
