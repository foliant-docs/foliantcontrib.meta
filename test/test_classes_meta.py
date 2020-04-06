import yaml
from unittest import TestCase
from unittest.mock import patch, mock_open

from foliant.meta.classes import (Section, Chapter, Meta,
                                  MetaDublicateIDError)


class TestLoadMetaFromFile(TestCase):
    def test_load_sample_file(self):
        source = {
            'version': '1.0',
            'chapters': [{
                'name': 'index',
                'filename': 'src/index.md',
                'section': {
                    'id': 'main_descr',
                    'title': 'index',
                    'level': 0,
                    'data': {
                        'conf': True,
                        'id': 'main_descr',
                        'type': 'main',
                        'relates': ['glossary.md']
                    },
                    'start': 0,
                    'end': 4655,
                    'children': [{
                        'id': 'comps_descr',
                        'title': 'Components description',
                        'level': 1,
                        'data': {
                            'conf': True,
                            'id': 'comps_descr',
                            'relates': ['main_descr']
                        },
                        'start': 1224,
                        'end': 4267,
                        'children': []
                    }]
                }
            }, {
                'name': 'glossary',
                'filename': 'src/glossary.md',
                'section': {
                    'id': 'glossary',
                    'title': 'glossary',
                    'level': 0,
                    'data': {},
                    'start': 0,
                    'end': 446,
                    'children': []
                }
            }]
        }
        meta = Meta()
        with patch('builtins.open', mock_open(read_data=yaml.dump(source))):
            meta.load_meta_from_file('mocked')
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
