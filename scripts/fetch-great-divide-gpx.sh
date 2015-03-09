#!/bin/bash

CA_PATH=http://www.adventurecycling.org/routes-and-maps/adventure-cycling-route-network/gps-information/route-gps-waypoints/great-divide-canada/
US_PATH=http://www.adventurecycling.org/routes-and-maps/adventure-cycling-route-network/gps-information/route-gps-waypoints/great-divide-mountain-bike-route/

SCRIPT_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
_GPX=$SCRIPT_DIR/../gpx/
mkdir -p $_GPX
GPX_OUTPUT_DIR=$(cd $_GPX && pwd)

TMP_DIR=/tmp/gpx-routes
rm -rf $TMP_DIR
mkdir -p $TMP_DIR
pushd $TMP_DIR > /dev/null

echo "Downloading Canada route"
curl -o ca-route.zip $CA_PATH

echo "Downloading United States route"
curl -o us-route.zip $US_PATH

unzip -q ca-route.zip -d ca-route
unzip -q us-route.zip -d us-route

cp -r ca-route/DC_Routes/*.gpx $GPX_OUTPUT_DIR
cp -r us-route/GD_Routes/*.gpx $GPX_OUTPUT_DIR
echo "Extracted CA and US Great Divide GPX routes to $GPX_OUTPUT_DIR"

popd > /dev/null
rm -rf $TMP_DIR
