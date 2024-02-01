from rest_framework.parsers import JSONParser
from rest_framework.exceptions import ParseError
from datetime import datetime

class CustomTimeSeriesParser(JSONParser):
    # media_type = 'text/plain'
    # media_type = 'application/json'

    def parse(self, stream, media_type=None, parser_context=None):
        # request = parser_context['request']
        # data = stream.read().decode('utf-8')
        # Get the format from the query parameters
        # date_format = request.query_params.get('format', 'default')
        data = super().parse(stream, media_type=media_type, parser_context=parser_context)
        return data
        # try:
        #     # Try parsing the date using the specified format
        #     date_obj = datetime.strptime(data, date_format)
        # except ValueError:
        #     raise ParseError(f'Invalid date format. Use the specified format: {date_format}.')
        #
        # return {'date': date_obj}