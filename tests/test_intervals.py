from unittest import TestCase
from datetime import date, datetime
import json

from intervalgenerator.intervals import *

class IntervalResultTest(TestCase):
    """ Testing all things related to the IntervalResult class """
    def setUp(self):
        self.interval_begin_date = date(2016, 4, 2)
        self.interval_end_date = date(2016, 5, 2)
        self.interval_interval = intervals.YEAR
        self.interval_is_fixed = False

    def test_intervalresult_serializable(self):
        res = IntervalResult()
        res.begin_date = self.interval_begin_date
        res.end_date = self.interval_end_date
        res.interval = self.interval_interval
        res.is_fixed = self.interval_is_fixed

        try: json.dumps(res)
        except Exception as e: self.fail("Could not JSON-serialize IntervalResult. " + str(e))

    def test_intervalresult_types(self):
        res = IntervalResult()

        # begin_date
        with self.assertRaises(TypeError): res.begin_date = "hi"
        try: res.begin_date = self.interval_begin_date
        except Exception as e: self.fail("Could not set begin_date to a date object. " + str(e))
        try: res.begin_date = datetime(2015, 1, 3, 5, 40, 14)
        except Exception as e: self.fail("Could not set begin_date to a datetime object. " + str(e))
        self.assertEqual(type(res.begin_date), datetime, "begin_date is not of type datetime. " + str(type(res.begin_date)))

        # end_date
        with self.assertRaises(TypeError): res.end_date = True
        try: res.end_date = self.interval_end_date
        except Exception as e: self.fail("Could not set end_date to a date object. " + str(e))
        try: res.end_date = datetime(2015, 1, 3, 5, 40, 14)
        except Exception as e: self.fail("Could not set end_date to a datetime object. " + str(e))
        self.assertEqual(type(res.end_date), datetime, "end_date is not of type datetime. " + str(type(res.end_date)))

        # interval
        with self.assertRaises(TypeError): res.interval = 4
        try: res.interval = self.interval_interval
        except Exception as e: self.fail("Could not set interval to an intervals object. " + str(e))
        self.assertEqual(type(res.interval), intervals, "interval is not of type intervals. " + str(type(res.interval)))

        # is_fixed
        with self.assertRaises(TypeError): res.is_fixed = 4.32
        try: res.is_fixed = self.interval_is_fixed
        except Exception as e: self.fail("Could not set is_fixed to an bool object. " + str(e))
        self.assertEqual(type(res.is_fixed), bool, "is_fixed is not of type bool. " + str(type(res.is_fixed)))

    def test_valid_date_range(self):
        res = IntervalResult()

        # valid ranges
        try: res.set_date_range(date(2015, 1, 4), date(2015, 1, 4))
        except Exception as e: self.fail("Valid date range is invalid (same day). " + str(e))

        try: res.set_date_range(date(2015, 1, 4), date(2015, 1, 30))
        except Exception as e: self.fail("Valid date range is invalid (days in same month). " + str(e))

        try: res.set_date_range(date(2015, 1, 4), date(2015, 2, 4))
        except Exception as e: self.fail("Valid date range is invalid (months in same year). " + str(e))

        try: res.set_date_range(date(2014, 1, 4), date(2015, 2, 4))
        except Exception as e: self.fail("Valid date range is invalid (separate years). " + str(e))

        try: res.set_date_range(date(2015, 1, 4), datetime(2015, 1, 4, 5, 6, 7))
        except Exception as e: self.fail("Valid date range is invalid (date/datetime). " + str(e))

        try: res.set_date_range(None, datetime(2015, 1, 4, 5, 6, 7))
        except Exception as e: self.fail("Valid date range is invalid (None begin_date). " + str(e))

        try: res.set_date_range(date(2015, 1, 4), None)
        except Exception as e: self.fail("Valid date range is invalid (None end_date). " + str(e))

        try: res.set_date_range(None, None)
        except Exception as e: self.fail("Valid date range is invalid (None range). " + str(e))

        # invalid ranges
        with self.assertRaises(ValueError): res.set_date_range(date(2015, 2, 5), date(2010, 5, 3)) # years are wrong
        with self.assertRaises(ValueError): res.set_date_range(date(2015, 6, 5), date(2015, 5, 3)) # months are wrong
        with self.assertRaises(ValueError): res.set_date_range(date(2015, 5, 5), date(2015, 5, 3)) # days are wrong

    def test_intervaleresult_getters_and_setters(self):
        res = IntervalResult()
        res.begin_date = self.interval_begin_date
        res.end_date = self.interval_end_date
        res.interval = self.interval_interval
        res.is_fixed = self.interval_is_fixed

        self.assertEqual(res.begin_date, datetime.combine(self.interval_begin_date, datetime.min.time()), "begin_date is not what it was set to. " + str(res.begin_date))
        self.assertEqual(res.end_date, datetime.combine(self.interval_end_date, datetime.min.time()), "end_date is not what it was set to. " + str(res.end_date))
        self.assertEqual(res.interval, self.interval_interval, "interval is not what it was set to. " + str(res.interval))
        self.assertEqual(res.is_fixed, self.interval_is_fixed, "is_fixed is not what it was set to. " + str(res.is_fixed))


        with self.assertRaises(AttributeError):
            # setter
            res['invalid_key'] = "hello"
        with self.assertRaises(AttributeError):
            # getter
            print res['invalid_key']

class IntervalsTest(TestCase):
    """ Testing all things related to the intervals class """
    def test_intervals_all_implemented(self):
        begin_date = date(2016, 01, 01)
        end_date = date(2016, 02, 29)
        # actual begin date and end date doesn't matter here - only testing that they're all supported
        for i in intervals:
            try:
                results = intervalgenerator(begin_date, end_date, i)
            except NotImplementedError:
                self.fail("intervalgenerator does not implement interval " + i.name)

class IntervalGeneratorTest(TestCase):
    """ Testing all things related to the intervalgenerator class"""
    def test_intervals_yearly(self):
        begin_date = date(2011, 01, 01)
        end_date = date(2015, 12, 31)

        results = intervalgenerator(begin_date, end_date, intervals.YEAR)

        # TODO implement @test
