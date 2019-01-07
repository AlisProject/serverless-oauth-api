option = None


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
