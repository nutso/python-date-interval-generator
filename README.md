# Python Date Interval Generator
Generate a set of date ranges

## Usage

from intervalgenerator.intervals import intervalgenerator, intervals



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


## Release Notes

### 0.0.1

* Initial release

## Tests

python -m unittest discover -v tests

coverage run -m unittest discover -v tests
coverage report -m

## Build

python setup.py sdist
python setup.py bdist_wheel --universal

Test submit:
python setup.py sdist upload -r https://testpypi.python.org/pypi

Test intall:
pip install -i https://testpypi.python.org/pypi python-date-interval-generator


Actual submit:
python setup.py sdist upload
