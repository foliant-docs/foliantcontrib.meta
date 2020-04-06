import yaml
from unittest import TestCase
from unittest.mock import patch, mock_open

from foliant.meta.classes import (Section, Chapter, Meta, MetaDublicateIDError,
                                  MetaChapterDoesNotExistError,
                                  MetaSectionDoesNotExistError)
from foliant.meta.generate import load_meta
from .utils import TEST_DATA_PATH


class TestLoadMetaFromFile(TestCase):
    maxDiff = None

    def test_load_sample_file1(self):
        meta = Meta()
        with open(TEST_DATA_PATH / 'meta1.yml', encoding='utf8') as f:
            source = yaml.load(f, yaml.Loader)
        meta.load_meta_from_file(TEST_DATA_PATH / 'meta1.yml')
        self.assertEqual(meta.dump(), source)

    def test_load_sample_file2(self):
        meta = Meta()
        with open(TEST_DATA_PATH / 'meta2.yml', encoding='utf8') as f:
            source = yaml.load(f, yaml.Loader)
        meta.load_meta_from_file(TEST_DATA_PATH / 'meta2.yml')
        self.assertEqual(meta.dump(), source)

    def test_load_sample_file3(self):
        meta = Meta()
        with open(TEST_DATA_PATH / 'meta3.yml', encoding='utf8') as f:
            source = yaml.load(f, yaml.Loader)
        meta.load_meta_from_file(TEST_DATA_PATH / 'meta3.yml')
        self.assertEqual(meta.dump(), source)


class TestProcessIds(TestCase):
    def test_load_sample_file(self):
        section1 = Section(level=0,
                           start=0,
                           end=100,
                           data={'id': 'id1'},
                           title='title1')
        section2 = Section(level=1,
                           start=10,
                           end=100,
                           data={'id': 'id2'},
                           title='title2')
        chapter1 = Chapter(filename='filename',
                           name='chapter_name',
                           main_section=None)
        section1.add_child(section2)
        chapter1.main_section = section1

        section3 = Section(level=0,
                           start=0,
                           end=100,
                           data={'id': 'id3'},
                           title='title3')
        section4 = Section(level=1,
                           start=10,
                           end=100,
                           data={'id': 'id4'},
                           title='title4')
        chapter2 = Chapter(filename='filename2',
                           name='chapter_name2',
                           main_section=None)
        section3.add_child(section4)
        chapter2.main_section = section3

        meta = Meta()
        meta.add_chapter(chapter1)
        meta.add_chapter(chapter2)

        expected_ids = ['id1', 'id2', 'id3', 'id4']

        meta.process_ids()
        for section, expected_id in zip(meta.iter_sections(), expected_ids):
            self.assertEqual(section.id, expected_id)

    def test_dublicate_ids(self):
        section1 = Section(level=0,
                           start=0,
                           end=100,
                           data={'id': 'id1'},
                           title='title1')
        section2 = Section(level=1,
                           start=10,
                           end=100,
                           data={'id': 'id1'},
                           title='title2')
        chapter1 = Chapter(filename='filename',
                           name='chapter_name',
                           main_section=None)
        section1.add_child(section2)
        chapter1.main_section = section1

        meta = Meta()
        meta.add_chapter(chapter1)

        with self.assertRaises(MetaDublicateIDError):
            meta.process_ids()

    def test_generate_ids(self):
        section1 = Section(level=0,
                           start=0,
                           end=100,
                           data={'id': 'id1'},
                           title='title1')
        section2 = Section(level=1,
                           start=10,
                           end=100,
                           data={},
                           title='My Section Title (78)')
        chapter1 = Chapter(filename='filename',
                           name='chapter_name',
                           main_section=None)
        section1.add_child(section2)
        chapter1.main_section = section1

        section3 = Section(level=0,
                           start=0,
                           end=100,
                           data={'id': 'original'},
                           title='title3')
        section4 = Section(level=1,
                           start=10,
                           end=100,
                           data={},
                           title='original')
        chapter2 = Chapter(filename='filename2',
                           name='chapter_name2',
                           main_section=None)
        section3.add_child(section4)
        chapter2.main_section = section3

        meta = Meta()
        meta.add_chapter(chapter1)
        meta.add_chapter(chapter2)

        expected_ids = ['id1', 'my-section-title-78', 'original', 'original-2']

        meta.process_ids()
        for section, expected_id in zip(meta.iter_sections(), expected_ids):
            self.assertEqual(section.id, expected_id)


class TestGetChapter(TestCase):
    def setUp(self):
        md_root = 'test/test_data/load_meta'
        chapters = [
            'chapter_only_yfm.md',
            'chapter_with_meta.md',
            'chapter_with_one_meta_tag.md',
            'chapter_without_meta.md'
        ]
        self.meta = load_meta(chapters, md_root)

    def test_wrong_chapter(self):
        with self.assertRaises(MetaChapterDoesNotExistError):
            self.meta.get_chapter('wrong/chapter/path')

    def test_relative_path(self):
        filename = 'test/test_data/load_meta/chapter_with_meta.md'
        chapter = self.meta.get_chapter(filename)
        self.assertTrue(chapter.filename.endswith('chapter_with_meta.md'))

    def test_absolute_path(self):
        filename = TEST_DATA_PATH / 'load_meta/chapter_with_meta.md'
        chapter = self.meta.get_chapter(filename)
        self.assertTrue(chapter.filename.endswith('chapter_with_meta.md'))


class TestGetByID(TestCase):
    def test_id_exists(self):
        meta = Meta()
        meta.load_meta_from_file(TEST_DATA_PATH / 'meta3.yml')
        id_ = 'subsection'
        section = meta.get_by_id(id_)
        self.assertEqual(section.id, id_)

    def test_id_doesnt_exist(self):
        meta = Meta()
        meta.load_meta_from_file(TEST_DATA_PATH / 'meta3.yml')
        id_ = 'nonexistant_id'
        with self.assertRaises(MetaSectionDoesNotExistError):
            section = meta.get_by_id(id_)
