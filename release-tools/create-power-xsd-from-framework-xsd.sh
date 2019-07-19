#!/bin/bash

# load shared env vars
echo "Loading shared environment variables including new NewsML-G2 version number"
. release-tools/newsmlg2-config-vars.sh

echo "Removing old $COMBINED_XSD_WITH_REVISION"
rm -f $POWER_XSD  #  don't complain if the file doesn't already exist

echo "Creating new $COMBINED_XSD_WITH_REVISION from $FRAMEWORK_XSD_WITH_REVISION"
java -cp $SAXON_PATH net.sf.saxon.Transform -xsl:$NEWSMLG2_BUILD_XSLT -s:$FRAMEWORK_XSD_WITH_REVISION >$COMBINED_XSD_WITH_REVISION

echo "Copying $COMBINED_XSD_WITH_REVISION to parent folder $COMBINED_XSD_NO_REVISION"
cp $COMBINED_XSD_WITH_REVISION $COMBINED_XSD_NO_REVISION
echo "Done."
