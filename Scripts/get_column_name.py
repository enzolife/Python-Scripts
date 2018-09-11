from pandas import Series, DataFrame
import pandas as pd
import glob

def get_column_name(frame):
    return frame[0:1].stack()