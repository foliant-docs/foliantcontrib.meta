'''Module defining load_meta function for generating metadata from md-sources'''

import re

from pathlib import Path, PosixPath
from logging import getLogger

from .tools import (FlatChapters, get_meta_dict_from_yfm,
                    get_meta_dict_from_meta_tag, iter_chunks,
                    get_header_content)
from .classes import Meta, Chapter, Section

logger = getLogger('flt.meta')


class Chunk:
    '''
    Mini-class for a part of MD-source from one heading to the next of same
    or lower level
    '''

    __slots__ = ['title', 'level', 'content', 'start', 'end']

    def __init__(self, title: str, level: int,
                 content: str, start: int, end: int):
        self.title = title
        self.level = level
        self.content = content
        self.start = start
        self.end = end

    def __repr__(self):
        return f'<Chunk: [{self.level}] {self.title[:15]}>'


def load_meta(chapters: list, md_root: str or PosixPath = 'src') -> Meta:
    '''
    Collect metadata from chapters list and load them into Meta class.

    :param chapters: list of chapters from foliant.yml
    :param md_root: root folder where the md-files are stored. Usually either
                    <workingdir> or <srcdir>

    :returns: Meta object
    '''
    logger.debug(f'LOAD_META start.\nchapters: {chapters}\nmd_root: {md_root}')

    c = FlatChapters(chapters=chapters, parent_dir=md_root)

    meta = Meta()
    for path_ in c.paths:
        name = str(path_.relative_to(md_root))
        chapter = get_meta_for_chapter(path_, name)
        if chapter:
            meta.add_chapter(chapter)

    meta.process_ids()
    return meta


def get_meta_for_chapter(ch_path: str or PosixPath,
                         name: str or None = None) -> Chapter:
    '''
    Get metadata for one chapter.

    :param ch_path: path to chapter source file.
    :param name:    chapter name. If None — it's equal to ch_path.

    :returns: a Chapter object.
    '''
    chapter_path = Path(ch_path)
    logger.debug(f'Getting meta for chapter {chapter_path}')
    if not chapter_path.exists():
        logger.debug(f'Chapter does not exist, skipping')
        return None
    with open(chapter_path, encoding='utf8') as f:
        content = f.read()

    chapter = Chapter(filename=str(chapter_path),
                      name=name or str(chapter_path))
    header, chunks = split_by_headings(content)

    main_section = get_section(header)
    if chunks and not get_section(chunks[0]) and chunks[0].level == 1:
        # if the first heading is of level 1 (#) and doesn't have meta, set main
        #  section's title to this heading value
        main_section.title = chunks[0].title
    chapter.main_section = main_section

    current_section = main_section
    for chunk in chunks:
        section = get_section(chunk)
        if section:  # look for parent section
            while section.level <= current_section.level:
                current_section = current_section.parent
            current_section.add_child(section)
            current_section = section

    return chapter


def split_by_headings(content: str) -> (Chunk, [Chunk]):
    '''
    Split content string into Chunk objects by headings. Return a tuple of
    (header, chunks), where header is a Chunk object for header (content before
    first heading), and chunks is a list of Chunk objects for other headings.

    :param content: content string to be split into chunks

    :returns: a tuple with two elements:
        (a header Chunk object,
         a list of title Chunk objects)
    '''

    header = Chunk(title='',
                   level=0,
                   content=get_header_content(content),
                   start=0,
                   end=len(content))

    chunks = []
    for title, level, content, start, end in iter_chunks(content):
        chunks.append(Chunk(title, level, content, start, end))

    fix_chunk_ends(chunks)

    return header, chunks


def fix_chunk_ends(chunks: list):
    '''
    Fix chunks `end` parameter (in place).

    After splitting content into chunks each chunk's end parameter value is
    the beginning of next heading. We need to fix that to the beginning of
    the next heading _of the same or higher level_.

    :param chunks: list of Chunk objects to be fixed
    '''

    for i in range(len(chunks) - 1):
        j = i + 1
        while (chunks[j].level > chunks[i].level):
            j += 1
            if j == len(chunks):  # reached the end of the document
                break
        chunks[i].end = chunks[j - 1].end


def get_section(chunk: Chunk) -> Section or None:
    '''
    Parse chunk content and create a Section object from its metadata.
    If no metadata in chunk — return None.
    '''
    logger.debug(f'Parsing chunk {chunk}')
    yfm_data = None
    if chunk.level == 0:  # main section
        # main section must always be present in header (0-level chunk), but it
        # may be overriden by metadata in <meta> tag, which has higher priority
        yfm_data = get_meta_dict_from_yfm(chunk.content)

    tag_data = get_meta_dict_from_meta_tag(chunk.content)

    data = tag_data if tag_data is not None else yfm_data
    title = re.sub('{#.+?}$', '', chunk.title).strip()
    if data is not None:
        logger.debug(f'Adding section. Title: {title}, data: {data}')
        result = Section(chunk.level, chunk.start, chunk.end,
                         data, title=title)
        return result
