# Maintenance notes

These notes are only of relevance to the maintainers of NewsML-G2 at IPTC.

## Releasing a new version of NewsML-G2

Steps to create and release an update to the standard:

### High-level overview of the steps required (see detailed steps below)

- Copy the latest version of schema files into the
  `specification/FileVersion_<revision>` folder based on our new revision number
- Update the files in `specification/FileVersion_<revision>` with new version
  numbers and dates
- Make the required schema changes to the `specification/FileVersion<revision>`
  files
- Create the "All" version from the individual versions in the
  `FileVersion_<revision>` folder
- Copy the new files to specification/individual folder, removing revision info
  from the filenames
- Check that the schema file works by validating against example documents
- Create documentation using XML Spy
- Make release version to be uploaded to iptc.org

### In detail

1.  Create a new GitHub branch for the changes: `git checkout -b newsmlN.NN`
    (or `newsmlN.NN_N`)
2.  Update the `release-tools/newsmlg2-config-vars.sh` file with the version
    numbers of the old and new versions and revision
3.  Don't forget to run it! `source release-tools/newsmlg2-config-vars.sh`
4.  Run `release-tools/update-xsd-version-no.sh` to update
    `XML-Schema_FileVersion_N` files to refer to the new version
5.  Run `release-tools/update-version-no-in-files.sh` to update version
    numbers and dates in the schema documents
6.  By hand, make the XML schema changes that are needed in the
    `XML-Schema_FileVersion_#` folder, including any outstanding [change
    requests from the dev.iptc.org
    site](http://dev.iptc.org/G2-Change-Requests-HP)
7.  Run `release-tools/move-to-individual.sh`
    This copies and renames the individual schema component files from the
    `XML-Schema_FileVersion_#` folder to the `specification/individual` folder.
    The script also removes a _<revision> reference inside the schema files.
8.  Run the script that uses an XSLT stylesheet to create the master version
    from the framework version in the specification/individual folder:
    `release-tools/create-power-xsd-from-framework-xsd.sh`
9.  Run `release-tools/update-version-no-in-examples.sh` which updates version
    number references within each file in examples/*.xml (except for the older
    examples which need to refer to 2.24 because that's the last version
    supported by the Core version of the standard)
10. Run `release-tools/update-catalog-version-in-examples.sh` which updates
    the catalog number referred from example files.
11. Run `release-tools/test-newsml-examples.sh` which runs `xmllint` over the
    examples folder to make sure no errors have been introduced.
12. Run `tests/runtests.py` to run the unit tests and make sure that the new
    version doesn't break any old test cases. You should also write new unit
    tests for the changes being added, if you haven't already.
13. Use XML Spy to create XML Schema documentation from the master XSD schema
    file and the "individual" schemas. Save them to
    `specification/XML-Schema-Doc-Power`.
14. Print-to-PDF change requests from dev.iptc.org for inclusion in release pack
    to be sent to delegates, if necessary.
15. Update the documentation page in documentation/NewsML-G2-documentation.md to
    point to the appropriate versions of the specs, XML Schema docs and
    guidelines.
16. Run the script to move all files to the release folder and create ZIP files
    of the release: `release-tools/create-release.sh`
17. Commit and push all changes to GitHub: `git push origin -u my-new-branch`
    (Our `.gitignore` file already suppresses sending ZIP files to GitHub.)
18. Create a pull request from the branch on GitHub.com.

### After the Standards Committee approves the new version:

1.  Update the APPROVED_DATE in `release-tools/newsmlg2-config-vars.sh`
2.  Run the above steps 3, 5, 7, 8, 10, 12, 14, 15 again to update files with
    the approval date (this should be quick, just running scripts, except for
    the XML Spy documentation step)
3.  Commit changes and merge the pull request into the main branch on GitHub
4.  Upload the "releases/N.NN" folder and the ZIP files to the iptc.org server
5.  Update the redirects in iptc.org/std/.htaccess to point to the latest
    versions of XML Schema documentation.
6.  Update the http://dev.iptc.org/G2-Approved-Changes page documenting the
    changes made.
7.  Tag the release in GitHub: `git tag N.NN.N`, `git push --tags`)
8.  Move the CR page on dev.iptc.org to "G2 Approved Changes" area
9.  Update the http://dev.iptc.org/G2-Approved-Changes page to refer to the
    approved CR.

### To update unit tests:

1.  Create a new schema referring to the latest schema version, in the
    `tests/schema_versions` folder on the working branch.
2.  Update the `tests/run-tests.py` script to refer to the new version.
3.  Make a new folder in `tests/unit_test_files` with the new version number
    and put new test files there.
