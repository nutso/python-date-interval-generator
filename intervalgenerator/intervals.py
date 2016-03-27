# -*- coding: utf-8 -*-
try:
    from enum import Enum
except ImportError:
    from enum34 import Enum

from dateutil.rrule import * # TODO only what we need ...

from datetime import date, datetime, timedelta
import time

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
    Sequentially-ordered list of IntervalResult objects
    """

    # used to normalize and validate the requested range
    overall_interval = IntervalResult()
    overall_interval.begin_date = begin_date
    overall_interval.end_date = end_date

    day_before = begin_date - timedelta(days=1)

    rrule_param = None

    if(interval == intervals.YEAR):
        rrule_param = YEARLY

    if(interval == intervals.DAY):
        rrule_param = DAILY

    if(interval == intervals.PART):
        # have to calculate the length of each part
        # TODO make sure that time parts are ignored in the comparison for is_partial ?
        total_days = (overall_interval.end_date - overall_interval.begin_date).days
        new_interval_count = total_days * 1.0 / interval_count
        if(new_interval_count >= 1): # no partial days
            # convert it into a DAILY rrule
            rrule_param = DAILY
            interval_count = int(new_interval_count) # TODO make sure it rounds down ... floor maybe?

    if(interval == intervals.QUARTER):
        # convert it into months
        rrule_param = DAILY
        interval_count = interval_count * 3

    if(interval == intervals.WEEK):
        rrule_param = WEEKLY


    if(interval == intervals.MONTH):
        rrule_param = MONTHLY
        # have to do a different formulation for monthly - to handle recurrence on e.g. the 31st of the month
        # interval_end_dates = list(rrule(rrule_param, cache=False, interval=interval_count, dtstart=(day_before + timedelta(days=-1)), until=(end_date + timedelta(days=31)), bysetpos=1, bymonthday=(begin_date.day, -2)))
        interval_begin_dates = list(rrule(rrule_param, cache=False, interval=interval_count, dtstart=begin_date, until=end_date, bysetpos=1, bymonthday=(begin_date.day, -1)))
        interval_end_dates = list(rrule(rrule_param, cache=False, interval=interval_count, dtstart=day_before, bysetpos=1, bymonthday=(day_before.day, -2), count=(len(interval_begin_dates) + 1)))

    elif(rrule_param is None):
        # interval not in supported intervals
        raise NotImplementedError
    else:
        # TODO confirm that 'until' is inclusive
        # TODO this is only if not is_fixed
        interval_begin_dates = list(rrule(rrule_param, cache=False, interval=interval_count, dtstart=begin_date, until=end_date))
        interval_end_dates = list(rrule(rrule_param, cache=False, interval=interval_count, dtstart=day_before, count=(len(interval_begin_dates) + 1)))

    return_results = []
    for i, i_begin_date in enumerate(interval_begin_dates):
        new_interval = IntervalResult()
        new_interval.begin_date = i_begin_date

        next_interval_i = i+1
        if(next_interval_i < len(interval_begin_dates)): # all but the last one
            new_interval.end_date = (interval_begin_dates[next_interval_i] - timedelta(days=1)) # day before the next interval begins
            new_interval.is_partial = False
        else:
            new_interval.end_date = end_date # overall end date

            # print "(" + str(new_interval.end_date) + ", " + str(interval_end_dates[next_interval_i]) + ")"
            new_interval.is_partial = (new_interval.end_date != interval_end_dates[next_interval_i])
            """
            if(len(return_results) == 0):
                # this will be the first and only
                # it's not partial because it's the entire date range requested
                new_interval.is_partial = False
            else:
                if(interval == intervals.MONTH):
                    # TODO this doesn't take into account e.g. 30th of Jan
                    # months have varying length in days
                    new_interval.is_partial = (return_results[-1].end_date.day != new_interval.end_date.day)

                else:
                    # TODO handle leap year...
                    # get length of most recent result
                    interval_length_days = (return_results[-1].end_date - return_results[-1].begin_date).days
                    my_length_days = (new_interval.end_date - new_interval.begin_date).days
                    new_interval.is_partial = (my_length_days != interval_length_days)
            """
        return_results.append(new_interval)

    return return_results
