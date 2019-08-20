'''
Preprocessor for Foliant documentation authoring tool.
Removes section meta-data from the document and adds seeds.
'''
from foliant.preprocessors.base import BasePreprocessor
from foliant.meta_commands.generate import generate_meta, get_mark


class Preprocessor(BasePreprocessor):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logger = self.logger.getChild('meta')

        self.logger.debug(f'Preprocessor inited: {self.__dict__}')

    def mark_meta_blocks(self, content: str, chapter) -> str:
        offset = 0
        for section in chapter:
            ms = get_mark('start',
                          section.chapter.name,
                          section.name)
            me = get_mark('end',
                          section.chapter.name,
                          section.name)
            start = section.span[0] + offset
            end = section.span[1] + offset
            content = content[:start] + ms + content[start:end] + me +\
                content[end:]
            offset += len(ms + me)
        return content

    def apply(self):
        self.logger.info('Applying preprocessor')
        self.logger.info('Generating meta')
        meta = generate_meta(self.context, self.logger)

        for chapter in meta:
            chapter_filename = self.working_dir / chapter.name
            with open(chapter_filename) as f:
                content = f.read()

            processed_content = self.mark_meta_blocks(content, chapter)

            with open(chapter_filename, 'w') as f:
                f.write(processed_content)

        self.logger.info('Preprocessor applied')
