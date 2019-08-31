#import datetime as dt
import subprocess as sp

user = "malin013"
keyword = "自炊 from:"+user
limit = "5"
#begindate = str(dt.date(2006, 3, 21))
#enddate = str(dt.date.today())
output_path = "data.json"

# currently doesnt work..
#sp.call(["twitterscraper", keyword, " -l"+limit," -bd"+begindate, " -ed"+enddate, "-o"+output_path])

sp.call(["twitterscraper", keyword, "-l "+limit, "-o"+output_path])

