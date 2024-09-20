#!/bin/bash

# load shared env vars
echo "Loading shared environment variables including new NewsML-G2 version number"
. release-tools/newsmlg2-config-vars.sh

echo "Emptying folder in case it already existed"
rm -fr releases/$NEW_NEWSMLG2_VERSION
rm -fr releases/NewsML-G2_$NEW_NEWSMLG2_VERSION*.zip

echo "Creating release folder releases/$NEW_NEWSMLG2_VERSION"
mkdir -p releases/$NEW_NEWSMLG2_VERSION

echo "Copying release files to the release folder"
cp -r documentation examples LICENSE README.md releases/$NEW_NEWSMLG2_VERSION/

echo "Copying README files to the release folder"
python -m markdown README.md >releases/$NEW_NEWSMLG2_VERSION/README.html
python -m markdown documentation/NewsML-G2-documentation.md >releases/$NEW_NEWSMLG2_VERSION/documentation/index.html

echo "Copying specification (minus XML Schema docs) to the release folder"
mkdir -p releases/$NEW_NEWSMLG2_VERSION/specification
cp -r specification/NewsML-G2_2*Power.xsd specification/XML-Schema_FileVersion_* specification/individual specification/xml.xsd releases/$NEW_NEWSMLG2_VERSION/specification/

ZIP_PATH=`which zip`

cd releases
echo "Creating ZIP file (version without XML Schema documentation) using $ZIP_PATH"
$ZIP_PATH -r -9 NewsML-G2_$NEW_NEWSMLG2_VERSION-noXMLdocu.zip $NEW_NEWSMLG2_VERSION/documentation $NEW_NEWSMLG2_VERSION/specification $NEW_NEWSMLG2_VERSION/examples $NEW_NEWSMLG2_VERSION/LICENSE $NEW_NEWSMLG2_VERSION/README.md $NEW_NEWSMLG2_VERSION/README.html
cd ..

echo "Copying XML Schema documentation to release folder"
cp -r specification/XML-Schema-Doc-Power releases/$NEW_NEWSMLG2_VERSION/specification/

echo "Creating ZIP file (version with documentation) using $ZIP_PATH"
cd releases
$ZIP_PATH -r -9 NewsML-G2_$NEW_NEWSMLG2_VERSION.zip $NEW_NEWSMLG2_VERSION/documentation $NEW_NEWSMLG2_VERSION/specification $NEW_NEWSMLG2_VERSION/examples $NEW_NEWSMLG2_VERSION/LICENSE $NEW_NEWSMLG2_VERSION/README.md $NEW_NEWSMLG2_VERSION/README.html
cd ..

echo "Creating ZIP file of documentation alone using $ZIP_PATH"
cd releases/$NEW_NEWSMLG2_VERSION/specification
$ZIP_PATH -r -9 XML-Schema-Doc-Power.zip XML-Schema-Doc-Power
cd ../../..

echo "Done."
echo "Now copy releases/NewsML-G2_$NEW_NEWSMLG2_VERSION-noXMLdocu.zip, releases/NewsML-G2_$NEW_NEWSMLG2_VERSION.zip and the releases/$NEW_NEWSMLG2_VERSION folder to iptc.org/std"
