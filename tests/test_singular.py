import pytest

from singular import implement, singular

mapper_fields = {
    'time': 'time',
    'current': 'current',
    'cycle': 'cycle',
    'voltage': 'voltage',
    'capacity': 'capacity',
    'dcapacity': 'dcapacity'
}


@pytest.fixture
def mapper():
    return singular.Mapper(**mapper_fields)


def test_mapper_initialization(mapper):
    assert isinstance(mapper, singular.Mapper)


def test_mapper_fields(mapper):
    assert mapper.__dict__ == mapper_fields


def test_mapper_flip(mapper):
    """Absolutely stupid test bc I'm relying on symmetry."""
    assert mapper.flip() == mapper_fields


def test_cycler_parse(cycler):
    pass


@pytest.fixture
def biologic(dummy_filenames):
    biologic = implement.biologic()

    return biologic.load(dummy_filenames['biologic'])


def test_biologic_load(biologic):

    assert len(biologic.timeseries) > 0


def test_biologic_parse(biologic, expected_columns):
    biologic.parse()

    assert biologic.timeseries.index.name == 'time'

    expected_columns.extend(['capacity', 'dcapacity'])
    
    for column in expected_columns:
        assert column in biologic.timeseries.columns


@pytest.fixture
def ivium(dummy_filenames):
    ivium = implement.ivium()

    return ivium.load(dummy_filenames['ivium'])


def test_ivium_load(ivium):    
    assert len(ivium.timeseries) > 0


def test_ivium_parse(ivium, expected_columns):
    assert ivium.timeseries.index.name == 'time'

    for column in expected_columns:
        assert column in ivium.timeseries.columns


@pytest.fixture
def neware(dummy_filenames):
    neware = implement.neware()

    return neware.load(dummy_filenames['neware'])


def test_neware_load(neware):
    assert len(ivium.timeseries) > 0


def test_neware_parse(neware, expected_columns):
    assert neware.timeseries.index.name == 'time'

    for column in expected_columns:
        assert column in neware.timeseries.columns

@pytest.fixture
def squidstat(dummy_filenames):
    squidstat = implement.squidstat()

    return squidstat.load(dummy_filenames['squidstat'])


def test_squidstat_load(squidstat):
    assert len(ivium.timeseries) > 0


def test_squidstat_parse(squidstat, expected_columns):
    assert squidstat.timeseries.index.name == 'time'

    for column in expected_columns:
        assert column in squidstat.timeseries.columns