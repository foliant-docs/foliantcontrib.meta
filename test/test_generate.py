from unittest import TestCase
from unittest.mock import Mock, patch
from foliant.meta.generate import (Chunk, fix_chunk_ends, get_section)


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
        with patch('foliant.meta.generate.get_meta_dict_from_yfm',
                   return_value=data_yfm),\
                patch('foliant.meta.generate.get_meta_dict_from_meta_tag',
                      return_value=data_tag):
            return get_section(chunk)

    def test_empty_header(self):
        data_yfm = {}
        data_tag = None
        level = 0
        chunk = Chunk(title='Title',
                      level=level,
                      content='',
                      start=0,
                      end=100)
        s = self.mock_gen_section(level, data_yfm, data_tag, chunk)
        self.assertEqual(s.data, data_yfm)
        self.assertEqual(chunk.title, s.title)
        self.assertEqual(chunk.level, s.level)
        self.assertEqual(chunk.start, s.start)
        self.assertEqual(chunk.end, s.end)

    def test_nonempty_header(self):
        data_yfm = {'field1': 'value1', 'field2': 2}
        data_tag = None
        level = 0
        s = self.mock_gen_section(level, data_yfm, data_tag)
        self.assertEqual(s.data, data_yfm)

    def test_header_with_tag(self):
        data_yfm = {}
        data_tag = {'field1': 'value1', 'field2': 2}
        level = 0
        s = self.mock_gen_section(level, data_yfm, data_tag)
        self.assertEqual(s.data, data_tag)

    def test_header_with_tag_and_yfm(self):
        data_yfm = {'field1': 'value1', 'field2': 2}
        data_tag = {'field3': 'value3', 'field4': 4}
        level = 0
        s = self.mock_gen_section(level, data_yfm, data_tag)
        self.assertEqual(s.data, data_tag)

    def test_section_with_meta(self):
        data_yfm = {}
        data_tag = {'field1': 'value1', 'field2': 2}
        level = 1
        chunk = Chunk(title='Title',
                      level=level,
                      content='',
                      start=0,
                      end=100)
        s = self.mock_gen_section(level, data_yfm, data_tag)
        self.assertEqual(s.data, data_tag)
        self.assertEqual(chunk.title, s.title)
        self.assertEqual(chunk.level, s.level)
        self.assertEqual(chunk.start, s.start)
        self.assertEqual(chunk.end, s.end)

    def test_section_with_empty_meta(self):
        data_yfm = {'ignored': 'ignored'}
        data_tag = {}
        level = 2
        chunk = Chunk(title='Title',
                      level=level,
                      content='',
                      start=0,
                      end=100)
        s = self.mock_gen_section(level, data_yfm, data_tag)
        self.assertEqual(s.data, data_tag)
        self.assertEqual(chunk.title, s.title)
        self.assertEqual(chunk.level, s.level)
        self.assertEqual(chunk.start, s.start)
        self.assertEqual(chunk.end, s.end)

    def test_section_without_meta(self):
        data_yfm = {}
        data_tag = None
        level = 3
        s = self.mock_gen_section(level, data_yfm, data_tag)
        self.assertIsNone(s)
