from readline import insert_text

from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from django.utils.translation import gettext_lazy as _


class BusStopInlineFormSet(BaseInlineFormSet):
    def check_bus_shift_period(self, min_arrival_at, max_arrival_at):
        """Check wheter the bus already has a shift overlap period."""
        if (
            self.instance.bus.shifts.exclude(id=self.instance.pk)
            .filter_intersecting_period(min_arrival_at, max_arrival_at)
            .exists()
        ):
            raise ValidationError(
                _("This bus is already assigned to another shift during this period")
            )

    def check_driver_shift_period(self, min_arrival_at, max_arrival_at):
        """Check whether the driver already has a journey period that overlaps with their shift."""
        if (
            self.instance.driver.shifts.exclude(id=self.instance.pk)
            .filter_intersecting_period(min_arrival_at, max_arrival_at)
            .exists()
        ):
            raise ValidationError(
                _("This driver is already assigned to another shift during this period")
            )

    def clean(self):
        super().clean()

        if not self.instance.bus:
            raise ValidationError(_("Please select a bus"))

        if not self.instance.driver:
            raise ValidationError(_("Please select a driver"))

        stops = [
            form.cleaned_data
            for form in self.forms
            if form.cleaned_data and not form.cleaned_data.get("DELETE")
        ]
        if len(stops) < 2:
            raise ValidationError(_("A shift must contain at least 2 stops."))

        nb_places = len(set([cleaned_data["place"].id for cleaned_data in stops]))
        if nb_places < 2:
            raise ValidationError(_("A shift must contain at least 2 different stops."))

        arrivals_at = [cleaned_data["arrival_at"] for cleaned_data in stops]
        min_arrival_at = min(arrivals_at)
        max_arrival_at = max(arrivals_at)

        self.check_bus_shift_period(
            min_arrival_at=min_arrival_at, max_arrival_at=max_arrival_at
        )

        self.check_driver_shift_period(
            min_arrival_at=min_arrival_at, max_arrival_at=max_arrival_at
        )
