import json
import os

import pytest
import requests

with open('config.json', 'r') as file:
    config = json.load(file)

BASE_DIRECTORY: str = config['base_directory']
PARTIAL_PATHS = config['partial_paths']
DROPS = config['drops']

@pytest.fixture
def dummy_ids():
    return {
        'ivium': '20210621_c10x3_c3_acoustics60',
        'squidstat': '1_AP_Si_Formation_EIS-Open Circuit Potential 20230623 175329',
        'biologic': 'KS_2023_05_16_cont',
        'neware': 'GM_GT_FR2_2023_05_04_1'
    }

@pytest.fixture
def expected_columns():
    return ['voltage', 'current', 'cycle']  # in this order, needed for ivium


def download(partial_path, filename) -> None:
    """Download examples files of each format from our data lake."""

    path = generate_path(BASE_DIRECTORY, filename)

    if os.path.exists(path):
        return

    url = generate_path(DROPS['url'], partial_path)
    response = requests.get(url, auth=(DROPS['user'], DROPS['pass']))
    save(response=response, path=path)


def extract_filename(partial_path):
    return partial_path.split('/')[-1]


def generate_path(*parts):
    return '/'.join(parts)


def save(response, path):    
    with open(path , 'wb') as file:
        file.write(response.content)


@pytest.fixture(scope='session')
def base_directory():
    return BASE_DIRECTORY


@pytest.fixture(scope='session')
def dummy_filenames():
    dummy_filenames = dict()

    for cycler_type, partial_path in PARTIAL_PATHS.items():
        dummy_filenames[cycler_type] = extract_filename(partial_path)
        download(partial_path=partial_path, filename=dummy_filenames[cycler_type])

    return dummy_filenames
