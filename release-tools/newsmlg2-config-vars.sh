# Shared env vars used by other scripts in "release-tools"

## These vars must be edited for each new release:

# The initial revision of a new version is 1, first change becomes revision 2
export NEWSMLG2_VERSION="2.29"
export NEWSMLG2_REVISION="1"

# This should refer to the latest publicly released version and revision
export OLD_NEWSMLG2_VERSION="2.28"
export OLD_NEWSMLG2_REVISION="2"

## we shouldn't need to alter anything below here

# The date that these changes are being made - inserted into the XML Schema docs
export TODAY=$(date +%Y-%m-%d)

# This will need to change based on your local path
export SAXON_PATH="../../../saxon/saxon_java_he/saxon9he.jar"

export NEWSMLG2_BUILD_XSLT="release-tools/xslt/Build-ALLschema-XSLT1.xslt"
export NEWSMLG2_REVISION_PATH="specification/XML-Schema_FileVersion_$NEWSMLG2_REVISION"
export NEWSMLG2_NOREV_PATH="specification"
export FRAMEWORK_XSD_WITH_REVISION="$NEWSMLG2_REVISION_PATH/NewsML-G2_$NEWSMLG2_VERSION-spec-Framework-Power_$NEWSMLG2_REVISION.xsd"
export FRAMEWORK_XSD_NO_REVISION="$NEWSMLG2_NOREV_PATH/NewsML-G2_$NEWSMLG2_VERSION-spec-Framework-Power.xsd"
export COMBINED_XSD_WITH_REVISION="$NEWSMLG2_REVISION_PATH/NewsML-G2_$NEWSMLG2_VERSION-spec-All-Power_$NEWSMLG2_REVISION.xsd"
export COMBINED_XSD_NO_REVISION="$NEWSMLG2_NOREV_PATH/NewsML-G2_$NEWSMLG2_VERSION-spec-All-Power.xsd"
export OLD_COMBINED_XSD_NO_REVISION="$NEWSMLG2_NOREV_PATH/NewsML-G2_$OLD_NEWSMLG2_VERSION-spec-All-Power.xsd"
