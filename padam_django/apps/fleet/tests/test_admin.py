from datetime import datetime

from django.test import Client, TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from padam_django.apps.fleet.factories import (
    BusShiftFactory,
    BusStopFactory,
    set_datetime,
)
from padam_django.apps.geography.factories import PlaceFactory
from padam_django.apps.users.factories import UserFactory


class AdminBusStopFormsetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.shift = BusShiftFactory()
        cls.bus = cls.shift.bus
        cls.driver = cls.shift.driver
        cls.place1 = PlaceFactory()
        cls.place2 = PlaceFactory()

        cls.user = UserFactory(is_staff=True, is_superuser=True)
        cls.client = Client()

    def setUp(self):
        self.client.force_login(self.user)

    def build_formset_data(self, entries):
        data = {
            "bus": self.bus.id,
            "driver": self.driver.id,
            "stops-TOTAL_FORMS": str(len(entries)),
            "stops-INITIAL_FORMS": "0",
            "stops-MIN_NUM_FORMS": "0",
            "stops-MAX_NUM_FORMS": "1000",
        }
        for i, entry in enumerate(entries):
            for key, value in entry.items():
                if type(value) is datetime:
                    data[f"stops-{i}-{key}_0"] = value.date()
                    data[f"stops-{i}-{key}_1"] = value.time()
                else:
                    data[f"stops-{i}-{key}"] = value

        return data

    def test_one_place(self):
        url = reverse("admin:fleet_busshift_change", args=(self.shift.id,))
        data = self.build_formset_data(
            [{"place": self.place1.id, "arrival_at": set_datetime(12)}]
        )

        response = self.client.post(url, data)

        self.assertContains(response, _("A shift must contain at least 2 stops."))

    def test_check_bus_shift_period(self):
        shift = BusShiftFactory(bus=self.bus)
        BusStopFactory(shift=shift, arrival_at=set_datetime(12))
        url = reverse("admin:fleet_busshift_change", args=(self.shift.id,))
        data = self.build_formset_data(
            [
                {"place": self.place1.id, "arrival_at": set_datetime(12)},
                {"place": self.place2.id, "arrival_at": set_datetime(12, 30)},
            ]
        )

        response = self.client.post(url, data)

        self.assertContains(
            response,
            _("This bus is already assigned to another shift during this period"),
        )
