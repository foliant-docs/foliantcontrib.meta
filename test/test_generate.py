import yaml
from unittest import TestCase
from unittest.mock import Mock, patch
from pathlib import Path

from foliant.meta.generate import (Chunk, fix_chunk_ends, get_section,
                                   split_by_headings, get_meta_for_chapter,
                                   load_meta)

from .utils import get_test_data_text, TEST_DATA_PATH


class TestFixChunkEnds(TestCase):
    def test_no_need_to_fix(self):
        levels = [1, 1, 1, 1, 1]
        pos = [0, 100, 200, 300, 400, 500]
        starts = pos[:-1]
        ends = pos[1:]

        expected_starts = starts
        expected_ends = ends
        chunks = [Chunk(title='',
                        level=level,
                        content='',
                        start=start,
                        end=end) for level, start, end in zip(levels,
                                                              starts,
                                                              ends)]
        fix_chunk_ends(chunks)
        for chunk, start, end in zip(chunks, expected_starts, expected_ends):
            self.assertEqual((chunk.start, chunk.end), (start, end))

    def test_need_to_fix(self):
        levels = [1,   2,   3,   1,   2,   1]
        pos = [0, 100, 200, 300, 400, 500, 600]
        starts = pos[:-1]
        ends = pos[1:]

        expected_starts = starts
        expected_ends = [300, 300, 300, 500, 500, 600]
        chunks = [Chunk(title='',
                        level=level,
                        content='',
                        start=start,
                        end=end) for level, start, end in zip(levels,
                                                              starts,
                                                              ends)]
        fix_chunk_ends(chunks)
        for chunk, start, end in zip(chunks, expected_starts, expected_ends):
            self.assertEqual((chunk.start, chunk.end), (start, end))


class TestSplitByHeadings(TestCase):
    def test_split_by_headings(self):
        source = get_test_data_text('split_by_headings.md')

        titles = [
            'First heading',
            'Second heading',
            'Third heading',
            'Fourth heading',
            'Fifth heading'
        ]
        levels = [1,     2,   3,   1,     2]
        starts = [40,   303, 568, 833,  1097]
        ends =   [833, 833, 833, 1361, 1361]
        expected_header_content = '---\nfield: value\n#commented: field\n---\n\n'
        expected_chunk_content = '''
<meta field="value"></meta>

Lorem ipsum dolor sit amet, consectetur adipisicing elit. Dolorem maxime animi laborum laboriosam in aliquid id dicta alias, voluptas. Facere voluptates ducimus aliquam. Asperiores atque amet error eius cumque. Nam.\n\n'''
        header, chunks = split_by_headings(source)
        self.assertEqual(header.title, '')
        self.assertEqual(header.level, 0)
        self.assertEqual(header.content, expected_header_content)
        self.assertEqual(header.start, 0)
        self.assertEqual(header.end, 1361)

        for chunk in chunks:
            expected_title = titles.pop(0)
            expected_level = levels.pop(0)
            expected_start = starts.pop(0)
            expected_end = ends.pop(0)
            self.assertEqual(chunk.title, expected_title)
            self.assertEqual(chunk.level, expected_level)
            self.assertEqual(chunk.start, expected_start)
            self.assertEqual(chunk.end, expected_end)
            self.assertEqual(chunk.content, expected_chunk_content)


