from pathlib import Path

import pytest

from singular import implement, utils


def test_experiment_raise_exception_if_not_found():
    with pytest.raises(FileNotFoundError):
        utils.find_experiment('this_does_not_exist')


def test_find_experiment(dummy_filenames, base_directory):

    for filename in dummy_filenames.values():
        path = utils.find_experiment(filename)
        assert path == Path(base_directory, filename)


@pytest.fixture
def dummy_echem_for_fixing_cycle(dummy_filenames):
    dummy_file = dummy_filenames['ivium']

    return implement.load(dummy_file.split('.')[0])
    

def test_fix_cycle(dummy_echem_for_fixing_cycle):
    utils.fix_cycle(dummy_echem_for_fixing_cycle)

    # Difficult to test whether this fixes it correctly!
    assert sum(dummy_echem_for_fixing_cycle['cycle'].to_numpy()) > 0
    
    