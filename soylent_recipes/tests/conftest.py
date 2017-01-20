import pytest

# http://stackoverflow.com/a/30091579/1031434
from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE, SIG_DFL) # Ignore SIGPIPE

@pytest.fixture
def usda_data_dir(pytestconfig):
    '''
    USDA SR28 data dir
    '''
    return pytestconfig.rootdir / 'data/usda_nutrient_db_sr28'