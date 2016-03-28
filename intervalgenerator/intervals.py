# -*- coding: utf-8 -*-
try:
    from enum import Enum
except ImportError:
    from enum34 import Enum

from dateutil.rrule import * # TODO only what we need ...
from dateutil.relativedelta import relativedelta

from datetime import date, datetime, timedelta
import time
import math
import calendar

# TODO placeholder so we can prepare to localize strings until we actually localize strings
# ref: https://docs.python.org/2/library/gettext.html
# ref: http://www.wefearchange.org/2012/06/the-right-way-to-internationalize-your.html
# look into gettext, as well as babel and i18n libraries
def _(message): return message

class intervals(Enum):
    YEAR = 'y'
    """ Yearly """

    MONTH = 'm'
    """ Monthly """

    DAY = 'd'
    """ Daily """

    QUARTER = 'q'
    """ Quarterly (4 times per year/equivalend to three months) """

    WEEK = 'w'
    """ Weekly """

    PART = 'p'
    """ A specific number of parts - e.g. running daily for 7 days is equivalent to asking for 7 parts for the same range """

class IntervalResult(dict):
    """
    Subclass of dict makes it JSON serializable via json.dumps()
    """

    def __init__(self, begin_date=None, end_date=None, is_partial=None):
        super(type(self), self).__init__()

        self.begin_date = begin_date
        self.end_date = end_date
        self.is_partial = is_partial


    def __my_properties(self):
        """ Gets a list of @property-defined properties for the current class only (no super) """
        return [k for k,v in self.__class__.__dict__.items() if type(v) is property]

    def __getitem__(self, key):
        if(key not in self.__my_properties()):
            raise AttributeError("No attribute '" + str(key) + "'")
        return super(type(self), self).__getitem__(key)

    def __setitem__(self, key, value):
        if(key not in self.__my_properties()):
            raise AttributeError("No attribute '" + str(key) + "'")
        super(type(self), self).__setitem__(key, value)

    def set_date_range(self, begin_date, end_date):
        """ Shortcut to set the begin date and end date at the same time, so you don't have to None out one if it's changing """
        if(end_date is None):
            self['end_date'] = end_date
        if(begin_date is None):
            self['begin_date'] = begin_date

        if(end_date is not None and begin_date is not None):
            # faking a comparator since date and datetime objects are not comparable apparently
            error_msg = "begin_date (" + str(begin_date) + ") must come before or on end_date (" + str(end_date) + ") if both begin_date and end_date are set. "
            if(begin_date.year > end_date.year):
                raise ValueError(_(error_msg))

            if(begin_date.year == end_date.year):
                if(begin_date.month > end_date.month):
                    raise ValueError(_(error_msg))

                if(begin_date.month == end_date.month and begin_date.day > end_date.day):
                    raise ValueError(_(error_msg))

        # we don't care about times ... at least not yet

        # either one is None
        if begin_date:
            self['begin_date'] = time.mktime(begin_date.timetuple())
        if end_date:
            self['end_date'] = time.mktime(end_date.timetuple())

    @property
    def begin_date(self):
        """
        Get the interval begin date. Always of type datetime (even if it was set to a date)
        """
        if 'begin_date' not in self or not self['begin_date']: return None
        return datetime.fromtimestamp(self['begin_date'])
    @begin_date.setter
    def begin_date(self, begin_date):
        """
        Set the interval begin date to either a date or a datetime.
        """
        if(not isinstance(begin_date, (date, datetime, type(None)))):
            raise TypeError(_("begin_date must be of type date or datetime"))
        self.set_date_range(begin_date, self.end_date)

    @property
    def end_date(self):
        """
        Get the interval end date. Always of type datetime (even if it was set to a date)
        """
        if 'end_date' not in self or not self['end_date']: return None
        return datetime.fromtimestamp(self['end_date'])
    @end_date.setter
    def end_date(self, end_date):
        if(not isinstance(end_date, (date, datetime, type(None)))):
            raise TypeError(_("end_date must be of type date or datetime"))
        self.set_date_range(self.begin_date, end_date)
    @property
    def is_partial(self):
        return self['is_partial']
    @is_partial.setter
    def is_partial(self, is_partial):
        if(not isinstance(is_partial, (bool, type(None)))):
            raise TypeError(_("is_partial must be of type bool"))
        self['is_partial'] = is_partial

