# Maintenance notes

Notes only used by the maintainers of NewsML-G2 at IPTC.

## Releasing a new version of NewsML-G2

Steps to release an update to the standard:

1. Create a new GitHub branch for the changes
2. Update the version number in all files: (TODO: write a script for this based on Michael's C# tool)
  * Change filenames of specification/individual to match the new version number using `release-tools/update_xsd_version_no.sh`
  * Change version number references within each file in specification/individual/*.xsd
  * Change version number references within each file in examples/*.xml
  * `specification/individual/NewsML-xx-Framework` file has two headers - both need to be updated with version number and any date changes - can cut and paste from one section to the other.
  * create new folder under "releases" wth new version number e.g. "2.28_2"
  * Update `release-tools/newsmlg2-config-vars.sh` to use the correct version number.
3. Make the XML schema changes that are needed, including change requests from dev.iptc.org
4. Run the script that uses an XSLT stylesheet to create the master version from the framework version:
    `release-tools/create-power-xsd-from-framework-xsd.sh`
5. Run `xmllint` over the examples folder to make sure no errors have been introduced using a script:
    `release-tools/test-newsml-examples.sh`
6. Use XML Spy to create XML Schema documentation from the master XSD file. Save them to
`specification/XML-Schema-Doc-Power`.
7. Print change requests to PDF for inclusion in release pack to be sent to delegates
8. Run the script to move all files to the release folder and create ZIP files to send to delegates:
    `release-tools/create-release.sh`
