#!/bin/bash

# load shared env vars
echo "Loading shared environment variables including new NewsML-G2 version number..."
. release-tools/newsmlg2-config-vars.sh

# For a simple minor version bump, these two paths might be the same
OLD_XSD_PATH="specification/XML-Schema_FileVersion_$OLD_NEWSMLG2_REVISION"
NEW_XSD_PATH="specification/XML-Schema_FileVersion_$NEWSMLG2_REVISION"

OLD_VERSION=$OLD_NEWSMLG2_VERSION
NEW_VERSION=$NEWSMLG2_VERSION

echo "Moving XML Schema files to temporary location for processing..."
TEMP_OLD_PATH=$(mktemp -d)
mv $OLD_XSD_PATH $TEMP_OLD_PATH

echo "Moving XML Schema files to $NEW_XSD_PATH and updating to new version number..."

if [ ! -d "$NEW_XSD_PATH" ]
then
    echo "  Making new folder for $NEW_XSD_PATH"
    mkdir -p $NEW_XSD_PATH
else
    echo "  Removing existing files in $NEW_XSD_PATH"
    git rm $NEW_XSD_PATH/*
    mkdir -p $NEW_XSD_PATH
fi

for component in "CatalogItem" "ConceptItem" "Framework" "KnowledgeItem" \
                 "NewsItem" "NewsMessage" "PackageItem" "PlanningItem"
do
    OLD_FILE="${TEMP_OLD_PATH}/XML-Schema_FileVersion_${OLD_NEWSMLG2_REVISION}/NewsML-G2_${OLD_VERSION}-spec-${component}-Power_${OLD_NEWSMLG2_REVISION}.xsd"
    NEW_FILE="${NEW_XSD_PATH}/NewsML-G2_${NEW_VERSION}-spec-${component}-Power_${NEWSMLG2_REVISION}.xsd"
    # remove the target (including from git repo) if it exists already
    if [ -f "$NEW_FILE" ]; then
        echo "  Removing existing file $NEW_FILE"
        git rm $NEW_FILE 
    fi
    echo "  Moving $component from $OLD_XSD_PATH to $NEW_XSD_PATH"
    mv $OLD_FILE $NEW_FILE
done

echo "Done. Now run release-tools/update-version-no-in-files.sh to update"
echo "version references in these files."
