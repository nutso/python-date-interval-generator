from unittest import TestCase
from datetime import date, datetime
import json
import pprint

from intervalgenerator.intervals import *

class IntervalResultTest(TestCase):
    """ Testing all things related to the IntervalResult class """
    def setUp(self):
        self.interval_begin_date = date(2016, 4, 2)
        self.interval_end_date = date(2016, 5, 2)
        self.interval_is_partial = False

    def test_intervalresult_serializable(self):
        res = IntervalResult()
        res.begin_date = self.interval_begin_date
        res.end_date = self.interval_end_date
        res.is_partial = self.interval_is_partial

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

        # is_partial
        with self.assertRaises(TypeError): res.is_partial = 4.32
        try: res.is_partial = self.interval_is_partial
        except Exception as e: self.fail("Could not set is_partial to an bool object. " + str(e))
        self.assertEqual(type(res.is_partial), bool, "is_partial is not of type bool. " + str(type(res.is_partial)))

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
        res.is_partial = self.interval_is_partial

        self.assertEqual(res.begin_date, datetime.combine(self.interval_begin_date, datetime.min.time()), "begin_date is not what it was set to. " + str(res.begin_date))
        self.assertEqual(res.end_date, datetime.combine(self.interval_end_date, datetime.min.time()), "end_date is not what it was set to. " + str(res.end_date))
        self.assertEqual(res.is_partial, self.interval_is_partial, "is_partial is not what it was set to. " + str(res.is_partial))

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

    tested_combinations = {}

    def assert_for_results(self, results, expected_results, interval, description):
        """
        Centralizing testing of a given intervalgenerator result set and the expected results.
        Asserts that the results and expected results are of the same length, and that both
        the order of results and the content of results are equal.

        Parameters
        ----------
        results: list<IntervalResult>
            actual results
        expected_results: list<IntervalResult>
            expected results
        description: string
            description to include with the assert statement in case of failures.
            Should relate to the expected descriptions in tested_combinations
            A ": " is appended at the end and additional information may be provided.
        """
        if(interval not in self.tested_combinations):
            self.tested_combinations[interval.value] = []
        self.tested_combinations[interval.value].append(description)

        description = description + ": "
        pp = pprint.PrettyPrinter(indent=3)

        self.assertEqual(len(results), len(expected_results), description + "Results are not of equal length")

        for i, value in enumerate(results):
            self.assertEqual(value, expected_results[i], description + "Result at index " + str(i) + " are not equal. \n\nResults: \n" + pp.pformat(results) + "\n\nExpected Results: \n" + pp.pformat(expected_results))

    def test_intervals_yearly(self):
        """
        Testing intervalgenerator for various intervals.YEAR configurations.
        """

        results = intervalgenerator(date(2011, 01, 01), date(2015, 12, 31), intervals.YEAR, is_fixed=False)
        expected_results = [
            IntervalResult(begin_date=date(2011, 1, 1), end_date=date(2011, 12, 31), is_partial=False),
            IntervalResult(begin_date=date(2012, 1, 1), end_date=date(2012, 12, 31), is_partial=False),
            IntervalResult(begin_date=date(2013, 1, 1), end_date=date(2013, 12, 31), is_partial=False),
            IntervalResult(begin_date=date(2014, 1, 1), end_date=date(2014, 12, 31), is_partial=False),
            IntervalResult(begin_date=date(2015, 1, 1), end_date=date(2015, 12, 31), is_partial=False),
        ]
        self.assert_for_results(results, expected_results, intervals.YEAR, "relative/complete/1")

    @classmethod
    def tearDownClass(self):
        # for each interval type, test: is_fixed=True/False; with partials/without partials; interval_count default and > 1

        expected_strings = [
            # is_fixed = False, no partials present, interval_count=1
            "relative/complete/1",
            # is_fixed = True, no partials present, interval_count=1
            "fixed/complete/1",
            # is_fixed = False, partials present, interval_count=1
            "relative/partial/1",
            # is_fixed = True, partials present, interval_count=1
            "fixed/partial/1",
            # is_fixed = False, no partials present, interval_count=n
            "relative/complete/n",
            # is_fixed = True, no partials present, interval_count=n
            "fixed/complete/n",
            # is_fixed = False, partials present, interval_count=n
            "relative/partial/n",
            # is_fixed = True, partials present, interval_count=n
            "fixed/partial/n",
        ]
        for i in intervals:
            i = i.value

            # make sure each interval type is tested @test
            assert (i in self.tested_combinations), str(intervals(i)) + " not tested."

            for e in expected_strings:
                assert (e in self.tested_combinations[i]), e + " not tested"
