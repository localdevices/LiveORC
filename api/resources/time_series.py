"""resources file for tabular downloads of TimeSeries model. """
from import_export import resources
from api.models import TimeSeries


class TimeSeriesResource(resources.ModelResource):

    class Meta:
        model = TimeSeries
        fields = ('id', 'site__name','timestamp', 'h', 'q_05', 'q_25', 'q_50', 'q_75', 'q_95', 'fraction_velocimetry')
        export_order = ('id', 'site__name', 'timestamp', 'h', 'q_05', 'q_25', 'q_50', 'q_75', 'q_95', 'fraction_velocimetry')

    @classmethod
    def get_display_name(cls):
        return "Time series"  # Customize this display name as needed

    def get_export_headers(self, fields=None):
        headers = super().get_export_headers(fields=fields)
        header_mapping = {"site__name": "site"}
        # Replace the original headers with custom headers
        custom_headers = [header_mapping.get(header, header) for header in headers]
        return custom_headers

    def export(self, queryset=None, *args, **kwargs):
        data = kwargs["export_form"].data
        start_date = data.get("start_date", None)
        end_date = data.get("end_date", None)
        site = data.get("site", None)
        if not queryset:
            queryset = self.get_queryset()

        queryset = queryset.filter(site=site)
        if start_date and end_date:
            queryset = queryset.filter(timestamp__range=(start_date, end_date))
        elif start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        elif end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        return super().export(queryset, *args, **kwargs)
