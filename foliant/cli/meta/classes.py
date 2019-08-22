'''Module defining Meta class'''

from pathlib import Path, PosixPath
from yaml import load, Loader


class Meta:
    def __init__(self,
                 filename: str or PosixPath):
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
        self.name = chapter_dict['chapter']
        self.title = chapter_dict['title']
        self.yfm = chapter_dict['yfm']

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.name}>'
