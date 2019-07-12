#!/bin/bash

# load shared env vars
echo "Loading shared environment variables including new NewsML-G2 version number"
. release-tools/newsmlg2-config-vars.sh

# create local vars
MASTER_XSD="$NEWSMLG2_SOURCE_PATH/NewsML-G2_$NEWSMLG2_VERSION-spec-Framework-Power.xsd"
POWER_XSD="$NEWSMLG2_TARGET_PATH/NewsML-G2_$NEWSMLG2_VERSION-spec-All-Power.xsd"

echo "Removing old $POWER_XSD"
rm -f $POWER_XSD  #  don't complain if the file doesn't already exist

echo "Creating new $POWER_XSD from $MASTER_XSD"
java -cp $SAXON_PATH net.sf.saxon.Transform -xsl:$NEWSMLG2_BUILD_XSLT -s:$MASTER_XSD >$POWER_XSD

echo "Done."
