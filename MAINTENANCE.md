# Maintenance notes

Notes only used by the maintainers of NewsML-G2 at IPTC.

## Releasing a new version of NewsML-G2

Steps to release an update to the standard:

1. Create a new GitHub branch for the changes: `git checkout -b my-new-branch`
2. For a major or minor version change...
   For a revision change, copy the XML-Schema_FileVersion_# folder e.g. to the appropriate revision number (the first release is always revision 1, the first fix is always revision 2)
3. Check that the version numbers are correct in `release-tools/newsmlg2-config-vars.sh`
4. Update the version number in all files: (TODO: write a script for this based on Michael's C# tool)
    1. Update `release-tools/newsmlg2-config-vars.sh` to use the correct version number. This is
    used by the release scripts.
    2. Change filenames of specification/individual XSDs to match the new version number using
    `release-tools/update_xsd_version_no.sh`
    3. Change version number references within each file in specification/individual/*.xsd
    4. Change version number references within each file in examples/*.xml
    5. `specification/individual/NewsML-xx-Framework` file has two headers - both need to be
    updated with version number and any date changes - can cut and paste from one section to the other.
5. Make the XML schema changes that are needed in the `XML-Schema_FileVersion_#` folder, including
   any outstanding [change requests from the dev.iptc.org site](http://dev.iptc.org/G2-Change-Requests-HP)
6. Copy from the XML-Schema_FileVersion_# folder to the specification/individual folder
7. Run the script that uses an XSLT stylesheet to create the master version from the framework
   version in the specification/individual version:
    `release-tools/create-power-xsd-from-framework-xsd.sh`
8. Run `xmllint` over the examples folder to make sure no errors have been introduced using a script:
    `release-tools/test-newsml-examples.sh`
9. Use XML Spy to create XML Schema documentation from the master XSD schema file and the
   "individual" schemas. Save them to `specification/XML-Schema-Doc-Power`.
10. Print change requests from dev.iptc.org to PDF for inclusion in release pack to be sent to
   delegates, if necessary.
11. Run the script to move all files to the release folder and create ZIP files to send to delegates:
    `release-tools/create-release.sh`
12. Commit and push all changes to GitHub: `git push origin -u my-new-branch`
   (Our `.gitignore` file already suppresses sending ZIP files and the XML Schema docs to GitHub.)
13. Upload the "release/N.NN" folder and the ZIP files to the iptc.org server
14. Update the redirects on iptc.org to point to the latest versions of XML Schema documentation.
15. Update the http://dev.iptc.org/G2-Approved-Changes page documenting the changes made.
