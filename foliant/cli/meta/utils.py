from pathlib import Path, PosixPath
from .classes import Chapter, Section


def get_source(chapter: Chapter, src_dir: str or PosixPath) -> str:
    '''get source of a chapter'''
    chapter_file = Path(src_dir) / chapter.name
    with open(chapter_file, encoding='utf8') as f:
        return f.read()


def get_section_source(section: Section, src_dir: str or PosixPath) -> str:
    '''get source of a chapter'''
    chapter_source = get_source(section.chapter, src_dir)
    return chapter_source[section.start: section.end]


def get_processed(chapter: Chapter, working_dir: str or PosixPath) -> str:
    '''get processed chapter text'''
    chapter_file = Path(working_dir) / chapter.name
    with open(chapter_file, encoding='utf8') as f:
        return f.read()


def get_processed_section(section: Section, working_dir: str or PosixPath) -> str:
    chapter_content = get_processed(section.chapter, working_dir)
