#!/bin/bash

# load shared env vars
echo "Loading shared environment variables including new NewsML-G2 version number..."
. release-tools/newsmlg2-config-vars.sh

EXAMPLE_DIR="examples"

echo "Updating example files to use latest IPTC catalog number..."

# update XML Schema declarations
sed -i '' "s/catalog.IPTC-G2-Standards_\d\d.xml/catalog.IPTC-G2-Standards_${CATALOG_VERSION}.xml/g" $EXAMPLE_DIR/*

echo "Done. Now try validating the examples against the new schema with xmllint."
