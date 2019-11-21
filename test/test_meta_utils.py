from unittest import TestCase
from foliant.cli.meta.utils import convert_to_id, remove_meta


class TestConvertToId(TestCase):
    def test_spaces(self):
        labels = ['nochange', 'Capital', 'Capital Space', 'trailing ', ' preceding']
        expected_list = ['nochange', 'capital', 'capital-space', 'trailing', 'preceding']
        for label, expected in zip(labels, expected_list):
            self.assertEqual(convert_to_id(label, []), expected)

    def test_symbols(self):
        labels = ['under_score',
                  'Hy-phen',
                  'Braces (aka parenthesis)',
                  '/slashes/slashes/',
                  'Also, with numbers: 19']
        expected_list = ['under_score',
                         'hy-phen',
                         'braces-aka-parenthesis',
                         'slashes-slashes',
                         'also-with-numbers-19']
        for label, expected in zip(labels, expected_list):
            self.assertEqual(convert_to_id(label, []), expected)

    def test_existing_ids(self):
        existing = ['existing-id', 'existing-2', 'number-1']
        labels = ['existing-id', 'existing', 'existing', 'Number 1']
        expected_list = ['existing-id-2', 'existing', 'existing-3', 'number-1-2']
        for label, expected in zip(labels, expected_list):
            self.assertEqual(convert_to_id(label, existing), expected)

        for added in expected_list:
            self.assertIn(added, existing)


class TestRemoveMeta(TestCase):
    def test_no_meta(self):
        source = ('# Title\n\nLorem ipsum dolor sit amet.\n Lorem ipsum dolor sit amet,'
                  'consectetur adipisicing elit.\n\nNatus laboriosam animi ipsam'
                  'molestias doloremque voluptatum.')
        self.assertEqual(remove_meta(source), source)

    def test_tag(self):
        source = '''# Title

<meta
    id="id1"
    field1="value1">
</meta>

Lorem ipsum dolor sit amet, consectetur adipisicing elit.
Earum mollitia voluptatum sequi cumque eos eaque!

## Subtitle

<meta></meta>

Lorem ipsum dolor sit amet, consectetur adipisicing elit.
Veniam, reiciendis facilis distinctio illo possimus libero.'''
        expected = '''# Title



Lorem ipsum dolor sit amet, consectetur adipisicing elit.
Earum mollitia voluptatum sequi cumque eos eaque!

## Subtitle



Lorem ipsum dolor sit amet, consectetur adipisicing elit.
Veniam, reiciendis facilis distinctio illo possimus libero.'''
        self.assertEqual(remove_meta(source), expected)

    def test_yfm(self):
        source = '''---
id: id1
field1: value1
---

# Title

Lorem ipsum dolor sit amet, consectetur adipisicing elit.
Earum mollitia voluptatum sequi cumque eos eaque!'''
        expected = '''

# Title

Lorem ipsum dolor sit amet, consectetur adipisicing elit.
Earum mollitia voluptatum sequi cumque eos eaque!'''
        self.assertEqual(remove_meta(source), expected)
