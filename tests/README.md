# NewsML-G2 Unit Test Suite

[![IPTC](https://circleci.com/gh/iptc/newsml-g2.svg?style=svg)](https://app.circleci.com/pipelines/github/iptc/newsml-g2)

We have created a set of unit tests for NewsML-G2, based on a set of test files
that the IPTC NewsML-G2 Working Group have used internally over the years.

The tests fulfil multiple purposes:

 *  They allow us to be confident that as we make changes for future versions of
    NewsML-G2, we do not unintentionally break backwards-compatibility with
    previous 2.x versions of the schema
 *  They document the changes that have been made to NewsML-G2 over the years,
    aligning with the "Changes to NewsML-G2 and related standards" section of
    the NewsML-G2 Guidelines, found at
    https://www.iptc.org/std/NewsML-G2/guidelines/#changes-to-newsml-g2-and-related-standards
 *  They provide a clear way of showing what is possible in NewsML-G2 through
    valid example files.

## File layout

The `schema_versions` folder contains copies of the XML Schema files for every
version of NewsML-G2 and NAR (IPTC's News Architecture).

The `unit_test_files` folder contains sub-folders, one for each tested version
of NewsML-G2. Within these folders are `should_pass` and `should_fail` folders.
These contain individual NewsML-G2 XML files which should either pass or fail
validation against the version of the schema relating to the parent folder.

For example all files in `unit_test_files/2.25/should_pass` should pass XML
Schema validation against the schema file
`schema_versions/NewsML-G2_2.25-spec-All-Power.xsd`.

## Running the tests

The test runner `run_tests.py` is a Python 3 script. It requires one
Python module, the XML parser `lxml`. The `requirements.txt` file
can be used to load the appropriate Python requirements.

Here is one way you can run the tests on your own machine:

    $ python3 -m venv newsmlg2tests  # create a Python virtual environment
    $ source newsmlg2tests/bin/activate  # switch to the virtual env
    (newsmlg2tests) $ python3 -m pip install -r requirements.txt 
    Collecting lxml==4.5.1 (from -r requirements.txt (line 1))
      Using cached https://files.pythonhosted.org/packages/01/89/cb97f90a061106a526ff22358f186bad6d0505d0e02559aeabdd2f906f8e/lxml-4.5.1-cp37-cp37m-macosx_10_9_x86_64.whl
    Installing collected packages: lxml
    Successfully installed lxml-4.5.1
    (newsmlg2tests) $ python3 runtests.py 
    ..
    ----------------------------------------------------------------------
    Ran 1291 tests in 0.463s

    OK

## Automated testing with CircleCI

Thanks to CircleCI, we automatically run the unit tests on each commit
to this repository.

## Notes on the tests

NewsML 2.23 introduced the concept of embedding RightsML documents into
NewsML-G2. The tests for this feature under
`unit_test_files/2.23/should_pass/` therefore require the XML Schema validator
to validate against both the NewsML-G2 and the RightsML XML Schemas. To allow
for this we created a dummy schema, `schema_versions/G2-multi-schema-2.23.xsd`
which imports both the NewsML-G2 2.23 and RightsML/ODRL schemas.

This means that the 2.23 tests can't be included in regressions for other
NewsML-G2 versions, without creating a dummy schema for each new version of
NewsML-G2. Therefore they are commented out until we can find a better solution.
