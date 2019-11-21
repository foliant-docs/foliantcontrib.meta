import yaml

from pathlib import Path, PosixPath
from .patterns import (YFM_PATTERN, META_TAG_PATTERN, OPTION_PATTERN,
                       HEADER_PATTERN, CHUNK_PATTERN)


def flatten_seq(seq):
    """convert a sequence of embedded sequences into a plain list"""
    result = []
    vals = seq.values() if type(seq) == dict else seq
    for i in vals:
        if type(i) in (dict, list):
            result.extend(flatten_seq(i))
        else:
            result.append(i)
    return result


class FlatChapters:
    """
    Helper class converting chapter list of complicated structure
    into a plain list of chapter names or path to actual md files
    in the src dir.
    """

    def __init__(self,
                 chapters: list,
                 parent_dir: PosixPath = Path('src')):
        self._chapters = chapters
        self._parent_dir = Path(parent_dir)

    def __len__(self):
        return len(self.flat)

    def __getitem__(self, ind: int):
        return self.flat[ind]

    def __contains__(self, item: str):
        return item in self.flat

    def __iter__(self):
        return iter(self.flat)

    @property
    def flat(self):
        """Flat list of chapter file names"""
        return flatten_seq(self._chapters)

    @property
    def list(self):
        """Original chapters list"""
        return self._chapters

    @property
    def paths(self):
        """Flat list of PosixPath objects relative to project root."""
        return (self._parent_dir / chap for chap in self.flat)


def get_meta_dict_from_yfm(source: str) -> dict:
    '''Look for YAML Front Matter and return resulting dict'''
    data = None
    yfm_match = YFM_PATTERN.search(source)
    if yfm_match:
        data = yaml.load(yfm_match.group('yaml'), yaml.Loader)
    return data or {}


def get_meta_dict_from_meta_tag(source: str) -> dict or None:
    '''
    Look for meta tags in the source resulting dict of metadata.
    If there are no meta tags in source — return None.

    :param source: section source without title

    :returns: meta dict or None if no meta tags in section.
    '''
    data = None
    meta_match = META_TAG_PATTERN.search(source)
    if meta_match:
        option_string = meta_match.group('options')
        if not option_string:
            data = {}
        else:
            data = {option.group('key'): yaml.load(option.group('value'),
                                                   yaml.Loader)
                    for option in OPTION_PATTERN.finditer(option_string)}
    return data


def get_header_content(source: str) -> str:
    '''
    Search source for header (content before first heading) and return it.
    If there's no first heading — return the whole source.

    TODO: the pattern breaks on a commented line in YFM
    '''
    main_match = HEADER_PATTERN.search(source)
    if main_match:
        return main_match.group('content')
    else:
        return source


def iter_chunks(source: str):
    '''
    Split source string by headings and return each heading with its content
    and level.

    :param source: source string to parse.

    :returns: iterator yielding tuple:
        (heading title,
         heading level,
         heading content,
         start position,
         end position)

    TODO: seems that this pattern also is far from perfect
    '''
    for chunk in CHUNK_PATTERN.finditer(source):
        yield (chunk.group('title'),
               len(chunk.group('level')),
               chunk.group('content'),
               chunk.start(),
               chunk.end())
