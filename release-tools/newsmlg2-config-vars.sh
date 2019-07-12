# Shared env vars used by other scripts in "release-tools"

export NEWSMLG2_VERSION="2.28"

# This will need to change based on your local paths (TODO: make this configurable)
export SAXON_PATH="../../../saxon/saxon_java_he/saxon9he.jar"

export NEWSMLG2_BUILD_XSLT="release-tools/xslt/Build-ALLschema-XSLT1.xslt"
export NEWSMLG2_SOURCE_PATH="specification/individual"
export NEWSMLG2_TARGET_PATH="specification/"
export MASTER_XSD="$NEWSMLG2_SOURCE_PATH/NewsML-G2_$NEWSMLG2_VERSION-spec-Framework-Power.xsd"
export POWER_XSD="$NEWSMLG2_TARGET_PATH/NewsML-G2_NEWSMLG2_VERSION-spec-All-Power.xsd"
