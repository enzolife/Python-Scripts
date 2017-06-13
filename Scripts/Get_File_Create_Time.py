# coding: utf-8

# In[5]:

import os
import platform
import time


# In[15]:

# 获得创建时间
def creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':

        timestamp = os.path.getctime(path_to_file)
        time_edited = change_timestamp_to_normal_days(timestamp)

        return time_edited
    else:
        stat = os.stat(path_to_file)
        try:
            return change_timestamp_to_normal_days(stat.st_birthtime)
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return change_timestamp_to_normal_days(stat.st_mtime)


# 修改时间格式
def change_timestamp_to_normal_days(time_before):
    timeArray = time.localtime(time_before)
    otherStyleTime = time.strftime("%Y-%m-%d", timeArray)
    return otherStyleTime
