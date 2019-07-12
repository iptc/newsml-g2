#!/bin/bash

# load shared env vars
echo "Loading shared environment variables including new NewsML-G2 version number"
. release-tools/newsmlg2-config-vars.sh

# create local vars
echo "Creating release folder if it doesn't already exist"
mkdir releases/$NEWSMLG2_VERSION

echo "Emptying folder in case it already existed"
rm -fr releases/$NEWSMLG2_VERSION/*

echo "Copying release files to the release folder"
cp -r specification documentation examples LICENSE README.md releases/$NEWSMLG2_VERSION

cd releases/$NEWSMLG2_VERSION
echo "Creating ZIP file (version with no documentation)"
zip -r -9 --exclude=XML-Schema-Doc-Power ../NewsML-G2_$NEWSMLG2_VERSION-noXMLdocu.zip documentation specification examples LICENSE README.md
echo "Creating ZIP file (version with documentation)"
zip -r -9 ../NewsML-G2_$NEWSMLG2_VERSION.zip documentation specification examples LICENSE README.md
cd ../..

echo "Done."
