from datetime import datetime

import factory
from django.utils import timezone
from faker import Faker

from padam_django.apps.geography.factories import PlaceFactory

from . import models

fake = Faker(["fr"])


def set_datetime(h=0, m=0):
    return timezone.make_aware(datetime(2025, 11, 22, h, m))


class DriverFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory("padam_django.apps.users.factories.UserFactory")

    class Meta:
        model = models.Driver


class BusFactory(factory.django.DjangoModelFactory):
    licence_plate = factory.LazyFunction(fake.license_plate)

    class Meta:
        model = models.Bus


class BusShiftFactory(factory.django.DjangoModelFactory):
    bus = factory.SubFactory(BusFactory)
    driver = factory.SubFactory(DriverFactory)

    class Meta:
        model = models.BusShift


class BusStopFactory(factory.django.DjangoModelFactory):
    shift = factory.SubFactory(BusShiftFactory)
    place = factory.SubFactory(PlaceFactory)
    arrival_at = factory.LazyFunction(lambda: set_datetime(10))

    class Meta:
        model = models.BusStop
