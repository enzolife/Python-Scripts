import datetime
import calendar
from time import gmtime, strftime


def get_today_date():
    today_date = datetime.date.today() + datetime.timedelta(days=0)
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


def get_current_week_num():
    yesterday = get_yesterday_date()
    week_num = yesterday.isocalendar()[1]
    return week_num


def get_current_year():
    yesterday = get_yesterday_date()
    current_year = yesterday.year
    return current_year


def get_current_month():
    yesterday = get_yesterday_date()
    current_month = yesterday.month
    return current_month


def get_start_end_of_certain_month(months_to_minus, start_or_end):
    compared_date = get_yesterday_date()
    i = 0
    while i < months_to_minus:
        end_of_certain_month = datetime.date(compared_date.year, compared_date.month, 1) + datetime.timedelta(days=-1)
        start_of_certain_month = datetime.date(end_of_certain_month.year, end_of_certain_month.month, 1)
        compared_date = start_of_certain_month
        i = i + 1
    if start_or_end == 'start':
        return start_of_certain_month
    elif start_or_end == 'end':
        return end_of_certain_month


def get_current_datetime():
    current_datetime = datetime.datetime.now()
    return current_datetime


if __name__ == '__main__':
    print('Today: %s' % get_today_date())
    print('Yesterday: %s' % get_yesterday_date())
    print('Last Sunday: %s' % get_last_sunday())
    print('Last Monday: %s' % get_last_monday())
    print('This Monday: %s' % get_this_monday())
    print('Start of This Month: %s' % get_start_of_this_month())
    print('End of This Month: %s' % get_end_of_this_month())
    print('Start of Last Month: %s' % get_start_of_last_month())
    print('End of Last Month: %s' % get_end_of_last_month())
    print('WTD duration: %s' % get_wtd_duration())
    print('MTD duration: %s' % get_mtd_duration())
    print('M-1 duration: %s' % get_last_month_duration())
    print('Yesterday Week Num: %s' % get_current_week_num())
    print('Yesterday Year: %s' % get_current_year())
    print('Yesterday Month: %s' % get_current_month())
    print('M-3 start: %s' % get_start_end_of_certain_month(3, "start"))
    print('M-3 end: %s' % get_start_end_of_certain_month(3, "end"))
    print('M-2 start: %s' % get_start_end_of_certain_month(2, "start"))
    print('M-2 end: %s' % get_start_end_of_certain_month(2, "end"))
    print('M-1 start: %s' % get_start_end_of_certain_month(1, "start"))
    print('M-1 end: %s' % get_start_end_of_certain_month(1, "end"))
    print('Current Date & Time: %s' % get_current_datetime())
    print((get_yesterday_date() + datetime.timedelta(days=-1)).weekday())
