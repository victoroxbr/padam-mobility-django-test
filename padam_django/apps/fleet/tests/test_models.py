from django.test import TestCase

from padam_django.apps.fleet.factories import (
    BusShiftFactory,
    BusStopFactory,
    set_datetime,
)
from padam_django.apps.fleet.models import BusShift


class BusShiftQuerySetTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.shift = BusShiftFactory()

        cls.first_stop = BusStopFactory(shift=cls.shift, arrival_at=set_datetime(10))
        BusStopFactory(shift=cls.shift, arrival_at=set_datetime(10, 30))
        cls.last_stop = BusStopFactory(shift=cls.shift, arrival_at=set_datetime(11))

    def test_filter_intersecting_period_overlapping_left(self):
        self.assertTrue(
            BusShift.objects.filter_intersecting_period(
                set_datetime(9), set_datetime(10)
            )
        )

    def test_filter_intersecting_period_overlapping_right(self):
        self.assertTrue(
            BusShift.objects.filter_intersecting_period(
                set_datetime(11), set_datetime(12)
            )
        )

    def test_filter_intersecting_period_inside_period(self):
        self.assertTrue(
            BusShift.objects.filter_intersecting_period(
                set_datetime(10, 20), set_datetime(10, 30)
            )
        )

    def test_filter_intersecting_period_no_match_before(self):
        self.assertFalse(
            BusShift.objects.filter_intersecting_period(
                set_datetime(9), set_datetime(9, 59)
            )
        )

    def test_filter_intersecting_period_no_match_after(self):
        self.assertFalse(
            BusShift.objects.filter_intersecting_period(
                set_datetime(11, 1), set_datetime(12)
            )
        )

    def test_departure_at(self):
        self.assertEqual(self.shift.departure_at, set_datetime(10))

    def test_arrival_at(self):
        self.assertEqual(self.shift.arrival_at, set_datetime(11))

    def test_shift_duration(self):
        self.assertEqual(self.shift.shift_duration, 60)

    def test_first_place_name(self):
        self.assertEqual(self.shift.first_place_name, self.first_stop.place.name)

    def test_last_place_name(self):
        self.assertEqual(self.shift.last_place_name, self.last_stop.place.name)


class BusStopTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.bus_stop = BusStopFactory()

    def test_unique_together_shift_arrival_at(self):
        with self.assertRaises(Exception):
            BusStopFactory(
                shift=self.bus_stop.shift, arrival_at=self.bus_stop.arrival_at
            )