class TestGetSection(TestCase):
    def mock_gen_section(self, level, data_yfm, data_tag, chunk_ext=None):
        if chunk_ext is not None:
            chunk = chunk_ext
        else:
            chunk = Chunk(title='Title',
                          level=level,
                          content='',
                          start=0,
                          end=100)
        with patch(
            'foliant.meta.generate.get_meta_dict_from_yfm',
            return_value=data_yfm
        ) as mock_yfm, patch(
            'foliant.meta.generate.get_meta_dict_from_meta_tag',
            return_value=data_tag
        ) as mock_tag:
            section = get_section(chunk)
            return section, mock_yfm, mock_tag

    def test_main_empty_header(self):
        data_yfm = {}
        data_tag = None
        level = 0
        chunk = Chunk(title='Title',
                      level=level,
                      content='',
                      start=0,
                      end=100)
        s, mock_yfm, mock_tag = self.mock_gen_section(level, data_yfm, data_tag, chunk)
        self.assertEqual(s.data, data_yfm)
        self.assertEqual(chunk.title, s.title)
        self.assertEqual(chunk.level, s.level)
        self.assertEqual(chunk.start, s.start)
        self.assertEqual(chunk.end, s.end)
        self.assertTrue(mock_yfm.called)
        self.assertTrue(mock_tag.called)

    def test_main_nonempty_header(self):
        data_yfm = {'field1': 'value1', 'field2': 2}
        data_tag = None
        level = 0
        s, mock_yfm, mock_tag = self.mock_gen_section(level, data_yfm, data_tag)
        self.assertEqual(s.data, data_yfm)
        self.assertTrue(mock_yfm.called)
        self.assertTrue(mock_tag.called)

    def test_main_header_with_tag(self):
        data_yfm = {}
        data_tag = {'field1': 'value1', 'field2': 2}
        level = 0
        s, mock_yfm, mock_tag = self.mock_gen_section(level, data_yfm, data_tag)
        self.assertEqual(s.data, data_tag)
        self.assertTrue(mock_yfm.called)
        self.assertTrue(mock_tag.called)

    def test_main_header_with_tag_and_yfm(self):
        data_yfm = {'field1': 'value1', 'field2': 2}
        data_tag = {'field3': 'value3', 'field4': 4}
        level = 0
        s, mock_yfm, mock_tag = self.mock_gen_section(level, data_yfm, data_tag)
        self.assertEqual(s.data, data_tag)
        self.assertTrue(mock_yfm.called)
        self.assertTrue(mock_tag.called)

    def test_section_with_meta(self):
        data_yfm = {'ignored': 'ignored'}
        data_tag = {'field1': 'value1', 'field2': 2}
        level = 1
        chunk = Chunk(title='Title',
                      level=level,
                      content='',
                      start=0,
                      end=100)
        s, mock_yfm, mock_tag = self.mock_gen_section(level, data_yfm, data_tag)
        self.assertEqual(s.data, data_tag)
        self.assertEqual(chunk.title, s.title)
        self.assertEqual(chunk.level, s.level)
        self.assertEqual(chunk.start, s.start)
        self.assertEqual(chunk.end, s.end)
        self.assertFalse(mock_yfm.called)
        self.assertTrue(mock_tag.called)

    def test_section_with_customid(self):
        data_yfm = {'ignored': 'ignored'}
        data_tag = {'field1': 'value1', 'field2': 2}
        level = 1
        chunk = Chunk(title='Title {#title}',
                      level=level,
                      content='',
                      start=0,
                      end=100)
        s, mock_yfm, mock_tag = self.mock_gen_section(level, data_yfm, data_tag)
        self.assertEqual(s.data, data_tag)
        self.assertEqual('Title', s.title)
        self.assertEqual(chunk.level, s.level)
        self.assertEqual(chunk.start, s.start)
        self.assertEqual(chunk.end, s.end)
        self.assertFalse(mock_yfm.called)
        self.assertTrue(mock_tag.called)

    def test_section_with_empty_meta(self):
        data_yfm = {'ignored': 'ignored'}
        data_tag = {}
        level = 2
        chunk = Chunk(title='Title',
                      level=level,
                      content='',
                      start=0,
                      end=100)
        s, mock_yfm, mock_tag = self.mock_gen_section(level, data_yfm, data_tag)
        self.assertEqual(s.data, data_tag)
        self.assertEqual(chunk.title, s.title)
        self.assertEqual(chunk.level, s.level)
        self.assertEqual(chunk.start, s.start)
        self.assertEqual(chunk.end, s.end)
        self.assertFalse(mock_yfm.called)
        self.assertTrue(mock_tag.called)

    def test_section_without_meta(self):
        data_yfm = {'ignored': 'ignored'}
        data_tag = None
        level = 3
        s, mock_yfm, mock_tag = self.mock_gen_section(level, data_yfm, data_tag)
        self.assertIsNone(s)
        self.assertFalse(mock_yfm.called)
        self.assertTrue(mock_tag.called)


