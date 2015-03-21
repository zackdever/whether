import gpxpy
from gpxpy import geo

def main(start, end, gpx_file):
    with open(gpx_file) as f:
        gpx = gpxpy.parse(f)

    duration = total_days(start, end)
    #location_by_day = {}
    distance = get_total_distance(gpx.routes)
    miles = int(round(meters_to_miles(distance)))

    print 'Trip summary: %s to %s (%d days), %s miles' % (start, end, duration,
                                                          miles)

def get_total_distance(routes):
    """
    Travel all points on the routes and return the total distance.
    """
    total_distance, p1, p2 = 0, None, None
    def distance(p1, p2):
        return geo.distance(p1.latitude, p1.longitude, p1.elevation,
                            p2.latitude, p2.longitude, p2.elevation)
    for route in routes:
        for point in route.points:
            p1 = p2
            p2 = point
            if p1 and p2:
                total_distance += distance(p1, p2)
    return total_distance

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
