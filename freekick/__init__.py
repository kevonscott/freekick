import platform
from pathlib import Path

from packaging.version import Version

from .utils._version import __version__
from .utils.freekick_logging import _logger

ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
ESTIMATOR_LOCATION = DATA_DIR / "learner_model"

# Ensure we are using the min_supported_platform
# We also need to ensure this only executes once and not all imports.
# TODO: Maybe use sitecustomize.py for checking instead?
_PLATFORM_CHECK = False
if not _PLATFORM_CHECK:
    min_supported_platform = Version("3.10.0")
    current_platform = Version(platform.python_version())
    if current_platform < min_supported_platform:
        raise RuntimeError(
            f"Unsupported platform {current_platform}! The minimum supported"
            f" Python version is {min_supported_platform}"
        )
    _PLATFORM_CHECK = True
