import datetime
import calendar

def get_yesterday_date():
    yesterday_date = datetime.date.today() + datetime.timedelta(days=-1)
    return yesterday_date

yesterday = get_yesterday_date()
idx = (yesterday.weekday())+1


print(get_yesterday_date())
print(idx)


