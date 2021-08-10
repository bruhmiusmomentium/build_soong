#!/usr/bin/env python
#
# Copyright (C) 2021 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Unit tests for verify_overlaps_test.py."""
import io
import unittest

from verify_overlaps import *

class TestSignatureToElements(unittest.TestCase):

    def signatureToElements(self, signature):
        return InteriorNode().signatureToElements(signature)

    def test_signatureToElements_1(self):
        expected = [
            'package:java',
            'package:lang',
            'class:ProcessBuilder',
            'class:Redirect',
            'class:1',
            'member:<init>()V',
        ]
        self.assertEqual(expected, self.signatureToElements(
            "Ljava/lang/ProcessBuilder$Redirect$1;-><init>()V"))

    def test_signatureToElements_2(self):
        expected = [
            'package:java',
            'package:lang',
            'class:Object',
            'member:hashCode()I',
        ]
        self.assertEqual(expected, self.signatureToElements(
            "Ljava/lang/Object;->hashCode()I"))

    def test_signatureToElements_3(self):
        expected = [
            'package:java',
            'package:lang',
            'class:CharSequence',
            'class:',
            'class:ExternalSyntheticLambda0',
            'member:<init>(Ljava/lang/CharSequence;)V',
        ]
        self.assertEqual(expected, self.signatureToElements(
            "Ljava/lang/CharSequence$$ExternalSyntheticLambda0;"
            "-><init>(Ljava/lang/CharSequence;)V"))

