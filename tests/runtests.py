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

TEST_FILES_FOLDER = "unit_test_files"
EXAMPLE_FILES_FOLDER = os.path.join(DIRNAME, '..', 'examples')
SPECIFICATION_EXAMPLES_FOLDER = os.path.join(DIRNAME, '..', 'newsml-g2-guidelines', '_includes', 'GuidelinesCodeExamples')
GUIDELINES_EXAMPLES_FOLDER = os.path.join(DIRNAME, '..', 'newsml-g2-guidelines', '_includes', 'GuidelinesCodeExamples')


class TestNewsMLSchema(unittest.TestCase):
    newsmlg2_schema = None
    newsmlg2_dev_schema = None

    def __init__(self, *args, **kwargs):
        """
        Set up paths and load the schema.

        If we put this in setUp() rather than __init__(), it would
        load the schema for each test which is unnecessary.
        """
        self.current_path = os.path.dirname(__file__)
        with open(NEWSMLG2_SCHEMA) as schemafile:
            self.newsmlg2_schema = lxml.etree.XMLSchema(file=schemafile)
        with open(NEWSMLG2_DEV_SCHEMA) as devschemafile:
            self.newsmlg2_dev_schema = lxml.etree.XMLSchema(file=devschemafile)
        return super(TestNewsMLSchema, self).__init__(*args, **kwargs)

    # HELPER FUNCTIONS

    def get_files_in_folder(self, folder_name):
        folder_name = os.path.join(
                        self.current_path,
                        folder_name
                    )
        return [
            os.path.join(folder_name, file)
            for file in os.listdir(folder_name)
            if file.endswith('.xml')
        ]

    def get_test_files_in_folder(self, test_folder_name):
        return self.get_files_in_folder(
                 os.path.join(
                    TEST_FILES_FOLDER,
                    test_folder_name
                 )
               )

    def load_test_file(self, file_name):
        with open(file_name, 'r') as xmlfile:
            instance = lxml.etree.parse(xmlfile)
        return instance

    def folder_should_pass(self, schema=None, folder_name=None):
        testfiles = self.get_test_files_in_folder(folder_name)
        for file in testfiles:
            with self.subTest(file=file):
                instance = self.load_test_file(file)
                self.newsmlg2_schema.assertValid(instance)
                #self.assertTrue(
                #    self.newsmlg2_schema.validate(instance)
                #)

    def folder_should_fail(self, schema=None, folder_name=None):
        testfiles = self.get_test_files_in_folder(folder_name)
        for file in testfiles:
            with self.subTest(file=file):
                instance = self.load_test_file(file)
                self.assertFalse(
                    self.newsmlg2_schema.validate(instance)
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

    def test_all_passing_unit_test_files_against_latest_schema(self):
        """
        Run files in TEST_FILES_FOLDER/should_pass against the latest NewsML-G2
        schema. They should all pass (ie they are all valid against the schema).

        We use "subTest" so we can see which file failed in test output.
        """
        self.folder_should_pass(
            schema=self.newsmlg2_schema,
            folder_name=os.path.join(LATEST_SCHEMA_VERSION, 'should_pass')
        )

    def test_failing_unit_test_files_against_latest_schema(self):
        """
        Run files in TEST_FILES_FOLDER/should_fail against the latest NewsML-G2
        schema. They should all fail (ie they are all invalid in some way).
        """
        self.folder_should_fail(
            schema=self.newsmlg2_schema,
            folder_name=os.path.join(LATEST_SCHEMA_VERSION, 'should_fail')
        )

    def test_all_passing_unit_test_files_against_dev_schema(self):
        """
        Run files in TEST_FILES_FOLDER/dev/should_pass against the dev schema.
        They should all pass (ie they are all valid against the schema).
        """
        self.folder_should_pass(
            schema=self.newsmlg2_dev_schema,
            folder_name=os.path.join(LATEST_SCHEMA_VERSION, 'should_pass')
        )

    def test_failing_unit_test_files_against_dev_schema(self):
        """
        Run files in TEST_FILES_FOLDER/dev/should_fail against the dev schema.
        They should all fail (ie they are all invalid in some way).
        """
        #self.folder_should_fail(
        #    schema=self.ninjsdev_schema,
        #    folder_name=os.path.join('dev', 'should_fail')
        #)


if __name__ == '__main__':
    unittest.main()
