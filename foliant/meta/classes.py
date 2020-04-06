'''Module defining Meta class'''

from __future__ import annotations
import yaml

from schema import Schema, Optional
from pathlib import Path, PosixPath

from .tools import convert_to_id, remove_meta


SECTION_SCHEMA = Schema(
    {
        'title': str,
        'start': int,
        'end': int,
        'level': int,
        'id': str,
        Optional('children', default=[]): [dict],
        Optional('data', default={}): dict
    }
)

META_SCHEMA = Schema(
    {
        'version': str,
        'chapters': [
            {
                'name': str,
                'section': SECTION_SCHEMA,
                'filename': str
            }
        ]
    }
)


class MetaHierarchyError(Exception):
    pass


class MetaDublicateIDError(Exception):
    pass


class MetaSectionDoesNotExistError(Exception):
    pass


class MetaChapterNotAssignedError(Exception):
    pass


class MetaChapterDoesNotExistError(Exception):
    pass


class Meta:
    syntax_version = '1.0'

    def __init__(self):
        self.chapters = []
        self.filename = None

    def load_meta_from_file(self, filename: str or PosixPath):
        '''
        Load metadata from yaml-file into the Chapter and Section objects and
        save them into the attributes of this Meta object instance.

        :param filename: the name of the yaml-file with metadata.
        '''
        def load_section(section_dict: dict) -> Section:
            '''
            Create a section from the dictionary with its data, recursively
            creating all the child sections and connecting them together.

            :param section_dict: dictionary with section data, loaded from meta yaml

            :returns: a constructed Section object
            '''
            data = SECTION_SCHEMA.validate(section_dict)
            section = Section(level=data['level'],
                              start=data['start'],
                              end=data['end'],
                              data=data['data'],
                              title=data['title'])
            for child in data['children']:
                section.add_child(load_section(child))
            return section

        self.filename = Path(filename)

        with open(filename) as f:
            unchecked_data = yaml.load(f, yaml.Loader)
        data = META_SCHEMA.validate(unchecked_data)

        for chapter_dict in data['chapters']:
            chapter = Chapter(filename=chapter_dict['filename'],
                              name=chapter_dict['name'])
            chapter.main_section = load_section(section_dict=chapter_dict['section'])
            self.chapters.append(chapter)

        self.process_ids()

    def add_chapter(self, chapter: Chapter):
        '''
        Add a chapter to list of chapters, and its dict version into data.

        :param chapter: a Chapter object to be added
        '''
        self.chapters.append(chapter)

    def iter_sections(self):
        '''
        :yields: each section of each chapter in the correct order
        '''
        for chapter in self.chapters:
            yield from chapter.iter_sections()

    def get_chapter(self, filename: str or PosixPath) -> Chapter:
        '''
        Get Chapter by its filename.

        :param filename: path to file, relative to execution dir or absolute.

        :returns: Chapter object for this filename or raises MetaChapterDoesNotExistError.
        '''
        for chapter in self.chapters:
            p1 = Path(chapter.filename).resolve()
            p2 = Path(filename).resolve()
            if p1 == p2:
                return chapter
        else:
            raise MetaChapterDoesNotExistError(f"Chapter {filename} does not exist")

    def process_ids(self):
        '''
        Validate section ids for dublicates;
        Fill up missing section ids based on their titles.
        '''
        ids = []
        for section in self.iter_sections():
            if 'id' in section.data:
                if section.data['id'] in ids:
                    raise MetaDublicateIDError(f'Dublicate ids: {section.data["id"]}')
                else:
                    section.id = section.data['id']
                    ids.append(section.id)

        for section in self.iter_sections():
            if section.id is None:
                section.id = convert_to_id(section.title, ids)
                ids.append(section.id)

    def get_by_id(self, id_: str) -> Section:
        '''
        Find section by id and return it or error.

        :param id: id of the section to be found

        :returns: Section object of queried id
        '''
        for section in self.iter_sections():
            if section.id == id_:
                return section
        else:
            raise MetaSectionDoesNotExistError(f"Can't find section with id {id_}")

    def dump(self):
        '''
        :returns: a meta dictionary ready to be saved into yaml-file
        '''
        return {'version': self.syntax_version,
                'chapters': [ch.to_dict() for ch in self.chapters]}

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.filename or "file name not specified"}>'

    def __getitem__(self, ind: int):
        return self.chapters[ind]

    def __iter__(self):
        return iter(self.chapters)

    def __len__(self):
        return len(self.chapters)


