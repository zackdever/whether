#!/usr/bin/env python
"""
The Great Divide route provided by Adventure Cycling includes alternate routes.
This reads in the full route and writes a new GPX file with only what we
consider to be the main route.
i.e. Canada and the main US route including the offshoot around Grand Teton NP.
"""

import argparse
import gpxpy

def main(full_route_path, main_route_path):
    with open(full_route_path) as full_route_file:
        gpx = gpxpy.parse(full_route_file)
        gpx.routes = get_main_routes(gpx.routes)
        with open(main_route_path, 'w') as main_route_file:
            main_route_file.write(gpx.to_xml())

def get_main_routes(routes):
    """
    Only return the "main" routes.
    http://www.adventurecycling.org/default/assets/File/Routes_Maps/pdf/GPSUserGuide.pdf
    0: main route
    P: Canada route
    7: a major out and back by Grand Teton NP. not a detour, should likely do this
    """
    main_routes = set(['0', 'P', '7'])
    return [r for r in routes if r.name[1] in main_routes]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('route', help='Complete Great Divide GPX file')
    parser.add_argument('-o', help='Output file')
    args = parser.parse_args()
    main(args.route, args.o)
    print 'Wrote main route GPX to %s' % args.o
