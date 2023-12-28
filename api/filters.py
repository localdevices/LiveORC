import django_filters
from .models import TimeSeries

class TimeSeriesFilter(django_filters.FilterSet):
    startDateTime = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    endDateTime = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='lte')


    class Meta:
        model = TimeSeries
        fields = []