from collections import defaultdict, OrderedDict
import os

import forecastio
import gpxpy

FORECAST_KEY = os.environ['FORECAST']

def main(start_date, end_date, gpx_file):
    with open(gpx_file) as f:
        gpx = gpxpy.parse(f)
    gpx.tracks = make_tracks(gpx.routes, start_date, end_date)

    duration = total_days(start_date, end_date)
    distance = get_total_distance(gpx.routes)
    miles = int(round(meters_to_miles(distance)))
    trackpoints_by_day = get_trackpoints_by_day(gpx.tracks)

    print 'Trip summary: %s to %s (%d days), %s miles' % (start_date, end_date,
                                                          duration, miles)
    for day, points in trackpoints_by_day.items():
        point = points[len(points) / 2]
        weather = get_weather(point.latitude, point.longitude, point.time)
        high = weather['temperatureMax']
        low = weather['temperatureMin']
        print '%s: High %s\tLow %s\t%s' % (day, high, low, weather['summary'])
    return trackpoints_by_day

def get_weather(lat, lng, time):
    """
    'apparentTemperatureMax': 80.44,
    'apparentTemperatureMaxTime': 1412197200,
    'apparentTemperatureMin': 51.27,
    'apparentTemperatureMinTime': 1412168400,
    'cloudCover': 0.01,
    'dewPoint': 39.32,
    'humidity': 0.42,
    'icon': u'clear-day',
    'moonPhase': 0.25,
    'precipIntensity': 0,
    'precipIntensityMax': 0,
    'precipProbability': 0,
    'pressure': 1007.88,
    'summary': u'Clear throughout the day.',
    'sunriseTime': 1412168944,
    'sunsetTime': 1412211650,
    'temperatureMax': 82.45,
    'temperatureMaxTime': 1412197200,
    'temperatureMin': 51.27,
    'temperatureMinTime': 1412168400,
    'time': 1412143200,
    'visibility': 9.62,
    'windBearing': 256,
    'windSpeed': 6.77
    """
    forecast = forecastio.load_forecast(FORECAST_KEY, lat, lng, time=time,
                                        units='us')
    return forecast.daily().data[0].d

def get_trackpoints_by_day(tracks):
    """
    Return a dictionary of trackpoint lists, keyed by date.
    """
    trackpoints = defaultdict(list)
    for track in tracks:
        for segment in track.segments:
            for point in segment.points:
                trackpoints[point.time.date()].append(point)

    date_sorted = OrderedDict()
    for date, points in sorted(trackpoints.items()):
        date_sorted[date] = points
    return date_sorted

def make_tracks(routes, start_date, end_date):
    """
    Construct tracks with time from the given routes.
    Time is set relative to each point's position along the route, with the
    starting point have the start date and the last point having end date.
    """
    start_datetime = datetime.datetime.combine(start_date, datetime.datetime.min.time())
    total_distance = get_total_distance(routes)
    duration = total_days(start_date, end_date)
    tracks = []

    traveled, previous_point = 0, None
    for route in routes:
        points = []
        for p in route.points:
            if previous_point:
                traveled += get_distance(previous_point, p)
                trip_time = duration * traveled / total_distance
                time = start_datetime + datetime.timedelta(days=trip_time)
            else:
                time = start_datetime
            previous_point = p
            point = gpxpy.gpx.GPXTrackPoint(latitude=p.latitude,
                       longitude=p.longitude, elevation=p.elevation,
                       time=time, symbol=p.symbol, comment=p.comment,
                       horizontal_dilution=p.horizontal_dilution,
                       vertical_dilution=p.vertical_dilution,
                       position_dilution=p.position_dilution, name=p.name)
            points.append(point)
        track = gpxpy.gpx.GPXTrack(name=route.name,
                                   description=route.description,
                                   number=route.number)
        track.segments.append(gpxpy.gpx.GPXTrackSegment(points))
        tracks.append(track)
    return tracks

def get_total_distance(routes):
    """
    Travel all points on the routes and return the total distance.
    """
    total_distance = 0
    previous_point = None
    for route in routes:
        for point in route.points:
            if previous_point:
                total_distance += get_distance(previous_point, point)
            previous_point = point
    return total_distance

def get_distance(p1, p2):
    return gpxpy.geo.distance(p1.latitude, p1.longitude, p1.elevation,
                              p2.latitude, p2.longitude, p2.elevation)

def meters_to_miles(meters):
    return meters / 1609.34

def total_days(start, end):
    return (end - start + datetime.timedelta(days=1)).days

if __name__ == '__main__':
    import argparse
    import datetime

    date_format = 'YYYY-MM-DD'

    def date_arg(s):
        try:
            return datetime.datetime.strptime(s, '%Y-%m-%d').date()
        except ValueError:
            msg = 'Not a valid date (%s): %s' % (date_format, s)
            raise argparse.ArgumentTypeError(msg)

    def days_arg(s):
        try:
            days = int(s)
        except ValueError:
            msg = 'Days must be a whole number: %s' % s
            raise argparse.ArgumentTypeError(msg)
        if days <= 0:
            msg = 'Days must be greater than 0: %s' % days
            raise argparse.ArgumentTypeError(msg)
        return days

    parser = argparse.ArgumentParser()
    parser.add_argument('--start', help='Start date %s' % date_format,
                        type=date_arg)
    parser.add_argument('--end', help='End date %s' % date_format,
                        type=date_arg)
    parser.add_argument('--days', help='Duration of trip in days',
                        type=days_arg)
    parser.add_argument('--gpx', help='GPX file')
    args = parser.parse_args()

    date_error = ('Invalid date arguments. Must provide either --start and '
                  '--end dates, or --days with either --start or --end dates.')
    if args.start and args.end:
        if args.days:
            parser.error(date_error)
        elif args.start > args.end:
            parser.error('Start date cannot be after end date.')
    elif not (args.start or args.end):
        parser.error(date_error)
    elif not args.days:
        parser.error(date_error)

    # We have valid dates
    start = args.start or args.end - datetime.timedelta(days=args.days - 1)
    end = args.end or args.start + datetime.timedelta(days=args.days - 1)

    main(start, end, args.gpx)
