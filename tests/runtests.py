#!/usr/bin/env python3

# -*- coding: utf-8 -*-

# Copyright (c) 2020 International Press Telecommunications Council (IPTC)
#
# The MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
NewsML-G2 unit test runner
"""

import lxml
import lxml.etree
import unittest
import os

DIRNAME = os.path.dirname(__file__)

LATEST_SCHEMA_VERSION = "2.29"
NEWSMLG2_SCHEMA = os.path.join(
    DIRNAME, '..', 'specification',
    'NewsML-G2_2.29-spec-All-Power.xsd'
)
NEWSMLG2_DEV_SCHEMA = os.path.join(
    DIRNAME, '..', 'dev-schema',
    'NewsML-G2dev_0.4_nar229.xsd'
)

TEST_FILES_FOLDER = os.path.join(
    DIRNAME, 'unit_test_files'
)
SCHEMA_FILES_FOLDER = os.path.join(
    DIRNAME, 'schema_versions'
)

SCHEMA_VERSIONS = {
    "dev": {
        "schema_file": os.path.join(
            DIRNAME, '..', 'dev-schema', 'NewsML-G2dev_0.4_nar229.xsd'
        ),
        "should_pass_folders": [
            os.path.join(TEST_FILES_FOLDER, 'dev', 'should_pass'),
            os.path.join(TEST_FILES_FOLDER, '2.29', 'should_pass'),
            os.path.join(TEST_FILES_FOLDER, '2.28', 'should_pass'),
            os.path.join(TEST_FILES_FOLDER, '2.27', 'should_pass'),
            os.path.join(TEST_FILES_FOLDER, '2.26', 'should_pass'),
            os.path.join(TEST_FILES_FOLDER, '2.25', 'should_pass'),
            os.path.join(TEST_FILES_FOLDER, '2.24', 'should_pass')
        ],
        "should_fail_folders": [
            os.path.join(TEST_FILES_FOLDER, 'dev', 'should_fail')
        ],
    },
    "2.29": {
        "schema_file": os.path.join(
            DIRNAME, '..', 'specification', 'NewsML-G2_2.29-spec-All-Power.xsd'
        ),
        "should_pass_folders": [
            os.path.join(TEST_FILES_FOLDER, '2.29', 'should_pass'),
            os.path.join(TEST_FILES_FOLDER, '2.28', 'should_pass'),
            os.path.join(TEST_FILES_FOLDER, '2.27', 'should_pass'),
            os.path.join(TEST_FILES_FOLDER, '2.26', 'should_pass'),
            os.path.join(TEST_FILES_FOLDER, '2.25', 'should_pass'),
            os.path.join(TEST_FILES_FOLDER, '2.24', 'should_pass')
        ],
        "should_fail_folders": [
            os.path.join(TEST_FILES_FOLDER, '2.29', 'should_fail')
        ],
     },
    "2.28": {
        "schema_file": os.path.join(
            SCHEMA_FILES_FOLDER, 'NewsML-G2_2.28-spec-All-Power.xsd'
        ),
        "should_pass_folders": [
            os.path.join(TEST_FILES_FOLDER, '2.28', 'should_pass'),
            os.path.join(TEST_FILES_FOLDER, '2.27', 'should_pass'),
            os.path.join(TEST_FILES_FOLDER, '2.26', 'should_pass'),
            os.path.join(TEST_FILES_FOLDER, '2.25', 'should_pass'),
            os.path.join(TEST_FILES_FOLDER, '2.24', 'should_pass')
        ],
        "should_fail_folders": [
            os.path.join(TEST_FILES_FOLDER, '2.28', 'should_fail'),
            os.path.join(TEST_FILES_FOLDER, '2.29', 'should_fail')
        ],
    },
    "2.27": {
        "schema_file": os.path.join(
            SCHEMA_FILES_FOLDER, 'NewsML-G2_2.27-spec-All-Power.xsd'
        ),
        "should_pass_folders": [
            os.path.join(TEST_FILES_FOLDER, '2.27', 'should_pass'),
            os.path.join(TEST_FILES_FOLDER, '2.26', 'should_pass'),
            os.path.join(TEST_FILES_FOLDER, '2.25', 'should_pass'),
            os.path.join(TEST_FILES_FOLDER, '2.24', 'should_pass')
        ],
        "should_fail_folders": [
            os.path.join(TEST_FILES_FOLDER, '2.27', 'should_fail'),
            os.path.join(TEST_FILES_FOLDER, '2.28', 'should_fail'),
            os.path.join(TEST_FILES_FOLDER, '2.29', 'should_fail')
        ],
    },
    "2.26": {
        "schema_file": os.path.join(
            SCHEMA_FILES_FOLDER, 'NewsML-G2_2.26-spec-All-Power.xsd'
        ),
        "should_pass_folders": [
            os.path.join(TEST_FILES_FOLDER, '2.26', 'should_pass'),
            os.path.join(TEST_FILES_FOLDER, '2.25', 'should_pass'),
            os.path.join(TEST_FILES_FOLDER, '2.24', 'should_pass')
        ],
        "should_fail_folders": [
            os.path.join(TEST_FILES_FOLDER, '2.26', 'should_fail'),
            os.path.join(TEST_FILES_FOLDER, '2.27', 'should_fail'),
            os.path.join(TEST_FILES_FOLDER, '2.28', 'should_fail'),
            os.path.join(TEST_FILES_FOLDER, '2.29', 'should_fail')
        ],
    },
    "2.25": {
        "schema_file": os.path.join(
            SCHEMA_FILES_FOLDER, 'NewsML-G2_2.25-spec-All-Power.xsd'
        ),
        "should_pass_folders": [
            os.path.join(TEST_FILES_FOLDER, '2.25', 'should_pass'),
            os.path.join(TEST_FILES_FOLDER, '2.24', 'should_pass'),
            # os.path.join(TEST_FILES_FOLDER, '2.23', 'should_pass'),
            os.path.join(TEST_FILES_FOLDER, '2.22', 'should_pass')
        ],
        "should_fail_folders": [
            os.path.join(TEST_FILES_FOLDER, '2.25', 'should_fail'),
            os.path.join(TEST_FILES_FOLDER, '2.26', 'should_fail'),
            os.path.join(TEST_FILES_FOLDER, '2.27', 'should_fail'),
            os.path.join(TEST_FILES_FOLDER, '2.28', 'should_fail'),
            os.path.join(TEST_FILES_FOLDER, '2.29', 'should_fail')
        ],
    },
    "2.24": {
        "schema_file": os.path.join(
            SCHEMA_FILES_FOLDER, 'NewsML-G2_2.24-spec-All-Power.xsd'
        ),
        "should_pass_folders": [
            os.path.join(TEST_FILES_FOLDER, '2.24', 'should_pass'),
            # os.path.join(TEST_FILES_FOLDER, '2.23', 'should_pass'),
            os.path.join(TEST_FILES_FOLDER, '2.22', 'should_pass')
        ],
        "should_fail_folders": [
            os.path.join(TEST_FILES_FOLDER, '2.24', 'should_fail'),
            os.path.join(TEST_FILES_FOLDER, '2.25', 'should_fail'),
            os.path.join(TEST_FILES_FOLDER, '2.26', 'should_fail'),
            os.path.join(TEST_FILES_FOLDER, '2.27', 'should_fail'),
            os.path.join(TEST_FILES_FOLDER, '2.28', 'should_fail'),
            os.path.join(TEST_FILES_FOLDER, '2.29', 'should_fail')
        ]
    },
    "2.23": {
        "schema_file": os.path.join(
            # SCHEMA_FILES_FOLDER, 'NewsML-G2_2.23-spec-All-Power.xsd'
            SCHEMA_FILES_FOLDER, 'G2-multi-schema-2.23.xsd'
        ),
        "should_pass_folders": [
            os.path.join(TEST_FILES_FOLDER, '2.23', 'should_pass'),
            os.path.join(TEST_FILES_FOLDER, '2.22', 'should_pass')
        ],
        "should_fail_folders": [
            os.path.join(TEST_FILES_FOLDER, '2.23', 'should_fail'),
            os.path.join(TEST_FILES_FOLDER, '2.24', 'should_fail'),
            os.path.join(TEST_FILES_FOLDER, '2.25', 'should_fail'),
            os.path.join(TEST_FILES_FOLDER, '2.26', 'should_fail'),
            os.path.join(TEST_FILES_FOLDER, '2.27', 'should_fail'),
            os.path.join(TEST_FILES_FOLDER, '2.28', 'should_fail'),
            os.path.join(TEST_FILES_FOLDER, '2.29', 'should_fail')
        ]
    },
    "2.22": {
        "schema_file": os.path.join(
            SCHEMA_FILES_FOLDER, 'NewsML-G2_2.22-spec-All-Power.xsd'
        ),
        "should_pass_folders": [
            os.path.join(TEST_FILES_FOLDER, '2.22', 'should_pass')
        ],
        "should_fail_folders": [
            os.path.join(TEST_FILES_FOLDER, '2.22', 'should_fail'),
            os.path.join(TEST_FILES_FOLDER, '2.23', 'should_fail'),
            os.path.join(TEST_FILES_FOLDER, '2.24', 'should_fail'),
            os.path.join(TEST_FILES_FOLDER, '2.25', 'should_fail'),
            os.path.join(TEST_FILES_FOLDER, '2.26', 'should_fail'),
            os.path.join(TEST_FILES_FOLDER, '2.27', 'should_fail'),
            os.path.join(TEST_FILES_FOLDER, '2.28', 'should_fail'),
            os.path.join(TEST_FILES_FOLDER, '2.29', 'should_fail')
        ]
    },
    "2.21": {
        "schema_file": os.path.join(
            SCHEMA_FILES_FOLDER, 'NewsML-G2_2.21-spec-All-Power.xsd'
        ),
        "should_pass_folders": [
            os.path.join(TEST_FILES_FOLDER, '2.21', 'should_pass')
        ],
        "should_fail_folders": [
            os.path.join(TEST_FILES_FOLDER, '2.21', 'should_fail'),
            os.path.join(TEST_FILES_FOLDER, '2.22', 'should_fail'),
            os.path.join(TEST_FILES_FOLDER, '2.23', 'should_fail'),
            os.path.join(TEST_FILES_FOLDER, '2.24', 'should_fail'),
            os.path.join(TEST_FILES_FOLDER, '2.25', 'should_fail'),
            os.path.join(TEST_FILES_FOLDER, '2.26', 'should_fail'),
            os.path.join(TEST_FILES_FOLDER, '2.27', 'should_fail'),
            os.path.join(TEST_FILES_FOLDER, '2.28', 'should_fail'),
            os.path.join(TEST_FILES_FOLDER, '2.29', 'should_fail')
        ]
    }
}

"""
We make extensive use of subTest, so we want to count the number of subTests
run, not just the number of top-level tests (which is only 2 in our case!)
"""
class CountSubtestsResult(unittest.TextTestResult):
    def addSubTest(self, test, subtest, outcome):
        # handle failures calling base class
        super(CountSubtestsResult, self).addSubTest(test, subtest, outcome)
        # add to total number of tests run
        self.testsRun += 1 

class TestNewsMLSchema(unittest.TestCase):
    newsmlg2_schema = None
    newsmlg2_dev_schema = None
    schemas = {}

    # use the above helper class to count subtests
    # def run(self, test_result=None):
    #     return super(TestNewsMLSchema, self).run(CountSubtestsResult())

    def __init__(self, *args, **kwargs):
        """
        Set up paths and load the schema.

        If we put this in setUp() rather than __init__(), it would
        load the schema for each test which is unnecessary.
        """
        self.current_path = DIRNAME
        for schema_version, schema in SCHEMA_VERSIONS.items():
            self.schemas[schema_version] = lxml.etree.XMLSchema(
                file=schema['schema_file']
            )
        with open(NEWSMLG2_SCHEMA) as schemafile:
            self.newsmlg2_schema = lxml.etree.XMLSchema(file=schemafile)
        return super(TestNewsMLSchema, self).__init__(*args, **kwargs)

    # HELPER FUNCTIONS

    def get_files_in_folder(self, folder_name):
        return [
            os.path.join(folder_name, file)
            for file in os.listdir(folder_name)
            if file.endswith('.xml')
        ]

    def load_test_file(self, file_name):
        with open(file_name, 'r') as xmlfile:
            instance = lxml.etree.parse(xmlfile)
        return instance

    def folder_should_pass(self, schema=None, folder_name=None):
        testfiles = self.get_files_in_folder(folder_name)
        for file in testfiles:
            with self.subTest(file=file):
                instance = self.load_test_file(file)
                schema.assertValid(instance)

    def folder_should_fail(self, schema=None, folder_name=None):
        testfiles = self.get_files_in_folder(folder_name)
        for file in testfiles:
            with self.subTest(file=file):
                instance = self.load_test_file(file)
                self.assertFalse(
                    schema.validate(instance)
                )

    # TESTS START HERE

    def test_simplest_instance_newsmlg2(self):
        instance = """<?xml version="1.0" encoding="UTF-8"?>
