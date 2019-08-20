'''Module defining Meta class'''

from pathlib import Path, PosixPath
from yaml import load, Loader


def get_mark(mode, chapter, section: str) -> str:
    return '\n\n<!-- meta {mode} {chapter}:{section} -->\n\n'.format(**locals())


class Meta:
    def __init__(self, filename: str or PosixPath):
        with open(filename) as f:
            self._data = load(f.read(), Loader)
        self.filename = Path(filename)
        self.chapters = [Chapter(c) for c in self._data]

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.filename}>'

    def __getitem__(self, ind: int):
        return self.chapters[ind]

    def __iter__(self):
        return iter(self.chapters)

    def __len__(self):
        return len(self.chapters)


class Chapter:
    def __init__(self, chapter_dict: dict):
        self._data = chapter_dict
        self.name = chapter_dict['name']
        self.sections = [Section(n, s, self)
                         for n, s in chapter_dict['sections'].items()]

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.name}>'

    def __getitem__(self, ind: int):
        return self.sections[ind]

    def __iter__(self):
        return iter(self.sections)

    def __len__(self):
        return len(self.sections)


class Section:
    def __init__(self, name: str, section_dict: dict, chapter):
        self._data = section_dict
        self.chapter = chapter
        self.name = name
        self.title = section_dict['title']
        self.span = section_dict['span']
        self.yfm = section_dict['yfm']

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.name}>'

    def __getitem__(self, ind: str):
        return self.yfm[ind]

    def __contains__(self, ind: str):
        return ind in self.yfm

    def __iter__(self):
        return iter(self.yfm)

    def source(self, src_path: str or PosixPath = Path('src')):
        with open(src_path / self.name) as f:
            return f.read()[self.span[0]:self.span[1]]

    def get(self, key, default=None):
        return self.yfm.get(key, default)

    def keys(self):
        return self.yfm.keys()

    def items(self):
        return self.yfm.items()

    def values(self):
        return self.yfm.values()

    def get_processed_text(self, workdir: str or PosixPath):
        with open(Path(workdir) / self.chapter.name) as f:
            text = f.read()
        start_mark = get_mark('start', self.chapter.name, self.name)
        start = text.index(start_mark) + len(start_mark)
        end = text.index(get_mark('end', self.chapter.name, self.name))
        return text[start:end]
