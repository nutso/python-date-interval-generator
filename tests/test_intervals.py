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

    # TODO test that begin_date is always <= end_date @test

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
