from django.contrib import admin

from . import forms, models

admin.site.register(models.Bus)
admin.site.register(models.Driver)


class BusStopInline(admin.TabularInline):
    model = models.BusStop
    ordering = ["arrival_at"]
    formset = forms.BusStopInlineFormSet

    def get_extra(self, request, obj=None, **kwargs):
        return 0 if obj else 2


@admin.register(models.BusShift)
class BusShiftAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "bus",
        "driver",
        "departure_at",
        "first_place_name",
        "arrival_at",
        "last_place_name",
        "shift_duration",
    )
    inlines = [BusStopInline]