class Chapter:
    def __init__(self, filename: str, name: str, main_section: Section = None):
        self.name = name
        self.filename = filename
        self._main_section = None
        if main_section:
            self.main_section = main_section

    @property
    def main_section(self):
        return self._main_section

    @main_section.setter
    def main_section(self, value: Section):
        self._main_section = value
        self._main_section.chapter = self
        for child in self._main_section.iter_children():
            child.chapter = self
        if not self._main_section.title:
            self._main_section.title = self.name

    def get_section_by_offset(self, offset: int) -> Section:
        '''
        Get the lowest-level meta-section for the place in text described by
        offset.

        :param offset: offset of the place in source

        :returns: section for the requested place in text.
        '''
        if offset > self.main_section.end:
            raise IndexError("Offset cannot be bigger than the chapter's length"
                             f" ({offset} > {self.main_section.end})")
        result = None
        for section in self.iter_sections():
            if (section.start <= offset) and (section.end >= offset):
                result = section
            if section.start > offset:
                break
        return result

    def to_dict(self):
        ''' :returns: a dictionary ready to be saved into yaml-file'''
        return {'name': self.name,
                'filename': self.filename,
                'section': self._main_section.to_dict()}

    def iter_sections(self):
        ''':yields: the main section and each subsection in the correct order'''
        yield self._main_section
        for child in self._main_section.children:
            yield child
            yield from child.iter_children()

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.name}>'


class Section:
    def __init__(self,
                 level: int,
                 start: int,
                 end: int,
                 data: dict = {},
                 title: str = ''):
        self.title = title
        self.level = level
        self.start = start
        self.end = end
        self.children = []
        self._parent = None
        self.id = None
        self.chapter = None
        self.data = data

    def add_child(self, section):
        '''
        - Check that potential child has a higher level and add it to the children
        list attribute.
        - Also set its chapter to be the same as this section's chapter
        - and specify this section as child's parent.

        :param section: a Section object to be added as a child
        '''
        if section.level <= self.level:
            raise MetaHierarchyError("Error adding child. Child level must be"
                                     f" higher than parent's. {section.level} <= {self.level}")
        self.children.append(section)
        section.chapter = self.chapter
        section.parent = self

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, section):
        self._parent = section

    @property
    def filename(self):
        '''link to this section's chapter filename'''
        return self.chapter.filename

    def is_main(self) -> bool:
        '''Determine whether the section is main or not'''
        return self.level == 0 and self.parent is None

    def to_dict(self):
        ''':returns: a dictionary ready to be saved into yaml-file'''
        return {'id': self.id,
                'title': self.title,
                'level': self.level,
                'data': self.data,
                'start': self.start,
                'end': self.end,
                'children': [child.to_dict() for child in self.children]}

    def iter_children(self):
        ''':yields: each subsection in the correct order'''
        for child in self.children:
            yield child
            yield from child.iter_children()

    def get_source(self, without_meta=True) -> str:
        '''
        Get section source text.

        :param without_meta: if True — all meta tags will be removed from the
                             returned source.

        :returns: section source
        '''

        if not self.chapter:
            raise MetaChapterNotAssignedError('Chapter is not assigned. Can\'t determine filename.')
        with open(self.chapter.filename) as f:
            chapter_source = f.read()

        source = chapter_source[self.start: self.end]
        if without_meta:
            source = remove_meta(source)
        return source

    def __repr__(self):
        short_name = self.title[:20] + '...' if len(self.title) > 23 else self.title
        return f'<{self.__class__.__name__}: [{self.level}] {short_name}>'
