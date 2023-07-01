from pathlib import Path

import pytest

from singular import implement, singular


@pytest.fixture
def initialized_cyclers():
    initializers = (
        implement.biologic,
        implement.ivium,
        implement.neware,
        implement.squidstat
    )
    return implement.initialize(initializers)


def test_initialize_cyclers(initialized_cyclers):
    
    assert isinstance(initialized_cyclers, list)

    for cycler in initialized_cyclers:
        assert isinstance(cycler, singular.Cycler)


def test_match_cycler(initialized_cyclers, dummy_ids):

    for dummy_id in dummy_ids.values():
        cycler, path = implement.match_cycler(
            cyclers=initialized_cyclers,
            id_=dummy_id
        )

        assert isinstance(cycler, singular.Cycler)
        assert isinstance(path, Path)


def test_load(dummy_ids, expected_columns):
    for dummy_id in dummy_ids.values():
        echem = implement.load(id_=dummy_id)

    for expected_column in expected_columns:
        assert expected_column in echem.columns
