# -*- coding: utf-8 -*-
try:
    from enum import Enum
except ImportError:
    from enum34 import Enum

from dateutil.rrule import * # TODO only what we need ...

from datetime import date, datetime
import time

# TODO placeholder so we can prepare to localize strings until we actually localize strings
# ref: https://docs.python.org/2/library/gettext.html
# ref: http://www.wefearchange.org/2012/06/the-right-way-to-internationalize-your.html
# look into gettext, as well as babel and i18n libraries
def _(message): return message

class intervals(Enum):
    # TODO comments
    YEAR = 'y'
    MONTH = 'm'
    DAY = 'd'
    QUARTER = 'q'
    WEEK = 'w'

class IntervalResult(dict):
    """
    Subclass of dict makes it JSON serializable via json.dumps()
    """

    @property
    def begin_date(self):
        """
        Get the interval begin date. Always of type datetime (even if it was set to a date)
        """
        return datetime.fromtimestamp(self['begin_date'])
    @begin_date.setter
    def begin_date(self, begin_date):
        """
        Set the interval begin date to either a date or a datetime.
        """
        if(not isinstance(begin_date, (date, datetime))):
            raise TypeError(_("begin_date must be of type date or datetime"))
        self['begin_date'] = time.mktime(begin_date.timetuple())

    @property
    def end_date(self):
        """
        Get the interval end date. Always of type datetime (even if it was set to a date)
        """
        return datetime.fromtimestamp(self['end_date'])
    @end_date.setter
    def end_date(self, end_date):
        if(not isinstance(end_date, (date, datetime))):
            raise TypeError(_("end_date must be of type date or datetime"))
        self['end_date'] = time.mktime(end_date.timetuple())

    @property
    def interval(self):
        return intervals(self['interval'])
    @interval.setter
    def interval(self, interval):
        if(not isinstance(interval, intervals)):
            raise TypeError(_("interval must be of type intervals"))
        self['interval'] = interval.value

    @property
    def is_fixed(self):
        return self['is_fixed']
    @is_fixed.setter
    def is_fixed(self, is_fixed):
        if(not isinstance(is_fixed, bool)):
            raise TypeError(_("is_fixed must be of type bool"))
        self['is_fixed'] = is_fixed

def intervalgenerator(begin_date, end_date, interval, interval_count=1, is_fixed=False):
    """
    Generate a non-overlapping set of date intervals from begin_date to end_date

    Parameters
    ----------
    begin_date date or datetime
        Inclusive start date from which to generate intervals.
        If a datetime is provided, only the date portion will be used.
    end_date date or datetime
        Inclusive end date from which to generate intervals.
        If a datetime is provided, only the date portion will be used.
    interval intervalgenerator.intervals
        Duration that each time interval should span.
        If an invalid or unsupported interval is provided, @raise NotImplementedError
    interval_count int, optional
        Number of intervals to include in each IntervalResult, e.g. 2 --> a 2-year span if interval is intervals.YEAR.
        Defaults to 1.
    is_fixed boolean, optional
        Whether the interval should be fixed (true) or relative (false). Defaults to false.
        A fixed interval takes a complete interval as its interval, e.g. the calendar year for intervals.YEAR.
        Both the first and the last intervals may be partial.
        A relative interval calculates the interval based on the begin_date, e.g. if begin_date is February 1, 2013
        and interval is intervals.YEAR then each interval will start on February 1 of each year.
        Only the last interval may be partial.

    Returns
    -------
    List of IntervalResult objects
    """

    # begin_date, end_date, interval, interval_count=1, is_fixed=False

    # TODO if interval not in (supported) intervals, raise NotImplementedError


    return []