def last_day_of_month(any_day):
    """
    Given a datetime (or date) object, return the last day in the given month. Handles leap years as well.
    From http://stackoverflow.com/a/13565185.

    Parameters
    ----------
    any_day     datetime or date
        a date with the month and year for which you want the number of days

    Returns
    -------
    the last day of the month as a date or datetime ?
    """
    # TODO confirm return type for comment
    next_month = any_day.replace(day=28) + timedelta(days=4)  # this will never fail
    return next_month - timedelta(days=next_month.day)

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
        Note that WEEK uses the current calendar.firstweekday setting, which defaults to 0 (Monday) for fixed weekly increments.
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
    Sequentially-ordered list of IntervalResult objects
    """

    # used to normalize and validate the requested range
    overall_interval = IntervalResult()
    overall_interval.begin_date = begin_date
    overall_interval.end_date = end_date
    original_interval = interval

    day_before = begin_date - timedelta(days=1)

    rrule_param = None
    return_results = []

    if(interval == intervals.YEAR):
        rrule_param = YEARLY

        if(is_fixed and (begin_date.day != 1 or begin_date.month != 1)):
            # set the first interval
            new_interval = IntervalResult()
            new_interval.begin_date = begin_date
            new_interval.end_date = date((begin_date.year + interval_count - 1), 12, 31)
            new_interval.is_partial = True
            return_results.append(new_interval)

            # reset begin date to beginning of next year and let 'normal' handling take over
            begin_date = new_interval.end_date + timedelta(days=1)


    if(interval == intervals.DAY):
        rrule_param = DAILY
        # no need to worry about is_fixed - handled the same regardless

    if(interval == intervals.PART):
        if(interval_count == 1):
            # just return the original date range
            new_interval = IntervalResult()
            new_interval.begin_date = begin_date
            new_interval.end_date = end_date
            new_interval.is_partial = False
            return [new_interval]

        # have to calculate the length of each part
        # TODO make sure that time parts are ignored in the comparison for total days
        total_days = (overall_interval.end_date - overall_interval.begin_date).days + 1
        new_interval_count = int(math.floor(total_days * 1.0 / interval_count))
        if(new_interval_count >= 1): # no partial days
            # convert it into a DAILY rrule
            rrule_param = DAILY
            interval_count = new_interval_count

        # no need to worry about is_fixed - handled the same regardless

    if(interval == intervals.QUARTER): # this check must come before the MONTH check
        # convert it into months
        interval_count = interval_count * 3
        interval = intervals.MONTH

    if(interval == intervals.WEEK):
        rrule_param = WEEKLY
        if(is_fixed and begin_date.weekday() != calendar.firstweekday()):
            # set the first interval
            days_to_end_of_week = (7 - calendar.firstweekday() - begin_date.weekday()) - 1
            new_interval = IntervalResult()
            new_interval.begin_date = begin_date
            new_interval.end_date = begin_date + relativedelta(days=(days_to_end_of_week)) + relativedelta(days=(7*(interval_count -1)))
            new_interval.is_partial = True
            return_results.append(new_interval)
            # reset begin date to beginning of next week and let 'normal' handling take over
            begin_date = new_interval.end_date + timedelta(days=1)

    if(interval == intervals.MONTH):
        rrule_param = MONTHLY
        if(is_fixed and begin_date.day > 1):
            # set the first interval
            new_interval = IntervalResult()
            new_interval.begin_date = begin_date
            new_interval.end_date = last_day_of_month(begin_date + relativedelta(months=(interval_count-1)))
            new_interval.is_partial = True
            return_results.append(new_interval)

            # reset begin date to beginning of next month and let 'normal' handling take over
            begin_date = new_interval.end_date + timedelta(days=1)

        # have to do a different formulation for monthly - to handle recurrence on e.g. the 31st of the month
        if(begin_date.day > 28):
            last_day = last_day_of_month(begin_date)
            offset_from_last_day = ((last_day - begin_date).days + 1) * -1 # multiply by negative 1 to tell rrule to go backwards from the last day; add one because -1 means use the last day

            interval_begin_dates = list(rrule(rrule_param, cache=False, interval=interval_count, dtstart=begin_date, until=end_date, bysetpos=1, bymonthday=(begin_date.day, offset_from_last_day)))
            interval_end_dates = list(rrule(rrule_param, cache=False, interval=interval_count, dtstart=day_before, bysetpos=1, bymonthday=(day_before.day, offset_from_last_day - 1), count=(len(interval_begin_dates) + 1)))
        elif(begin_date.day == 1): # day_before day depends on month
            interval_begin_dates = list(rrule(rrule_param, cache=False, interval=interval_count, dtstart=begin_date, until=end_date))
            interval_end_dates = list(rrule(rrule_param, cache=False, interval=interval_count, dtstart=day_before, bysetpos=1, bymonthday=(day_before.day, -1), count=(len(interval_begin_dates) + 1)))
        else:
            interval_begin_dates = list(rrule(rrule_param, cache=False, interval=interval_count, dtstart=begin_date, until=end_date))
            interval_end_dates = list(rrule(rrule_param, cache=False, interval=interval_count, dtstart=day_before, count=(len(interval_begin_dates) + 1)))


    elif(rrule_param is None):
        # interval not in supported intervals
        raise NotImplementedError
    else:
        interval_begin_dates = list(rrule(rrule_param, cache=False, interval=interval_count, dtstart=begin_date, until=end_date))
        interval_end_dates = list(rrule(rrule_param, cache=False, interval=interval_count, dtstart=day_before, count=(len(interval_begin_dates) + 1)))

    for i, i_begin_date in enumerate(interval_begin_dates):
        new_interval = IntervalResult()
        new_interval.begin_date = i_begin_date

        next_interval_i = i+1
        if(next_interval_i < len(interval_begin_dates)): # all but the last one
            new_interval.end_date = (interval_begin_dates[next_interval_i] - timedelta(days=1)) # day before the next interval begins
            new_interval.is_partial = False
        else:
            new_interval.end_date = end_date # overall end date

            if(is_fixed and interval == intervals.MONTH):
                new_interval.is_partial = (new_interval.end_date != last_day_of_month(new_interval.end_date))

                if(original_interval == intervals.QUARTER and
                    new_interval.end_date != datetime(new_interval.end_date.year, 3, 31) and
                    new_interval.end_date != datetime(new_interval.end_date.year, 6, 30) and
                    new_interval.end_date != datetime(new_interval.end_date.year, 9, 30) and
                    new_interval.end_date != datetime(new_interval.end_date.year, 12, 31)):

                    new_interval.is_partial = True
            elif(is_fixed and interval == intervals.WEEK):
                new_interval.is_partial = (new_interval.end_date.weekday() != 6)

            else:
                # print "(" + str(new_interval.end_date) + ", " + str(interval_end_dates[next_interval_i]) + ") -- " + str(new_interval.end_date != interval_end_dates[next_interval_i])
                # print interval_end_dates
                new_interval.is_partial = (new_interval.end_date != interval_end_dates[next_interval_i])

        return_results.append(new_interval)

    return return_results
