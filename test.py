from twitterscraper import query_tweets

"""
    params
    q: keyword included in tweet
    user: username written after @
"""

q = '自炊'
user = 'malin013'
datapath = 'test.json'

if __name__ == '__main__':
    twitterscraping()
    list_of_tweets = query_tweets(q+" :from "+user, 10)

    with open(datapath, 'w') as f: 
        for tweet in query_tweets("Trump OR Clinton", 10):
            f.write(tweet.encode('utf-8'))
        f.close()
