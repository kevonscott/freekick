import os

from freekick.utils.freekick_config import _set_environ

# Use testing.env variables for testing configuation
_set_environ(environment="TEST")


def ensure_test_env():
    """Ensures we are using test env for testing.

    Import this function at the top of each test file.
    This method shoud not really be needed when calling tests from the command
    line and the one-liner above is enough to set the env for all tests before
    execution. However, IDEs such as vscode will encounter errors in test
    discovery because the env is not set beforehand. Therefore, this is just a
    convenience funtion that triggers the line above upon import and often do
    not enven need to execute this function.
    """
    current_env: str | None = os.environ.get("DEV", None)
    if not current_env or current_env != "TEST":
        _set_environ(environment="TEST")