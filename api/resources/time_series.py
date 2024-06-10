"""resources file for tabular downloads of TimeSeries model. """
from import_export import resources
from api.models import TimeSeries


class TimeSeriesResource(resources.ModelResource):

    class Meta:
        model = TimeSeries
        fields = ('id', 'timestamp', 'h', 'q_05', 'q_25', 'q_50', 'q_75', 'q_95', 'fraction_velocimetry')
        export_order = ('id', 'timestamp', 'h', 'q_05', 'q_25', 'q_50', 'q_75', 'q_95', 'fraction_velocimetry')

    @classmethod
    def get_display_name(cls):
        return "Time series"  # Customize this display name as needed

    def export(self, queryset=None, *args, **kwargs):
        data = kwargs["export_form"].data
        start_date = data.get("start_date", None)
        end_date = data.get("end_date", None)

        if not queryset:
            queryset = self.get_queryset()

        if start_date and end_date:
            queryset = queryset.filter(timestamp__range=(start_date, end_date))
        elif start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        elif end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        return super().export(queryset, *args, **kwargs)