<newsItem
    xmlns="http://iptc.org/std/nar/2006-10-01/"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    guid="simplest-test"
    standard="NewsML-G2"
    standardversion="2.29"
    conformance="power"
    xml:lang="en-GB">
    <catalogRef href="http://www.iptc.org/std/catalog/catalog.IPTC-G2-Standards_35.xml" />
    <itemMeta>
        <itemClass qcode="ninat:text" />
        <provider qcode="nprov:REUTERS" />
        <versionCreated>2018-10-21T16:25:32-05:00</versionCreated>
    </itemMeta>
    <contentSet>
        <inlineXML contenttype="application/nitf+xml">
        </inlineXML>
    </contentSet>
</newsItem>
"""
        parser = lxml.etree.XMLParser(schema=self.newsmlg2_schema)
        self.assertIsNotNone(
            lxml.etree.fromstring(bytes(instance, encoding='utf-8'), parser)
        )

    def test_all_schema_versions_against_pass_and_fail_tests(self):
        """
        Run files in TEST_FILES_FOLDER/should_pass against the latest NewsML-G2
        schema. They should all pass (ie they are all valid against the schema).

        Within folder_should_pass and folder_should_fail, we  use "subTest" so
        we can see which file failed the test.
        """
        for schema_version, schema in SCHEMA_VERSIONS.items():
            for should_pass_folder in schema['should_pass_folders']:
                self.folder_should_pass(
                    schema=self.schemas[schema_version],
                    folder_name=should_pass_folder
                )
            for should_fail_folder in schema['should_fail_folders']:
                self.folder_should_fail(
                    schema=self.schemas[schema_version],
                    folder_name=should_fail_folder
                )

if __name__ == '__main__':
    unittest.main(testRunner=unittest.TextTestRunner(resultclass=CountSubtestsResult))

