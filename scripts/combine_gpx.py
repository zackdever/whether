#!/usr/bin/env python
"""
Combine multiple GPX files into a single GPX file.
$ ./combine_gpx.py *.gpx -o combined.gpx
"""

import argparse

from gpxpy.gpxxml import join_gpxs

parser = argparse.ArgumentParser()
parser.add_argument('gpx', help='GPX files to combine', nargs='+')
parser.add_argument('-o', help='Output file', default='combined.gpx')
args = parser.parse_args()

with open(args.o, 'w') as f:
    f.write(join_gpxs(open(f).read() for f in args.gpx))
