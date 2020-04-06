'''Module holding various re patterns used by meta subsystem'''

import re


YFM_PATTERN = re.compile(r'^---(?P<yaml>.+?\n)---', re.DOTALL)

META_TAG_PATTERN = re.compile(
    rf'(?<!\<)\<meta(\s(?P<options>[^\<\>]*))?\>' +
    rf'(?P<body>.*?)\<\/meta\>',
    flags=re.DOTALL
)

OPTION_PATTERN = re.compile(
    r'(?P<key>[A-Za-z_:][0-9A-Za-z_:\-\.]*)=(\'|")(?P<value>.+?)\2',
    flags=re.DOTALL
)

HEADER_PATTERN = re.compile(r'^(?P<content>[\s\S]*?)(?=^#{1,6} .+)',
                            flags=re.MULTILINE)

CHUNK_PATTERN = re.compile(r'^(?P<level>#{1,6}) (?P<title>.+)\n(?P<content>(^(?!#{1,6} ).*\n?)+)',
                           flags=re.MULTILINE)
