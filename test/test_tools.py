from unittest import TestCase
from foliant.meta.tools import (get_meta_dict_from_yfm,
                                get_meta_dict_from_meta_tag,
                                get_header_content,
                                iter_chunks,
                                convert_to_id,
                                remove_meta)


class TestGetMetaDictFromYfm(TestCase):
    def test_yfm_present(self):
        source = '''---
field1: value1
field2: 2
field3:
    - li1
    - li2
field4:
    subfield1: subvalue
    subfield2: true
---

# First caption

content
'''
        expected = {'field1': 'value1',
                    'field2': 2,
                    'field3': ['li1', 'li2'],
                    'field4': {'subfield1': 'subvalue',
                               'subfield2': True}}
        self.assertEqual(get_meta_dict_from_yfm(source), expected)

    def test_yfm_with_comments(self):
        source = '''---
field1: value1
field2: 2
field3:  # this is important
    - li1
    - li2
#field31: commented
field4:
    subfield1: subvalue
    subfield2: true
---

# First caption

content
'''
        expected = {'field1': 'value1',
                    'field2': 2,
                    'field3': ['li1', 'li2'],
                    'field4': {'subfield1': 'subvalue',
                               'subfield2': True}}
        self.assertEqual(get_meta_dict_from_yfm(source), expected)

    def test_yfm_missing(self):
        source = '''# First caption

content
'''
        self.assertEqual(get_meta_dict_from_yfm(source), {})

    def test_yfm_incorrect(self):
        source = '''\n---\nfield: value\n---\n\n# First caption

content
'''
        self.assertEqual(get_meta_dict_from_yfm(source), {})


class TestGetMetaDictFromMetaTag(TestCase):
    def test_meta_tag_present(self):
        source = '''
Lorem ipsum dolor sit amet.

<meta field1="value1" field2="2" field3="['li1', 'li2']" field4="{subfield1: subvalue, subfield2: true}"></meta>

Lorem ipsum dolor sit amet, consectetur.
'''
        expected = {'field1': 'value1',
                    'field2': 2,
                    'field3': ['li1', 'li2'],
                    'field4': {'subfield1': 'subvalue',
                               'subfield2': True}}
        self.assertEqual(get_meta_dict_from_meta_tag(source), expected)

    def test_meta_tag_formatted(self):
        source = '''
Lorem ipsum dolor sit amet.

<meta
    field1="value1"
    field2="2"
    field3="
        - li1
        - li2"
    field4="
        subfield1: subvalue
        subfield2: true
    "
>
</meta>

Lorem ipsum dolor sit amet, consectetur.
'''
        expected = {'field1': 'value1',
                    'field2': 2,
                    'field3': ['li1', 'li2'],
                    'field4': {'subfield1': 'subvalue',
                               'subfield2': True}}
        self.assertEqual(get_meta_dict_from_meta_tag(source), expected)

    def test_no_options(self):
        source = '''
Lorem ipsum dolor sit amet.

<meta>Tag content is ignored</meta>

Lorem ipsum dolor sit amet, consectetur.
'''
        self.assertEqual(get_meta_dict_from_meta_tag(source), {})

    def test_meta_tag_missing(self):
        source = '''Lorem ipsum dolor sit amet.'''
        self.assertIsNone(get_meta_dict_from_meta_tag(source))

    def test_meta_tag_error(self):
        source = '''
Lorem ipsum dolor sit amet.

<meta field="value1"></mema>

Lorem ipsum dolor sit amet, consectetur.
'''
        self.assertIsNone(get_meta_dict_from_meta_tag(source))

    def test_two_meta_tags(self):
        source = '''
Lorem ipsum dolor sit amet.

<meta field1="value1" field2="value2"></meta>

Lorem ipsum dolor sit amet, consectetur.

<meta field1="newvalue1" field2="newvalue2"></meta>

Lorem ipsum dolor sit amet, consectetur.
'''
        expected = {'field1': 'value1', 'field2': 'value2'}
        self.assertEqual(get_meta_dict_from_meta_tag(source), expected)


