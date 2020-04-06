from unittest import TestCase

from foliant.meta.classes import Section, Chapter
from foliant.meta.generate import get_meta_for_chapter
from .utils import get_test_data_text, TEST_DATA_PATH


class TestMainSection(TestCase):
    def test_set_main_section(self):
        section = Section(level=0,
                          start=0,
                          end=100,
                          data={'id': 'id1'},
                          title='title1')
        chapter = Chapter(filename='filename',
                          name='chapter_name')
        chapter.main_section = section
        self.assertIs(section.chapter, chapter)
        self.assertIs(chapter.main_section, section)

    def test_autoset_title(self):
        section = Section(level=0,
                          start=0,
                          end=100,
                          data={'id': 'id1'},
                          title='')
        chapter = Chapter(filename='filename',
                          name='chapter_name')
        chapter.main_section = section
        self.assertEqual(section.title, chapter.name)

    def test_set_children_chapter(self):
        main_section = Section(level=0,
                         start=0,
                         end=200,
                         data={'field1': 'val1'},
                         title="Parent Title")
        child1 = Section(level=1,
                         start=110,
                         end=140,
                         data={'field2': 'val2'},
                         title="Child Title 1")
        child11 = Section(level=2,
                          start=120,
                          end=130,
                          data={'field2': 'val2'},
                          title="Child Title 11")
        child12 = Section(level=2,
                          start=130,
                          end=140,
                          data={'field2': 'val2'},
                          title="Child Title 12")
        child2 = Section(level=1,
                         start=140,
                         end=150,
                         data={'field2': 'val2'},
                         title="Child Title 2")
        child3 = Section(level=1,
                         start=150,
                         end=160,
                         data={'field2': 'val2'},
                         title="Child Title 3")
        main_section.add_child(child1)
        main_section.add_child(child2)
        main_section.add_child(child3)
        child1.add_child(child11)
        child1.add_child(child12)
        chapter = Chapter('some/filename.md', 'name', main_section)
        for child in chapter.iter_sections():
            self.assertEqual(child.chapter, chapter)


class TestGetSectionByOffset(TestCase):
    def test_no_meta(self):
        chapter = get_meta_for_chapter(TEST_DATA_PATH / 'load_meta/chapter_without_meta.md')
        offsets = [0, 500, 900, 2391]
        main_section = chapter.main_section
        for offset in offsets:
            self.assertEqual(chapter.get_section_by_offset(offset), main_section)

    def test_out_of_range(self):
        chapter = get_meta_for_chapter(TEST_DATA_PATH / 'load_meta/chapter_without_meta.md')
        with self.assertRaises(IndexError):
            chapter.get_section_by_offset(100000)

    def test_with_meta(self):
        chapter = get_meta_for_chapter(TEST_DATA_PATH / 'load_meta/chapter_with_one_meta_tag.md')
        offsets = [100, 500, 1100]
        main_section = chapter.main_section
        section = main_section.children[0]
        self.assertEqual(chapter.get_section_by_offset(offsets.pop(0)), main_section)
        self.assertEqual(chapter.get_section_by_offset(offsets.pop(0)), section)
        self.assertEqual(chapter.get_section_by_offset(offsets.pop(0)), section)

    def test_offset_in_heading(self):
        chapter = get_meta_for_chapter(TEST_DATA_PATH / 'load_meta/chapter_with_one_meta_tag.md')
        offsets = [
            470,  # beginning of heading
            471,  # between ##
            477,  # inside heading
            487   # end of heading
        ]
        main_section = chapter.main_section
        section = main_section.children[0]
        self.assertEqual(chapter.get_section_by_offset(offsets.pop(0)), section)
        self.assertEqual(chapter.get_section_by_offset(offsets.pop(0)), section)
        self.assertEqual(chapter.get_section_by_offset(offsets.pop(0)), section)
        self.assertEqual(chapter.get_section_by_offset(offsets.pop(0)), section)

    def test_yfm_and_meta(self):
        chapter = get_meta_for_chapter(TEST_DATA_PATH / 'load_meta/chapter_with_meta.md')
        offsets = [
            25,    # main section YFM
            75,    # main section header
            190,   # main section first heading
            325,   # first section heading
            450,   # first section
            1000,  # second section
            1500,  # main section again
        ]

        main_section = chapter.main_section
        section1 = main_section.children[0]
        section2 = section1.children[0]

        self.assertEqual(chapter.get_section_by_offset(offsets.pop(0)), main_section)
        self.assertEqual(chapter.get_section_by_offset(offsets.pop(0)), main_section)
        self.assertEqual(chapter.get_section_by_offset(offsets.pop(0)), main_section)
        self.assertEqual(chapter.get_section_by_offset(offsets.pop(0)), section1)
        self.assertEqual(chapter.get_section_by_offset(offsets.pop(0)), section1)
        self.assertEqual(chapter.get_section_by_offset(offsets.pop(0)), section2)
        self.assertEqual(chapter.get_section_by_offset(offsets.pop(0)), main_section)


