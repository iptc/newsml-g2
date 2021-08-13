#!/bin/bash

# load shared env vars
echo "Loading shared environment variables including new NewsML-G2 version number..."
. release-tools/newsmlg2-config-vars.sh

# For a simple minor version bump, these two paths might be the same
OLD_XSD_PATH="specification/XML-Schema_FileVersion_$OLD_NEWSMLG2_REVISION"
NEW_XSD_PATH="specification/XML-Schema_FileVersion_$NEW_NEWSMLG2_REVISION"

OLD_VERSION=$OLD_NEWSMLG2_VERSION
NEW_VERSION=$NEW_NEWSMLG2_VERSION

EXAMPLE_DIR="examples"

echo "Updating example files in $NEW_XSD_PATH to use new version number..."

# update XML Schema declarations
sed -i '' "s/NewsML-G2_${OLD_VERSION}/NewsML-G2_${NEW_VERSION}/g" $EXAMPLE_DIR/*
# update standardversion="2.28" etc
sed -i '' "s/standardversion=\"${OLD_VERSION}\"/standardversion=\"${NEW_VERSION}\"/" $EXAMPLE_DIR/*

echo "Removing old schema file in $EXAMPLE_DIR and moving new schema..."
rm -f $EXAMPLE_DIR/NewsML-G2_${OLD_VERSION}-spec-All-Power.xsd
cp $COMBINED_XSD_NO_REVISION $EXAMPLE_DIR/NewsML-G2_${NEW_VERSION}-spec-All-Power.xsd

echo "Done. Now try validating the examples against the new schema with xmllint."
