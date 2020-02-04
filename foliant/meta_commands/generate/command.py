'''Meta command which generates the meta file'''

import yaml

from foliant.meta_commands.base import BaseMetaCommand

from foliant.meta.generate import load_meta


class MetaCommand(BaseMetaCommand):
    '''Meta command which generates the meta file'''
    defaults = {'filename': 'meta.yml'}
    config_section = 'meta'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.meta = None

    def _gen_meta(self):
        '''Generate meta yaml and return it as string'''

        if 'chapters' not in self.config:
            return ''
        self.meta = load_meta(self.config['chapters'])

    def run(self):
        self.logger.debug('Meta command generate started')

        self._gen_meta()
        with open(self.options['filename'], 'w', encoding='utf8') as f:
            yaml.dump(self.meta.dump(),
                      f,
                      default_flow_style=False,
                      allow_unicode=True,
                      sort_keys=False)
        self.meta.filename = self.options['filename']

        self.logger.debug('Meta command generate finished')
