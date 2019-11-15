from logging import Logger

from foliant.cli.meta.classes import Meta
from .command import MetaCommand


def generate_meta(context: dict, logger: Logger):
    '''
    Helper function to generate meta.yml to be run from anywhere

    Returns meta filename (relative to project root).
    '''
    meta_command = MetaCommand(context, logger)
    meta_command.run()
    return Meta(meta_command.options['filename'])