class TestGetMetaForChapter(TestCase):
    def test_nonexisting_file(self):
        path = Path('some_nonexistant_path.exe')
        self.assertFalse(path.exists())
        self.assertIsNone(get_meta_for_chapter(path))

    def test_chapter(self):
        ch_path = TEST_DATA_PATH / 'chapter.md'
        ch_name = 'Chapter name'
        chapter = get_meta_for_chapter(ch_path, ch_name)
        expected_main_section_data = {
            'field1': 'value1',
            'field2': ['li1', 'li2'],
            'field3': True
        }
        expected_child1_data = {'field1': 'val1'}
        expected_child2_data = {
            'field1': {'key1': 'val1', 'key2': 'val2'},
            'field2': ['li1', 'li2', 'li3']
        }

        self.assertEqual(chapter.filename, str(ch_path))
        main_section = chapter.main_section
        self.assertEqual(main_section.data, expected_main_section_data)
        self.assertEqual(len(main_section.children), 1)
        child1 = main_section.children[0]
        self.assertEqual(child1.data, expected_child1_data)
        self.assertEqual(len(child1.children), 1)
        child2 = child1.children[0]
        self.assertEqual(child2.data, expected_child2_data)
        self.assertEqual(len(child2.children), 0)

    def test_chapter_name(self):
        ch_path = TEST_DATA_PATH / 'chapter.md'
        ch_name = 'Chapter name'
        chapter = get_meta_for_chapter(ch_path, ch_name)

        self.assertEqual(chapter.name, ch_name)
        chapter_no_name = get_meta_for_chapter(ch_path)
        self.assertEqual(chapter_no_name.name, str(ch_path))

    def test_main_section_title(self):
        ch_path = TEST_DATA_PATH / 'chapter.md'
        chapter = get_meta_for_chapter(ch_path)
        main_section = chapter.main_section
        self.assertEqual(main_section.title, 'First heading')

    def test_empty_chapter(self):
        ch_path = TEST_DATA_PATH / 'empty_chapter.md'
        chapter = get_meta_for_chapter(ch_path)
        main_section = chapter.main_section
        self.assertEqual(main_section.data, {})
        self.assertEqual(len(main_section.children), 0)

    def test_chapter_only_yfm(self):
        ch_path = TEST_DATA_PATH / 'chapter_only_yfm.md'
        expected_data = {'field1': 'value1', 'field2': True}

        chapter = get_meta_for_chapter(ch_path)
        main_section = chapter.main_section
        self.assertEqual(main_section.data, expected_data)
        self.assertEqual(len(main_section.children), 0)

    def test_chapter_only_meta_tag(self):
        ch_path = TEST_DATA_PATH / 'chapter_only_meta_tag.md'
        expected_data = {'field1': 'value1', 'field2': True}

        chapter = get_meta_for_chapter(ch_path)
        main_section = chapter.main_section
        self.assertEqual(main_section.data, expected_data)
        self.assertEqual(len(main_section.children), 0)


class TestLoadMeta(TestCase):
    maxDiff = None

    def test_folder(self):
        md_root = 'test/test_data/load_meta'
        chapters = [
            'chapter_only_yfm.md',
            'chapter_with_meta.md',
            'chapter_with_one_meta_tag.md',
            'chapter_without_meta.md'
        ]
        with open('test/test_data/load_meta.yml') as f:
            expected = yaml.load(f, yaml.Loader)
        meta = load_meta(chapters, md_root)
        self.assertEqual(meta.dump(), expected)
