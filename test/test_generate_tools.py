from unittest import TestCase
from foliant.meta_commands.generate.tools import (get_meta_dict_from_yfm,
                                                  get_meta_dict_from_meta_tag,
                                                  get_header_content,
                                                  iter_chunks)


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

    def test_yfm_missing(self):
        source = '''# First caption

content
'''
        self.assertEqual(get_meta_dict_from_yfm(source), {})


class TestGetMetaDictFromMetaTag(TestCase):
    def test_meta_tag_present(self):
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
        subfield2: true">
</meta>

Lorem ipsum dolor sit amet, consectetur.
'''
        expected = {'field1': 'value1',
                    'field2': 2,
                    'field3': ['li1', 'li2'],
                    'field4': {'subfield1': 'subvalue',
                               'subfield2': True}}
        self.assertEqual(get_meta_dict_from_meta_tag(source), expected)

    def test_meta_tag_missing(self):
        source = '''Lorem ipsum dolor sit amet.'''
        self.assertIsNone(get_meta_dict_from_meta_tag(source))

    def test_no_options(self):
        source = '''
Lorem ipsum dolor sit amet.

<meta>Tag content is ignored</meta>

Lorem ipsum dolor sit amet, consectetur.
'''
        self.assertEqual(get_meta_dict_from_meta_tag(source), {})


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
        content = '<meta field="value"></meta>\n\nLorem ipsum dolor sit amet.\n\nLorem ipsum dolor sit amet, consectetur adipisicing elit. Maiores, ex.'
        source = (f'{header}'  # 22
                  f'# {titles[0]}\n\n{content}\n\n'  # 162
                  f'## {titles[1]}\n\n{content}\n\n'  # 303
                  f'### {titles[2]}\n\n{content}\n\n')  # 445
        levels = [1, 2, 3]

        pos = [22, 162, 303, 445]
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
