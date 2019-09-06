#!/bin/bash
  
# load shared env vars
echo "Loading shared environment variables including new NewsML-G2 version number"
. release-tools/newsmlg2-config-vars.sh

SOURCE_FOLDER="specification/XML-Schema_FileVersion_$NEWSMLG2_REVISION"
TARGET_FOLDER="specification/individual"
echo "Moving schema files from $SOURCE_FOLDER to $TARGET_FOLDER"

for component in "CatalogItem" "ConceptItem" "Framework" "KnowledgeItem" \
                 "NewsItem" "NewsMessage" "PackageItem" "PlanningItem"
do
    echo "Moving ...$component..."
    cp $SOURCE_FOLDER/NewsML-G2_$NEWSMLG2_VERSION-spec-$component-Power_$NEWSMLG2_REVISION.xsd \
       $TARGET_FOLDER/NewsML-G2_$NEWSMLG2_VERSION-spec-$component-Power.xsd
done
