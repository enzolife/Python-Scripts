import datetime
import calendar


def get_today_date():
    today_date = datetime.date.today()
    return today_date


def get_yesterday_date():
    yesterday_date = datetime.date.today() + datetime.timedelta(days=-1)
    return yesterday_date


def get_last_sunday():
    yesterday = get_yesterday_date()
    idx = yesterday.weekday() + 1
    sun = yesterday - datetime.timedelta(idx)
    return sun


def get_last_monday():
    last_sunday = get_last_sunday()
    mon = last_sunday + datetime.timedelta(days=-6)
    return mon


def get_this_monday():
    yesterday = get_yesterday_date()
    idx = yesterday.weekday() + 1
    thismon = yesterday - datetime.timedelta(idx - 1)
    return thismon


def get_start_of_this_month():
    yesterday = get_yesterday_date()
    start_date = datetime.date(yesterday.year, yesterday.month, 1)
    return start_date


def get_end_of_this_month():
    yesterday = get_yesterday_date()
    end_date = datetime.date(yesterday.year, yesterday.month, calendar.mdays[yesterday.month])
    return end_date


def get_start_of_last_month():
    yesterday = get_yesterday_date()
    start_date = datetime.date(yesterday.year, yesterday.month, 1)
    return start_date


def get_end_of_last_month():
    start_of_this_month = get_start_of_this_month()
    end_of_last_month = start_of_this_month + datetime.timedelta(days=-1)
    return end_of_last_month


def get_start_of_last_month():
    end_of_last_month = get_end_of_last_month()
    start_of_last_month = datetime.date(end_of_last_month.year, end_of_last_month.month, 1)
    return start_of_last_month


def get_wtd_duration():
    start = get_this_monday()
    end = get_yesterday_date()
    duration = (end - start).days + 1
    return duration


def get_mtd_duration():
    start = get_start_of_this_month()
    end = get_yesterday_date()
    duration = (end - start).days + 1
    return duration


def get_last_month_duration():
    start = get_start_of_last_month()
    end = get_end_of_last_month()
    duration = (end - start).days + 1
    return duration

# print('Today: %s' % get_today_date())
# print('Yesterday: %s' % get_yesterday_date())
# print('Last Sunday: %s' % get_last_sunday())
# print('Last Monday: %s' % get_last_monday())
# print('This Monday: %s' % get_this_monday())
# print('Start of This Month: %s' % get_start_of_this_month())
# print('End of This Month: %s' % get_end_of_this_month())
# print('Start of Last Month: %s' % get_start_of_last_month())
# print('End of Last Month: %s' % get_end_of_last_month())
# print('WTD duration: %s' % get_wtd_duration())
# print('MTD duration: %s' % get_mtd_duration())
# print('M-1 duration: %s' % get_last_month_duration())
