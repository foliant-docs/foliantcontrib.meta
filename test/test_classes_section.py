from unittest import TestCase
from unittest.mock import Mock

from foliant.meta.classes import Section, MetaHierarchyError


class TestAddChild(TestCase):
    def test_add_child_with_lower_level(self):
        parent = Section(level=1,
                         start=0,
                         end=100,
                         data={},
                         title="Parent Title")
        chapter = Mock()
        parent.chapter = chapter
        child = Section(level=3,
                        start=10,
                        end=90,
                        data={},
                        title="Child Title")
        parent.add_child(child)
        self.assertIn(child, parent.children)
        self.assertIs(parent.chapter, child.chapter)
        self.assertIs(child.parent, parent)

    def test_add_child_with_higher_level(self):
        parent = Section(level=2,
                         start=0,
                         end=100,
                         data={},
                         title="Parent Title")
        chapter = Mock()
        parent.chapter = chapter
        child = Section(level=1,
                        start=110,
                        end=190,
                        data={},
                        title="Child Title")
        with self.assertRaises(MetaHierarchyError):
            parent.add_child(child)
        self.assertNotIn(child, parent.children)
        self.assertIsNone(child.chapter)
        self.assertIsNone(child.parent)


class TestIsMain(TestCase):
    def test_should_be_main(self):
        section = Section(level=0,
                          start=0,
                          end=100,
                          data={},
                          title="Main Title")
        self.assertTrue(section.is_main)

    def test_should_not_be_main(self):
        section1 = Section(level=1,
                           start=0,
                           end=100,
                           data={},
                           title="Main Title")
        section2 = Section(level=0,
                           start=0,
                           end=100,
                           data={},
                           title="Main Title")
        section2.parent = section1

        self.assertFalse(section1.is_main())
        self.assertFalse(section2.is_main())


class TestToDict(TestCase):

    maxDiff = None

    def test_single(self):
        section = Section(level=0,
                          start=0,
                          end=100,
                          data={'field': 'value'},
                          title="Main Title")
        section.id = '1'
        expected = {
            'id': '1',
            'title': "Main Title",
            'level': 0,
            'data': {'field': 'value'},
            'start': 0,
            'end': 100,
            'children': []
        }
        self.assertEqual(section.to_dict(), expected)

    def test_with_children(self):
        parent = Section(level=0,
                         start=0,
                         end=200,
                         data={'field1': 'val1'},
                         title="Parent Title")
        child1 = Section(level=1,
                         start=110,
                         end=190,
                         data={'field2': 'val2'},
                         title="Child Title 1")
        child2 = Section(level=2,
                         start=150,
                         end=190,
                         data={'field3': 'val3'},
                         title="Child Title 2")
        parent.id = '1'
        child1.id = '2'
        child2.id = '3'

        parent.add_child(child1)
        child1.add_child(child2)
        expected = {
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
        self.assertEqual(parent.to_dict(), expected)


class TestIterChildren(TestCase):

    def test_no_children(self):
        parent = Section(level=0,
                         start=0,
                         end=200,
                         data={'field1': 'val1'},
                         title="Parent Title")
        i = parent.iter_children()
        with self.assertRaises(StopIteration):
            next(i)

    def test_with_children(self):
        parent = Section(level=0,
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
        parent.add_child(child1)
        parent.add_child(child2)
        parent.add_child(child3)
        child1.add_child(child11)
        child1.add_child(child12)

        children = [child1, child11, child12, child2, child3]
        for child in parent.iter_children():
            self.assertEqual(child, children.pop(0))
