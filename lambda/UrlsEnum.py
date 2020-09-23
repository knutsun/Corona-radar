import enum


class Urls(enum.Enum):

    States = 'http://coronavirusapi.com/states.csv'
    Time_series = 'http://coronavirusapi.com/time_series.csv'
    Time_series_by_state = 'http://coronavirusapi.com/getTimeSeries/'
