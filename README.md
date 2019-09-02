# Tweet2Insta

Collect tweets of specified user, and post Instagram
This one doesn't require Twitter APIs, but needs Instagram API below:
https://www.instagram.com/developer/

## Requirements
You have to create your own `config.py`.
See `requirements.txt` or just `$ pip install -r requirements.txt`

and `$ pip install twitterscraper`

## Usage
1. Create MySQLDB

```
mysql>
USE mysql;
ALTER USER 'root'@'localhost' identified BY 'root';
flush privileges;
create database tweet2insta;
use tweet2insta;
create table tweets (id bigint not null primary key, datetime datetime, text text, img_path varchar(255));
alter table tweets default character set utf8mb4;
alter table tweets modify text varchar(255) character set utf8mb4;
```

2. Make dir
`$ mkdir img && mkdir html`

3. Scrape tweets via twitterscraper
`$ python twitterscraping.py`

4. Store data into DB, and post Instagram
`$ python Tweet2Insta.py`

## References
- twitterscraper
https://github.com/taspinar/twitterscraper
