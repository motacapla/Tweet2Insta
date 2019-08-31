# Tweet2Insta

Collect tweets of specified user, and post Instagram
This one doesn't require Twitter APIs, but needs Instagram API below:
https://www.instagram.com/developer/

## Requirements
You have to create your own `config.py`.
See `requirements.txt` or just `$ pip install -r requirements.txt`

and `$ pip install twitterscraper`

## Usage
1. Scrape tweets via twitterscraper
`$ python twitterscraping.py`

2. Store data into DB, and post Instagram
`$ python Tweet2Insta.py`

## References
- twitterscraper
https://github.com/taspinar/twitterscraper
