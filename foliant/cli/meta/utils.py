from foliant.meta_commands.generate.patterns import META_TAG_PATTERN, YFM_PATTERN


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
    ''':returns: source string with meta tags removed'''
    result = YFM_PATTERN.sub('', source)
    result = META_TAG_PATTERN.sub('', result)
    return result


def get_processed(*args, **kwargs):
    raise RuntimeError('Please update Confluence backend to the latest version!')
