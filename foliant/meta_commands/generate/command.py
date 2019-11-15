'''Meta command which generates the meta file'''

import yaml

from foliant.meta_commands.base import BaseMetaCommand
from foliant.cli.meta.classes import Meta

from .tools import FlatChapters
from .generate import load_meta


# def get_yfm(content: str):
#     '''Get YAML front matter from md-file content'''
#     match = re.search(YFM_PATTERN, content)
#     if match:
#         return yaml.load(match.group('yaml'), yaml.Loader)
#     else:
#         return {}


# def get_title(content: str, yfm: dict, ch_name: str):
#     '''Return proper title of the main section:

#     If field 'title' is in yfm — return its value;
#     If not — return first heading of the document;
#     If there are no headings — return the name of the file without extension.
#     '''
#     if 'title' in yfm:
#         return yfm['title']

#     pattern = re.compile(r'^#+\s+(.+)', re.MULTILINE)
#     match = re.search(pattern, content)
#     if match:
#         return match.group(1)
#     else:
#         return Path(ch_name).stem


def update_meta(context: dict, logger):
    '''
    Helper function to generate and update meta.yml to be run from anywhere

    :returns: meta filename (relative to project root).
    '''
    meta_command = MetaCommand(context, logger)
    meta_command.run()
    return Meta(meta_command.options['filename'])


def generate_meta(context, logger):
    '''
    for backward compatibility
    '''
    update_meta(context, logger)


class MetaCommand(BaseMetaCommand):
    '''Meta command which generates the meta file'''
    defaults = {'filename': 'meta.yml'}
    config_section = 'meta'

    def _gen_meta(self):
        '''Generate meta yaml and return it as string'''

        if 'chapters' not in self.config:
            return ''
        meta = load_meta(self.config['chapters'])
        return meta.dump()

    def run(self):
        self.logger.debug('Meta command generate started')

        meta = self._gen_meta()
        with open(self.options['filename'], 'w', encoding='utf8') as f:
            yaml.dump(meta,
                      f,
                      default_flow_style=False,
                      allow_unicode=True,
                      sort_keys=False)

        self.logger.debug('Meta command generate finished')
