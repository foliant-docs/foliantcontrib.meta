from .command import MetaCommand


def update_meta(context: dict, logger):
    '''
    Helper function to generate and update meta.yml to be run from anywhere

    :returns: meta filename (relative to project root).
    '''
    meta_command = MetaCommand(context, logger)
    meta_command.run()
    return meta_command.meta


def generate_meta(context, logger):
    '''
    for backward compatibility
    '''
    update_meta(context, logger)
