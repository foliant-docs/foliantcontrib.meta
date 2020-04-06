import yaml
import re

from pathlib import Path, PosixPath
from logging import getLogger

from .patterns import (YFM_PATTERN, META_TAG_PATTERN, OPTION_PATTERN,
                       HEADER_PATTERN, CHUNK_PATTERN)

logger = getLogger('flt.meta')


def flatten_seq(seq):
    """convert a sequence of embedded sequences into a plain list"""
    result = []
    vals = seq.values() if type(seq) == dict else seq
    for i in vals:
        if isinstance(i, (dict, list)):
            result.extend(flatten_seq(i))
        elif isinstance(i, str):
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
    '''
    Look for YAML Front Matter and return resulting dict.
    If there is no YFM — return empty dict.
    '''
    data = {}
    yfm_match = YFM_PATTERN.search(source)
    if yfm_match:
        logger.debug(f'Found YFM:\n{yfm_match.group("yaml")}')
        data = yaml.load(yfm_match.group('yaml'), yaml.Loader)
    return data


def get_meta_dict_from_meta_tag(source: str) -> dict or None:
    '''
    Look for meta tags in the source resulting dict of metadata.
    If there are no meta tags in source — return None.
    If there are several — choose the first one.

    :param source: section source without title

    :returns: meta dict or None if no meta tags in section.
    '''
    data = None
    meta_match = META_TAG_PATTERN.search(source)
    if meta_match:
        logger.debug(f'Found meta tag: \n{meta_match.group(0)}')
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
    '''
    yfm_offset = 0
    if source.startswith('---\n'):
        # cut out YFM manually, otherwise the regex pattern considers
        # YAML comments as headings
        pattern = re.compile(r'^---[\s\S]+\n---$', re.MULTILINE)

        match = pattern.search(source)
        if match:
            # compensate chunks offsets for removed YFM
            yfm_offset = match.end()
            source = pattern.sub('', source, 1)

    for chunk in CHUNK_PATTERN.finditer(source):
        yield (chunk.group('title'),
               len(chunk.group('level')),
               chunk.group('content'),
               chunk.start() + yfm_offset,
               chunk.end() + yfm_offset)


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


def remove_meta(source: str):
    '''
    Remove meta tags from source string. Whitespaces in the beginning of the
    file are also trimmed

    :param source: source string where meta tags should be removes.

    :returns: source string with meta tags removed
    '''
    result = YFM_PATTERN.sub('', source).lstrip(' \n')
    result = META_TAG_PATTERN.sub('', result)
    return result


def get_processed(*args, **kwargs):
    raise RuntimeError('Please update Confluence backend to the latest version!')
