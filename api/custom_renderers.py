import json

from rest_framework.renderers import *
import csv
from io import StringIO
from api.models import Site

class PIJSONRenderer(JSONRenderer):
    media_type = 'application/json'
    # # add additional property
    # format_param = 'format'

    format = 'pijson'

    def pijsonify(self, data):
        # fixed PI-JSON header
        header = {
            "version": "1.23",
            "timeZone": "0.0"
        }
        meta_vars = ["id", "timestamp", "creator", "site"]
        var_mapping = {
            "h": "h",
            "q_05": "q.05",
            "q_25": "q.25",
            "q_50": "q.50",
            "q_75": "q.75",
            "q_95": "q.95",
            "wetted_surface": "A.wet",
            "wetted_perimeter": "P.wet",
            "fraction_velocimetry": "v.frac"
        }
        units = {
            "h": "m",
            "q_05": "m3/s",
            "q_25": "m3/s",
            "q_50": "m3/s",
            "q_75": "m3/s",
            "q_95": "m3/s",
            "wetted_surface": "m2",
            "wetted_perimeter": "m",
            "fraction_velocimetry": "%"
        }
        # use one sample record to fill in headers
        sample_rec = data[0]
        site = Site.objects.get(pk=sample_rec["site"])
        lon = site.geom.x
        lat = site.geom.y
        name = site.name

        # make list of variables
        variables = data[0].keys()
        variables = [var for var in variables if var not in meta_vars]
        # create headers:
        ts_headers = {
            var: {
                "type": "instantaneous",
                # "moduleInstanceId": "ImportObserved",
                "locationId": data[0]["site"],
                "parameterId": var_mapping[var],  # following typical FEWS naming conventions
                "timeStep": {
                    "unit": "nonequidistant"
                },
                "startDate": {
                    "date": data[0]["timestamp"][0:10],
                    "time": data[0]["timestamp"][-9:-1],
                },
                "endDate": {
                    "date": data[-1]["timestamp"][0:10],
                    "time": data[-1]["timestamp"][-9:-1],
                },
                "missVal": "-999.0",
                "stationName": name,
                "lat": lat,
                "lon": lon,
                "units": units[var],
            } for var in variables
        }
        # create time series
        ts_events = {
            var: [
                {
                    "date": d["timestamp"][0:10],
                    "time": d["timestamp"][-9:-1],
                    "value": "-999.0" if d[var] is None else "{:f}".format(d[var]),
                    "flag": "1" if d[var] is None else "0"
                } for d in data

            ] for var in variables
        }
        data = {**header, **{
            "timeSeries": [ {
                "header": ts_headers[h],
                "events": ts_events[e]
            }
            for h, e in zip(ts_headers, ts_events)]
        }}
        return json.dumps(data)

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Render `data` into JSON, returning a bytestring.
        """
        if data is None:
            return b''

        renderer_context = renderer_context or {}
        indent = self.get_indent(accepted_media_type, renderer_context)

        if indent is None:
            separators = SHORT_SEPARATORS if self.compact else LONG_SEPARATORS
        else:
            separators = INDENT_SEPARATORS
        ret = self.pijsonify(data)

        # We always fully escape \u2028 and \u2029 to ensure we output JSON
        # that is a strict javascript subset.
        # See: https://gist.github.com/damncabbage/623b879af56f850a6ddc
        ret = ret.replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
        return ret.encode()
