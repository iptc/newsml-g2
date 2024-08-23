# Shared env vars used by other scripts in "release-tools"

## These vars must be edited for each new release:

# The initial revision of a new version is 1, first change becomes revision 2
export NEW_NEWSMLG2_VERSION="2.35"
export NEW_NEWSMLG2_REVISION="1"

# This should refer to the latest publicly released version and revision
export OLD_NEWSMLG2_VERSION="2.34"
export OLD_NEWSMLG2_REVISION="1"

# Actual or expected approval date
export APPROVAL_DATE="2024-10-02"

## we shouldn't need to alter anything below here

# The date that these changes are being made - inserted into the XML Schema docs
export TODAY=$(date +%Y-%m-%d)

# This will need to change based on your local path
THISDIR="$(dirname "$0")"
export SAXON_PATH="$THISDIR/../../../saxon/saxon-he-11.3.jar"

export NEWSMLG2_BUILD_XSLT="release-tools/xslt/Build-ALLschema-XSLT1.xslt"
export NEWSMLG2_REVISION_PATH="specification/XML-Schema_FileVersion_$NEW_NEWSMLG2_REVISION"
export NEWSMLG2_NOREV_PATH="specification"
export FRAMEWORK_XSD_WITH_REVISION="$NEWSMLG2_REVISION_PATH/NewsML-G2_$NEW_NEWSMLG2_VERSION-spec-Framework-Power_$NEW_NEWSMLG2_REVISION.xsd"
export FRAMEWORK_XSD_NO_REVISION="$NEWSMLG2_NOREV_PATH/NewsML-G2_$NEW_NEWSMLG2_VERSION-spec-Framework-Power.xsd"
export COMBINED_XSD_WITH_REVISION="$NEWSMLG2_REVISION_PATH/NewsML-G2_$NEW_NEWSMLG2_VERSION-spec-All-Power_$NEW_NEWSMLG2_REVISION.xsd"
export COMBINED_XSD_NO_REVISION="$NEWSMLG2_NOREV_PATH/NewsML-G2_$NEW_NEWSMLG2_VERSION-spec-All-Power.xsd"
export OLD_COMBINED_XSD_NO_REVISION="$NEWSMLG2_NOREV_PATH/NewsML-G2_$OLD_NEWSMLG2_VERSION-spec-All-Power.xsd"
