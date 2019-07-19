# Shared env vars used by other scripts in "release-tools"

export NEWSMLG2_VERSION="2.28"
export NEWSMLG2_REVISION="2"

# This will need to change based on your local path
export SAXON_PATH="../../../saxon/saxon_java_he/saxon9he.jar"

export NEWSMLG2_BUILD_XSLT="release-tools/xslt/Build-ALLschema-XSLT1.xslt"
export NEWSMLG2_REVISION_PATH="specification/XML-Schema_FileVersion_$NEWSMLG2_REVISION"
export NEWSMLG2_NOREV_PATH="specification"
export FRAMEWORK_XSD_WITH_REVISION="$NEWSMLG2_REVISION_PATH/NewsML-G2_$NEWSMLG2_VERSION-spec-Framework-Power_$NEWSMLG2_REVISION.xsd"
export FRAMEWORK_XSD_NO_REVISION="$NEWSMLG2_NOREV_PATH/NewsML-G2_$NEWSMLG2_VERSION-spec-Framework-Power.xsd"
export COMBINED_XSD_WITH_REVISION="$NEWSMLG2_REVISION_PATH/NewsML-G2_$NEWSMLG2_VERSION-spec-All-Power_$NEWSMLG2_REVISION.xsd"
export COMBINED_XSD_NO_REVISION="$NEWSMLG2_NOREV_PATH/NewsML-G2_$NEWSMLG2_VERSION-spec-All-Power.xsd"
