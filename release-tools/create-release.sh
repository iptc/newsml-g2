#!/bin/bash

# load shared env vars
echo "Loading shared environment variables including new NewsML-G2 version number"
. release-tools/newsmlg2-config-vars.sh

echo "Emptying folder in case it already existed"
rm -fr releases/$NEWSMLG2_VERSION
rm -fr releases/NewsML-G2_$NEWSMLG2_VERSION*.zip

echo "Creating release folder"
mkdir -p releases/$NEWSMLG2_VERSION

echo "Copying release files to the release folder"
cp -r documentation examples LICENSE releases/$NEWSMLG2_VERSION/
cp -r README.md releases/$NEWSMLG2_VERSION/NewsML-G2-README.md

echo "Copying specification (minus XML Schema docs) to the release folder"
mkdir -p releases/$NEWSMLG2_VERSION/specification
cp -r specification/NewsML-G2_2*Power.xsd specification/XML-Schema_FileVersion_* specification/individual specification/xml.xsd releases/$NEWSMLG2_VERSION/specification/

ZIP_PATH=`which zip`

cd releases
echo "Creating ZIP file (version without XML Schema documentation) using $ZIP_PATH"
$ZIP_PATH -r -9 NewsML-G2_$NEWSMLG2_VERSION-noXMLdocu.zip $NEWSMLG2_VERSION/documentation $NEWSMLG2_VERSION/specification $NEWSMLG2_VERSION/examples $NEWSMLG2_VERSION/LICENSE $NEWSMLG2_VERSION/NewsML-G2-README.md
cd ..

echo "Copying XML Schema documentation to release folder"
cp -r specification/XML-Schema-Doc-Power releases/$NEWSMLG2_VERSION/specification/

echo "Creating ZIP file (version with documentation) using $ZIP_PATH"
cd releases
$ZIP_PATH -r -9 NewsML-G2_$NEWSMLG2_VERSION.zip $NEWSMLG2_VERSION/documentation $NEWSMLG2_VERSION/specification $NEWSMLG2_VERSION/examples $NEWSMLG2_VERSION/LICENSE $NEWSMLG2_VERSION/NewsML-G2-README.md
cd ..

echo "Creating ZIP file of documentation alone using $ZIP_PATH"
cd releases/$NEWSMLG2_VERSION/specification
$ZIP_PATH -r -9 XML-Schema-Doc-Power.zip XML-Schema-Doc-Power
cd ../../..

echo "Done."