class TestGetHeaderContent(TestCase):
    def test_header_present(self):
        source = '''---
field1: value1
field2: 2
field3:
    - li1
    - li2
field4:
    subfield1: subvalue
    subfield2: true
---

Header text

# First caption

content
'''
        expected = '''---
field1: value1
field2: 2
field3:
    - li1
    - li2
field4:
    subfield1: subvalue
    subfield2: true
---

Header text

'''
        self.assertEqual(get_header_content(source), expected)

    def test_only_yfm(self):
        source = '''---
field1: value1
#field2: 2
field3:
    - li1
    - li2
field4:
    subfield1: subvalue
    subfield2: true
---

# First caption

content
'''
        expected = '''---
field1: value1
#field2: 2
field3:
    - li1
    - li2
field4:
    subfield1: subvalue
    subfield2: true
---

'''
        self.assertEqual(get_header_content(source), expected)

    def test_meta_tag(self):
        source = '''
<meta field1="value1" field3="
    - li1
    - li2
"
field4="
    subfield1: subvalue
    subfield2: true
">
</meta>

Header content

# First caption

content
'''
        expected = '''
<meta field1="value1" field3="
    - li1
    - li2
"
field4="
    subfield1: subvalue
    subfield2: true
">
</meta>

Header content

'''
        self.assertEqual(get_header_content(source), expected)

    def test_no_header(self):
        source = '# First caption right away\n\Lorem ipsum dolor sit amet.'

        self.assertEqual(get_header_content(source), '')

    def test_no_headings(self):
        source = 'line1\n\nline2\n\nline3\n\nline4\n\nline5\n\nline6\n\n'

        self.assertEqual(get_header_content(source), source)


class TestIterChunks(TestCase):
    def test_three_chunks(self):
        header = '---\nfield: value\n---\n\n'
        titles = ['title1', 'title2', 'title3']
        content = '<meta field="value"></meta>\n\nLorem ipsum #dolor sit amet.\n\n#######Lorem ipsum dolor sit amet, consectetur adipisicing elit. Maiores, ex.'
        source = (f'{header}'  # 2 (YFM is cut out)
                  f'# {titles[0]}\n\n{content}\n\n'  # 150
                  f'## {titles[1]}\n\n{content}\n\n'  # 299
                  f'### {titles[2]}\n\n{content}\n\n')  # 449
        levels = [1, 2, 3]

        pos = [22, 170, 319, 469]
        starts = pos[:-1]
        ends = pos[1:]

        for title, level, c_content, start, end in iter_chunks(source):
            self.assertEqual(title, titles.pop(0))
            self.assertEqual(c_content, f'\n{content}\n\n')
            self.assertEqual(level, levels.pop(0))
            self.assertEqual(start, starts.pop(0))
            self.assertEqual(end, ends.pop(0))

    def test_comments_in_yfm(self):
        header = '---\nfield: value\n# field2: value2\n---\n\n'
        titles = ['title1', 'title2', 'title3']
        content = '<meta field="value"></meta>\n\nLorem ipsum #dolor sit amet.\n\n#######Lorem ipsum dolor sit amet, consectetur adipisicing elit. Maiores, ex.'
        source = (f'{header}'  # 2 (YFM is cut out)
                  f'# {titles[0]}\n\n{content}\n\n'  # 150
                  f'## {titles[1]}\n\n{content}\n\n'  # 299
                  f'### {titles[2]}\n\n{content}\n\n')  # 449
        levels = [1, 2, 3]

        pos = [39, 187, 336, 486]
        starts = pos[:-1]
        ends = pos[1:]

        for title, level, c_content, start, end in iter_chunks(source):
            self.assertEqual(title, titles.pop(0))
            self.assertEqual(c_content, f'\n{content}\n\n')
            self.assertEqual(level, levels.pop(0))
            self.assertEqual(start, starts.pop(0))
            self.assertEqual(end, ends.pop(0))

    def test_no_headings(self):
        source = 'Lorem ipsum dolor sit amet.\n\nConsectetur adipisicing elit.\n\nFugit impedit laborum, necessitatibus voluptatum minima sunt.'
        result = iter_chunks(source)
        with self.assertRaises(StopIteration):
            next(result)


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
        expected = '''# Title

Lorem ipsum dolor sit amet, consectetur adipisicing elit.
Earum mollitia voluptatum sequi cumque eos eaque!'''
        self.assertEqual(remove_meta(source), expected)
