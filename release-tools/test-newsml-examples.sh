#!/bin/bash

# load shared env vars
echo "Loading shared environment variables including new NewsML-G2 version number"
. release-tools/newsmlg2-config-vars.sh

# create local vars
POWER_XSD="$NEWSMLG2_TARGET_PATH/NewsML-G2_$NEWSMLG2_VERSION-spec-All-Power.xsd"

echo "Testing example files against the new schema (note that not all examples will validate properly)"
xmllint --noout --schema $POWER_XSD examples/*.xml

echo "Done."
