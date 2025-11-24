from django.db import models
from django.utils.translation import gettext_lazy as _


class Driver(models.Model):
    user = models.OneToOneField(
        "users.User", on_delete=models.CASCADE, related_name="driver"
    )

    def __str__(self):
        return f"Driver: {self.user.username} (id: {self.pk})"


class Bus(models.Model):
    licence_plate = models.CharField("Name of the bus", max_length=10)

    class Meta:
        verbose_name_plural = "Buses"

    def __str__(self):
        return f"Bus: {self.licence_plate} (id: {self.pk})"


class BusShiftQuerySet(models.QuerySet):
    def filter_intersecting_period(self, min_arrival_at, max_arrival_at):
        return self.alias(
            min_arrival_at=models.Min("stops__arrival_at"),
            max_arrival_at=models.Max("stops__arrival_at"),
        ).filter(min_arrival_at__lte=max_arrival_at, max_arrival_at__gte=min_arrival_at)


class BusShiftManager(models.Manager):
    def get_queryset(self):
        return BusShiftQuerySet(self.model, using=self._db)

    def filter_intersecting_period(self, min_arrival_at, max_arrival_at):
        return self.get_queryset().filter_intersecting_period(
            min_arrival_at, max_arrival_at
        )


class BusShift(models.Model):
    bus = models.ForeignKey(
        Bus, on_delete=models.SET_NULL, null=True, related_name="shifts"
    )

    driver = models.ForeignKey(
        Driver, on_delete=models.SET_NULL, null=True, related_name="shifts"
    )

    objects = BusShiftManager()

    @property
    def first_stop(self):
        return self.stops.first()

    @property
    def last_stop(self):
        return self.stops.last()

    @property
    def departure_at(self):
        first_stop = self.first_stop
        return first_stop.arrival_at if first_stop else None

    @property
    def arrival_at(self):
        last_stop = self.last_stop
        return last_stop.arrival_at if last_stop else None

    def get_shift_duration(self):
        """Shift duration in minutes."""
        arrival_at = self.arrival_at
        departure_at = self.departure_at
        if arrival_at is None or departure_at is None:
            return None

        return round((self.arrival_at - self.departure_at).total_seconds() // 60)

    get_shift_duration.short_description = _("Duration (in minutes)")
    shift_duration = property(get_shift_duration)

    @property
    def first_place(self):
        first_stop = self.first_stop
        return first_stop.place if first_stop else None

    @property
    def first_place_name(self):
        first_place = self.first_place
        return first_place.name if first_place else None

    @property
    def last_place(self):
        last_stop = self.last_stop
        return last_stop.place if last_stop else None

    @property
    def last_place_name(self):
        last_place = self.last_place
        return last_place.name if last_place else None

    def __str__(self):
        return f"Shift: {self.bus} - {self.driver} (id: {self.pk})"


class BusStop(models.Model):
    shift = models.ForeignKey(BusShift, on_delete=models.CASCADE, related_name="stops")

    place = models.ForeignKey(
        "geography.Place", on_delete=models.CASCADE, related_name="shift_stops"
    )

    arrival_at = models.DateTimeField()

    class Meta:
        ordering = ["arrival_at"]
        unique_together = ("shift", "arrival_at")

    def __str__(self):
        return f"Stop: {self.place} - {self.arrival_at} (id: {self.pk})"
