#!/usr/bin/env bash
#
# Validate the NewsML-G2 example documents against the current Power schema.
#
# Every .xml file in examples/ is validated unless it is listed in
# examples/VALIDATION-EXCLUSIONS.txt, so a newly added example is covered
# automatically rather than having to be added to a list by hand. That same
# exclusions file is read by tests/runtests.py, which is what covers the
# examples in CI.
#
# Exits non-zero if any example fails to validate. Run from anywhere.

set -eu

cd "$(dirname "$0")/.."

# shellcheck source=newsmlg2-config-vars.sh
. release-tools/newsmlg2-config-vars.sh

POWER_XSD="$COMBINED_XSD_NO_REVISION"
EXAMPLE_DIR="examples"
EXCLUSIONS_FILE="$EXAMPLE_DIR/VALIDATION-EXCLUSIONS.txt"

if ! command -v xmllint >/dev/null 2>&1; then
    echo "ERROR: xmllint not found. Install libxml2 (macOS: it ships with the" >&2
    echo "       system; Debian/Ubuntu: apt-get install libxml2-utils)." >&2
    echo "       CI validates the examples via tests/runtests.py instead." >&2
    exit 1
fi

if [ ! -f "$POWER_XSD" ]; then
    echo "ERROR: schema not found: $POWER_XSD" >&2
    echo "       Check NEW_NEWSMLG2_VERSION in release-tools/newsmlg2-config-vars.sh" >&2
    exit 1
fi

if [ ! -f "$EXCLUSIONS_FILE" ]; then
    echo "ERROR: exclusions file not found: $EXCLUSIONS_FILE" >&2
    exit 1
fi

# Strip comments and blank lines.
EXCLUDED=$(sed -e 's/#.*//' -e '/^[[:space:]]*$/d' "$EXCLUSIONS_FILE")

is_excluded() {
    printf '%s\n' "$EXCLUDED" | grep -qxF "$1"
}

echo "Validating examples in $EXAMPLE_DIR against $POWER_XSD"

failed=0
validated=0
skipped=0

for path in "$EXAMPLE_DIR"/*.xml; do
    name=$(basename "$path")

    if is_excluded "$name"; then
        skipped=$((skipped + 1))
        # An excluded file that now validates means the exclusion is stale.
        if xmllint --noout --schema "$POWER_XSD" "$path" >/dev/null 2>&1; then
            echo "NOTE: $name is excluded but now validates."
            echo "      Remove it from $EXCLUSIONS_FILE."
        fi
        continue
    fi

    if xmllint --noout --schema "$POWER_XSD" "$path"; then
        validated=$((validated + 1))
    else
        failed=$((failed + 1))
    fi
done

# Report any excluded entry that no longer exists, so the list cannot rot.
printf '%s\n' "$EXCLUDED" | while IFS= read -r name; do
    [ -n "$name" ] || continue
    if [ ! -f "$EXAMPLE_DIR/$name" ]; then
        echo "NOTE: excluded file no longer exists: $name"
    fi
done

echo
echo "$validated validated, $skipped skipped, $failed failed."

if [ "$failed" -gt 0 ]; then
    echo "FAILED: $failed example(s) do not validate against $POWER_XSD" >&2
    exit 1
fi

echo "Done."
