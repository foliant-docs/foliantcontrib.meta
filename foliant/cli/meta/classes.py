'''Module defining Meta class'''

import yaml
import re

from schema import Schema, Optional
from pathlib import Path, PosixPath


SECTION_SCHEMA = Schema(
    {
        'title': str,
        'start': int,
        'end': int,
        'level': int,
        Optional('id'): str,
        Optional('children', default=[]): [dict],
        Optional('data', default={}): dict
    }
)

META_SCHEMA = Schema(
    [
        {
            'name': str,
            'section': SECTION_SCHEMA,
            'filename': str
        }
    ]
)


class MetaHierarchyError(Exception):
    pass


class MetaDublicateIDError(Exception):
    pass


class MetaSectionDoesNotExistError(Exception):
    pass


class MetaChapterNotAssignedError(Exception):
    pass


class Section:
    def __init__(self,
                 level: int,
                 start: int,
                 end: int,
                 data: dict = {},
                 title: str = '',
                 chapter=None):
        self.title = title
        self.level = level
        self.start = start
        self.end = end
        self.children = []
        self._parent = None
        self.id = None
        self.chapter = chapter
        self.data = data

    def add_child(self, section):
        '''
        Check that potential child has a higher level and add it to the children
        list attribute. Also set its chapter to be the same of this section's
        chapter and specify this section as child's parent.

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

    def get_source(self, remove_meta=True):
        '''
        Get section source text.

        :param remove_meta: if True — all meta tags will be removed from the
                            source.

        :returns: section source
        '''
        def remove_meta(source: str):
            ''':returns: source string with meta tags removed'''
            META_TAG_PATTERN = re.compile(
                rf'(?<!\<)\<meta(\s(?P<options>[^\<\>]*))?\>' +
                rf'(?P<body>.*?)\<\/meta\>',
                flags=re.DOTALL
            )
            return META_TAG_PATTERN.sub('', source)

        if not self.chapter:
            raise MetaChapterNotAssignedError('Chapter is not assigned. Can\'t determine filename.')
        with open(self.chapter.filename) as f:
            chapter_source = f.read()

        source = chapter_source[self.start: self.end]
        if remove_meta:
            source = remove_meta(source)
        return source

    def __repr__(self):
        short_name = self.title[:20] + '...' if len(self.title) > 23 else self.title
        return f'<{self.__class__.__name__}: [{self.level}] {short_name}>'


class Chapter:
    def __init__(self, filename: str, name: str, main_section: Section = None):
        self._main_section = Section
        self.name = name
        self.filename = filename

    @property
    def main_section(self):
        return self._main_section

    @main_section.setter
    def main_section(self, value: Section):
        self._main_section = value
        self._main_section.chapter = self

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


def convert_to_id(title: str, existing_ids: list) -> str:
    '''
    (based on convert_to_anchor function from apilinks preprocessor)
    Convert heading into id. Guaranteed to be unique among `existing_ids`.

    >>> convert_to_id('GET /endpoint/method{id}')
    'get-endpoint-method-id'
    '''

    id_ = ''
    accum = False
    for char in title:
        if char == '_' or char.isalnum():
            if accum:
                accum = False
                id_ += f'-{char.lower()}'
            else:
                id_ += char.lower()
        else:
            accum = True
    id_ = id_.strip(' -')

    counter = 1
    result = id_
    while result in existing_ids:
        counter += 1
        result = '-'.join([id_, str(counter)])
    existing_ids.append(result)
    return result


class Meta:
    def __init__(self,
                 filename: str or PosixPath or None = None):
        self.data = []
        self.chapters = []
        if filename and Path(filename).exists():
            self.load_meta_from_file(filename)
        else:
            self.filename = None

    def load_meta_from_file(self, filename: str or PosixPath):
        '''
        Load metadata from yaml-file into the Chapter and Section objects and
        save them into the attributes of this Meta object instance.

        :param filename: the name of the yaml-file with metadata.
        '''
        def load_section(section_dict: dict,
                         chapter: Chapter) -> Section:
            '''
            Create a section from the dictionary with its data, recursively
            creating all the child sections and connecting them together.

            :param section_dict: dictionary with section data, loaded from meta yaml
            :param chapter: Chapter object into which the section must be included

            :returns: a constructed Section object
            '''
            data = SECTION_SCHEMA.validate(section_dict)
            section = Section(level=data['level'],
                              start=data['start'],
                              end=data['end'],
                              data=data['data'],
                              title=data['title'],
                              chapter=chapter)
            for child in data['children']:
                section.add_child(load_section(child, chapter))
            return section

        self.filename = Path(filename)

        with open(filename) as f:
            unchecked_data = yaml.load(f, yaml.Loader)
        self.data = META_SCHEMA.validate(unchecked_data)

        for chapter_dict in self.data:
            chapter = Chapter(filename=chapter_dict['filename'],
                              name=chapter_dict['name'])
            chapter.main_section = load_section(section_dict=chapter_dict['section'],
                                                chapter=chapter)
            self.chapters.append(chapter)

    def add_chapter(self, chapter: Chapter):
        '''
        Add a chapter to list of chapters, and its dict version into data.

        :param chapter: a Chapter object to be added
        '''
        self.chapters.append(chapter)
        self.data.append(chapter.to_dict())

    def iter_sections(self):
        '''
        :yields: each section of each chapter in the correct order
        '''
        for chapter in self.chapters:
            yield from chapter.iter_sections()

    def fillup_missing_info(self):
        '''Fill up missing sections info like titles and ids from their properties.'''
        ids = []
        for section in self.iter_sections():
            if 'id' in section.data:
                if section.data['id'] in ids:
                    raise MetaDublicateIDError(f'Dublicate ids: {section.data["id"]}')
                else:
                    section.id = section.data['id']
                    ids.append(section.id)

        for chapter in self.chapters:
            if not chapter.main_section.title:
                chapter.main_section.title = chapter.name

        for section in self.iter_sections():
            if not section.id:
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
        :returns: a list of chapter dicts ready to be saved into yaml-file
        '''
        return [ch.to_dict() for ch in self.chapters]

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.filename or "file name not specified"}>'

    def __getitem__(self, ind: int):
        return self.chapters[ind]

    def __iter__(self):
        return iter(self.chapters)

    def __len__(self):
        return len(self.chapters)