class TestIterSections(TestCase):

    def test_only_main(self):
        main_section = Section(level=0,
                               start=0,
                               end=200,
                               data={'field1': 'val1'},
                               title="Parent Title")
        chapter = Chapter('some/filename.md', 'name', main_section)
        i = chapter.iter_sections()
        self.assertEqual(next(i), main_section)
        with self.assertRaises(StopIteration):
            next(i)

    def test_with_children(self):
        main_section = Section(level=0,
                         start=0,
                         end=200,
                         data={'field1': 'val1'},
                         title="Parent Title")
        chapter = Chapter('some/filename.md', 'name', main_section)
        child1 = Section(level=1,
                         start=110,
                         end=140,
                         data={'field2': 'val2'},
                         title="Child Title 1")
        child11 = Section(level=2,
                          start=120,
                          end=130,
                          data={'field2': 'val2'},
                          title="Child Title 11")
        child12 = Section(level=2,
                          start=130,
                          end=140,
                          data={'field2': 'val2'},
                          title="Child Title 12")
        child2 = Section(level=1,
                         start=140,
                         end=150,
                         data={'field2': 'val2'},
                         title="Child Title 2")
        child3 = Section(level=1,
                         start=150,
                         end=160,
                         data={'field2': 'val2'},
                         title="Child Title 3")
        main_section.add_child(child1)
        main_section.add_child(child2)
        main_section.add_child(child3)
        child1.add_child(child11)
        child1.add_child(child12)

        sections = [main_section, child1, child11, child12, child2, child3]
        for section in chapter.iter_sections():
            self.assertEqual(section, sections.pop(0))


class TestToDict(TestCase):

    maxDiff = None

    def test_single_section(self):
        main_section = Section(level=0,
                               start=0,
                               end=100,
                               data={'field': 'value'},
                               title="Main Title")
        main_section.id = '1'
        chapter = Chapter('some/filename.md', 'name', main_section)
        expected = {
            'name': 'name',
            'filename': 'some/filename.md',
            'section': {
                'id': '1',
                'title': "Main Title",
                'level': 0,
                'data': {'field': 'value'},
                'start': 0,
                'end': 100,
                'children': []
            }
        }
        self.assertEqual(chapter.to_dict(), expected)

    def test_with_children(self):
        main_section = Section(level=0,
                         start=0,
                         end=200,
                         data={'field1': 'val1'},
                         title="Parent Title")
        child1 = Section(level=1,
                         start=110,
                         end=190,
                         data={'field2': 'val2'},
                         title="Child Title 1",)
        child2 = Section(level=2,
                         start=150,
                         end=190,
                         data={'field3': 'val3'},
                         title="Child Title 2")
        main_section.id = '1'
        child1.id = '2'
        child2.id = '3'

        main_section.add_child(child1)
        child1.add_child(child2)
        chapter = Chapter('some/filename.md', 'name', main_section)

        expected = {
            'name': 'name',
            'filename': 'some/filename.md',
            'section': {
                'id': '1',
                'title': "Parent Title",
                'level': 0,
                'data': {'field1': 'val1'},
                'start': 0,
                'end': 200,
                'children': [
                    {
                        'id': '2',
                        'title': "Child Title 1",
                        'level': 1,
                        'data': {'field2': 'val2'},
                        'start': 110,
                        'end': 190,
                        'children': [
                            {
                                'id': '3',
                                'title': "Child Title 2",
                                'level': 2,
                                'data': {'field3': 'val3'},
                                'start': 150,
                                'end': 190,
                                'children': []
                            }
                        ]
                    }
                ]
            }
        }
        self.assertEqual(chapter.to_dict(), expected)
