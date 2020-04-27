#!/bin/bash
  
# load shared env vars
echo "Loading shared environment variables including new NewsML-G2 version number"
. release-tools/newsmlg2-config-vars.sh

SOURCE_FOLDER="specification/XML-Schema_FileVersion_${NEWSMLG2_REVISION}"
TARGET_FOLDER="specification/individual"

echo "Removing old files from ${TARGET_FOLDER}"

rm -f ${TARGET_FOLDER}/NewsML-G2_${OLD_NEWSMLG2_VERSION}*

echo "Moving schema files from $SOURCE_FOLDER to $TARGET_FOLDER"

for component in "CatalogItem" "ConceptItem" "Framework" "KnowledgeItem" \
                 "NewsItem" "NewsMessage" "PackageItem" "PlanningItem"
do
    echo "Copying $component from $SOURCE_FOLDER to $TARGET_FOLDER"
    OLD_FILE="$SOURCE_FOLDER/NewsML-G2_$NEWSMLG2_VERSION-spec-$component-Power_$NEWSMLG2_REVISION.xsd"
    NEW_FILE="$TARGET_FOLDER/NewsML-G2_$NEWSMLG2_VERSION-spec-$component-Power.xsd"
    cp $OLD_FILE $NEW_FILE
    sed -i '' "s/NewsML\-G2_${NEWSMLG2_VERSION}\-spec\-Framework-Power_${NEWSMLG2_REVISION}/NewsML-G2_$NEWSMLG2_VERSION-spec-Framework-Power/" $NEW_FILE
done

FRAMEWORK_XSD="${TARGET_FOLDER}/NewsML-G2_${NEWSMLG2_VERSION}-spec-Framework-Power.xsd"
echo "Removing _${NEWSMLG2_REVISION} extension in in ${FRAMEWORK_XSD} includes"
sed -i '' "s/\\(\-Power\\)_${NEWSMLG2_REVISION}/\1/g" $FRAMEWORK_XSD
echo "Done."

