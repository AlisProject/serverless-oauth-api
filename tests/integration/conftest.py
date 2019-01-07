import pytest
from .common import api_deploy, api_remove, get_endpoint_url
option = None

@pytest.fixture(scope='session', autouse=True)
def setup_teardown():
    api_deploy(option.stage, option.region)
    yield
    api_remove(option.stage, option.region)

@pytest.fixture(scope='module', autouse=True)
def endpoint():
    yield(get_endpoint_url(option.stage, option.region))

def pytest_addoption(parser):
    parser.addoption(
        "--stage", action='store', help="stage name"
    )

    parser.addoption(
        "--region", action='store', help="region"
    )


def pytest_configure(config):
    global option
    option = config.option
