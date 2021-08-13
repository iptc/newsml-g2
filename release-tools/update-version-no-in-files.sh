#!/bin/bash

# load shared env vars
echo "Loading shared environment variables including new NewsML-G2 version number..."
. release-tools/newsmlg2-config-vars.sh

# For a simple minor version bump, these two paths might be the same
OLD_XSD_PATH="specification/XML-Schema_FileVersion_$OLD_NEWSMLG2_REVISION"
NEW_XSD_PATH="specification/XML-Schema_FileVersion_$NEW_NEWSMLG2_REVISION"

OLD_VERSION=$OLD_NEWSMLG2_VERSION
NEW_VERSION=$NEW_NEWSMLG2_VERSION

echo "Updating XML Schema files in $NEW_XSD_PATH to use new version number"

for component in "CatalogItem" "ConceptItem" "Framework" "KnowledgeItem" \
                 "NewsItem" "NewsMessage" "PackageItem" "PlanningItem"
do
    NEW_FILE="${NEW_XSD_PATH}/NewsML-G2_${NEW_VERSION}-spec-${component}-Power_${NEW_NEWSMLG2_REVISION}.xsd"
    echo "  Updating version number references in $NEW_FILE"
    sed -i '' "s/version=\\\"$OLD_VERSION\\\"/version=\\\"$NEW_VERSION\\\"/" $NEW_FILE
    sed -i '' "s/documentation>NewsML\-G2\ $OLD_VERSION/documentation>NewsML\-G2\ $NEW_VERSION/g" $NEW_FILE
    sed -i '' "s/document version ${OLD_NEWSMLG2_REVISION}/document version ${NEW_NEWSMLG2_REVISION}/g" $NEW_FILE
    sed -i '' "s/fname=\\\"NewsML-G2_${OLD_VERSION}-spec-\(.*\)-Power_${OLD_NEWSMLG2_REVISION}.xsd/fname=\\\"NewsML-G2_${NEW_VERSION}-spec-\1-Power_${NEW_NEWSMLG2_REVISION}.xsd/g" $NEW_FILE
    sed -i '' "s/\\(Date of creation of this XML Schema document revision: \\)[0-9]*\-[0-9]*\-[0-9]*/\1$TODAY/g" $NEW_FILE
    sed -i '' "s/\\(Approval of this XML Schema version: \\)[0-9x]*\-[0-9x]*\-[0-9x]*/\1$APPROVAL_DATE/g" $NEW_FILE
    sed -i '' "s/NewsML\-G2_${OLD_VERSION}\-spec\-Framework-Power_${OLD_NEWSMLG2_REVISION}/NewsML-G2_$NEW_VERSION-spec-Framework-Power_$NEW_NEWSMLG2_REVISION/g" $NEW_FILE
done

echo "Altering version and revision numbers in Framework XSD includes"
FRAMEWORK_XSD="${NEW_XSD_PATH}/NewsML-G2_${NEW_VERSION}-spec-Framework-Power_${NEW_NEWSMLG2_REVISION}.xsd"
# NewsML-G2_2.28-spec-ConceptItem-Power_2.xsd -> NewsML-G2_2.29-spec-ConceptItem-Power_1.xsd
sed -i '' "s/NewsML-G2_${OLD_NEWSMLG2_VERSION}_spec-\\([a-zA-Z]+\\)\-Power_${OLD_NEWSMLG2_REVISION}/NewsML-G2_${NEW_NEWSMLG2_VERSION}_spec-\1-Power_${NEW_NEWSMLG2_REVISION}/g" $FRAMEWORK_XSD
echo "Done."
