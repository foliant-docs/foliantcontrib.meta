import re
import yaml

from pathlib import PosixPath
from .tools import FlatChapters
from foliant.cli.meta.classes import Meta, Chapter, Section

YFM_PATTERN = re.compile(r'^\s*---(?P<yaml>.+?\n)---', re.DOTALL)

META_TAG_PATTERN = re.compile(
    rf'(?<!\<)\<meta(\s(?P<options>[^\<\>]*))?\>' +
    rf'(?P<body>.*?)\<\/meta\>',
    flags=re.DOTALL
)
OPTION_PATTERN = re.compile(
    r'(?P<key>[A-Za-z_:][0-9A-Za-z_:\-\.]*)=(\'|")(?P<value>.+?)\2',
    flags=re.DOTALL
)


class Chunk:
    __slots__ = ['title', 'level', 'content', 'start', 'end']

    def __init__(self, title, level, content, start, end):
        self.title = title
        self.level = level
        self.content = content
        self.start = start
        self.end = end

    def __repr__(self):
        return f'<Chunk: [{self.level}] {self.title[:15]}>'


def get_section(chunk: Chunk):
    data = None
    if chunk.level == 0:  # main section
        data = {}  # main section must always be present
        yfm_match = YFM_PATTERN.search(chunk.content)
        if yfm_match:
            data = yaml.load(yfm_match.group('yaml'), yaml.Loader)
    meta_match = META_TAG_PATTERN.search(chunk.content)
    if meta_match:
        option_string = meta_match.group('options')
        if not option_string:
            data = {}
        else:
            data = {option.group('key'): yaml.load(option.group('value'),
                                                   yaml.Loader)
                    for option in OPTION_PATTERN.finditer(option_string)}
    if data is not None:
        result = Section(chunk.level, chunk.start, chunk.end,
                         data, title=chunk.title)
        return result


def split_by_headings(content: str):
    '''
    Split content string into Chunk objects by headings. Return a tuple of
    (header, chunks), where header is a Chunk object for header (content before
    first heading), and chunks is a list of Chunk objects for other headings.
    '''

    # TODO: this pattern breaks on a commented line in YFM
    main_pattern = re.compile(r'^(?P<content>[\s\S]*?)(?=^#+ .+)',
                              flags=re.MULTILINE)
    main_match = main_pattern.search(content)
    if main_match:
        header = Chunk('', 0, main_match.group('content'), 0, len(content))
    else:  # there are no headings in the chapter. Taking whole content as header
        header = Chunk('', 0, content, 0, len(content))

    chunks = []
    # TODO: seems that this patter also is far from perfect
    heading_section_pattern = \
        re.compile(r'^(?P<level>#+) (?P<title>.+)\n(?P<content>(?:\n[^#]*)+)',
                   flags=re.MULTILINE)
    for heading_section in heading_section_pattern.finditer(content):
        chunk = Chunk(heading_section.group('title'),
                      len(heading_section.group('level')),
                      heading_section.group('content'),
                      heading_section.start(),
                      heading_section.end())
        chunks.append(chunk)

    # setting proper `end` parameters. For each heading `end` parameter is the
    # `start` of the heading of the same level or higher
    for i in range(len(chunks) - 1):
        j = i + 1
        while (chunks[j].level > chunks[i].level):
            j += 1
            if j == len(chunks):  # reached the end of the document
                break
        chunks[i].end = chunks[j - 1].end

    return header, chunks


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
        if char == '_' or char.isalpha():
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


def get_meta_for_chapter(ch_path: PosixPath, ids: list) -> Chapter:
    '''
    Get metadata for one chapter.

    :param ch_path: path to chapter source file.
    :param ids: — list of ids already used in metadata.

    :returns: a Chapter object.
    '''
    if not ch_path.exists():
        return
    with open(ch_path, encoding='utf8') as f:
        content = f.read()

    chapter = Chapter(filename=str(ch_path),
                      name=ch_path.stem)
    header, chunks = split_by_headings(content)

    main_section = get_section(header)
    chapter.main_section = main_section

    current_section = main_section
    for chunk in chunks:
        section = get_section(chunk)
        if section:
            while section.level <= current_section.level:
                current_section = current_section.parent
            current_section.add_child(section)
            current_section = section

    return chapter


def load_meta(chapters: list, md_root: str or PosixPath = 'src') -> Meta:
    '''
    Collect metadata from chapters list and load them into Meta class.

    :param chapters: list of chapters from foliant.yml
    :param md_root: root folder where the md-files are stored. Usually either
                    <workingdir> or <srcdir>

    :returns: Meta object
    '''
    c = FlatChapters(chapters=chapters, parent_dir=md_root)

    ids = []
    meta = Meta()
    for path_ in c.paths:
        chapter = get_meta_for_chapter(path_, ids)
        if chapter:
            meta.add_chapter(chapter)

    meta.fillup_missing_info()
    return meta
