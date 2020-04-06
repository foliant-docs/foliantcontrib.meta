import os

from pathlib import Path

TEST_DATA_PATH = Path(os.path.abspath(__file__)).parent / 'test_data'


def get_test_data_text(filename: str) -> str:
    '''Load text from a file in test_data folder and return it'''
    with open(TEST_DATA_PATH / filename, encoding='utf8') as f:
        return f.read()