class TestDetectOverlaps(unittest.TestCase):

    def read_flag_trie_from_string(self, csv):
        with io.StringIO(csv) as f:
            return read_flag_trie_from_stream(f)

    def read_signature_csv_from_string_as_dict(self, csv):
        with io.StringIO(csv) as f:
            return read_signature_csv_from_stream_as_dict(f)

    def extract_subset_from_monolithic_flags_as_dict_from_string(self, monolithic, patterns):
        with io.StringIO(patterns) as f:
            return extract_subset_from_monolithic_flags_as_dict_from_stream(monolithic, f)

    extractInput = '''
Ljava/lang/Object;->hashCode()I,public-api,system-api,test-api
Ljava/lang/Object;->toString()Ljava/lang/String;,blocked
Ljava/util/zip/ZipFile;-><clinit>()V,blocked
Ljava/lang/Character$UnicodeScript;->of(I)Ljava/lang/Character$UnicodeScript;,blocked
Ljava/lang/Character;->serialVersionUID:J,sdk
Ljava/lang/ProcessBuilder$Redirect$1;-><init>()V,blocked
'''

    def test_extract_subset_signature(self):
        monolithic = self.read_flag_trie_from_string(TestDetectOverlaps.extractInput)

        patterns = 'Ljava/lang/Object;->hashCode()I'

        subset = self.extract_subset_from_monolithic_flags_as_dict_from_string(monolithic, patterns)
        expected = {
            'Ljava/lang/Object;->hashCode()I': {
                None: ['public-api', 'system-api', 'test-api'],
                'signature': 'Ljava/lang/Object;->hashCode()I',
            },
        }
        self.assertEqual(expected, subset)

    def test_extract_subset_class(self):
        monolithic = self.read_flag_trie_from_string(TestDetectOverlaps.extractInput)

        patterns = 'java/lang/Object'

        subset = self.extract_subset_from_monolithic_flags_as_dict_from_string(monolithic, patterns)
        expected = {
            'Ljava/lang/Object;->hashCode()I': {
                None: ['public-api', 'system-api', 'test-api'],
                'signature': 'Ljava/lang/Object;->hashCode()I',
            },
            'Ljava/lang/Object;->toString()Ljava/lang/String;': {
                None: ['blocked'],
                'signature': 'Ljava/lang/Object;->toString()Ljava/lang/String;',
            },
        }
        self.assertEqual(expected, subset)

    def test_extract_subset_outer_class(self):
        monolithic = self.read_flag_trie_from_string(TestDetectOverlaps.extractInput)

        patterns = 'java/lang/Character'

        subset = self.extract_subset_from_monolithic_flags_as_dict_from_string(monolithic, patterns)
        expected = {
            'Ljava/lang/Character$UnicodeScript;->of(I)Ljava/lang/Character$UnicodeScript;': {
                None: ['blocked'],
                'signature': 'Ljava/lang/Character$UnicodeScript;->of(I)Ljava/lang/Character$UnicodeScript;',
            },
            'Ljava/lang/Character;->serialVersionUID:J': {
                None: ['sdk'],
                'signature': 'Ljava/lang/Character;->serialVersionUID:J',
            },
        }
        self.assertEqual(expected, subset)

    def test_extract_subset_nested_class(self):
        monolithic = self.read_flag_trie_from_string(TestDetectOverlaps.extractInput)

        patterns = 'java/lang/Character$UnicodeScript'

        subset = self.extract_subset_from_monolithic_flags_as_dict_from_string(monolithic, patterns)
        expected = {
            'Ljava/lang/Character$UnicodeScript;->of(I)Ljava/lang/Character$UnicodeScript;': {
                None: ['blocked'],
                'signature': 'Ljava/lang/Character$UnicodeScript;->of(I)Ljava/lang/Character$UnicodeScript;',
            },
        }
        self.assertEqual(expected, subset)

    def test_extract_subset_package(self):
        monolithic = self.read_flag_trie_from_string(TestDetectOverlaps.extractInput)

        patterns = 'java/lang/*'

        subset = self.extract_subset_from_monolithic_flags_as_dict_from_string(monolithic, patterns)
        expected = {
            'Ljava/lang/Character$UnicodeScript;->of(I)Ljava/lang/Character$UnicodeScript;': {
                None: ['blocked'],
                'signature': 'Ljava/lang/Character$UnicodeScript;->of(I)Ljava/lang/Character$UnicodeScript;',
            },
            'Ljava/lang/Character;->serialVersionUID:J': {
                None: ['sdk'],
                'signature': 'Ljava/lang/Character;->serialVersionUID:J',
            },
            'Ljava/lang/Object;->hashCode()I': {
                None: ['public-api', 'system-api', 'test-api'],
                'signature': 'Ljava/lang/Object;->hashCode()I',
            },
            'Ljava/lang/Object;->toString()Ljava/lang/String;': {
                None: ['blocked'],
                'signature': 'Ljava/lang/Object;->toString()Ljava/lang/String;',
            },
            'Ljava/lang/ProcessBuilder$Redirect$1;-><init>()V': {
                None: ['blocked'],
                'signature': 'Ljava/lang/ProcessBuilder$Redirect$1;-><init>()V',
            },
        }
        self.assertEqual(expected, subset)

    def test_extract_subset_recursive_package(self):
        monolithic = self.read_flag_trie_from_string(TestDetectOverlaps.extractInput)

        patterns = 'java/**'

        subset = self.extract_subset_from_monolithic_flags_as_dict_from_string(monolithic, patterns)
        expected = {
            'Ljava/lang/Character$UnicodeScript;->of(I)Ljava/lang/Character$UnicodeScript;': {
                None: ['blocked'],
                'signature': 'Ljava/lang/Character$UnicodeScript;->of(I)Ljava/lang/Character$UnicodeScript;',
            },
            'Ljava/lang/Character;->serialVersionUID:J': {
                None: ['sdk'],
                'signature': 'Ljava/lang/Character;->serialVersionUID:J',
            },
            'Ljava/lang/Object;->hashCode()I': {
                None: ['public-api', 'system-api', 'test-api'],
                'signature': 'Ljava/lang/Object;->hashCode()I',
            },
            'Ljava/lang/Object;->toString()Ljava/lang/String;': {
                None: ['blocked'],
                'signature': 'Ljava/lang/Object;->toString()Ljava/lang/String;',
            },
            'Ljava/lang/ProcessBuilder$Redirect$1;-><init>()V': {
                None: ['blocked'],
                'signature': 'Ljava/lang/ProcessBuilder$Redirect$1;-><init>()V',
            },
            'Ljava/util/zip/ZipFile;-><clinit>()V': {
                None: ['blocked'],
                'signature': 'Ljava/util/zip/ZipFile;-><clinit>()V',
            },
        }
        self.assertEqual(expected, subset)

    def test_extract_subset_invalid_pattern_wildcard_and_member(self):
        monolithic = self.read_flag_trie_from_string(TestDetectOverlaps.extractInput)

        patterns = 'Ljava/lang/*;->hashCode()I'

        with self.assertRaises(Exception) as context:
            self.extract_subset_from_monolithic_flags_as_dict_from_string(monolithic, patterns)
        self.assertTrue("contains wildcard * and member signature hashCode()I" in str(context.exception))

    def test_read_trie_duplicate(self):
        with self.assertRaises(Exception) as context:
            self.read_flag_trie_from_string('''
Ljava/lang/Object;->hashCode()I,public-api,system-api,test-api
Ljava/lang/Object;->hashCode()I,blocked
''')
        self.assertTrue("Duplicate signature: Ljava/lang/Object;->hashCode()I" in str(context.exception))

    def test_read_trie_missing_member(self):
        with self.assertRaises(Exception) as context:
            self.read_flag_trie_from_string('''
Ljava/lang/Object,public-api,system-api,test-api
''')
        self.assertTrue("Invalid signature: Ljava/lang/Object, does not identify a specific member" in str(context.exception))

    def test_match(self):
        monolithic = self.read_signature_csv_from_string_as_dict('''
Ljava/lang/Object;->hashCode()I,public-api,system-api,test-api
''')
        modular = self.read_signature_csv_from_string_as_dict('''
Ljava/lang/Object;->hashCode()I,public-api,system-api,test-api
''')
        mismatches = compare_signature_flags(monolithic, modular)
        expected = []
        self.assertEqual(expected, mismatches)

    def test_mismatch_overlapping_flags(self):
        monolithic = self.read_signature_csv_from_string_as_dict('''
Ljava/lang/Object;->toString()Ljava/lang/String;,public-api
''')
        modular = self.read_signature_csv_from_string_as_dict('''
Ljava/lang/Object;->toString()Ljava/lang/String;,public-api,system-api,test-api
''')
        mismatches = compare_signature_flags(monolithic, modular)
        expected = [
            (
                'Ljava/lang/Object;->toString()Ljava/lang/String;',
                ['public-api', 'system-api', 'test-api'],
                ['public-api'],
            ),
        ]
        self.assertEqual(expected, mismatches)


    def test_mismatch_monolithic_blocked(self):
        monolithic = self.read_signature_csv_from_string_as_dict('''
Ljava/lang/Object;->toString()Ljava/lang/String;,blocked
''')
        modular = self.read_signature_csv_from_string_as_dict('''
Ljava/lang/Object;->toString()Ljava/lang/String;,public-api,system-api,test-api
''')
        mismatches = compare_signature_flags(monolithic, modular)
        expected = [
            (
                'Ljava/lang/Object;->toString()Ljava/lang/String;',
                ['public-api', 'system-api', 'test-api'],
                ['blocked'],
            ),
        ]
        self.assertEqual(expected, mismatches)

    def test_mismatch_modular_blocked(self):
        monolithic = self.read_signature_csv_from_string_as_dict('''
Ljava/lang/Object;->toString()Ljava/lang/String;,public-api,system-api,test-api
''')
        modular = self.read_signature_csv_from_string_as_dict('''
Ljava/lang/Object;->toString()Ljava/lang/String;,blocked
''')
        mismatches = compare_signature_flags(monolithic, modular)
        expected = [
            (
                'Ljava/lang/Object;->toString()Ljava/lang/String;',
                ['blocked'],
                ['public-api', 'system-api', 'test-api'],
            ),
        ]
        self.assertEqual(expected, mismatches)

    def test_missing_from_monolithic(self):
        monolithic = self.read_signature_csv_from_string_as_dict('')
        modular = self.read_signature_csv_from_string_as_dict('''
Ljava/lang/Object;->toString()Ljava/lang/String;,public-api,system-api,test-api
''')
        mismatches = compare_signature_flags(monolithic, modular)
        expected = [
            (
                'Ljava/lang/Object;->toString()Ljava/lang/String;',
                ['public-api', 'system-api', 'test-api'],
                [],
            ),
        ]
        self.assertEqual(expected, mismatches)

    def test_missing_from_modular(self):
        monolithic = self.read_signature_csv_from_string_as_dict('''
Ljava/lang/Object;->hashCode()I,public-api,system-api,test-api
''')
        modular = {}
        mismatches = compare_signature_flags(monolithic, modular)
        expected = [
            (
                'Ljava/lang/Object;->hashCode()I',
                [],
                ['public-api', 'system-api', 'test-api'],
            ),
        ]
        self.assertEqual(expected, mismatches)

    def test_blocked_missing_from_modular(self):
        monolithic = self.read_signature_csv_from_string_as_dict('''
Ljava/lang/Object;->hashCode()I,blocked
''')
        modular = {}
        mismatches = compare_signature_flags(monolithic, modular)
        expected = [
            (
                'Ljava/lang/Object;->hashCode()I',
                [],
                ['blocked'],
            ),
        ]
        self.assertEqual(expected, mismatches)

if __name__ == '__main__':
    unittest.main(verbosity=2)
